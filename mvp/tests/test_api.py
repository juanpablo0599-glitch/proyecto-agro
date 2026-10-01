"""Prueba de punta a punta: levanta el servidor real en un puerto libre y recorre el flujo principal."""

import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as servidor_app  # noqa: E402
from copiloto import conocimiento  # noqa: E402


class TestFlujoCompleto(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = mock.patch.dict(os.environ, {"COPILOTO_MOCK": "1"})
        cls.env.start()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.srv = servidor_app.crear_servidor(0, os.path.join(cls.tmp.name, "test.db"), host="127.0.0.1")
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        cls.hilo = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.hilo.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.srv.app.con.close()
        cls.tmp.cleanup()
        cls.env.stop()

    def pedir(self, ruta, datos=None):
        cuerpo = json.dumps(datos).encode() if datos is not None else None
        req = urllib.request.Request(self.base + ruta, data=cuerpo,
                                     headers={"Content-Type": "application/json"},
                                     method="POST" if datos is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                tipo = r.headers.get("Content-Type", "")
                crudo = r.read()
                return r.status, (json.loads(crudo) if "json" in tipo else crudo.decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def test_01_sirve_la_app_y_los_estaticos(self):
        estado, html = self.pedir("/")
        self.assertEqual(estado, 200)
        self.assertIn("Copiloto Rural", html)
        for ruta in ("/static/app.js", "/static/estilos.css", "/sw.js", "/manifest.webmanifest"):
            self.assertEqual(self.pedir(ruta)[0], 200, ruta)
        self.assertEqual(self.pedir("/static/../app.py")[0], 404)

    def test_02_salud_y_conocimiento(self):
        estado, salud = self.pedir("/api/salud")
        self.assertEqual(salud["modo_asistente"], "mock")
        estado, kb = self.pedir("/api/conocimiento")
        self.assertEqual(estado, 200)
        self.assertIn("sembradora", kb["checklists"])

    def test_03_flujo_maquinista_y_dueno(self):
        # El maquinista hace el checklist de la cosechadora y marca un crítico mal.
        items = {i["id"]: True for i in conocimiento.CHECKLISTS["cosechadora"]}
        items["radiador"] = False
        estado, ck = self.pedir("/api/checklists", {"uid": "e2e-1", "operario_id": 1, "maquina_id": 2,
                                                    "lote_id": 3, "items": items,
                                                    "observaciones": "Radiador tapado de pelusa"})
        self.assertEqual(estado, 201)
        self.assertEqual(ck["resultado"], "no_apta")

        # Calibra la pulverizadora.
        estado, cal = self.pedir("/api/calibraciones", {
            "operario_id": 2, "maquina_id": 3, "tipo": "pulverizadora",
            "entradas": {"volumen_l_ha": 80, "velocidad_km_h": 18, "distancia_picos_cm": 52.5,
                         "medidos_l_min": [1.26, 1.25, 1.27]}})
        self.assertEqual(estado, 201)
        self.assertTrue(cal["aprobada"])

        # Pregunta al asistente (mock).
        estado, q = self.pedir("/api/consultas", {"operario_id": 1, "maquina_id": 2,
                                                  "pregunta": "se pierde grano por la cola"})
        self.assertEqual(estado, 201)
        self.assertEqual(q["guia_id"], "cosecha_perdidas_cola")

        # Completa una lección.
        mod = conocimiento.MODULOS[4]
        estado, prog = self.pedir("/api/progreso", {"operario_id": 3, "modulo_id": mod["id"],
                                                    "respuestas": [p["correcta"] for p in mod["preguntas"]]})
        self.assertTrue(prog["aprobado"])

        # El dueño ve todo en el tablero.
        estado, t = self.pedir("/api/tablero")
        self.assertEqual(estado, 200)
        la_verde = next(m for m in t["maquinas"] if m["id"] == 2)
        self.assertEqual(la_verde["estado"], "parada")
        self.assertTrue(any("La Verde" in a["texto"] and a["nivel"] == "alta" for a in t["alertas"]))
        self.assertIn("impacto", t)

        # Constancia para el productor del lote 3, donde trabajó la cosechadora.
        estado, c = self.pedir("/api/lotes/3/constancia")
        self.assertEqual(estado, 200)
        self.assertEqual(c["labores"][0]["checklist"], "no_apta")
        self.assertEqual(self.pedir("/api/lotes/999/constancia")[0], 400)

    def test_04_sync_offline(self):
        ops = [{"tipo": "checklist", "datos": {"uid": "e2e-off", "operario_id": 3, "maquina_id": 6,
                                               "items": {i["id"]: True for i in conocimiento.CHECKLISTS["tractor"]}}}]
        estado, r = self.pedir("/api/sync", {"operaciones": ops})
        self.assertEqual(estado, 200)
        self.assertEqual(r["ok"], 1)
        estado, r = self.pedir("/api/sync", {"operaciones": ops})
        self.assertTrue(r["resultados"][0]["duplicado"])

    def test_05_errores_devuelven_400_o_404(self):
        self.assertEqual(self.pedir("/api/checklists", {"operario_id": 1})[0], 400)
        self.assertEqual(self.pedir("/api/no-existe")[0], 404)
        self.assertEqual(self.pedir("/api/operarios/abc/progreso")[0], 400)
        self.assertEqual(self.pedir("/api/sync", {"operaciones": "x"})[0], 400)
        req = urllib.request.Request(self.base + "/api/consultas", data=b"{no es json",
                                     headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=10)
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
