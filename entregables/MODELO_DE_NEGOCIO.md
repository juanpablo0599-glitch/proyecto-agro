# Modelo de negocio — "Copiloto Rural"

**Idea A reformulada:** un copiloto de bolsillo para el maquinista (checklists, calibración y diagnóstico, que funciona sin señal), con registro de práctica y un tablero para el contratista. Más adelante suma un programa de formación con certificación avalada.

**Fecha:** 2026-10-01 · Las cifras marcadas 🔶 son **supuestos propios** para validar. Las ✅ están en `/investigacion/idea-a.md` con su fuente.

**Tipo de cambio supuesto:** 🔶 **USD 1 = ARS 1.450** (en febrero de 2026 el BNA estaba a $1.435 ✅, según rosario3/FACMA). Los precios se fijan en USD y se cobran en pesos al cambio del día, igual que hacen los contratistas con sus tarifas.

---

## 1. Propuesta de valor por segmento

| Segmento | Quién es | Dolor principal | Qué le damos | Cómo lo mide |
|---|---|---|---|---|
| **Contratista mediano** (2–6 equipos, 3.000–15.000 ha/año) — *segmento inicial* | Dueño/a de la empresa, muchas veces maneja también. ~12.000 contratistas en el país ✅ | Operarios nuevos sin experiencia, rotación ✅ ("el costo oculto más alto"), roturas, reclamos del productor por la calidad del trabajo | Operario nuevo que rinde antes, checklists diarios con registro, alertas de problemas, tablero del estado del equipo, constancia de calidad para mostrarle al cliente | Menos roturas evitables, pérdidas de cosecha medidas (kg/ha), menos reclamos, menos días de "aprendizaje" |
| **Contratista grande / empresa agropecuaria** (10+ equipos) | Gerente de operaciones o jefe de maquinaria | Estandarizar cómo trabajan 20–50 operarios en distintas zonas | Lo mismo, más reportes por operario y por máquina, y un programa interno de formación | Indicadores por equipo; cumplimiento del Dto. 617/97 (capacitación documentada) ✅ |
| **Maquinista** (usuario, no paga) | Tractorista, maquinista de cosechadora, operario de pulverizadora o sembradora | "Me tiran la máquina nueva y nadie me explica"; miedo a romper; poca señal | Respuestas claras en su idioma, paso a paso, sin señal; registro de su progreso; credencial que se lleva si cambia de trabajo | Usos por jornada, módulos completados |
| **Productor que contrata servicios** (beneficiario) | Productor que contrata la cosecha o la pulverización | No sabe si la labor se hizo bien | Constancia de checklist y calibración del equipo que entró a su campo | Satisfacción, repetición del servicio |
| **Aliados** | Cámaras de FACMA, RENATRE, universidades, INTA, ART | Necesitan llegar a más operarios (sus cursos tienen 12–20 cupos ✅) | Plataforma para la práctica entre clases, seguimiento de egresados | Egresados activos |

**En una frase para el contratista:** *"Tu operario nuevo trabaja como uno con experiencia más rápido, y vos ves desde tu celular que el equipo salió bien revisado y calibrado."*

---

## 2. Quién paga y quién usa
- **Paga:** el contratista o la empresa (B2B). El maquinista no paga nunca.
- **Usa todos los días:** el maquinista (asistente y checklists).
- **Mira una vez por día:** el dueño o el encargado (tablero).
- **Avala (más adelante):** una institución (para la certificación).

---

## 3. Modelo de ingresos y precios tentativos

| Producto | Qué incluye | Precio USD | Precio ARS (🔶 a 1.450) | Supuesto |
|---|---|---|---|---|
| **Piloto** | 60 días, hasta 4 máquinas, con medición inicial y final | **Gratis** a cambio de datos y de un testimonio | — | Para ganar los primeros 5 casos |
| **Plan Equipo** (contratista mediano) | Asistente + checklists + registro + tablero, por **máquina activa** | **USD 25 / máquina / mes**, se cobra 10 meses al año (los 2 meses sin campaña, gratis) | **$36.250 / máquina / mes** | 🔶 ≈ el costo de **~0,25 ha** de cosecha de soja (USD 97/ha ✅ FACMA). Para un equipo que cosecha 2.000 ha/año, es el 0,13% de su facturación de cosecha. |
| **Plan Empresa** (10+ máquinas) | Lo anterior + reportes por operario + configuración de checklists propios + soporte prioritario | **USD 20 / máquina / mes**, mínimo 10 | **$29.000 / máquina / mes** | Descuento por volumen |
| **Programa "Operario Copiloto"** (fase 2, con aval) | Formación híbrida (ver §8) + evaluación práctica en campo + credencial | **USD 280 / operario** | **$406.000 / operario** | 🔶 La diplomatura arancelada de referencia cuesta $1,5 M ✅ (UNRC, para técnicos). Lo comparable para operarios es gratis, así que lo que se cobra es la práctica en campo, la evaluación y el seguimiento, no la clase. |
| **Auditoría de labor** (servicio) | Medición de pérdidas de cosecha con el método INTA, o chequeo de la calibración de la pulverizadora, con informe | **USD 150 / visita** | **$217.500 / visita** | Sirve para entrar al cliente y demostrar el valor con números |

**"Máquina activa"** = la que registró al menos una jornada en el mes. Si la máquina está parada, no se cobra. Se paga en pesos, por mes o por campaña.

**Regla de neutralidad (por el conflicto de interés y por confianza):** el producto **no recomienda marcas ni productos fitosanitarios**, no tiene publicidad de insumos y no vende datos a terceros.

---

## 4. Unit economics gruesos (🔶 todo es supuesto a validar)

### 4.1 Cliente tipo: contratista mediano
- 4 máquinas activas × USD 25 × 10 meses = **USD 1.000 / año**
- 2 operarios por año en el Programa (desde el año 2) × USD 280 = **USD 560 / año**
- 1 auditoría de labor por año = **USD 150**
- **Ingreso por cliente: ~USD 1.150 el año 1 → ~USD 1.700 desde el año 2**

### 4.2 Costos variables por cliente (año)
| Concepto | Cálculo | USD/año |
|---|---|---|
| IA (API de Claude) | 🔶 4 operarios × 6 consultas/día × 150 días = 3.600 consultas × ~USD 0,025 (modelo `claude-opus-5-5` a USD 4/20 por millón de tokens; ~2.500 tokens de entrada y ~800 de salida por consulta, con esfuerzo bajo) | ~90 |
| Hosting y SMS/WhatsApp | 🔶 prorrateado | ~30 |
| Soporte humano (escalamientos) | 🔶 ~1 h/mes × 10 meses × USD 10/h | ~100 |
| **Total variable** | | **~USD 220** |

**Margen bruto del software: ~80%.** El Programa de formación tiene más costo (instructor y traslados): 🔶 margen del ~50%.

### 4.3 Costo de adquisición (CAC)
- 🔶 La socia visita o llama, demo en el galpón, piloto de 60 días con 2 visitas. Viáticos + tiempo ≈ **USD 300–500 por cliente ganado** (suponiendo que 1 de cada 3 pilotos convierte).
- **Recupero del CAC:** USD 400 / (USD 1.150 − 220)/12 ≈ **5 meses**.

### 4.4 Punto de equilibrio para dos personas
- 🔶 Costos fijos: USD 1.200/mes por socio (retiro mínimo, al principio part-time) × 2 + USD 300/mes de herramientas, contador y viajes = **~USD 2.700/mes ≈ USD 32.400/año**.
- Contribución por cliente: ~USD 930/año (año 1) → **~35 contratistas medianos** para cubrir los costos. Es el **0,3% de los ~12.000 contratistas**. 🔶 Alcanzable en 12–18 meses si la conversión de los pilotos funciona.

### 4.5 Sensibilidad (lo que más mueve el resultado)
| Variable | Escenario pesimista | Escenario base | Efecto |
|---|---|---|---|
| Precio por máquina | USD 15 | USD 25 | El equilibrio pasa de 35 a ~60 clientes |
| Máquinas por cliente | 2 | 4 | El equilibrio pasa a ~70 clientes |
| Conversión del piloto | 1 de 6 | 1 de 3 | El CAC se duplica (~USD 800) |
| Costo de IA por consulta | USD 0,05 | USD 0,025 | Margen del 72% en vez del 80%; poco impacto |

### 4.6 Camino para escalar (más allá de la venta uno a uno)
- **Licencia para una cámara o cooperativa:** la asociación paga una cuota anual y ofrece el copiloto a sus socios como beneficio (🔶 USD 3.000–8.000/año según la cantidad de socios). Una sola venta trae decenas de usuarios.
- **Empresas agropecuarias grandes y cooperativas con flota propia:** Plan Empresa con 20–50 máquinas.
- **ART y aseguradoras de maquinaria:** pagan por operarios capacitados con registro (menos siniestros). Es una hipótesis para validar en el T4.
- 🔶 Sin alguno de estos tres canales, el negocio queda chico ("de autoempleo"). Con uno solo que funcione, puede pasar los USD 100.000/año en el año 2.

**Conclusión:** el negocio depende del **precio** y de las **máquinas por cliente**, no del costo de la IA. Eso es lo primero que hay que validar.

---

## 5. Estrategia de salida al mercado: primeros 90 días (oct-2026 → ene-2027)

**Contexto del calendario:** octubre a diciembre es siembra gruesa y pulverización intensa; diciembre y enero, cosecha fina; **febrero, preparación de la cosecha gruesa** (la ventana ideal para capacitar). En temporada **no se le vende un curso a nadie**; sí se puede probar un asistente en el lote.

| Semana | Qué | Quién | Meta |
|---|---|---|---|
| 1–2 | Declaración a compliance del empleador de JP. Lista de 30 contratistas de la red **propia** de la socia (nunca bases de la empresa). Guion de entrevista (ver PROXIMOS_PASOS). | Ambos | Compliance OK; 30 nombres |
| 2–5 | **15 entrevistas** (10 contratistas, 3 empresas agropecuarias, 2 técnicos de concesionario). Se muestra el MVP en el celular. | Socia (campo), JP (análisis) | Validar dolor, precio y formato |
| 4–6 | Ajustar el MVP con lo aprendido: checklists de sembradora y pulverizadora (temporada actual). Cargar el contenido técnico revisado. | JP | MVP v0.2 |
| 6–12 | **5 pilotos gratis** (60 días) en siembra y pulverización. Medición inicial: calibración de la pulverizadora y velocidad/densidad de siembra. | Ambos | ≥60% de las jornadas con checklist completado |
| 8–10 | Primera charla en una asociación de FACMA o en una cooperativa (presentación con los datos de los pilotos). | Socia | 1 aliado interesado |
| 10–13 | Cierre de pilotos: medición final, informe para cada contratista y **propuesta paga para la cosecha gruesa**. Preparar el stand o la charla para **Expoagro (9–12/3/2027)** ✅. | Ambos | **≥2 contratistas pagando** desde marzo |

**Canal principal del año 1:** venta directa de la socia + recomendación boca a boca entre contratistas. **Secundarios:** asociaciones de FACMA, **cooperativas y acopios que dan servicios de maquinaria a sus productores** (ACA y AFA tienen cientos de plantas ✅), técnicos de concesionarios (comisión por referido 🔶 del 20% del primer año).

**Requisito de producto que sale de la venta:** el checklist diario no puede llevar **más de 2 minutos**. Si le hace perder tiempo al operario, el dueño lo saca.

---

## 6. Roadmap a 12 meses

| Trimestre | Producto | Negocio |
|---|---|---|
| **T1 (oct–dic 2026)** | MVP: asistente (sembradora, pulverizadora, cosechadora), checklists, registro de práctica, tablero. Funciona offline. | 15 entrevistas, 5 pilotos |
| **T2 (ene–mar 2027)** | Medición de pérdidas de cosecha guiada (método INTA) dentro de la app; informe automático para el productor; consultas por audio. | 2–5 clientes pagos para la cosecha gruesa; presencia en Expoagro |
| **T3 (abr–jun 2027)** | Canal por WhatsApp (consultar sin abrir la app); checklists propios de cada empresa; varios contratistas a la vez. | 10–15 clientes; convenio con una asociación de FACMA o una cooperativa |
| **T4 (jul–sep 2027)** | **Programa "Operario Copiloto"** v1 con un aliado institucional (formación de invierno, antes de la siembra gruesa); credencial digital verificable. | Primera cohorte de 20–40 operarios; 20–30 clientes; propuesta a una ART o aseguradora |

**Fuera del alcance del año 1:** conectarse con la telemetría de las máquinas (John Deere, CNH, etc.), drones, mercado de trabajo de operarios.

---

## 7. Cómo se construye la defensa
1. **Contenido curado en lenguaje de campo**, revisado por técnicos y probado con operarios reales: cuesta tiempo y no se copia con un prompt.
2. **Historial de práctica de cada operario**: cuanto más se usa, más vale (para el contratista y para el operario).
3. **Aval institucional** de la certificación (RENATRE, una universidad, una cámara).
4. **Red de contratistas** y la reputación de la socia en el rubro.
5. **Neutralidad**: multimarca y sin insumos. Las marcas de maquinaria y de insumos no pueden ofrecer lo mismo de forma creíble.

---

## 8. Diseño del programa de capacitación ("Operario Copiloto")

**Para quién:** operarios con 0–3 años de experiencia, o con experiencia en máquinas mecánicas que pasan a máquinas con electrónica. También estudiantes de escuelas agrotécnicas.
**Formato:** **híbrido**. Micro-lecciones en el celular (que funcionan sin señal) + **2 jornadas presenciales de práctica en campo** + práctica supervisada en el trabajo real, registrada en la app.
**Duración total:** 🔶 **8 semanas, ~40 horas** (12 h en el celular, 16 h presenciales, 12 h de práctica registrada en el trabajo). Se dicta en la ventana sin campaña: **julio–agosto** (antes de la siembra gruesa) o **febrero** (antes de la cosecha gruesa).

### Módulos
| # | Módulo | Contenido | Horas | Evaluación |
|---|---|---|---|---|
| 0 | Seguridad primero | Riesgos de la maquinaria (Dto. 617/97 ✅), tomas de fuerza, enganche, tránsito por rutas, cansancio, primeros auxilios básicos, elementos de protección | 4 | Test en la app + checklist de seguridad en campo |
| 1 | El tractor y el mantenimiento diario | Chequeos antes de salir, fluidos, filtros, neumáticos, lectura del tablero, registro | 4 | Checklist observado por el instructor |
| 2 | Sembradora | Regulación de densidad y distribución, profundidad, velocidad (5–8 km/h ✅ INTA), calibración en el galpón y en el lote, monitores de siembra, conteo de plantas | 8 | Calibración real + conteo a campo (desvío ≤ 5% de la densidad objetivo 🔶) |
| 3 | Pulverizadora | Boquillas y tamaño de gota, caudal, presión, velocidad, cálculo de volumen por hectárea, prueba de jarra (caudal por pastilla), deriva y condiciones del tiempo, triple lavado, ley provincial y carnet de aplicador ✅ | 8 | Calibración real (desvío de caudal ≤ 10% entre pastillas 🔶) + preparación del carnet provincial |
| 4 | Cosechadora | Plataforma, cilindro y cóncavo, zarandas, ventilador, velocidad; **medición de pérdidas con el método INTA** (aros, tolerancia de 75 kg/ha en soja ✅) | 8 | Medición de pérdidas a campo con informe |
| 5 | Electrónica y agricultura de precisión | Guía y piloto, corte por secciones, dosis variable, monitores, descarga de datos, qué hacer cuando falla | 4 | Ejercicio práctico en el monitor |
| 6 | Trabajo con el cliente | Registro de la labor, comunicación con el productor, cuidado del campo ajeno, reportar incidentes | 2 | Caso simulado |
| 7 | Práctica supervisada | 10 jornadas reales con checklist y registro en la app; revisión del instructor a distancia | 12 | ≥10 jornadas registradas con checklist completo |

### Cómo se evalúa y se certifica
- **Teoría:** preguntas cortas en la app (con imágenes, poco texto), nota mínima del 70%.
- **Práctica:** evaluación en campo con rúbrica (checklists observados + calibración real + medición de pérdidas).
- **Evidencia:** jornadas registradas en la app, firmadas por el encargado del contratista.
- **Credencial:** digital, verificable con un código QR (nombre, módulos aprobados, fecha, aval). Se renueva cada 2 años con una actualización corta.

### Instituciones que podrían avalar el certificado (para conversar, sin contacto todavía)
| Institución | Por qué | Observación |
|---|---|---|
| **RENATRE** | Ya certifica competencias de "Operador de Maquinarias Agrícolas" ✅; acaba de firmar un convenio con Aapresid ✅ | La opción más natural para certificar **competencias laborales** |
| **Universidades nacionales con agronomía** (ej. UNR, UNLZ, UNRC, UNLPam) | Pueden emitir diplomaturas o cursos de extensión ✅ | UNR y UNLZ ya tienen sus propios cursos gratuitos: pueden ser aliados (les damos la práctica en la app) o competidores |
| **INTA** (EEA locales) | Contenido técnico de referencia (apps Criollo y Campero, métodos de pérdidas) ✅ | Aval técnico más que título |
| **Asociaciones de FACMA** (ej. Casilda, Tres Arroyos, Entre Ríos) | Son los clientes; pueden exigir la credencial a sus socios | FACMA ya trabaja con UNR y John Deere ✅ |
| **Bolsas de Cereales** (ej. Entre Ríos) | Ya hicieron formación dual con INTA ✅ | Aval regional |
| **Centros de Formación Profesional** provinciales | Certificados oficiales de formación profesional | Trámite provincial |

**Supuesto clave:** el programa arranca **con un solo aliado** y una cohorte chica (20–40 operarios) en el invierno de 2027. Sin aval, se ofrece como "constancia de práctica" (sin la palabra "certificado") para no prometer lo que no es.
