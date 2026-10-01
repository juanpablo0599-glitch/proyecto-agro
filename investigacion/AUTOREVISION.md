# Auto-revisiones por fase

Tres sombreros: (a) inversor escéptico, (b) contratista rural de 55 años con Android de gama baja y mala señal, (c) gerente de acopio / terminal portuaria.

## Fase 1 — Investigación

### Vuelta 1
| Sombrero | Debilidad más grave | Corrección |
|---|---|---|
| Inversor | "No hay ni un dato de que alguien pague. Todo lo comparable es gratis (cursos UNLZ/UNR/INTA, apps INTA)." | Busqué precios de software para contratistas (Auravant: plan gratis hasta 1.000 ha; pagos no publicados). Dejo explícito que la WTP es **hipótesis a validar** y lo paso a PROXIMOS_PASOS. Calculé un ancla de valor (pérdidas de cosecha evitables) marcada como estimación. |
| Contratista | "En el lote no hay señal. Si tu IA necesita internet, no me sirve." | Busqué datos de conectividad rural (43,4% de conectividad en población rural; 35% con banda ancha de calidad). Agregué requisito de diseño offline-first. |
| Gerente de acopio | "¿Y quién me paga a mí por tomar muestras? ¿Me obliga la ley?" | Investigué Res. Conjunta 3/2026: el acopio **puede** firmar convenios para financiar/coordinar muestras; analizan Cámaras Arbitrales; solo cultivares nuevos. Agregado en idea-b §7. |

### Vuelta 2
| Sombrero | Debilidad | Corrección |
|---|---|---|
| Inversor | "La cifra de 12.000 contratistas y el 70–90% del trabajo son de 2017. ¿Sigue valiendo?" | No encontré relevamiento más nuevo. Lo marco como dato viejo y uso rangos. Lo agrego a PREGUNTAS_ABIERTAS. |
| Contratista | "Los drones me están cambiando el negocio, ¿lo miraste?" | Investigué drones (20→2.000 unidades/año, certificación ANAC + provincial obligatoria). Nicho adyacente, ya cubierto por escuelas; lo dejo para roadmap. |
| Gerente de acopio | "Ya tengo un sistema de acopio que maneja la CPE." | Agregado en competencia de B como "lo que se hace hoy". |

Cierro Fase 1 con 2 vueltas: la tercera no agregaría datos nuevos verificables sin entrevistas.

## Fase 2 — Análisis y decisión

### Vuelta 1
| Sombrero | Debilidad más grave | Corrección |
|---|---|---|
| Inversor | "Le pusiste 2 en disposición a pagar a A y aun así la elegís. ¿No estás racionalizando? ¿Cuándo la matás?" | Agregué análisis de sensibilidad (pesos iguales: 3,44 vs 1,56) y **criterios explícitos para matar/pivotear** a los 90 días (§5.7). |
| Contratista | "Yo no confío en una app. Confío en el tipo que sabe." | Agregué **escalamiento a un humano** (§5.6) como parte del producto, no como extra. |
| Gerente de acopio | "Tu 'hueco' de software de cumplimiento para B es lo que mi proveedor de sistema de acopio va a agregar gratis en la próxima versión." | Lo dejé explícito como riesgo en el concepto B (ver abajo) y no cambia la decisión. |

### Vuelta 2
| Sombrero | Debilidad | Corrección |
|---|---|---|
| Inversor | "La defensabilidad de A es 2. Cualquiera arma un chat con IA." | Documentado en pre-mortem; la defensa se construye con aval institucional + datos de práctica + red. Se trabaja en Fase 3 (roadmap). |
| Contratista | "Si me vendés en plena siembra no te atiendo." | Calendario de ventas por campaña → Fase 3. |
| Gerente de acopio | Sin objeciones nuevas para A (no es su problema). | — |

Cierro Fase 2 con 2 vueltas.

## Fase 3 — Modelo de negocio

### Vuelta 1
| Sombrero | Debilidad más grave | Corrección |
|---|---|---|
| Inversor | "USD 1.150 por cliente por año es un ticket chico. Con 35 clientes apenas pagás dos sueldos mínimos. ¿Dónde está la escala?" | Agregué §4.6 "Camino para escalar": licencias para cámaras y cooperativas, Plan Empresa y ART/aseguradoras. Dejé explícito que, sin alguno de esos canales, es un negocio de autoempleo. |
| Contratista | "¿Y si la máquina está parada? No te pago por aire. Y si el checklist le lleva 10 minutos al operario, lo saco." | Definí "máquina activa" (se cobra solo si se usó en el mes) y agregué el requisito de que el checklist dure 2 minutos o menos. |
| Gerente de acopio / cooperativa | "Las cooperativas tenemos servicios de maquinaria y contratistas que trabajan para nuestros socios; ¿por qué no nos vendés a nosotros?" | Agregué las cooperativas y acopios con servicio de maquinaria como canal secundario. |

### Vuelta 2
| Sombrero | Debilidad | Corrección |
|---|---|---|
| Inversor | "El costo de la IA, ¿lo calculaste o lo inventaste?" | Calculado con el precio publicado de la API (USD 4/20 por millón de tokens para `claude-opus-5-5`) y supuestos de tokens. Sensibilidad: aunque se duplique, el margen sigue en ~73%. |
| Contratista | "Un curso de 8 semanas en plena campaña, imposible." | El programa se dicta solo en ventanas sin campaña (julio–agosto, febrero). Ya estaba; lo dejé explícito en §8. |
| Gerente de acopio | Sin objeciones nuevas. | — |

Cierro Fase 3 con 2 vueltas.

## Fase 4 — MVP

### Vuelta 1
| Sombrero | Debilidad más grave | Corrección |
|---|---|---|
| Inversor | "El tablero muestra estados pero no muestra **valor**. ¿Qué le hace pagar al contratista?" | Agregué el bloque **"Últimos 7 días, el Copiloto ayudó a…"**: salidas frenadas por un punto crítico, calibraciones fuera de rango detectadas, pérdida de cosecha medida y pedidos de ayuda resueltos. |
| Contratista (55 años, Android gama baja, mala señal) | "El tablero es eterno en el celular, y no quiero escribir." | Agrupé las alertas menores en una sola línea. Agregué la indicación de dictar con el micrófono del teclado. Medí el peso de la app: ~53 KB sin comprimir y sin frameworks; funciona sin señal (probado en Chromium con la red cortada: checklist y consulta quedan en cola y se sincronizan al volver la señal). |
| Gerente de acopio / productor | "¿Cómo sé que la máquina que entró a mi campo estaba bien?" | Agregué la **constancia de labor por lote** (checklist, operario, observaciones y calibraciones del equipo de los 3 días previos), imprimible o guardable como PDF. |

### Vuelta 2
| Sombrero | Debilidad | Corrección |
|---|---|---|
| Inversor | "¿La IA real funciona o solo el mock?" | Probé el camino con el SDK oficial real contra una API falsa local: el pedido sale con el modelo, el system prompt, el esfuerzo bajo y el fallback. Hay tests con un cliente simulado. Sin key no se puede probar contra la API real (límite de la misión). |
| Contratista | "Cualquiera puede elegir mi nombre y hacer el checklist por mí." | Documentado como límite: antes del piloto real hace falta un PIN por operario. |
| Gerente de acopio | "Los datos de hoy aparecían con hora futura." | Corregido en los datos de ejemplo. |

Cierro la Fase 4 con 2 vueltas.
