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
