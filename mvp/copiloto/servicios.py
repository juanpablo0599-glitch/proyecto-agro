"""Lógica de negocio: registrar checklists, calibraciones, consultas y progreso;
calcular el estado de las máquinas, las alertas y el tablero del dueño.

Todas las altas aceptan un `uid` generado por el cliente: si la app manda dos
veces lo mismo (por ejemplo al sincronizar después de estar sin señal), no se duplica.
"""

import json
import uuid
from datetime import datetime, timedelta

from . import asistente, calculos
from .conocimiento import CHECKLISTS, MODULOS


class ErrorDeDatos(ValueError):
    """Los datos enviados no son válidos (se responde 400)."""


def _hoy():
    return datetime.now().date()


def _fecha(valor):
    if not valor:
        return datetime.now().replace(microsecond=0).isoformat()
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "")).replace(microsecond=0).isoformat()
    except ValueError:
        raise ErrorDeDatos("Fecha inválida")


def _uid(datos):
    return str(datos.get("uid") or uuid.uuid4())


def _existe(con, tabla, uid):
    fila = con.execute(f"SELECT id FROM {tabla} WHERE uid = ?", (uid,)).fetchone()
    return fila["id"] if fila else None


def _obtener(con, tabla, id_):
    if id_ in (None, ""):
        return None
    fila = con.execute(f"SELECT * FROM {tabla} WHERE id = ?", (id_,)).fetchone()
    if not fila:
        raise ErrorDeDatos(f"No existe {tabla[:-1]} {id_}")
    return fila


# ---------------------------------------------------------------------------
# Checklists
# ---------------------------------------------------------------------------

def evaluar_checklist(tipo, items):
    """'no_apta' si falla un ítem crítico, 'con_observaciones' si falla otro, si no 'apta'.

    Un ítem que no vino se toma como NO revisado (falla), para no dar por bueno lo que no se miró.
    """
    if tipo not in CHECKLISTS:
        raise ErrorDeDatos(f"Tipo de máquina desconocido: {tipo}")
    fallo_critico = fallo_otro = False
    for item in CHECKLISTS[tipo]:
        ok = bool(items.get(item["id"], False))
        if not ok and item["critico"]:
            fallo_critico = True
        elif not ok:
            fallo_otro = True
    if fallo_critico:
        return "no_apta"
    if fallo_otro:
        return "con_observaciones"
    return "apta"


def registrar_checklist(con, datos, origen="online"):
    uid = _uid(datos)
    previo = _existe(con, "checklists", uid)
    if previo:
        return obtener_checklist(con, previo) | {"duplicado": True}
    operario = _obtener(con, "operarios", datos.get("operario_id"))
    maquina = _obtener(con, "maquinas", datos.get("maquina_id"))
    if not operario or not maquina:
        raise ErrorDeDatos("Faltan operario o máquina")
    _obtener(con, "lotes", datos.get("lote_id"))
    items = datos.get("items") or {}
    if not isinstance(items, dict):
        raise ErrorDeDatos("Los ítems tienen que ser un objeto {id: true/false}")
    validos = {i["id"] for i in CHECKLISTS[maquina["tipo"]]}
    items = {k: bool(v) for k, v in items.items() if k in validos}
    resultado = evaluar_checklist(maquina["tipo"], items)
    cur = con.execute(
        "INSERT INTO checklists (uid, operario_id, maquina_id, lote_id, fecha, items_json, resultado, "
        "observaciones, origen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (uid, operario["id"], maquina["id"], datos.get("lote_id") or None, _fecha(datos.get("fecha")),
         json.dumps(items), resultado, (datos.get("observaciones") or "").strip() or None, origen))
    con.commit()
    return obtener_checklist(con, cur.lastrowid) | {"duplicado": False}


def obtener_checklist(con, id_):
    f = con.execute("SELECT * FROM checklists WHERE id = ?", (id_,)).fetchone()
    d = dict(f)
    d["items"] = json.loads(d.pop("items_json"))
    fallados = [i for i in CHECKLISTS[_tipo_maquina(con, d["maquina_id"])] if not d["items"].get(i["id"])]
    d["fallados"] = [{"id": i["id"], "texto": i["texto"], "critico": i["critico"]} for i in fallados]
    d["mensaje"] = {
        "apta": "Máquina lista para salir. ¡Buen trabajo!",
        "con_observaciones": "Puede salir, pero hay cosas para revisar. Quedan anotadas para el encargado.",
        "no_apta": "NO SALE. Hay un punto crítico que resolver antes. Ya le avisamos al encargado.",
    }[d["resultado"]]
    return d


def _tipo_maquina(con, maquina_id):
    return con.execute("SELECT tipo FROM maquinas WHERE id = ?", (maquina_id,)).fetchone()["tipo"]


# ---------------------------------------------------------------------------
# Calibraciones
# ---------------------------------------------------------------------------

def registrar_calibracion(con, datos, origen="online"):
    uid = _uid(datos)
    previo = _existe(con, "calibraciones", uid)
    if previo:
        return _calibracion(con, previo) | {"duplicado": True}
    operario = _obtener(con, "operarios", datos.get("operario_id"))
    if not operario:
        raise ErrorDeDatos("Falta el operario")
    _obtener(con, "maquinas", datos.get("maquina_id"))
    tipo = datos.get("tipo")
    e = datos.get("entradas") or {}
    try:
        if tipo == "pulverizadora":
            obj = calculos.caudal_por_pastilla(e.get("volumen_l_ha"), e.get("velocidad_km_h"),
                                               e.get("distancia_picos_cm"))
            resultado = dict(obj)
            if e.get("medidos_l_min"):
                resultado |= calculos.verificar_pastillas(obj["caudal_l_min"], e["medidos_l_min"])
                resultado["texto"] = obj["texto"] + " " + resultado["texto"]
                aprobada = resultado["aprobada"]
            else:
                aprobada = True
        elif tipo == "siembra":
            obj = calculos.semillas_por_metro(e.get("plantas_ha"), e.get("distancia_surcos_cm"),
                                              e.get("pg", 90), e.get("eficiencia", 90))
            resultado = dict(obj)
            if e.get("contadas_10m"):
                ver = calculos.verificar_siembra(e["contadas_10m"], obj["semillas_por_metro"])
                resultado |= ver
                resultado["texto"] = obj["texto"] + " " + ver["texto"]
                aprobada = ver["aprobada"]
            else:
                aprobada = True
        elif tipo == "perdidas":
            resultado = calculos.perdidas_cosecha(e.get("granos_m2"), e.get("p1000_g"),
                                                  e.get("cultivo", "soja"))
            aprobada = resultado["veredicto"] != "alta"
        else:
            raise ErrorDeDatos("Tipo de calibración desconocido (pulverizadora, siembra o perdidas)")
    except calculos.DatoInvalido as err:
        raise ErrorDeDatos(str(err))
    cur = con.execute(
        "INSERT INTO calibraciones (uid, operario_id, maquina_id, tipo, entradas_json, resultado_json, "
        "aprobada, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uid, operario["id"], datos.get("maquina_id") or None, tipo, json.dumps(e), json.dumps(resultado),
         int(aprobada), _fecha(datos.get("fecha"))))
    con.commit()
    return _calibracion(con, cur.lastrowid) | {"duplicado": False}


def _calibracion(con, id_):
    d = dict(con.execute("SELECT * FROM calibraciones WHERE id = ?", (id_,)).fetchone())
    d["entradas"] = json.loads(d.pop("entradas_json"))
    d["resultado"] = json.loads(d.pop("resultado_json"))
    d["aprobada"] = bool(d["aprobada"])
    return d


# ---------------------------------------------------------------------------
# Consultas al asistente
# ---------------------------------------------------------------------------

def registrar_consulta(con, datos, origen="online"):
    uid = _uid(datos)
    previo = _existe(con, "consultas", uid)
    if previo:
        return dict(con.execute("SELECT * FROM consultas WHERE id = ?", (previo,)).fetchone()) | {"duplicado": True}
    operario = _obtener(con, "operarios", datos.get("operario_id"))
    if not operario:
        raise ErrorDeDatos("Falta el operario")
    maquina = _obtener(con, "maquinas", datos.get("maquina_id"))
    pregunta = (datos.get("pregunta") or "").strip()
    if not pregunta:
        raise ErrorDeDatos("La pregunta está vacía")
    if len(pregunta) > 1000:
        raise ErrorDeDatos("La pregunta es muy larga (máximo 1000 caracteres)")
    # Si la consulta se hizo sin señal, la app ya mostró una respuesta local: la guardamos tal cual.
    if datos.get("pedido_ayuda"):
        r = {"respuesta": "Pedido de ayuda enviado al encargado.", "modo": "pedido_ayuda",
             "guia_id": datos.get("guia_id"), "escalar": True}
    elif datos.get("respuesta_offline"):
        r = {"respuesta": datos["respuesta_offline"], "modo": "offline",
             "guia_id": datos.get("guia_id"), "escalar": bool(datos.get("escalar"))}
    else:
        r = asistente.responder(pregunta, maquina["tipo"] if maquina else None)
    cur = con.execute(
        "INSERT INTO consultas (uid, operario_id, maquina_id, pregunta, respuesta, modo, guia_id, escalada, "
        "resuelta, fecha) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, ?)",
        (uid, operario["id"], maquina["id"] if maquina else None, pregunta, r["respuesta"], r["modo"],
         r["guia_id"], int(r["escalar"]), _fecha(datos.get("fecha"))))
    con.commit()
    return dict(con.execute("SELECT * FROM consultas WHERE id = ?", (cur.lastrowid,)).fetchone()) | {"duplicado": False}


def resolver_consulta(con, consulta_id):
    cur = con.execute("UPDATE consultas SET resuelta = 1 WHERE id = ?", (consulta_id,))
    con.commit()
    if cur.rowcount == 0:
        raise ErrorDeDatos("No existe esa consulta")
    return {"id": consulta_id, "resuelta": True}


# ---------------------------------------------------------------------------
# Progreso de formación
# ---------------------------------------------------------------------------

def registrar_progreso(con, datos):
    operario = _obtener(con, "operarios", datos.get("operario_id"))
    if not operario:
        raise ErrorDeDatos("Falta el operario")
    modulo = next((m for m in MODULOS if m["id"] == datos.get("modulo_id")), None)
    if not modulo:
        raise ErrorDeDatos("Módulo desconocido")
    respuestas = datos.get("respuestas") or []
    if len(respuestas) != len(modulo["preguntas"]):
        raise ErrorDeDatos("Faltan respuestas")
    correctas = sum(1 for p, r in zip(modulo["preguntas"], respuestas) if r == p["correcta"])
    puntaje = round(correctas * 100 / len(modulo["preguntas"]))
    aprobado = puntaje >= 70
    previo = con.execute("SELECT puntaje FROM progreso WHERE operario_id = ? AND modulo_id = ?",
                         (operario["id"], modulo["id"])).fetchone()
    # Nos quedamos con el mejor intento.
    if not previo or puntaje >= previo["puntaje"]:
        con.execute("INSERT OR REPLACE INTO progreso (operario_id, modulo_id, puntaje, aprobado, fecha) "
                    "VALUES (?, ?, ?, ?, ?)", (operario["id"], modulo["id"], puntaje, int(aprobado), _fecha(None)))
        con.commit()
    return {"modulo_id": modulo["id"], "puntaje": puntaje, "aprobado": aprobado,
            "correctas": correctas, "total": len(modulo["preguntas"])}


def progreso_operario(con, operario_id):
    _obtener(con, "operarios", operario_id)
    filas = {r["modulo_id"]: dict(r) for r in
             con.execute("SELECT * FROM progreso WHERE operario_id = ?", (operario_id,))}
    modulos = []
    for m in MODULOS:
        f = filas.get(m["id"])
        modulos.append({"id": m["id"], "titulo": m["titulo"], "puntaje": f["puntaje"] if f else None,
                        "aprobado": bool(f and f["aprobado"])})
    aprobados = sum(1 for m in modulos if m["aprobado"])
    desde = (datetime.now() - timedelta(days=30)).isoformat()
    jornadas = con.execute("SELECT COUNT(*) FROM checklists WHERE operario_id = ? AND fecha >= ?",
                           (operario_id, desde)).fetchone()[0]
    calibraciones = con.execute("SELECT COUNT(*) FROM calibraciones WHERE operario_id = ? AND fecha >= ?",
                                (operario_id, desde)).fetchone()[0]
    return {"operario_id": operario_id, "modulos": modulos, "aprobados": aprobados, "total": len(MODULOS),
            "porcentaje": round(aprobados * 100 / len(MODULOS)), "jornadas_30d": jornadas,
            "calibraciones_30d": calibraciones}


# ---------------------------------------------------------------------------
# Estado del equipo, alertas y tablero del dueño
# ---------------------------------------------------------------------------

def _ultimo_checklist(con, maquina_id):
    f = con.execute("SELECT * FROM checklists WHERE maquina_id = ? ORDER BY fecha DESC, id DESC LIMIT 1",
                    (maquina_id,)).fetchone()
    return dict(f) if f else None


def estado_maquina(con, maquina):
    """'parada', 'atencion' u 'ok', con los motivos."""
    motivos = []
    estado = "ok"
    ult = _ultimo_checklist(con, maquina["id"])
    if ult and ult["fecha"][:10] == _hoy().isoformat():
        if ult["resultado"] == "no_apta":
            estado = "parada"
            motivos.append("Checklist de hoy NO APTA")
        elif ult["resultado"] == "con_observaciones":
            estado = "atencion"
            motivos.append("Checklist de hoy con observaciones")
    horas_desde_service = (maquina["horas"] or 0) - (maquina["ultimo_service_horas"] or 0)
    if horas_desde_service >= (maquina["service_cada_horas"] or 250):
        if estado == "ok":
            estado = "atencion"
        motivos.append(f"Service vencido ({horas_desde_service:.0f} h desde el último)")
    return {"estado": estado, "motivos": motivos, "ultimo_checklist": ult}


def alertas(con, empresa_id):
    lista = []
    hoy = _hoy().isoformat()
    maquinas = con.execute("SELECT * FROM maquinas WHERE empresa_id = ?", (empresa_id,)).fetchall()
    for m in maquinas:
        est = estado_maquina(con, m)
        for motivo in est["motivos"]:
            nivel = "alta" if est["estado"] == "parada" else "media"
            lista.append({"nivel": nivel, "tipo": "maquina", "maquina_id": m["id"],
                          "texto": f"{m['apodo']}: {motivo}",
                          "detalle": (est["ultimo_checklist"] or {}).get("observaciones")
                          if "Checklist" in motivo else None})
    desde = (datetime.now() - timedelta(days=7)).isoformat()
    for c in con.execute(
            "SELECT c.*, o.nombre AS operario, m.apodo FROM calibraciones c "
            "JOIN operarios o ON o.id = c.operario_id LEFT JOIN maquinas m ON m.id = c.maquina_id "
            "WHERE o.empresa_id = ? AND c.aprobada = 0 AND c.fecha >= ? ORDER BY c.fecha DESC",
            (empresa_id, desde)):
        res = json.loads(c["resultado_json"])
        lista.append({"nivel": "media", "tipo": "calibracion", "maquina_id": c["maquina_id"],
                      "texto": f"{c['apodo'] or 'Calibración'}: {res.get('texto', 'calibración fuera de rango')}",
                      "detalle": f"Registró {c['operario']} el {c['fecha'][:10]}"})
    for q in con.execute(
            "SELECT q.*, o.nombre AS operario FROM consultas q JOIN operarios o ON o.id = q.operario_id "
            "WHERE o.empresa_id = ? AND q.escalada = 1 AND q.resuelta = 0 ORDER BY q.fecha DESC", (empresa_id,)):
        lista.append({"nivel": "alta", "tipo": "consulta", "consulta_id": q["id"],
                      "texto": f"{q['operario']} pide ayuda: \"{q['pregunta'][:90]}\"",
                      "detalle": q["fecha"][:16].replace("T", " ")})
    trabajan = con.execute("SELECT id, nombre FROM operarios WHERE empresa_id = ? AND rol NOT LIKE 'Encargado%'",
                           (empresa_id,)).fetchall()
    for o in trabajan:
        hizo = con.execute("SELECT 1 FROM checklists WHERE operario_id = ? AND substr(fecha, 1, 10) = ?",
                           (o["id"], hoy)).fetchone()
        if not hizo:
            lista.append({"nivel": "baja", "tipo": "operario", "operario_id": o["id"],
                          "texto": f"{o['nombre']} no hizo checklist hoy", "detalle": None})
    orden = {"alta": 0, "media": 1, "baja": 2}
    lista.sort(key=lambda a: orden[a["nivel"]])
    return lista


def datos_empresa(con, empresa_id=1):
    emp = con.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,)).fetchone()
    if not emp:
        raise ErrorDeDatos("No existe la empresa")
    return {
        "empresa": dict(emp),
        "operarios": [dict(r) for r in con.execute("SELECT * FROM operarios WHERE empresa_id = ? ORDER BY id", (empresa_id,))],
        "maquinas": [dict(r) for r in con.execute("SELECT * FROM maquinas WHERE empresa_id = ? ORDER BY id", (empresa_id,))],
        "lotes": [dict(r) for r in con.execute("SELECT * FROM lotes WHERE empresa_id = ? ORDER BY id", (empresa_id,))],
    }


def tablero(con, empresa_id=1):
    base = datos_empresa(con, empresa_id)
    maquinas = []
    for m in con.execute("SELECT * FROM maquinas WHERE empresa_id = ? ORDER BY id", (empresa_id,)).fetchall():
        est = estado_maquina(con, m)
        ult = est["ultimo_checklist"]
        quien = None
        if ult:
            quien = con.execute("SELECT nombre FROM operarios WHERE id = ?", (ult["operario_id"],)).fetchone()["nombre"]
        maquinas.append({**dict(m), "estado": est["estado"], "motivos": est["motivos"],
                         "ultimo_checklist": {"fecha": ult["fecha"], "resultado": ult["resultado"],
                                              "operario": quien} if ult else None})
    operarios = []
    for o in base["operarios"]:
        p = progreso_operario(con, o["id"])
        operarios.append({**o, "formacion_pct": p["porcentaje"], "modulos_aprobados": p["aprobados"],
                          "jornadas_30d": p["jornadas_30d"], "calibraciones_30d": p["calibraciones_30d"]})
    hoy = _hoy().isoformat()
    checklists_hoy = [dict(r) for r in con.execute(
        "SELECT c.id, c.fecha, c.resultado, c.observaciones, o.nombre AS operario, m.apodo AS maquina "
        "FROM checklists c JOIN operarios o ON o.id = c.operario_id JOIN maquinas m ON m.id = c.maquina_id "
        "WHERE m.empresa_id = ? AND substr(c.fecha, 1, 10) = ? ORDER BY c.fecha DESC", (empresa_id, hoy))]
    consultas = [dict(r) for r in con.execute(
        "SELECT q.id, q.fecha, q.pregunta, q.modo, q.escalada, q.resuelta, o.nombre AS operario "
        "FROM consultas q JOIN operarios o ON o.id = q.operario_id WHERE o.empresa_id = ? "
        "ORDER BY q.fecha DESC LIMIT 10", (empresa_id,))]
    al = alertas(con, empresa_id)
    impacto = impacto_semana(con, empresa_id)
    resumen = {
        "maquinas_ok": sum(1 for m in maquinas if m["estado"] == "ok"),
        "maquinas_atencion": sum(1 for m in maquinas if m["estado"] == "atencion"),
        "maquinas_paradas": sum(1 for m in maquinas if m["estado"] == "parada"),
        "checklists_hoy": len(checklists_hoy),
        "alertas_altas": sum(1 for a in al if a["nivel"] == "alta"),
    }
    return {"empresa": base["empresa"], "resumen": resumen, "impacto": impacto, "maquinas": maquinas,
            "operarios": operarios, "alertas": al, "checklists_hoy": checklists_hoy, "consultas": consultas,
            "lotes": base["lotes"]}


def impacto_semana(con, empresa_id, dias=7):
    """Lo que el sistema 'atajó' en los últimos días: es el argumento de valor para el dueño."""
    desde = (datetime.now() - timedelta(days=dias)).isoformat()
    filtro = "FROM checklists c JOIN maquinas m ON m.id = c.maquina_id WHERE m.empresa_id = ? AND c.fecha >= ?"
    checklists = con.execute("SELECT COUNT(*) " + filtro, (empresa_id, desde)).fetchone()[0]
    frenadas = con.execute("SELECT COUNT(*) " + filtro + " AND c.resultado = 'no_apta'", (empresa_id, desde)).fetchone()[0]
    filtro_cal = ("FROM calibraciones c JOIN operarios o ON o.id = c.operario_id "
                  "WHERE o.empresa_id = ? AND c.fecha >= ?")
    calibraciones = con.execute("SELECT COUNT(*) " + filtro_cal, (empresa_id, desde)).fetchone()[0]
    fuera = con.execute("SELECT COUNT(*) " + filtro_cal + " AND c.aprobada = 0", (empresa_id, desde)).fetchone()[0]
    perdidas = [json.loads(r["resultado_json"])["kg_ha"] for r in con.execute(
        "SELECT c.resultado_json " + filtro_cal + " AND c.tipo = 'perdidas'", (empresa_id, desde))]
    ayuda = con.execute(
        "SELECT COUNT(*), COALESCE(SUM(q.resuelta), 0) FROM consultas q JOIN operarios o ON o.id = q.operario_id "
        "WHERE o.empresa_id = ? AND q.fecha >= ? AND q.escalada = 1", (empresa_id, desde)).fetchone()
    consultas = con.execute(
        "SELECT COUNT(*) FROM consultas q JOIN operarios o ON o.id = q.operario_id WHERE o.empresa_id = ? AND q.fecha >= ?",
        (empresa_id, desde)).fetchone()[0]
    return {
        "dias": dias,
        "checklists": checklists,
        "salidas_frenadas": frenadas,
        "calibraciones": calibraciones,
        "calibraciones_fuera_de_rango": fuera,
        "mediciones_perdidas": len(perdidas),
        "perdida_promedio_kg_ha": round(sum(perdidas) / len(perdidas), 1) if perdidas else None,
        "consultas": consultas,
        "pedidos_ayuda": ayuda[0],
        "pedidos_resueltos": ayuda[1],
    }


def constancia_lote(con, lote_id):
    """Constancia para el productor: qué equipos entraron a su lote, con qué checklist y calibraciones."""
    lote = _obtener(con, "lotes", lote_id)
    if not lote:
        raise ErrorDeDatos("Falta el lote")
    labores = []
    for c in con.execute(
            "SELECT c.*, o.nombre AS operario, m.apodo, m.tipo, m.marca FROM checklists c "
            "JOIN operarios o ON o.id = c.operario_id JOIN maquinas m ON m.id = c.maquina_id "
            "WHERE c.lote_id = ? ORDER BY c.fecha DESC", (lote_id,)):
        dia = c["fecha"][:10]
        cals = [_calibracion(con, r["id"]) for r in con.execute(
            "SELECT id FROM calibraciones WHERE maquina_id = ? AND substr(fecha, 1, 10) BETWEEN date(?, '-3 day') AND ?",
            (c["maquina_id"], dia, dia))]
        labores.append({
            "fecha": c["fecha"], "operario": c["operario"], "maquina": c["apodo"], "tipo": c["tipo"],
            "marca": c["marca"], "checklist": c["resultado"], "observaciones": c["observaciones"],
            "calibraciones": [{"tipo": k["tipo"], "fecha": k["fecha"], "aprobada": k["aprobada"],
                               "texto": k["resultado"].get("texto")} for k in cals],
        })
    empresa = con.execute("SELECT nombre FROM empresas WHERE id = ?", (lote["empresa_id"],)).fetchone()["nombre"]
    return {"lote": dict(lote), "contratista": empresa, "labores": labores,
            "emitida": datetime.now().replace(microsecond=0).isoformat()}


# ---------------------------------------------------------------------------
# Sincronización de lo que se cargó sin señal
# ---------------------------------------------------------------------------

def sincronizar(con, lote):
    """Procesa una lista de operaciones [{tipo, datos}] guardadas offline.

    Cada una se procesa por separado: si una falla, las demás siguen.
    """
    if not isinstance(lote, list):
        raise ErrorDeDatos("Se esperaba una lista de operaciones")
    funciones = {"checklist": registrar_checklist, "calibracion": registrar_calibracion,
                 "consulta": registrar_consulta}
    resultados = []
    for op in lote:
        tipo = (op or {}).get("tipo")
        datos = (op or {}).get("datos") or {}
        if tipo == "progreso":
            fn = lambda c, d, origen=None: registrar_progreso(c, d)  # noqa: E731
        else:
            fn = funciones.get(tipo)
        if not fn:
            resultados.append({"uid": datos.get("uid"), "ok": False, "error": f"Tipo desconocido: {tipo}"})
            continue
        try:
            r = fn(con, datos, origen="offline")
            resultados.append({"uid": datos.get("uid"), "ok": True, "duplicado": r.get("duplicado", False)})
        except ErrorDeDatos as err:
            resultados.append({"uid": datos.get("uid"), "ok": False, "error": str(err)})
    return {"procesadas": len(resultados), "ok": sum(1 for r in resultados if r["ok"]), "resultados": resultados}
