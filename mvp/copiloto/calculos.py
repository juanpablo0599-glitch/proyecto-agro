"""Calculadoras de campo. Funciones puras, sin dependencias.

Fórmulas estándar de calibración (las mismas que usan las apps del INTA y los
manuales de tecnología de aplicación). Cada función devuelve un dict con el
resultado y un texto corto para mostrar al operario.
"""


class DatoInvalido(ValueError):
    """Un dato de entrada falta o no tiene sentido."""


def _positivo(nombre, valor):
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise DatoInvalido(f"Falta el dato: {nombre}")
    if v <= 0:
        raise DatoInvalido(f"El dato '{nombre}' tiene que ser mayor que cero")
    return v


def caudal_por_pastilla(volumen_l_ha, velocidad_km_h, distancia_picos_cm):
    """Caudal que tiene que tirar cada pastilla (L/min).

    Q = V (L/ha) x v (km/h) x d (cm) / 60.000
    """
    v = _positivo("volumen (L/ha)", volumen_l_ha)
    vel = _positivo("velocidad (km/h)", velocidad_km_h)
    d = _positivo("distancia entre picos (cm)", distancia_picos_cm)
    q = v * vel * d / 60000
    return {
        "caudal_l_min": round(q, 3),
        "texto": f"Cada pastilla tiene que tirar {q:.2f} litros por minuto.",
    }


def verificar_pastillas(caudal_objetivo_l_min, medidos_l_min, tolerancia_pct=10):
    """Compara lo medido en la prueba de jarra contra el objetivo.

    Criterio usual: una pastilla que se aparta más de un 10% se limpia o se cambia.
    Devuelve el desvío de cada una y cuáles hay que revisar.
    """
    obj = _positivo("caudal objetivo (L/min)", caudal_objetivo_l_min)
    if not medidos_l_min:
        raise DatoInvalido("Cargá al menos una pastilla medida")
    detalle = []
    for i, m in enumerate(medidos_l_min, start=1):
        med = _positivo(f"pastilla {i}", m)
        desvio = (med - obj) / obj * 100
        detalle.append({
            "pastilla": i,
            "medido_l_min": round(med, 3),
            "desvio_pct": round(desvio, 1),
            "ok": abs(desvio) <= tolerancia_pct,
        })
    malas = [d["pastilla"] for d in detalle if not d["ok"]]
    promedio = sum(d["medido_l_min"] for d in detalle) / len(detalle)
    desvio_prom = (promedio - obj) / obj * 100
    if malas:
        texto = (f"Revisá o cambiá {len(malas)} pastilla(s): "
                 + ", ".join(str(p) for p in malas)
                 + f". Se aceptan hasta ±{tolerancia_pct:g}%.")
    else:
        texto = f"Todas las pastillas dentro de ±{tolerancia_pct:g}%. Bien."
    return {
        "detalle": detalle,
        "a_revisar": malas,
        "promedio_l_min": round(promedio, 3),
        "desvio_promedio_pct": round(desvio_prom, 1),
        "aprobada": not malas,
        "texto": texto,
    }


def semillas_por_metro(plantas_ha_objetivo, distancia_surcos_cm,
                       poder_germinativo_pct=90, eficiencia_implantacion_pct=90):
    """Semillas a tirar por metro lineal para lograr las plantas por hectárea objetivo.

    plantas/m = plantas/ha x distancia(m) / 10.000
    semillas/m = plantas/m / (PG x eficiencia)
    """
    pl = _positivo("plantas por hectárea", plantas_ha_objetivo)
    d = _positivo("distancia entre surcos (cm)", distancia_surcos_cm) / 100
    pg = _positivo("poder germinativo (%)", poder_germinativo_pct) / 100
    ef = _positivo("eficiencia de implantación (%)", eficiencia_implantacion_pct) / 100
    if pg > 1 or ef > 1:
        raise DatoInvalido("Los porcentajes no pueden pasar de 100")
    plantas_m = pl * d / 10000
    semillas_m = plantas_m / (pg * ef)
    return {
        "plantas_por_metro": round(plantas_m, 2),
        "semillas_por_metro": round(semillas_m, 2),
        "semillas_en_10_metros": round(semillas_m * 10, 1),
        "texto": (f"Tirá {semillas_m:.1f} semillas por metro "
                  f"(contá {semillas_m * 10:.0f} en 10 metros)."),
    }


def kg_semilla_por_ha(semillas_m2, p1000_g):
    """Kilos de semilla por hectárea. kg/ha = semillas/m² x P1000 (g) / 100."""
    s = _positivo("semillas por m²", semillas_m2)
    p = _positivo("peso de mil semillas (g)", p1000_g)
    kg = s * p / 100
    return {"kg_ha": round(kg, 1), "texto": f"Hacen falta {kg:.0f} kg de semilla por hectárea."}


def verificar_siembra(semillas_contadas_10m, semillas_objetivo_por_metro, tolerancia_pct=5):
    """Compara lo contado en 10 m (por cuerpo) contra el objetivo."""
    obj = _positivo("semillas objetivo por metro", semillas_objetivo_por_metro) * 10
    if not semillas_contadas_10m:
        raise DatoInvalido("Cargá al menos un cuerpo contado")
    detalle = []
    for i, c in enumerate(semillas_contadas_10m, start=1):
        try:
            cont = float(c)
        except (TypeError, ValueError):
            raise DatoInvalido(f"Falta el dato del cuerpo {i}")
        if cont < 0:
            raise DatoInvalido(f"El cuerpo {i} no puede ser negativo")
        desvio = (cont - obj) / obj * 100
        detalle.append({"cuerpo": i, "contadas": cont, "desvio_pct": round(desvio, 1),
                        "ok": abs(desvio) <= tolerancia_pct})
    malos = [d["cuerpo"] for d in detalle if not d["ok"]]
    texto = ("Todos los cuerpos dentro de lo esperado." if not malos else
             "Revisá los cuerpos: " + ", ".join(str(c) for c in malos)
             + f" (se aceptan hasta ±{tolerancia_pct:g}%).")
    return {"detalle": detalle, "a_revisar": malos, "aprobada": not malos, "texto": texto,
            "objetivo_en_10m": round(obj, 1)}


def perdidas_cosecha(granos_por_m2, p1000_g, cultivo="soja", tolerancia_kg_ha=None):
    """Pérdida de cosecha a partir de granos contados en el suelo (método de aros).

    kg/ha = granos/m² x P1000 (g) / 100
    Con 4 aros de 56 cm de diámetro se junta ~1 m² en total.
    """
    from .conocimiento import TOLERANCIA_PERDIDA_KG_HA

    try:
        g = float(granos_por_m2)
    except (TypeError, ValueError):
        raise DatoInvalido("Falta el dato: granos por m²")
    if g < 0:
        raise DatoInvalido("Los granos no pueden ser negativos")
    p = _positivo("peso de mil granos (g)", p1000_g)
    kg = g * p / 100
    tol = tolerancia_kg_ha if tolerancia_kg_ha is not None else TOLERANCIA_PERDIDA_KG_HA.get(cultivo)
    if tol is None:
        veredicto = "sin_tolerancia"
        texto = (f"Estás perdiendo {kg:.0f} kg/ha. No tengo cargada una tolerancia "
                 f"verificada para {cultivo}: consultala con el técnico.")
    elif kg <= tol:
        veredicto = "ok"
        texto = f"Pérdida de {kg:.0f} kg/ha: dentro de la tolerancia ({tol:g} kg/ha). Bien."
    else:
        veredicto = "alta"
        texto = (f"Pérdida de {kg:.0f} kg/ha: arriba de la tolerancia ({tol:g} kg/ha). "
                 f"Revisá la regulación (te sobran {kg - tol:.0f} kg/ha).")
    return {"kg_ha": round(kg, 1), "tolerancia_kg_ha": tol, "veredicto": veredicto, "texto": texto}
