# Resumen ejecutivo — para leer con el café

**Fecha:** 2026-10-01 · **Rama:** `claude/beautiful-goldberg-fowj1c`

## 1. Qué investigamos
Las dos ideas de la socia, solo con fuentes públicas (todas con link en `INVESTIGACION.md`):
- **A — IA para maquinistas + certificación.** El dolor es real: FACMA pide "tractoristas y maquinistas formados", el rubro promedia 48 años y la rotación es "el costo oculto más alto". Las pérdidas de cosecha de soja promedian **142 kg/ha** contra una tolerancia del INTA de **75 kg/ha** (USD 1.300 M/año solo en soja). Hay formación, pero **gratis y con pocos cupos** (UNR + John Deere + FACMA: 20 cupos; UNLZ: diplomatura gratuita). Las marcas meten IA en sus máquinas, pero **cada una para su marca**.
- **B — Trazabilidad de semillas.** La **Ley de Semillas no salió** (al 28/9/2026 ni siquiera entró al Congreso). Pero **el Estado ya arma el sistema por resolución**: Carta de Porte de Semillas (obligatoria desde el 1/12/2026), rótulo QR "IQR" en las bolsas, control de variedad en el primer punto de entrega (Res. Conjunta 3/2026, analizan las Cámaras Arbitrales) e IA del INASE para identificar variedades. Además, **Sembrá Evolución** (de las semilleras) ya cubre ~90% del área.

## 2. Qué decidimos y por qué
**Vamos con la Idea A** (puntaje ponderado **3,50 contra 1,55**; con pesos iguales, 3,44 contra 1,56).
- B compite contra el Estado y las semilleras, depende de una ley incierta, tiene ciclos de venta de 6–18 meses y un **conflicto de interés alto** para quien trabaja en una multinacional de insumos. Queda documentada como concepto, con las señales que justificarían reabrirla.
- A **no depende de ninguna ley**, es factible para dos personas y se puede probar con contratistas en 60–90 días.
- **Ajuste clave:** no arrancamos por la diplomatura (compite con cursos gratis de universidades). Arrancamos por un **"copiloto de bolsillo" multimarca que funciona sin señal**, con registro de práctica y un tablero para el dueño. La **certificación** llega en el invierno de 2027, con el aval de un aliado (RENATRE, una universidad o una cámara).
- **Modelo:** B2B al contratista. Piloto gratis de 60 días; después **USD 25 por máquina activa por mes** (es lo que cuesta cosechar ~¼ ha de soja con la tarifa de FACMA). Punto de equilibrio para dos personas: ~35 contratistas medianos (0,3% del total). **Todos estos números son hipótesis a validar.** Detalle en `MODELO_DE_NEGOCIO.md`.

## 3. Qué construimos
**Copiloto Rural** (`/mvp`), una app web mobile-first:
- **Maquinista:** checklist de 2 minutos (si falla algo crítico, "NO SALE"), calibración de pulverizadora (prueba de jarra), sembradora (semillas por metro) y pérdidas de cosecha (método de los aros del INTA), guías paso a paso con "cuándo parar", asistente para preguntar y lecciones cortas con progreso.
- **Dueño:** tablero con el estado de cada máquina, alertas, pedidos de ayuda, impacto de la semana y **constancia de labor por lote** para el productor.
- **Funciona sin señal** (probado: carga en el teléfono y sincroniza al volver la señal, sin duplicar).
- **IA:** usa Claude si hay `ANTHROPIC_API_KEY`; si no, **modo mock** con la base de conocimiento local. Las urgencias nunca pasan por la IA y nunca recomienda productos ni marcas.
- **51 tests en verde**, incluida una prueba de punta a punta con el servidor real.

## 4. Cómo verlo funcionando
```bash
cd mvp
python3 app.py          # no hace falta instalar nada (Python 3.9+)
```
Abrí **http://localhost:8000** y seguí el "recorrido sugerido" de `mvp/README.md` (5 minutos). Capturas en `entregables/capturas/`. Tests: `python3 -m unittest discover -s tests -t .` desde `mvp/`.

## 5. Los 3 riesgos principales
1. **Que nadie pague.** Todo lo comparable es gratis. *Mitigación:* vender resultados medibles (pérdidas, roturas, calidad para el cliente), probar el precio en el piloto y matar o pivotear a los 90 días si menos de 5 de 15 contratistas aceptan un piloto (criterios en `ANALISIS_Y_DECISION.md`).
2. **Que el operario no lo use.** *Mitigación:* 2 minutos, botones grandes, sin señal, dictado; que el dueño lo pida como rutina; probar primero con un "concierge" por WhatsApp.
3. **Conflicto de interés y confianza.** *Mitigación:* consulta a compliance del empleador antes de vender; neutralidad total (sin marcas ni productos); los datos son del contratista.

## 6. Qué hacer el lunes
1. JP: consulta a compliance. 2. Probar el MVP en los dos celulares. 3. Arrancar las **15 entrevistas** con las 10 preguntas de `PROXIMOS_PASOS.md`. 4. Pedirle a un técnico de confianza que revise las guías. Lo que no se pudo verificar está en `PREGUNTAS_ABIERTAS.md`.
