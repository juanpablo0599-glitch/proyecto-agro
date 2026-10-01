# MISIÓN NOCTURNA — Investigar, decidir y construir

Vas a trabajar solo durante toda la noche. **No hay ningún humano disponible.** Nadie va a responder preguntas ni aprobar nada. Vos planificás, ejecutás, te auto-revisás y seguís. Cuando dudes, elegí la opción más razonable, documentala en `DECISIONES.md` y avanzá. Nunca te quedes esperando input.

Escribí todo en español rioplatense, claro y directo.

---

## 1. Contexto

Somos dos socios: JP (analista senior de efectividad comercial en el agro, perfil datos/automatización, tiene una consultora chica de eficiencia comercial) y su socia (viene del agro, conoce el mundo de los productores y contratistas desde chica). Poco capital, mucha ejecución. Queremos un negocio que podamos validar y vender rápido.

La socia propuso dos ideas por audio (transcripción limpia):

### Idea A — IA para maquinistas + certificación
> "En el rubro del agro hay mucha deficiencia en la utilización correcta de las herramientas, las maquinarias, y no hay gente capacitada. ¿Por qué no inventamos una IA muy bajada a la tierra del maquinista para que logre operar con calidad? Y quizás armamos un curso tipo certificado, posta, tipo una diplomatura, y le anexamos el uso de una app. Y lo podemos vender a cualquier empresa grande."
> "Tiene mucho potencial para los productores más grandes. Existen cámaras de contratistas rurales. El público que podría pagar sería el productor grande, pero también el contratista: hay muchos contratistas grandes con esta problemática hace años — no tienen mano de obra calificada, y cada día con las nuevas tecnologías se les dificulta más."

### Idea B — Trazabilidad de semillas
> "Tengo toda la fe de que se va a dar la Ley de Semillas en Argentina. Tenemos que diseñar un sistema o una IA que garantice la trazabilidad de la procedencia de las semillas a los distribuidores y acopiadores. Hay que salir aceleradísimos porque es lo que se les va a pedir. Lo importante es poder entrar en los grandes puertos donde se hace la entrega y garantizar, con guías y demás, todo lo que tiene que ver con la trazabilidad."

**Restricción importante:** usá solo fuentes públicas. No uses ni supongas datos internos de ninguna empresa (ni segmentaciones de clientes, ni bases de una compañía en particular). Al evaluar cada idea, incluí como criterio el riesgo de conflicto de interés para alguien que trabaja en una multinacional de insumos agrícolas.

---

## 2. Reglas de trabajo autónomo

1. **Memoria entre sesiones.** Puede que te corten y te relancen varias veces en la noche. Al arrancar, SIEMPRE leé `ESTADO.md` (si existe) y seguí desde donde quedó. Actualizá `ESTADO.md` al terminar cada paso: fase actual, qué está hecho, qué sigue, bloqueos.
2. **Decisiones.** Cada decisión no trivial va a `DECISIONES.md` con: fecha/hora, decisión, alternativas consideradas, por qué.
3. **Git.** Commit después de cada avance significativo, con mensajes claros, y hacé push a la rama de esta sesión cada vez: es la única forma de que el trabajo quede guardado si la máquina se reinicia. Nunca toques la rama `main` directamente y no abras pull requests.
4. **No cortes antes de tiempo.** No termines tu turno hasta que exista el archivo `DONE`. Cuando cerrás una fase, pasá a la siguiente sin esperar confirmación de nadie.
5. **Nada de preguntar.** Si algo es ambiguo, asumí, documentá el supuesto en `DECISIONES.md` y seguí.
6. **Auto-revisión obligatoria.** Al cerrar cada fase, hacé una crítica dura desde 3 sombreros: (a) inversor escéptico, (b) contratista rural de 55 años con un Android de gama baja y señal mala en el campo, (c) gerente de acopio o de terminal portuaria. Listá las 3 debilidades más graves, corregilas y repetí. Máximo 3 vueltas por fase; después avanzá igual.
7. **Si algo falla 3 veces** (una librería, un sitio que no carga, un test), dejalo anotado en `ESTADO.md` como bloqueo, buscá una alternativa y seguí. No te trabes.
8. **Honestidad epistémica.** En la investigación, separá siempre: dato verificado (con URL y fecha de consulta) vs. estimación propia (con el razonamiento). Nunca inventes cifras, nombres de empresas ni fuentes. Si no encontrás algo, decí que no lo encontraste.

## 3. Límites duros (no negociables)

- Trabajá **solo dentro de este repositorio**. No toques otros repositorios.
- No gastes plata, no crees cuentas, no te registres en servicios, no compres dominios.
- No publiques nada, no hagas deploy, no mandes mails ni mensajes. El único push permitido es a la rama de esta sesión.
- No uses ni pidas credenciales. Si el MVP necesita un LLM, que funcione con `ANTHROPIC_API_KEY` si está en el entorno y, si no, con un **modo mock** que devuelva respuestas de ejemplo realistas. El MVP tiene que correr igual sin la key.
- Dependencias declaradas dentro del proyecto (package.json, requirements.txt, etc.) para que cualquiera pueda reproducirlo.
- No borres archivos que no hayas creado vos.

---

## 4. Fases

### Fase 0 — Setup (rápido)
Estructura:
```
/investigacion   notas crudas y fuentes por idea
/entregables     documentos finales
/mvp             el producto
ESTADO.md  DECISIONES.md
```

### Fase 1 — Investigación profunda (las dos ideas)
Usá búsqueda web a fondo. Para **cada idea** cubrí:

1. **Problema y mercado en Argentina:** cuántos contratistas rurales hay, qué porcentaje del trabajo agrícola hacen, parque de maquinaria, déficit de operarios calificados, salarios de maquinistas, costo de los errores de operación (pérdidas de cosecha, mala siembra, mala pulverización, roturas). Para B: volumen de semilla y grano, uso propio, cómo funciona hoy la comercialización y el control.
2. **Regulación (clave para B):** estado ACTUAL del proyecto de Ley de Semillas (verificá la fecha de la info; no asumas que se aprobó), Ley 20.247, rol del INASE, resoluciones vigentes sobre uso propio, Carta de Porte Electrónica, sistemas de control existentes en acopios y puertos. Para A: certificaciones de competencias laborales existentes, quién puede emitir una diplomatura (universidades, INTA, institutos), normas de seguridad.
3. **Competencia:** mínimo 10 jugadores/alternativas por idea entre directos, indirectos, internacionales y "lo que la gente hace hoy en lugar de comprar esto". Pistas para arrancar (verificalas, no las des por ciertas): plataformas de los fabricantes de maquinaria (centros de operaciones, apps de calibración), escuelas y cursos de operarios, cámaras y federaciones de contratistas, INTA, Aapresid, sistemas de verificación de semillas en acopios ya usados por la industria, soluciones de trazabilidad agro con blockchain/QR. Armá una **matriz de competencia** (qué hacen, a quién le venden, precio si es público, fortalezas, huecos).
4. **Compradores y disposición a pagar:** quién decide la compra, quién paga, cuánto pagan hoy por soluciones parecidas, ciclo de venta, estacionalidad (campaña gruesa/fina).
5. **Canales:** cámaras de contratistas, concesionarios de maquinaria, cooperativas, acopios, bolsas de cereales, eventos (Agroactiva, Expoagro).

Guardá notas y fuentes en `/investigacion/idea-a.md` y `/investigacion/idea-b.md`.

### Fase 2 — Análisis y decisión
Puntuá ambas ideas (1 a 5, con ponderación explícita y justificada) en: tamaño de mercado accesible, intensidad del dolor, disposición a pagar, intensidad competitiva (inversa), factibilidad para 2 personas con poco capital, tiempo hasta el primer ingreso, riesgo regulatorio/dependencia de que salga una ley, conflicto de interés para el socio que trabaja en una multinacional de insumos, y defensabilidad.

Hacé un **pre-mortem** de cada una ("pasó un año y fracasó: ¿por qué?").

Elegí la ganadora. Si salen parejas o la B depende de una ley incierta, construí el MVP de la ganadora y dejá para la otra un documento de concepto sólido. Todo a `/entregables/ANALISIS_Y_DECISION.md`.

### Fase 3 — Diseño de la solución
Para la ganadora: propuesta de valor por segmento, quién paga y quién usa, modelo de ingresos y pricing tentativo en ARS y USD (con supuestos), unit economics gruesos, estrategia de salida al mercado de los primeros 90 días, roadmap a 12 meses.
Si es la idea A, incluí además el diseño del programa de capacitación: módulos, duración, formato (híbrido, práctica en campo), cómo se evalúa y certifica, y posibles instituciones aliadas para avalar el certificado.
Va a `/entregables/MODELO_DE_NEGOCIO.md`.

### Fase 4 — Construcción del MVP
Requisitos:
- Corre local con **un solo comando** documentado en `/mvp/README.md`.
- Stack simple y mantenible (elegilo y justificalo en `DECISIONES.md`). Sin servicios pagos. Base de datos local (SQLite o archivos).
- **Mobile-first**, pensado para gente del campo: textos simples, botones grandes, poco tipeo, que funcione con mala conexión donde se pueda.
- Datos de ejemplo realistas (máquinas, lotes, operarios, semilleros, acopios, según la idea).
- LLM con modo mock (ver límites duros).
- Tests de lo principal y que pasen.
- Si es la idea A, como mínimo: asistente conversacional para el maquinista (calibración de sembradora y pulverizadora, checklists antes de salir, diagnóstico de problemas comunes), registro de práctica/progreso del operario, y vista para el dueño/contratista con el estado de su equipo.
- Si es la idea B, como mínimo: registro de lotes de semilla con origen, cadena de custodia (semillero → productor → acopio → puerto) con QR, validación y alertas de inconsistencias, y vista para el acopio/puerto.

Antes de dar el MVP por terminado: levantalo, probá el flujo principal de punta a punta y arreglá lo que falle.

### Fase 5 — Entregables finales
En `/entregables`:
- `RESUMEN_EJECUTIVO.md` — máximo 2 páginas, para leer con el café: qué investigaste, qué decidiste y por qué, qué construiste, cómo verlo funcionando, los 3 riesgos principales.
- `COMPETENCIA.md` — la matriz completa.
- `INVESTIGACION.md` — síntesis con fuentes.
- `ANALISIS_Y_DECISION.md` y `MODELO_DE_NEGOCIO.md`.
- `PITCH.md` — guion de 10 slides para presentarle a un contratista grande o a una cámara.
- `PROXIMOS_PASOS.md` — lo que necesita humanos: a quién entrevistar primero, 10 preguntas de validación para contratistas/acopios, experimentos baratos para validar antes de seguir construyendo.
- `PREGUNTAS_ABIERTAS.md` — todo lo que no pudiste resolver o verificar.

---

## 5. Criterio de terminado

Cuando todas las fases estén completas, la auto-revisión final hecha, el MVP corriendo con tests en verde y todo commiteado:
1. Actualizá `ESTADO.md` con "MISIÓN COMPLETA" y un resumen.
2. Creá un archivo vacío llamado `DONE` en la raíz, hacé commit y push.

Si todavía te queda tiempo y energía antes de eso, priorizá: calidad de la investigación > claridad de la decisión > pulido del MVP.
