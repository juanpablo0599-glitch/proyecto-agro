# Copiloto Rural — MVP

Copiloto de bolsillo para maquinistas y tablero para el contratista (Idea A).

- **Maquinista:** checklist antes de salir (2 minutos, con ítems críticos que no dejan salir la máquina), calibración de pulverizadora (caudal por pastilla + prueba de jarra), de sembradora (semillas por metro + control a campo) y medición de pérdidas de cosecha (método de los aros del INTA), guías paso a paso para problemas comunes, asistente para preguntar y lecciones cortas con registro de progreso.
- **Dueño / encargado:** tablero con el estado de cada máquina (lista / atención / parada), alertas ordenadas por gravedad, pedidos de ayuda, checklists del día, formación y actividad de cada operario.
- **Sin señal:** la app queda guardada en el teléfono (service worker). Checklists, calculadoras, guías y lecciones funcionan sin internet; lo que se carga queda en cola y se manda solo cuando vuelve la señal (sin duplicar).

## Cómo correrlo (un solo comando)

Requisito: **Python 3.9 o más nuevo**. No hace falta instalar nada más.

```bash
cd mvp
python3 app.py
```

Abrí **http://localhost:8000** en el navegador. Para probarlo en el celular, conectalo a la misma red Wi-Fi y abrí `http://IP-DE-TU-COMPU:8000` (o usá el modo "dispositivo móvil" de las herramientas del navegador).

- Otro puerto: `PORT=8080 python3 app.py`
- Base de datos: se crea sola en `mvp/data/copiloto.db` con datos de ejemplo. Para empezar de cero, borrá ese archivo. Para usar otra: `COPILOTO_DB=/ruta/otra.db python3 app.py`.

### Recorrido sugerido (5 minutos)
1. **"Soy maquinista u operario"** → elegí a *Lucas Giménez* → máquina *El Rojo (tractor)*.
2. **Checklist antes de salir:** marcá todo "Bien" salvo "Protección de la toma de fuerza" → resultado **NO SALE**.
3. **Calibrar → Pulverizadora:** cargá la prueba de jarra (por ejemplo 1.26, 1.25, 1.45, 1.27) → marca la pastilla 3 fuera de rango.
4. **Calibrar → Pérdidas de cosecha:** 84 granos/m² de soja → 143 kg/ha, arriba de la tolerancia del INTA (75 kg/ha).
5. **Tengo un problema → Sembradora → "Quedan dobles o fallas"** → "No, pedir ayuda al encargado".
6. **Preguntar:** "el motor calienta mucho".
7. Volvé al inicio → **"Soy dueño o encargado"** → mirá el tablero: máquina parada, pedidos de ayuda, calibraciones fuera de rango, service vencido.
8. **Sin señal:** en las herramientas del navegador poné la red en *Offline*, hacé un checklist y una pregunta: arriba aparece "Sin señal · N por enviar". Volvé a *Online* y se sincroniza solo.

## IA: real o mock

| Situación | Qué pasa |
|---|---|
| Sin `ANTHROPIC_API_KEY` (por defecto) | **Modo mock:** responde con la base de conocimiento local (guías revisadas, multimarca). Funciona sin internet. |
| Con `ANTHROPIC_API_KEY` y el paquete `anthropic` instalado | **Modo IA:** usa Claude (`claude-opus-5-5` por defecto, esfuerzo bajo) con reglas: respuestas cortas, seguridad primero, nunca recomienda marcas ni productos fitosanitarios, deriva al encargado si no sabe. Le pasa la guía local relacionada como contexto. |
| La IA falla (sin red, error, rechazo) | Responde igual con la base local (`modo: mock-respaldo`). |
| Pregunta urgente (accidente, incendio, humo…) | Siempre responde el protocolo fijo de seguridad, sin esperar a la IA, y marca la consulta como urgente. |

Para activar la IA:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # no se guarda en ningún archivo
python3 app.py
```

Variables opcionales: `COPILOTO_MODELO` (otro modelo), `COPILOTO_MOCK=1` (forzar mock), `COPILOTO_LOG=1` (ver pedidos HTTP).

## Tests

```bash
cd mvp
python3 -m unittest discover -s tests -t .
```

Cubren: fórmulas de calibración, reglas del checklist (un crítico mal = no sale; un ítem sin responder cuenta como no revisado), asistente en modo mock y en modo IA (con un cliente simulado: modelo, reglas, respaldo ante errores, urgencias), alertas y tablero, sincronización offline sin duplicados, y una prueba de punta a punta que levanta el servidor real.

## Estructura

```
mvp/
  app.py                  servidor HTTP (biblioteca estándar) y rutas /api
  copiloto/
    conocimiento.py       checklists, guías de diagnóstico, lecciones (contenido curado)
    calculos.py           calculadoras (caudal, semillas/m, pérdidas)
    asistente.py          asistente: IA (SDK anthropic) o mock
    servicios.py          reglas de negocio, alertas, tablero, sincronización
    db.py                 esquema SQLite y datos de ejemplo
  static/                 app web mobile-first (HTML/CSS/JS sin dependencias) + service worker
  tests/                  tests con unittest
  data/                   acá se crea la base (no se versiona)
```

## API (resumen)

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/api/salud` | Estado y modo del asistente |
| GET | `/api/conocimiento` | Checklists, guías y lecciones (la app lo guarda para usar sin señal) |
| GET | `/api/empresa` | Operarios, máquinas y lotes |
| GET | `/api/tablero` | Tablero del dueño |
| GET | `/api/operarios/{id}/progreso` | Formación y actividad de un operario |
| POST | `/api/checklists` | Registrar checklist `{uid, operario_id, maquina_id, lote_id, items:{id:bool}, observaciones}` |
| POST | `/api/calibraciones` | `{operario_id, maquina_id, tipo: pulverizadora|siembra|perdidas, entradas:{...}}` |
| POST | `/api/consultas` | Pregunta al asistente `{operario_id, maquina_id, pregunta}` |
| POST | `/api/consultas/{id}/resolver` | El encargado marca un pedido de ayuda como resuelto |
| POST | `/api/progreso` | Respuestas de una lección |
| POST | `/api/sync` | Lote de operaciones cargadas sin señal `{operaciones:[{tipo, datos}]}` |

## Límites conocidos (es un MVP)
- **Sin usuarios ni contraseñas:** el operario elige su nombre. Antes de un piloto real hace falta un PIN por operario y una clave para el tablero.
- **Una sola empresa** de ejemplo (el esquema ya soporta varias).
- El contenido técnico es general y multimarca; **tiene que revisarlo un técnico** antes de usarse con operarios reales. Los valores marcados como "criterio usual" (por ejemplo ±10% entre pastillas, ±5% entre cuerpos) son orientativos.
- Las tolerancias de pérdida de cosecha cargadas son solo las verificadas (soja: 75 kg/ha, INTA). Para otros cultivos la app muestra la pérdida y pide consultar al técnico.
- El servidor es el de la biblioteca estándar de Python: sirve para piloto y demo, no para producción a escala.
- Los datos de ejemplo (empresa, personas, productores) son **ficticios**.
