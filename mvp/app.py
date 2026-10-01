"""Copiloto Rural — servidor del MVP.

Uso:  python3 app.py            (desde la carpeta mvp)
      PORT=8080 python3 app.py  (otro puerto)

Solo usa la biblioteca estándar de Python. Si está instalado el paquete
`anthropic` y existe ANTHROPIC_API_KEY, el asistente usa IA; si no, modo mock.
"""

import json
import mimetypes
import os
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from copiloto import asistente, conocimiento, db, servicios  # noqa: E402

mimetypes.add_type("application/manifest+json", ".webmanifest")
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("image/svg+xml", ".svg")

ESTATICOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
MAX_CUERPO = 256 * 1024


class Aplicacion:
    """Encapsula la conexión a la base para que los tests puedan usar una base aparte."""

    def __init__(self, ruta_db=None):
        self.con = db.conectar(ruta_db)
        db.inicializar(self.con)
        self.lock = threading.Lock()  # sqlite: una escritura por vez


def crear_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CopilotoRural/0.1"

        def log_message(self, formato, *args):
            if os.environ.get("COPILOTO_LOG") == "1":
                super().log_message(formato, *args)

        # -- utilidades ---------------------------------------------------
        def _json(self, datos, estado=HTTPStatus.OK):
            cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
            self.send_response(estado)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def _error(self, mensaje, estado=HTTPStatus.BAD_REQUEST):
            self._json({"error": mensaje}, estado)

        def _leer_json(self):
            largo = int(self.headers.get("Content-Length") or 0)
            if largo > MAX_CUERPO:
                raise servicios.ErrorDeDatos("El envío es demasiado grande")
            crudo = self.rfile.read(largo) if largo else b"{}"
            try:
                return json.loads(crudo.decode("utf-8") or "{}")
            except (UnicodeDecodeError, json.JSONDecodeError):
                raise servicios.ErrorDeDatos("JSON inválido")

        def _archivo(self, ruta_relativa, cache="no-cache"):
            ruta = os.path.normpath(os.path.join(ESTATICOS, ruta_relativa))
            if not ruta.startswith(ESTATICOS) or not os.path.isfile(ruta):
                return self._error("No encontrado", HTTPStatus.NOT_FOUND)
            tipo = mimetypes.guess_type(ruta)[0] or "application/octet-stream"
            if tipo.startswith("text/") or tipo in ("application/javascript", "application/json", "application/manifest+json"):
                tipo += "; charset=utf-8"
            with open(ruta, "rb") as f:
                cuerpo = f.read()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", cache)
            self.end_headers()
            self.wfile.write(cuerpo)

        # -- rutas --------------------------------------------------------
        def do_GET(self):  # noqa: N802
            url = urlparse(self.path)
            p = url.path
            q = parse_qs(url.query)
            try:
                if p in ("/", "/index.html"):
                    return self._archivo("index.html")
                if p == "/sw.js":
                    return self._archivo("sw.js")
                if p == "/manifest.webmanifest":
                    return self._archivo("manifest.webmanifest")
                if p.startswith("/static/"):
                    return self._archivo(p[len("/static/"):])
                if p == "/api/salud":
                    return self._json({"ok": True, "modo_asistente": "ia" if asistente.ia_disponible() else "mock"})
                if p == "/api/conocimiento":
                    return self._json(conocimiento.para_json())
                empresa_id = int((q.get("empresa_id") or ["1"])[0])
                with app.lock:
                    if p == "/api/empresa":
                        datos = servicios.datos_empresa(app.con, empresa_id)
                    elif p == "/api/tablero":
                        datos = servicios.tablero(app.con, empresa_id)
                    elif p.startswith("/api/operarios/") and p.endswith("/progreso"):
                        datos = servicios.progreso_operario(app.con, int(p.split("/")[3]))
                    else:
                        datos = None
                if datos is None:
                    return self._error("No encontrado", HTTPStatus.NOT_FOUND)
                return self._json(datos)
            except servicios.ErrorDeDatos as e:
                return self._error(str(e))
            except ValueError:
                return self._error("Parámetro inválido")

        def do_POST(self):  # noqa: N802
            p = urlparse(self.path).path
            try:
                datos = self._leer_json()
                with app.lock:
                    if p == "/api/checklists":
                        return self._json(servicios.registrar_checklist(app.con, datos), HTTPStatus.CREATED)
                    if p == "/api/calibraciones":
                        return self._json(servicios.registrar_calibracion(app.con, datos), HTTPStatus.CREATED)
                    if p == "/api/consultas":
                        return self._json(servicios.registrar_consulta(app.con, datos), HTTPStatus.CREATED)
                    if p == "/api/progreso":
                        return self._json(servicios.registrar_progreso(app.con, datos), HTTPStatus.CREATED)
                    if p == "/api/sync":
                        return self._json(servicios.sincronizar(app.con, datos.get("operaciones")))
                    if p.startswith("/api/consultas/") and p.endswith("/resolver"):
                        return self._json(servicios.resolver_consulta(app.con, int(p.split("/")[3])))
                return self._error("No encontrado", HTTPStatus.NOT_FOUND)
            except servicios.ErrorDeDatos as e:
                return self._error(str(e))
            except ValueError:
                return self._error("Parámetro inválido")

    return Handler


def crear_servidor(puerto=8000, ruta_db=None, host="0.0.0.0"):
    app = Aplicacion(ruta_db)
    servidor = ThreadingHTTPServer((host, puerto), crear_handler(app))
    servidor.app = app
    return servidor


def main():
    puerto = int(os.environ.get("PORT", "8000"))
    servidor = crear_servidor(puerto)
    modo = "IA (Claude)" if asistente.ia_disponible() else "mock (sin IA, respuestas de la base local)"
    print(f"Copiloto Rural andando en http://localhost:{puerto}  —  asistente en modo {modo}")
    print("Cortá con Ctrl+C.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nChau.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
