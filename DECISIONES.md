# DECISIONES

Formato: fecha/hora (UTC) — decisión — alternativas — por qué.

## 2026-10-01 02:50 — Copiar MISION.md y runners al repo
- **Decisión:** el repo estaba vacío. Copié `MISION_1.md` (adjunto) como `MISION.md` en la raíz, más `correr_noche.sh` y `correr_noche.ps1`.
- **Alternativas:** dejarlos fuera del repo.
- **Por qué:** los runners buscan `MISION.md` en la raíz; si se relanza la sesión, la misión tiene que estar ahí. Además quedan versionados.

## 2026-10-01 02:50 — Rama de trabajo
- **Decisión:** todo se commitea y pushea a `claude/beautiful-goldberg-fowj1c`. No se toca `main` (no existe todavía) ni se abren PRs.
- **Por qué:** regla 3 de la misión y límites duros.

## 2026-10-01 03:40 — Ganadora: Idea A (con ajustes)
- **Decisión:** construir el MVP de la Idea A. Puntaje ponderado A 3,50 vs B 1,55 (pesos iguales: 3,44 vs 1,56).
- **Alternativas:** (1) Idea B; (2) construir ambas a medias; (3) un pivot de B a "software de cumplimiento CP Semillas" para acopios chicos.
- **Por qué:** B ya está siendo cubierta por el Estado (CP Semillas Res. INASE 475/2026, rótulo IQR, Res. Conjunta 3/2026, IA del INASE) y por las semilleras (Sembrá Evolución ~90% del área); depende de una ley que no entró al Congreso; y tiene conflicto de interés alto para el socio. A no depende de ninguna ley y es factible para 2 personas.

## 2026-10-01 03:40 — Reformular A: copiloto + registro primero, diplomatura después
- **Decisión:** el producto inicial es un "copiloto de bolsillo" (asistente + checklists + calibración offline) con registro de práctica y vista del dueño. La certificación/diplomatura es etapa 2 con aval de un aliado.
- **Alternativas:** arrancar por la diplomatura (como proponía la socia).
- **Por qué:** ya hay diplomaturas y cursos gratuitos (UNLZ+CRESTA, UNR+John Deere+FACMA, INTA+Bolsa ER); competir con gratis+universidad desde cero es caro y lento. El hueco real es el acompañamiento en el lote, multimarca, offline, y el registro verificable.

## 2026-10-01 03:40 — B queda como documento de concepto, sin MVP
- **Por qué:** la misión indica que si B depende de una ley incierta, se construye la ganadora y B queda como concepto. Además se dejan "señales para reabrir".

## 2026-10-01 04:10 — Precio por máquina activa, en USD cobrado en pesos
- **Decisión:** USD 25/máquina activa/mes (Plan Equipo), USD 20 (Plan Empresa, mínimo 10), 10 meses al año. Programa de formación USD 280/operario. Auditoría de labor USD 150.
- **Alternativas:** precio por operario; precio por hectárea; suscripción fija por empresa.
- **Por qué:** los operarios rotan (precio por operario castiga al que más rota); la máquina es estable y el contratista ya piensa sus costos por máquina. Por hectárea es más justo pero difícil de medir sin telemetría en el MVP. Se cobra en pesos al cambio del día, como hacen los contratistas con sus tarifas (FACMA las publica en USD).

## 2026-10-01 04:10 — Modelo de IA para el MVP
- **Decisión:** usar el SDK oficial `anthropic` (declarado en `requirements.txt`) con el modelo `claude-opus-5-5`, esfuerzo `low` y fallback del lado del servidor por defecto. El modelo se puede cambiar con la variable de entorno `COPILOTO_MODELO`. Si no hay `ANTHROPIC_API_KEY` o no está instalado el SDK, el MVP usa el **modo mock** (base de conocimiento local).
- **Alternativas:** llamar a la API por HTTP directo (sin SDK); modelo más barato por defecto.
- **Por qué:** la guía oficial recomienda el SDK y el modelo por defecto; el costo por consulta (~USD 0,025) no cambia el negocio (ver sensibilidad). El mock asegura que el MVP corra sin credenciales, como exige la misión.

## 2026-10-01 05:00 — Stack del MVP: Python estándar + SQLite + web sin frameworks
- **Decisión:** servidor con `http.server` de la biblioteca estándar de Python, base SQLite, frontend HTML/CSS/JS sin dependencias, PWA con service worker para funcionar sin señal. Única dependencia opcional: `anthropic` (para IA real).
- **Alternativas:** Flask/FastAPI + React; app nativa Android; bot de WhatsApp.
- **Por qué:** (1) un solo comando sin instalar nada (`python3 app.py`), máxima reproducibilidad; (2) la página pesa poco (sin frameworks) para Android de gama baja; (3) el service worker permite usar checklists, calculadoras, guías y lecciones sin señal, y encolar lo cargado; (4) mantenible por una persona con perfil de datos (JP). WhatsApp queda para el T3 del roadmap (requiere cuenta de negocio, que la misión prohíbe crear); app nativa es caro para validar.

## 2026-10-01 05:00 — Reglas de seguridad del asistente
- **Decisión:** las preguntas urgentes (accidente, humo, incendio, intoxicación) nunca pasan por la IA: se responde un protocolo fijo y se escala. Las preguntas de productos/dosis se derivan al marbete y al ingeniero agrónomo. Si la IA falla, responde la base local.
- **Por qué:** el costo de un error es alto (personas, máquinas, aplicaciones) y hay conflicto de interés si el asistente recomienda productos.

## 2026-10-01 05:00 — Identificación sin contraseña en el MVP
- **Decisión:** el operario elige su nombre; el tablero no pide clave.
- **Por qué:** es una demo local con datos ficticios; documentado como límite. Antes del piloto real: PIN por operario y clave del tablero.

## 2026-10-01 — Demo navegable publicada como página privada (pedido de JP)
- **Decisión:** JP, ya despierto, pidió ver la app porque no podía abrir `localhost` en la máquina de la nube. Publiqué una demo como página **privada** en claude.ai (solo la ve el dueño de la cuenta hasta que la comparta): https://claude.ai/artifact/UCnR1oToeKXnUuKYpeUynu
- **Alternativas:** solo capturas (no se puede probar); deploy en un hosting (requiere cuenta y servicio externo).
- **Por qué:** la regla nocturna de "no publicar" era para el trabajo sin supervisión; esto lo pidió el usuario y la página es privada. Para que corra sin servidor, armé `mvp/demo/backend_demo.js` (la lógica de servicios.py en JavaScript) y `mvp/demo/construir_demo.py`, que junta la app, ese backend y los mismos datos de ejemplo en un solo archivo. La navegación de `app.js` ahora guarda la ruta en memoria (en el marco embebido no siempre se puede tocar la URL); la app con servidor sigue funcionando igual (tests y prueba en navegador en verde).
