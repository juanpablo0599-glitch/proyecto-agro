"""Base de datos local (SQLite) y datos de ejemplo.

Los datos de ejemplo son FICTICIOS (empresa, personas y productores inventados).
Las localidades y marcas de maquinaria son reales para que el ejemplo se vea
como el parque mezclado de un contratista de verdad.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta

ESQUEMA = """
CREATE TABLE IF NOT EXISTS empresas (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    localidad TEXT,
    provincia TEXT
);
CREATE TABLE IF NOT EXISTS operarios (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL,
    telefono TEXT,
    ingreso TEXT
);
CREATE TABLE IF NOT EXISTS maquinas (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    tipo TEXT NOT NULL,
    apodo TEXT NOT NULL,
    marca TEXT,
    modelo TEXT,
    anio INTEGER,
    horas REAL DEFAULT 0,
    service_cada_horas REAL DEFAULT 250,
    ultimo_service_horas REAL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY,
    empresa_id INTEGER NOT NULL REFERENCES empresas(id),
    cliente TEXT NOT NULL,
    nombre TEXT NOT NULL,
    localidad TEXT,
    hectareas REAL,
    cultivo TEXT
);
CREATE TABLE IF NOT EXISTS checklists (
    id INTEGER PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    operario_id INTEGER NOT NULL REFERENCES operarios(id),
    maquina_id INTEGER NOT NULL REFERENCES maquinas(id),
    lote_id INTEGER REFERENCES lotes(id),
    fecha TEXT NOT NULL,
    items_json TEXT NOT NULL,
    resultado TEXT NOT NULL,
    observaciones TEXT,
    origen TEXT DEFAULT 'online'
);
CREATE TABLE IF NOT EXISTS calibraciones (
    id INTEGER PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    operario_id INTEGER NOT NULL REFERENCES operarios(id),
    maquina_id INTEGER REFERENCES maquinas(id),
    tipo TEXT NOT NULL,
    entradas_json TEXT NOT NULL,
    resultado_json TEXT NOT NULL,
    aprobada INTEGER NOT NULL,
    fecha TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY,
    uid TEXT UNIQUE NOT NULL,
    operario_id INTEGER NOT NULL REFERENCES operarios(id),
    maquina_id INTEGER REFERENCES maquinas(id),
    pregunta TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    modo TEXT NOT NULL,
    guia_id TEXT,
    escalada INTEGER NOT NULL DEFAULT 0,
    resuelta INTEGER NOT NULL DEFAULT 0,
    fecha TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progreso (
    operario_id INTEGER NOT NULL REFERENCES operarios(id),
    modulo_id TEXT NOT NULL,
    puntaje INTEGER NOT NULL,
    aprobado INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    PRIMARY KEY (operario_id, modulo_id)
);
"""

RUTA_POR_DEFECTO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                "data", "copiloto.db")


def ahora():
    return datetime.now().replace(microsecond=0)


def conectar(ruta=None):
    ruta = ruta or os.environ.get("COPILOTO_DB") or RUTA_POR_DEFECTO
    if ruta != ":memory:":
        os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    con = sqlite3.connect(ruta, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def inicializar(con, con_datos_ejemplo=True):
    con.executescript(ESQUEMA)
    vacia = con.execute("SELECT COUNT(*) FROM empresas").fetchone()[0] == 0
    if vacia and con_datos_ejemplo:
        cargar_datos_ejemplo(con)
    con.commit()


def _uid():
    return str(uuid.uuid4())


def cargar_datos_ejemplo(con):
    """Contratista ficticio de la zona de Casilda con parque mezclado y viejo."""
    hoy = ahora()
    con.execute("INSERT INTO empresas (id, nombre, localidad, provincia) VALUES (1, ?, ?, ?)",
                ("Servicios Agrícolas Los Aromos (ejemplo)", "Casilda", "Santa Fe"))

    operarios = [
        (1, "Raúl Benítez", "Maquinista de cosechadora", "3464-000001", "2009-03-01"),
        (2, "Matías Ferreyra", "Operario de pulverizadora", "3464-000002", "2024-08-15"),
        (3, "Lucas Giménez", "Tractorista / sembradora", "3464-000003", "2026-07-01"),
        (4, "Brenda Sosa", "Operaria de pulverizadora", "3464-000004", "2025-02-10"),
        (5, "Walter Quiroga", "Encargado de equipo", "3464-000005", "2003-11-20"),
    ]
    con.executemany("INSERT INTO operarios (id, empresa_id, nombre, rol, telefono, ingreso) "
                    "VALUES (?, 1, ?, ?, ?, ?)", operarios)

    maquinas = [
        # id, tipo, apodo, marca, modelo, año, horas, service cada, último service
        (1, "cosechadora", "La Colorada", "Case IH", "Axial", 2012, 6480, 250, 6300),
        (2, "cosechadora", "La Verde", "John Deere", "Convencional", 2008, 9120, 250, 8850),
        (3, "pulverizadora", "Autopropulsada 1", "Pla", "Autopropulsada 28 m", 2019, 3150, 250, 3000),
        (4, "pulverizadora", "Autopropulsada 2", "Metalfor", "Autopropulsada 27 m", 2022, 1640, 250, 1600),
        (5, "sembradora", "La Grande", "Crucianelli", "Neumática 16 surcos", 2016, 2210, 200, 2100),
        (6, "tractor", "El Rojo", "Massey Ferguson", "180 HP", 2014, 7850, 250, 7700),
    ]
    con.executemany("INSERT INTO maquinas (id, empresa_id, tipo, apodo, marca, modelo, anio, horas, "
                    "service_cada_horas, ultimo_service_horas) VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?)",
                    maquinas)

    lotes = [
        (1, "Establecimiento Don Ernesto (ejemplo)", "Lote 4 - Bajo", "Casilda", 120, "maiz"),
        (2, "Establecimiento Don Ernesto (ejemplo)", "Lote 7 - La Loma", "Casilda", 85, "soja"),
        (3, "Agropecuaria Las Tunas (ejemplo)", "Potrero Norte", "Chabás", 210, "soja"),
        (4, "Familia Peralta (ejemplo)", "El Molino", "Arteaga", 64, "maiz"),
        (5, "Agropecuaria Las Tunas (ejemplo)", "Lote 12", "Chabás", 150, "trigo"),
    ]
    con.executemany("INSERT INTO lotes (id, empresa_id, cliente, nombre, localidad, hectareas, cultivo) "
                    "VALUES (?, 1, ?, ?, ?, ?, ?)", lotes)

    from .conocimiento import CHECKLISTS

    def items_ok(tipo, fallan=()):
        return {i["id"]: (i["id"] not in fallan) for i in CHECKLISTS[tipo]}

    # Historial de checklists de los últimos 10 días (campaña de siembra/pulverización).
    historial = []
    for d in range(10, 0, -1):
        dia = (hoy - timedelta(days=d)).replace(hour=7, minute=10)
        historial.append((3, 5, 1, dia, "sembradora", ()))
        historial.append((2, 3, 3, dia, "pulverizadora", ()))
        if d % 2 == 0:
            historial.append((4, 4, 2, dia, "pulverizadora", ("agua_limpia",)))
    for operario, maquina, lote, fecha, tipo, fallan in historial:
        _insertar_checklist(con, operario, maquina, lote, fecha, tipo, items_ok(tipo, fallan))

    # Hoy: la sembradora salió bien; la Autopropulsada 2 NO salió (pérdida en mangueras).
    # A las 7:05 si ya pasó esa hora; si se abre de madrugada, unos minutos antes (sin cambiar de día).
    hoy_7 = hoy.replace(hour=7, minute=5)
    if hoy_7 > hoy:
        hoy_7 = max(hoy.replace(hour=0, minute=0, second=0), hoy - timedelta(minutes=20))
    _insertar_checklist(con, 3, 5, 4, hoy_7, "sembradora", items_ok("sembradora", ("monitor",)),
                        "El monitor marca alarma en el cuerpo 9, el cuerpo tira bien.")
    _insertar_checklist(con, 4, 4, 2, hoy_7, "pulverizadora", items_ok("pulverizadora", ("mangueras",)),
                        "Pierde por la conexión del botalón derecho.")

    # Calibraciones: una prueba de jarra con 2 pastillas fuera de rango.
    from . import calculos
    obj = calculos.caudal_por_pastilla(80, 18, 52.5)["caudal_l_min"]
    medidos = [1.27, 1.25, 1.24, 1.41, 1.26, 1.10, 1.25, 1.27]
    res = calculos.verificar_pastillas(obj, medidos)
    con.execute("INSERT INTO calibraciones (uid, operario_id, maquina_id, tipo, entradas_json, "
                "resultado_json, aprobada, fecha) VALUES (?, 2, 3, 'pulverizadora', ?, ?, ?, ?)",
                (_uid(), json.dumps({"volumen_l_ha": 80, "velocidad_km_h": 18, "distancia_picos_cm": 52.5,
                                     "medidos_l_min": medidos}),
                 json.dumps(res), int(res["aprobada"]), (hoy - timedelta(days=2)).isoformat()))
    sem = calculos.semillas_por_metro(80000, 52.5, 95, 90)
    ver = calculos.verificar_siembra([49, 50, 47, 51, 49], sem["semillas_por_metro"])
    con.execute("INSERT INTO calibraciones (uid, operario_id, maquina_id, tipo, entradas_json, "
                "resultado_json, aprobada, fecha) VALUES (?, 3, 5, 'siembra', ?, ?, ?, ?)",
                (_uid(), json.dumps({"plantas_ha": 80000, "distancia_surcos_cm": 52.5, "pg": 95,
                                     "eficiencia": 90, "contadas_10m": [49, 50, 47, 51, 49]}),
                 json.dumps({**sem, **ver}), int(ver["aprobada"]), (hoy - timedelta(days=1)).isoformat()))

    # Consultas previas (una escalada sin resolver).
    consultas = [
        (3, 5, "¿A qué velocidad tengo que ir con la sembradora en este lote?",
         "El INTA recomienda entre 5 y 8 km/h según la máquina...", "siembra_dobles_fallas", 0, 1),
        (2, 3, "Tengo una pastilla que tira mucho más que las otras", "Hacé la prueba de jarra...",
         "pulv_caudal_desparejo", 0, 1),
        (4, 4, "Pierde líquido por la conexión del botalón y no sé si cambiar la manguera o la abrazadera",
         "No apliques con pérdidas. Avisé al encargado para que lo revise.", None, 1, 0),
    ]
    for i, (op, maq, preg, resp, guia, esc, resuelta) in enumerate(consultas):
        con.execute("INSERT INTO consultas (uid, operario_id, maquina_id, pregunta, respuesta, modo, "
                    "guia_id, escalada, resuelta, fecha) VALUES (?, ?, ?, ?, ?, 'mock', ?, ?, ?, ?)",
                    (_uid(), op, maq, preg, resp, guia, esc, resuelta,
                     (hoy - timedelta(hours=30 - i * 10)).isoformat()))

    # Progreso de formación.
    progreso = [
        (1, "m0_seguridad", 100), (1, "m1_tractor", 100), (1, "m4_cosechadora", 100), (1, "m5_precision", 100),
        (2, "m0_seguridad", 100), (2, "m3_pulverizadora", 67),
        (3, "m0_seguridad", 100), (3, "m1_tractor", 50),
        (4, "m0_seguridad", 100), (4, "m3_pulverizadora", 100), (4, "m6_cliente", 100),
    ]
    for op, mod, p in progreso:
        con.execute("INSERT INTO progreso (operario_id, modulo_id, puntaje, aprobado, fecha) VALUES (?, ?, ?, ?, ?)",
                    (op, mod, p, int(p >= 70), (hoy - timedelta(days=5)).isoformat()))


def _insertar_checklist(con, operario, maquina, lote, fecha, tipo, items, observaciones=None):
    from .servicios import evaluar_checklist

    resultado = evaluar_checklist(tipo, items)
    con.execute("INSERT INTO checklists (uid, operario_id, maquina_id, lote_id, fecha, items_json, "
                "resultado, observaciones, origen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'online')",
                (_uid(), operario, maquina, lote, fecha.isoformat(), json.dumps(items), resultado,
                 observaciones))
