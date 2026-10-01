"""Arma la demo navegable de Copiloto Rural en un solo archivo HTML.

Uso (desde la carpeta mvp):  python3 demo/construir_demo.py

Junta en una página: los estilos y la app web (static/), el backend de demostración
(demo/backend_demo.js, que reemplaza al servidor Python dentro del navegador) y los datos
de ejemplo y la base de conocimiento, que salen del mismo código Python (db.py,
conocimiento.py, asistente.py). Así la demo y el MVP comparten contenido.

La salida (demo/copiloto-demo.html) es el cuerpo de la página sin <html>/<head>/<body>,
que es el formato que usa la publicación como Artifact en claude.ai.
"""

import json
import os
import sys
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
MVP = os.path.dirname(AQUI)
sys.path.insert(0, MVP)

from copiloto import asistente, conocimiento, db  # noqa: E402

SALIDA = os.path.join(AQUI, "copiloto-demo.html")

COLUMNAS_JSON = {"items_json": "items", "entradas_json": "entradas", "resultado_json": "resultado"}


def datos_de_ejemplo():
    generado = datetime.now().replace(microsecond=0).isoformat()
    con = db.conectar(":memory:")
    db.inicializar(con)
    tablas = {}
    for tabla in ("empresas", "operarios", "maquinas", "lotes", "checklists", "calibraciones", "consultas", "progreso"):
        filas = []
        for fila in con.execute(f"SELECT * FROM {tabla}"):
            d = dict(fila)
            for col, nombre in COLUMNAS_JSON.items():
                if col in d:
                    d[nombre] = json.loads(d.pop(col))
            filas.append(d)
        tablas[tabla] = filas
    return {
        "generado": generado,
        "conocimiento": conocimiento.para_json(),
        "asistente": {
            "urgentes": asistente.PALABRAS_URGENTES,
            "escalar": asistente.PALABRAS_ESCALAR,
            "producto": asistente.PALABRAS_PRODUCTO,
        },
        "tablas": tablas,
    }


def leer(*partes):
    with open(os.path.join(MVP, *partes), encoding="utf-8") as f:
        return f.read()


def json_para_script(obj):
    # Evita que un "</script>" dentro de los datos cierre la etiqueta.
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


ESTILOS_DEMO = """
/* Ajustes de la versión demo: barra de prueba y encabezado dentro del marco de claude.ai */
.barra { top: env(safe-area-inset-top, 0px); padding-top: 10px; }
.demo {
  background: var(--atencion-fondo); color: var(--texto);
  border-bottom: 2px solid var(--atencion);
  padding-block: 10px; padding-inline: 16px;
  font-size: 0.92rem;
}
.demo-dentro { max-width: 720px; margin: 0 auto; display: grid; gap: 8px; }
.demo-titulo { font-weight: 800; letter-spacing: 0.04em; text-transform: uppercase; font-size: 0.78rem; color: var(--atencion); }
.demo p { margin: 0; }
.demo-botones { display: flex; flex-wrap: wrap; gap: 8px; }
.demo-botones button {
  min-height: 44px; padding: 8px 14px; border-radius: 10px;
  border: 2px solid var(--atencion); background: var(--superficie); color: var(--texto);
  font: inherit; font-weight: 700; cursor: pointer;
}
.demo-botones button[aria-pressed="true"] { background: var(--atencion); border-color: var(--atencion); color: var(--superficie); }
.demo details summary { cursor: pointer; font-weight: 700; min-height: 32px; }
.demo ol { margin: 6px 0 0; padding-left: 1.3rem; }
.demo li { margin-bottom: 4px; }
"""

BARRA_DEMO = """
<section class="demo" aria-label="Versión de prueba">
  <div class="demo-dentro">
    <div class="demo-titulo">Versión de prueba</div>
    <p>Funciona en tu navegador con datos de ejemplo inventados. Lo que cargues queda solo en este dispositivo.</p>
    <div class="demo-botones">
      <button type="button" id="demo-senal" aria-pressed="false">Simular que no hay señal</button>
      <button type="button" id="demo-reiniciar">Empezar de nuevo</button>
    </div>
    <details id="demo-recorrido">
      <summary>Qué probar (5 minutos)</summary>
      <ol>
        <li><b>Soy maquinista</b> → Lucas Giménez → máquina <b>El Rojo</b>.</li>
        <li><b>Checklist</b>: todo "Bien" menos "Protección de la toma de fuerza" → sale <b>NO SALE</b>.</li>
        <li><b>Calibrar → Pulverizadora</b>: cargá 1.26, 1.25, 1.45 y 1.27 en la prueba de jarra.</li>
        <li><b>Calibrar → Pérdidas de cosecha</b>: 84 granos de soja → arriba de la tolerancia del INTA.</li>
        <li><b>Tengo un problema</b> → Sembradora → "Quedan dobles o fallas" → pedir ayuda.</li>
        <li><b>Preguntar</b>: "el motor calienta mucho".</li>
        <li>Tocá <b>Simular que no hay señal</b>, hacé otro checklist y mirá el aviso arriba. Volvé a tocar y se manda solo.</li>
        <li>Volvé al inicio → <b>Soy dueño o encargado</b>: tablero, alertas y constancia por lote.</li>
      </ol>
    </details>
  </div>
</section>
"""

SCRIPT_BARRA = """
(function () {
  const demo = window.CopilotoDemo;
  const $senal = document.getElementById("demo-senal");
  const $reiniciar = document.getElementById("demo-reiniciar");
  const pintar = () => {
    $senal.setAttribute("aria-pressed", String(demo.sinSenal));
    $senal.textContent = demo.sinSenal ? "Volver a tener señal" : "Simular que no hay señal";
  };
  $senal.addEventListener("click", () => { demo.simularSinSenal(!demo.sinSenal); pintar(); });
  let confirmar = null;
  $reiniciar.addEventListener("click", async () => {
    if (!confirmar) {
      $reiniciar.textContent = "¿Borrar lo que cargaste? Tocá de nuevo";
      confirmar = setTimeout(() => { confirmar = null; $reiniciar.textContent = "Empezar de nuevo"; }, 4000);
      return;
    }
    clearTimeout(confirmar); confirmar = null;
    if (demo.sinSenal) demo.simularSinSenal(false);
    demo.reiniciar();
    estado.chat = []; estado.operarioId = null; estado.maquinaId = null;
    await cargarBase();
    pintarSenal(); pintar();
    $reiniciar.textContent = "Listo, datos de ejemplo de nuevo";
    setTimeout(() => { $reiniciar.textContent = "Empezar de nuevo"; }, 2500);
    ir("#/inicio");
  });
  pintar();
})();
"""


def construir():
    datos = datos_de_ejemplo()
    html = f"""<title>Copiloto Rural</title>
<style>
{leer("static", "estilos.css")}
{ESTILOS_DEMO}
</style>
{BARRA_DEMO}
<header class="barra">
  <button id="btn-volver" class="volver" aria-label="Volver" hidden>‹</button>
  <h1 id="titulo">Copiloto Rural</h1>
  <span id="senal" class="senal" role="status" aria-live="polite">…</span>
</header>
<main id="vista" tabindex="-1"></main>
<script>window.COPILOTO_DEMO = true; window.COPILOTO_DATOS = {json_para_script(datos)};</script>
<script>
{leer("demo", "backend_demo.js")}
</script>
<script>
{leer("static", "app.js")}
</script>
<script>
{SCRIPT_BARRA}
</script>
"""
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(html)
    return SALIDA, len(html.encode("utf-8"))


if __name__ == "__main__":
    ruta, tamanio = construir()
    print(f"Demo armada en {ruta} ({tamanio / 1024:.0f} KB)")
