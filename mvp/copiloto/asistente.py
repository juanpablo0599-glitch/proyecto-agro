"""Asistente conversacional del maquinista.

Dos modos:
- "ia": usa Claude (SDK oficial `anthropic`) si hay ANTHROPIC_API_KEY y el SDK está instalado.
- "mock": responde con la base de conocimiento local. Es el modo por defecto y el
  respaldo ante cualquier error, así el MVP funciona sin credenciales y sin internet.

Reglas del asistente (en ambos modos): respuestas cortas y paso a paso, nunca
recomienda marcas ni productos fitosanitarios, prioriza la seguridad, y deriva a
una persona cuando el problema es grave o no sabe.
"""

import os
import unicodedata

from .conocimiento import GUIAS, TIPOS_MAQUINA

MODELO_POR_DEFECTO = "claude-opus-5-5"

PALABRAS_URGENTES = [
    "accidente", "herido", "lastimado", "sangre", "atrapado", "incendio", "fuego",
    "humo", "intoxicado", "intoxicacion", "mareado", "vuelco", "volco", "volcó",
]
PALABRAS_ESCALAR = [
    "rotura", "rompio", "roto", "ruido raro", "golpe", "no arranca",
    "pierde aceite", "pierde liquido", "pierde gasoil", "pierde agua", "chorrea",
]
PALABRAS_PRODUCTO = [
    "que producto", "qué producto", "que marca", "qué marca", "que herbicida", "qué herbicida",
    "que insecticida", "qué insecticida", "que fungicida", "qué fungicida", "dosis de",
    "cuanto producto", "cuánto producto", "que le echo", "qué le echo",
]

SISTEMA = """Sos "Copiloto Rural", un asistente para maquinistas y operarios de maquinaria agrícola en Argentina.
Hablás en español rioplatense, simple y directo, como un maquinista con experiencia que le explica a un compañero.

Reglas:
- Respuestas CORTAS: como máximo 6 pasos numerados, frases cortas. El operario lee en el celular, en la cabina.
- Primero la seguridad. Si hay riesgo para personas (accidente, incendio, intoxicación), lo primero es parar, alejarse y avisar.
- NO recomiendes marcas ni productos fitosanitarios, ni dosis. Para eso: "seguí el marbete y la receta del ingeniero agrónomo".
- Sos multimarca: si la respuesta depende del modelo de la máquina, decí "fijate en el manual de tu máquina" y explicá el principio general.
- Si no sabés o el problema puede ser una rotura, decilo y recomendá avisar al encargado. No inventes.
- Cuando corresponda, usá las referencias del INTA que te paso en el contexto (por ejemplo: sembrar a 5-8 km/h; tolerancia de pérdida de cosecha en soja 75 kg/ha).
- Terminá con una línea "Cuándo parar:" si hay algún riesgo de daño a la máquina, al cultivo o a las personas.
"""


def normalizar(texto):
    texto = (texto or "").lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def _contiene(texto_norm, palabras):
    return any(normalizar(p) in texto_norm for p in palabras)


def buscar_guia(pregunta, tipo_maquina=None):
    """Devuelve la guía que mejor matchea la pregunta (o None)."""
    t = normalizar(pregunta)
    mejor, mejor_puntaje = None, 0
    for g in GUIAS:
        puntaje = 0
        for palabra in g["palabras"]:
            if normalizar(palabra) in t:
                puntaje += 2 if " " in palabra else 1
        if puntaje == 0:
            continue
        if tipo_maquina and g["maquina"] == tipo_maquina:
            puntaje += 1.5
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = g, puntaje
    return mejor


def clasificar(pregunta):
    t = normalizar(pregunta)
    return {
        "urgente": _contiene(t, PALABRAS_URGENTES),
        "escalar": _contiene(t, PALABRAS_ESCALAR),
        "producto": _contiene(t, PALABRAS_PRODUCTO),
    }


def formatear_guia(guia):
    pasos = "\n".join(f"{i}. {p}" for i, p in enumerate(guia["pasos"], start=1))
    return f"{guia['titulo']}\n\n{pasos}\n\nCuándo parar: {guia['parar']}"


def respuesta_mock(pregunta, tipo_maquina=None):
    clase = clasificar(pregunta)
    guia = buscar_guia(pregunta, tipo_maquina)

    if clase["urgente"]:
        texto = ("PRIMERO LA SEGURIDAD.\n1. Pará la máquina y apagá el motor.\n"
                 "2. Alejate si hay fuego, humo o riesgo de vuelco.\n"
                 "3. Si hay alguien herido, llamá al 107 (emergencias médicas) o al 911.\n"
                 "4. Avisá al encargado ahora. Ya le dejé tu consulta marcada como URGENTE.")
        if guia:
            texto += "\n\n" + formatear_guia(guia)
        return {"respuesta": texto, "guia_id": guia["id"] if guia else None, "escalar": True}

    if clase["producto"]:
        texto = ("De productos y dosis no te puedo recomendar nada: eso lo define la receta del "
                 "ingeniero agrónomo y el marbete del producto. Sí te puedo ayudar a calibrar la "
                 "máquina para que tire exactamente el volumen que pide la receta. "
                 "Probá con el botón 'Calibrar'.")
        return {"respuesta": texto, "guia_id": None, "escalar": False}

    if guia:
        return {"respuesta": formatear_guia(guia), "guia_id": guia["id"], "escalar": clase["escalar"]}

    maquina = TIPOS_MAQUINA.get(tipo_maquina, "la máquina")
    texto = (f"No tengo una guía para eso todavía. Contame un poco más: ¿qué hace {maquina.lower()}, "
             "desde cuándo y qué estabas haciendo? Mientras tanto:\n"
             "1. Si hay ruido raro, olor a quemado o pérdida, pará y revisá con el motor apagado.\n"
             "2. Fijate en el manual de tu máquina.\n"
             "3. Le pasé tu consulta al encargado para que te llame.")
    return {"respuesta": texto, "guia_id": None, "escalar": True}


def _contexto_para_ia(pregunta, tipo_maquina, guia):
    partes = []
    if tipo_maquina:
        partes.append(f"Máquina del operario: {TIPOS_MAQUINA.get(tipo_maquina, tipo_maquina)}.")
    if guia:
        partes.append("Guía interna relacionada (contenido revisado):\n" + formatear_guia(guia))
    partes.append(f"Pregunta del operario: {pregunta}")
    return "\n\n".join(partes)


def ia_disponible():
    if os.environ.get("COPILOTO_MOCK") == "1":
        return False
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def respuesta_ia(pregunta, tipo_maquina=None):
    """Llama a Claude. Lanza excepción si falla (el que llama hace el respaldo a mock)."""
    import anthropic

    guia = buscar_guia(pregunta, tipo_maquina)
    clase = clasificar(pregunta)
    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model=os.environ.get("COPILOTO_MODELO", MODELO_POR_DEFECTO),
        max_tokens=4000,
        system=SISTEMA,
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[{"role": "user", "content": _contexto_para_ia(pregunta, tipo_maquina, guia)}],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("La IA no respondió esta consulta")
    texto = "".join(b.text for b in response.content if b.type == "text").strip()
    if not texto:
        raise RuntimeError("Respuesta vacía de la IA")
    return {
        "respuesta": texto,
        "guia_id": guia["id"] if guia else None,
        "escalar": clase["urgente"] or clase["escalar"] or guia is None,
    }


def responder(pregunta, tipo_maquina=None):
    """Punto de entrada. Devuelve dict con respuesta, modo, guia_id y escalar."""
    pregunta = (pregunta or "").strip()
    if not pregunta:
        return {"respuesta": "Escribí o dictá tu pregunta.", "modo": "mock", "guia_id": None, "escalar": False}

    # Lo urgente se responde siempre con el protocolo fijo, sin esperar a la IA.
    if clasificar(pregunta)["urgente"] or not ia_disponible():
        return {**respuesta_mock(pregunta, tipo_maquina), "modo": "mock"}
    try:
        return {**respuesta_ia(pregunta, tipo_maquina), "modo": "ia"}
    except Exception:  # cualquier problema de red, credenciales o API -> respaldo local
        return {**respuesta_mock(pregunta, tipo_maquina), "modo": "mock-respaldo"}
