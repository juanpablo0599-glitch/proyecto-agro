# Proyecto agro — Misión nocturna

Investigación, decisión y MVP sobre dos ideas de negocio para el agro argentino.

**Resultado:** gana la **Idea A** ("Copiloto Rural": copiloto de bolsillo para maquinistas + tablero para el contratista + certificación más adelante). La Idea B (trazabilidad de semillas) queda como documento de concepto.

## Por dónde empezar
1. `entregables/RESUMEN_EJECUTIVO.md` — 2 páginas.
2. Ver el MVP funcionando: `cd mvp && python3 app.py` → http://localhost:8000 (ver `mvp/README.md`).

## Mapa
| Carpeta / archivo | Qué hay |
|---|---|
| `entregables/` | RESUMEN_EJECUTIVO, INVESTIGACION, COMPETENCIA, ANALISIS_Y_DECISION, MODELO_DE_NEGOCIO, PITCH, PROXIMOS_PASOS, PREGUNTAS_ABIERTAS, capturas del MVP |
| `investigacion/` | Notas crudas con fuentes (idea-a, idea-b) y auto-revisiones por fase |
| `mvp/` | Copiloto Rural: servidor Python sin dependencias, app web offline, tests |
| `ESTADO.md` / `DECISIONES.md` | Estado de la misión y registro de decisiones |
| `MISION.md`, `correr_noche.*` | La misión original y los scripts para correrla de noche |
