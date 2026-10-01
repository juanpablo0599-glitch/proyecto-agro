"""Base de conocimiento curada del Copiloto Rural.

Todo el contenido es general, multimarca y sin recomendar productos ni marcas.
Las referencias numéricas verificadas vienen de publicaciones públicas del INTA
(ver /investigacion/idea-a.md). Lo que es criterio práctico y no está verificado
se marca con "criterio usual" para que el operario sepa que es orientativo.

Esta base la usan: el modo mock del asistente, las guías de diagnóstico,
los checklists y la versión offline de la app (se sirve como JSON).
"""

TIPOS_MAQUINA = {
    "tractor": "Tractor",
    "sembradora": "Sembradora",
    "pulverizadora": "Pulverizadora",
    "cosechadora": "Cosechadora",
}

# ---------------------------------------------------------------------------
# Checklists antes de salir (máximo ~10 ítems, pensados para 2 minutos)
# "critico": si falla, la máquina NO sale hasta resolverlo.
# ---------------------------------------------------------------------------
CHECKLISTS = {
    "tractor": [
        {"id": "aceite_motor", "texto": "Nivel de aceite de motor bien", "critico": True},
        {"id": "refrigerante", "texto": "Nivel de agua/refrigerante bien", "critico": True},
        {"id": "filtro_aire", "texto": "Filtro de aire limpio (sopleteado)", "critico": False},
        {"id": "neumaticos", "texto": "Cubiertas sin cortes y con presión pareja", "critico": False},
        {"id": "luces", "texto": "Luces y balizas andando (si va por ruta)", "critico": True},
        {"id": "toma_fuerza", "texto": "Protección de la toma de fuerza puesta", "critico": True},
        {"id": "perdidas", "texto": "Sin pérdidas de aceite ni gasoil debajo", "critico": False},
        {"id": "matafuego", "texto": "Matafuego cargado a bordo", "critico": True},
    ],
    "sembradora": [
        {"id": "dosificadores", "texto": "Placas/dosificadores correctos para la semilla", "critico": True},
        {"id": "tubos", "texto": "Tubos de bajada limpios y sin roturas", "critico": True},
        {"id": "cuchillas", "texto": "Cuchillas y discos abresurco sin desgaste grande", "critico": False},
        {"id": "profundidad", "texto": "Profundidad regulada pareja en todos los cuerpos", "critico": True},
        {"id": "ruedas_tapadoras", "texto": "Ruedas tapadoras y compactadoras giran bien", "critico": False},
        {"id": "monitor", "texto": "Monitor de siembra prendido y sin alarmas", "critico": False},
        {"id": "vacio", "texto": "Vacío/turbina sin pérdidas (si es neumática)", "critico": False},
        {"id": "engrase", "texto": "Engrase hecho", "critico": False},
    ],
    "pulverizadora": [
        {"id": "pastillas", "texto": "Pastillas limpias, todas del mismo tipo y tamaño", "critico": True},
        {"id": "filtros", "texto": "Filtros (principal, de línea y de pastilla) limpios", "critico": True},
        {"id": "mangueras", "texto": "Mangueras y conexiones sin pérdidas", "critico": True},
        {"id": "manometro", "texto": "Manómetro funcionando", "critico": True},
        {"id": "botalon", "texto": "Botalón parejo, sin golpes, altura regulada", "critico": False},
        {"id": "antigoteo", "texto": "Antigoteo funcionando (no chorrea al cortar)", "critico": False},
        {"id": "epp", "texto": "Elementos de protección personal a bordo", "critico": True},
        {"id": "viento", "texto": "Revisé viento, temperatura y humedad antes de aplicar", "critico": True},
        {"id": "agua_limpia", "texto": "Tanque de agua limpia para lavado de manos", "critico": False},
    ],
    "cosechadora": [
        {"id": "aceite_motor", "texto": "Nivel de aceite de motor e hidráulico bien", "critico": True},
        {"id": "radiador", "texto": "Radiador y panel rotativo limpios", "critico": True},
        {"id": "matafuego", "texto": "Matafuegos cargados (riesgo de incendio)", "critico": True},
        {"id": "correas", "texto": "Correas y cadenas con tensión correcta", "critico": False},
        {"id": "cuchillas", "texto": "Cuchilla de corte y puntones sanos", "critico": False},
        {"id": "zarandas", "texto": "Zarandas reguladas según cultivo", "critico": False},
        {"id": "limpieza", "texto": "Máquina limpia de rastrojo acumulado", "critico": True},
        {"id": "sensores", "texto": "Monitor y sensores de pérdida funcionando", "critico": False},
    ],
}

# ---------------------------------------------------------------------------
# Guías de diagnóstico de problemas comunes.
# palabras: disparadores para el buscador del modo mock (sin acentos, minúsculas).
# ---------------------------------------------------------------------------
GUIAS = [
    {
        "id": "siembra_dobles_fallas",
        "maquina": "sembradora",
        "titulo": "Quedan dobles o fallas en la línea",
        "palabras": ["doble", "dobles", "falla", "fallas", "salteo", "salta", "distribucion", "desparejo", "plantas juntas", "huecos"],
        "pasos": [
            "Bajá la velocidad: el INTA recomienda sembrar entre 5 y 8 km/h según la máquina. Ir más rápido arruina la distribución.",
            "Revisá que la placa o el disco sea el correcto para el tamaño de esa semilla.",
            "En neumáticas: controlá el vacío en el manómetro y buscá pérdidas en mangueras y tapas.",
            "Mirá el enrasador/singularizador: si está muy abierto da dobles, muy cerrado da fallas.",
            "Revisá que el tubo de bajada no esté sucio, roto o con barro.",
            "Hacé la prueba: sembrá 50 metros, destapá y contá semillas en 10 metros de cada cuerpo.",
        ],
        "parar": "Si un cuerpo da muy distinto a los demás después de los ajustes, pará y avisá al encargado: cada metro mal sembrado se pierde toda la campaña.",
    },
    {
        "id": "siembra_profundidad",
        "maquina": "sembradora",
        "titulo": "La profundidad queda despareja",
        "palabras": ["profundidad", "profunda", "superficial", "muy arriba", "muy abajo", "tapado", "no tapa", "semilla arriba"],
        "pasos": [
            "Bajá la velocidad (5 a 8 km/h): a más velocidad el cuerpo rebota.",
            "Revisá la presión de los resortes o del sistema de carga de cada cuerpo; que sea pareja.",
            "Controlá las ruedas limitadoras de profundidad: que estén todas en la misma posición.",
            "Revisá el desgaste de discos y cuchillas: un disco gastado no abre bien el surco.",
            "Si hay mucho rastrojo, revisá la cuchilla turbo y los limpiadores de surco.",
            "Medí: destapá 10 semillas por cuerpo y medí la profundidad con una regla.",
        ],
        "parar": "Si no logra profundidad pareja en el lote, pará y avisá: la emergencia despareja puede costar mucho rendimiento (el INTA habla de más de 1.400 kg/ha en maíz con mala siembra).",
    },
    {
        "id": "monitor_alarma",
        "maquina": "sembradora",
        "titulo": "El monitor de siembra marca alarma en un tubo",
        "palabras": ["monitor", "alarma", "sensor", "tubo", "pita", "suena", "luz roja"],
        "pasos": [
            "Pará y fijate si ese cuerpo está tirando semilla (tolva vacía, tubo tapado).",
            "Limpiá el sensor del tubo: el polvo y el curasemillas los ensucian y dan falsas alarmas.",
            "Revisá el cable y la ficha del sensor (golpes, humedad).",
            "Si la alarma sigue con el cuerpo funcionando bien, anotalo y avisá: puede ser el sensor.",
        ],
        "parar": "Nunca sigas sembrando con un cuerpo que no tira semilla.",
    },
    {
        "id": "pulv_caudal_desparejo",
        "maquina": "pulverizadora",
        "titulo": "Las pastillas tiran distinto (caudal desparejo)",
        "palabras": ["caudal", "pastilla", "pastillas", "pico", "picos", "tira distinto", "desparejo", "tapada", "tapado", "jarra"],
        "pasos": [
            "Hacé la prueba de jarra: juntá lo que tira cada pastilla durante 1 minuto a la presión de trabajo.",
            "Usá la calculadora de la app para saber cuánto tendría que tirar cada una.",
            "Limpiá con cepillo blando (nunca con alambre ni soplando con la boca) las que tiran de menos.",
            "Revisá los filtros de pastilla y de línea.",
            "Criterio usual: si una pastilla tira más de un 10% distinto de lo que tiene que tirar, se cambia.",
            "Cambiá todas juntas si están gastadas: una pastilla gastada tira de más.",
        ],
        "parar": "No apliques con pastillas tapadas o muy gastadas: quedan franjas sin control o con sobredosis.",
    },
    {
        "id": "pulv_deriva",
        "maquina": "pulverizadora",
        "titulo": "Riesgo de deriva (gota fina, viento)",
        "palabras": ["deriva", "viento", "gota", "gotas", "fina", "nube", "vuela", "temperatura", "humedad", "inversion"],
        "pasos": [
            "Medí viento, temperatura y humedad antes de arrancar y anotalo.",
            "No apliques con viento muy fuerte ni con calma total (puede haber inversión térmica).",
            "Bajá la presión: a más presión, gota más fina y más deriva.",
            "Usá la pastilla que indica el marbete del producto para el tamaño de gota (las de aire inducido hacen gota más grande).",
            "Bajá la altura del botalón a la recomendada para esa pastilla.",
            "Respetá las distancias a casas, escuelas, cursos de agua y lo que diga la ley de tu provincia.",
        ],
        "parar": "Si las condiciones no dan, NO se aplica. Es la decisión más barata. Avisá al encargado.",
    },
    {
        "id": "pulv_presion",
        "maquina": "pulverizadora",
        "titulo": "La presión sube y baja",
        "palabras": ["presion", "manometro", "sube", "baja", "oscila", "bomba", "regulador"],
        "pasos": [
            "Revisá el filtro principal: tapado hace oscilar la presión.",
            "Buscá aire en la succión: mangueras flojas o tanque casi vacío.",
            "Revisá el regulador de presión y el retorno.",
            "Controlá que el manómetro funcione (compará con uno nuevo).",
            "Mirá que la bomba gire a las vueltas indicadas.",
        ],
        "parar": "Si la presión no se estabiliza, no apliques: la dosis queda despareja.",
    },
    {
        "id": "pulv_espuma",
        "maquina": "pulverizadora",
        "titulo": "Se forma espuma o grumos en el tanque",
        "palabras": ["espuma", "grumo", "grumos", "mezcla", "corta", "precipita", "borra"],
        "pasos": [
            "Respetá el orden de carga que indica el marbete de cada producto.",
            "Cargá con agitación funcionando y el tanque con agua hasta la mitad por lo menos.",
            "Revisá la calidad del agua (agua dura o sucia trae problemas).",
            "Si tenés dudas de compatibilidad, hacé la prueba en un frasco antes.",
        ],
        "parar": "Si se corta la mezcla, no la apliques. Consultá al ingeniero agrónomo responsable de la receta.",
    },
    {
        "id": "cosecha_perdidas_cola",
        "maquina": "cosechadora",
        "titulo": "Se pierde grano por la cola",
        "palabras": ["cola", "zaranda", "zarandas", "ventilador", "sale grano", "tira grano", "perdida", "perdidas", "pierde"],
        "pasos": [
            "Medí primero: usá la calculadora de pérdidas de la app (aros en el suelo).",
            "Bajá la velocidad de avance: mucho material sobrecarga zarandas.",
            "Ajustá el ventilador: con mucho viento vuela grano, con poco se tapan las zarandas.",
            "Abrí un poco la zaranda superior si se ve grano limpio saliendo.",
            "Revisá que el retorno no esté sobrecargado.",
        ],
        "parar": "El INTA fija una tolerancia de 75 kg/ha de pérdida en soja. Si estás muy arriba y no bajás con los ajustes, avisá: es plata del productor que queda en el piso.",
    },
    {
        "id": "cosecha_perdidas_cabezal",
        "maquina": "cosechadora",
        "titulo": "Se pierde grano en el cabezal (plataforma)",
        "palabras": ["cabezal", "plataforma", "molinete", "desgrane", "vainas", "chaucha", "corte bajo", "puntones"],
        "pasos": [
            "Medí antes y después de la plataforma para saber dónde está la pérdida.",
            "Bajá la velocidad de avance.",
            "Ajustá el molinete: velocidad apenas mayor que la de avance, y la altura justa.",
            "Revisá la cuchilla y los puntones: una cuchilla en mal estado sacude la planta y desgrana.",
            "Cortá lo más bajo posible en soja para levantar las vainas de abajo.",
        ],
        "parar": "Si la pérdida de cabezal es alta en un cultivo seco, conviene cosechar en horas de más humedad. Consultalo con el encargado.",
    },
    {
        "id": "cosecha_grano_partido",
        "maquina": "cosechadora",
        "titulo": "El grano sale partido o con mucha basura",
        "palabras": ["partido", "partidos", "quebrado", "rotura de grano", "cilindro", "rotor", "concavo", "basura", "sucio", "tolva sucia"],
        "pasos": [
            "Si sale partido: bajá las vueltas del cilindro/rotor o abrí el cóncavo de a poco.",
            "Si sale con basura: ajustá zarandas y ventilador.",
            "Si queda grano en la vaina o espiga: lo contrario, más vueltas o cerrar cóncavo de a poco.",
            "Hacé un cambio por vez y revisá la tolva y la cola después de cada ajuste.",
        ],
        "parar": "Grano partido o sucio se castiga en el acopio. Si no lo podés corregir, avisá.",
    },
    {
        "id": "motor_temperatura",
        "maquina": "tractor",
        "titulo": "El motor calienta (temperatura alta)",
        "palabras": ["calienta", "temperatura", "recalienta", "agua", "radiador", "hierve", "termometro"],
        "pasos": [
            "Bajá la carga y dejá el motor en marcha lenta unos minutos (no lo apagues de golpe caliente).",
            "Con el motor frío: revisá el nivel de refrigerante. NUNCA abras la tapa del radiador en caliente.",
            "Limpiá el radiador y las rejillas: el rastrojo y la pelusa lo tapan.",
            "Revisá la correa del ventilador.",
        ],
        "parar": "Si la temperatura no baja, apagá y avisá. Un motor recalentado es una rotura muy cara.",
    },
    {
        "id": "incendio",
        "maquina": "cosechadora",
        "titulo": "Olor a quemado o principio de incendio",
        "palabras": ["fuego", "incendio", "humo", "quemado", "llama", "prende fuego"],
        "pasos": [
            "Pará la máquina, apagá el motor y bajate.",
            "Si es chico y es seguro, usá el matafuego apuntando a la base del fuego.",
            "Alejate y avisá de inmediato. Llamá a bomberos si no se controla.",
            "Prevención: limpiar todos los días el rastrojo acumulado en motor, escape y rodamientos.",
        ],
        "parar": "Tu vida vale más que la máquina. Si no se controla en segundos, alejate.",
    },
    {
        "id": "seguridad_toma_fuerza",
        "maquina": "tractor",
        "titulo": "Seguridad con la toma de fuerza y el enganche",
        "palabras": ["toma de fuerza", "cardan", "enganche", "seguridad", "atrapado", "accidente", "proteccion"],
        "pasos": [
            "Nunca pases por encima ni cerca del cardán girando.",
            "Desconectá la toma de fuerza y apagá el motor antes de destapar o desatorar algo.",
            "La protección del cardán tiene que estar puesta siempre.",
            "Enganchá con el tractor detenido y freno puesto; nadie entre el tractor y la herramienta mientras se mueve.",
            "Ropa ajustada, sin cosas colgando.",
        ],
        "parar": "Si falta una protección, la máquina no trabaja hasta reponerla.",
    },
]

# ---------------------------------------------------------------------------
# Módulos de formación (micro-lecciones con 2-3 preguntas). Se usan para
# registrar el progreso del operario. Corresponden al programa "Operario Copiloto".
# ---------------------------------------------------------------------------
MODULOS = [
    {
        "id": "m0_seguridad",
        "titulo": "Seguridad primero",
        "resumen": "Toma de fuerza, enganche, ruta, cansancio y elementos de protección.",
        "preguntas": [
            {"p": "Antes de desatorar algo en la herramienta, ¿qué hacés?",
             "opciones": ["Lo hago rápido con el motor en marcha", "Desconecto la toma de fuerza y apago el motor", "Le pido a otro que maneje mientras desatoro"],
             "correcta": 1},
            {"p": "¿La protección del cardán se puede sacar para trabajar más cómodo?",
             "opciones": ["Sí, si tengo cuidado", "No, tiene que estar siempre puesta"],
             "correcta": 1},
        ],
    },
    {
        "id": "m1_tractor",
        "titulo": "El tractor y el mantenimiento diario",
        "resumen": "Chequeos antes de salir, fluidos, filtros, cubiertas y registro.",
        "preguntas": [
            {"p": "El motor calienta. ¿Cuándo abrís la tapa del radiador?",
             "opciones": ["En caliente, para ver rápido", "Nunca en caliente; espero que enfríe"],
             "correcta": 1},
            {"p": "¿Qué ítem del checklist impide salir si falla?",
             "opciones": ["Filtro de aire sucio", "Matafuego sin carga", "Una cubierta con poco dibujo"],
             "correcta": 1},
        ],
    },
    {
        "id": "m2_sembradora",
        "titulo": "Sembradora",
        "resumen": "Densidad, distribución, profundidad y velocidad.",
        "preguntas": [
            {"p": "Según el INTA, ¿a qué velocidad conviene sembrar?",
             "opciones": ["Entre 5 y 8 km/h según la máquina", "Lo más rápido posible", "A 15 km/h siempre"],
             "correcta": 0},
            {"p": "¿Cómo controlás la distribución en el lote?",
             "opciones": ["Mirando desde la cabina", "Destapando y contando semillas en 10 metros por cuerpo"],
             "correcta": 1},
        ],
    },
    {
        "id": "m3_pulverizadora",
        "titulo": "Pulverizadora",
        "resumen": "Pastillas, caudal, presión, velocidad, deriva y condiciones del tiempo.",
        "preguntas": [
            {"p": "Si subís mucho la presión, la gota...",
             "opciones": ["se hace más grande", "se hace más fina y deriva más"],
             "correcta": 1},
            {"p": "¿Con qué limpiás una pastilla tapada?",
             "opciones": ["Con un alambre", "Soplando con la boca", "Con un cepillo blando"],
             "correcta": 2},
            {"p": "Hay mucho viento hacia unas casas. ¿Qué hacés?",
             "opciones": ["Aplico igual pero rápido", "No aplico y aviso al encargado"],
             "correcta": 1},
        ],
    },
    {
        "id": "m4_cosechadora",
        "titulo": "Cosechadora",
        "resumen": "Regulación, pérdidas y método de los aros del INTA.",
        "preguntas": [
            {"p": "¿Cuál es la tolerancia de pérdida de cosecha en soja según el INTA?",
             "opciones": ["75 kg/ha", "300 kg/ha", "No hay tolerancia"],
             "correcta": 0},
            {"p": "Sale grano partido. ¿Qué probás primero?",
             "opciones": ["Subir las vueltas del cilindro", "Bajar las vueltas o abrir el cóncavo de a poco"],
             "correcta": 1},
        ],
    },
    {
        "id": "m5_precision",
        "titulo": "Electrónica y agricultura de precisión",
        "resumen": "Monitores, guía, corte por secciones y qué hacer cuando fallan.",
        "preguntas": [
            {"p": "El monitor marca alarma en un tubo pero el cuerpo tira bien. ¿Qué hacés?",
             "opciones": ["Lo ignoro para siempre", "Limpio el sensor, reviso la ficha, lo anoto y aviso"],
             "correcta": 1},
        ],
    },
    {
        "id": "m6_cliente",
        "titulo": "Trabajo con el cliente",
        "resumen": "Registro de la labor, cuidado del campo ajeno, reportar incidentes.",
        "preguntas": [
            {"p": "Rompiste un alambrado del cliente. ¿Qué hacés?",
             "opciones": ["No digo nada", "Lo registro y aviso al encargado y al cliente"],
             "correcta": 1},
        ],
    },
]

# Tolerancias de pérdida de cosecha verificadas (kg/ha). Solo cargamos lo verificado.
TOLERANCIA_PERDIDA_KG_HA = {
    "soja": 75,  # INTA, ver investigacion/idea-a.md
}

# Peso de mil granos típico (g), para precargar las calculadoras. Valor editable por el usuario.
P1000_TIPICO_G = {"soja": 170, "maiz": 300, "trigo": 38, "girasol": 60}


def para_json():
    """Todo el conocimiento en un dict serializable (lo usa la app offline)."""
    return {
        "tipos_maquina": TIPOS_MAQUINA,
        "checklists": CHECKLISTS,
        "guias": GUIAS,
        "modulos": [
            {k: v for k, v in m.items()} for m in MODULOS
        ],
        "tolerancia_perdida_kg_ha": TOLERANCIA_PERDIDA_KG_HA,
        "p1000_tipico_g": P1000_TIPICO_G,
    }
