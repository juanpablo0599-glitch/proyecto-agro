import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copiloto import conocimiento, db, servicios  # noqa: E402


def base_nueva(con_datos=True):
    con = db.conectar(":memory:")
    db.inicializar(con, con_datos_ejemplo=con_datos)
    return con


def todos_bien(tipo):
    return {i["id"]: True for i in conocimiento.CHECKLISTS[tipo]}


class TestDatosEjemplo(unittest.TestCase):
    def test_carga_datos_realistas(self):
        con = base_nueva()
        datos = servicios.datos_empresa(con)
        self.assertEqual(len(datos["operarios"]), 5)
        self.assertEqual({m["tipo"] for m in datos["maquinas"]},
                         {"tractor", "sembradora", "pulverizadora", "cosechadora"})
        self.assertGreaterEqual(len(datos["lotes"]), 5)

    def test_no_duplica_si_se_inicializa_dos_veces(self):
        con = base_nueva()
        db.inicializar(con)
        self.assertEqual(con.execute("SELECT COUNT(*) FROM empresas").fetchone()[0], 1)


class TestChecklist(unittest.TestCase):
    def setUp(self):
        self.con = base_nueva()

    def test_evaluacion(self):
        items = todos_bien("pulverizadora")
        self.assertEqual(servicios.evaluar_checklist("pulverizadora", items), "apta")
        items["agua_limpia"] = False  # no crítico
        self.assertEqual(servicios.evaluar_checklist("pulverizadora", items), "con_observaciones")
        items["mangueras"] = False  # crítico
        self.assertEqual(servicios.evaluar_checklist("pulverizadora", items), "no_apta")

    def test_item_faltante_cuenta_como_no_revisado(self):
        items = todos_bien("tractor")
        del items["matafuego"]
        self.assertEqual(servicios.evaluar_checklist("tractor", items), "no_apta")

    def test_registrar_y_es_idempotente(self):
        datos = {"uid": "abc-1", "operario_id": 1, "maquina_id": 1, "items": todos_bien("cosechadora")}
        r1 = servicios.registrar_checklist(self.con, datos)
        r2 = servicios.registrar_checklist(self.con, datos)
        self.assertEqual(r1["resultado"], "apta")
        self.assertFalse(r1["duplicado"])
        self.assertTrue(r2["duplicado"])
        self.assertEqual(r1["id"], r2["id"])

    def test_checklist_no_apta_para_la_maquina_y_genera_alerta(self):
        items = todos_bien("cosechadora")
        items["matafuego"] = False
        r = servicios.registrar_checklist(self.con, {"operario_id": 1, "maquina_id": 1, "items": items})
        self.assertEqual(r["resultado"], "no_apta")
        self.assertIn("NO SALE", r["mensaje"])
        maq = self.con.execute("SELECT * FROM maquinas WHERE id = 1").fetchone()
        self.assertEqual(servicios.estado_maquina(self.con, maq)["estado"], "parada")
        alertas = servicios.alertas(self.con, 1)
        self.assertTrue(any(a["nivel"] == "alta" and "La Colorada" in a["texto"] for a in alertas))

    def test_datos_invalidos(self):
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_checklist(self.con, {"operario_id": 999, "maquina_id": 1, "items": {}})
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_checklist(self.con, {"operario_id": 1, "maquina_id": 1, "items": "mal"})


class TestCalibraciones(unittest.TestCase):
    def setUp(self):
        self.con = base_nueva()

    def test_pulverizadora_con_jarra(self):
        r = servicios.registrar_calibracion(self.con, {
            "operario_id": 2, "maquina_id": 3, "tipo": "pulverizadora",
            "entradas": {"volumen_l_ha": 100, "velocidad_km_h": 20, "distancia_picos_cm": 52.5,
                         "medidos_l_min": [1.75, 1.74, 2.2]}})
        self.assertFalse(r["aprobada"])
        self.assertEqual(r["resultado"]["a_revisar"], [3])

    def test_perdidas_altas_no_aprueba(self):
        r = servicios.registrar_calibracion(self.con, {
            "operario_id": 1, "maquina_id": 1, "tipo": "perdidas",
            "entradas": {"granos_m2": 90, "p1000_g": 170, "cultivo": "soja"}})
        self.assertFalse(r["aprobada"])

    def test_tipo_desconocido_y_dato_faltante(self):
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_calibracion(self.con, {"operario_id": 1, "tipo": "otro", "entradas": {}})
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_calibracion(self.con, {"operario_id": 1, "tipo": "siembra", "entradas": {}})


class TestConsultasYProgreso(unittest.TestCase):
    def setUp(self):
        self.con = base_nueva()
        self.env = mock.patch.dict(os.environ, {"COPILOTO_MOCK": "1"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_consulta_guarda_respuesta(self):
        r = servicios.registrar_consulta(self.con, {"operario_id": 3, "maquina_id": 5,
                                                    "pregunta": "la profundidad queda despareja"})
        self.assertEqual(r["guia_id"], "siembra_profundidad")
        self.assertEqual(r["modo"], "mock")

    def test_consulta_escalada_aparece_y_se_resuelve(self):
        r = servicios.registrar_consulta(self.con, {"operario_id": 3, "maquina_id": 6,
                                                    "pregunta": "se rompió algo, hace un ruido raro"})
        self.assertEqual(r["escalada"], 1)
        alertas = servicios.alertas(self.con, 1)
        self.assertTrue(any(a.get("consulta_id") == r["id"] for a in alertas))
        servicios.resolver_consulta(self.con, r["id"])
        self.assertFalse(any(a.get("consulta_id") == r["id"] for a in servicios.alertas(self.con, 1)))

    def test_pedido_de_ayuda_desde_una_guia(self):
        r = servicios.registrar_consulta(self.con, {"operario_id": 3, "maquina_id": 5, "pedido_ayuda": True,
                                                    "guia_id": "siembra_profundidad",
                                                    "pregunta": "Seguí la guía y no se solucionó"})
        self.assertEqual(r["modo"], "pedido_ayuda")
        self.assertEqual(r["escalada"], 1)

    def test_consulta_vacia_o_larga(self):
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_consulta(self.con, {"operario_id": 1, "pregunta": ""})
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.registrar_consulta(self.con, {"operario_id": 1, "pregunta": "x" * 1001})

    def test_progreso_aprueba_con_70(self):
        mod = conocimiento.MODULOS[3]  # pulverizadora, 3 preguntas
        correctas = [p["correcta"] for p in mod["preguntas"]]
        r = servicios.registrar_progreso(self.con, {"operario_id": 3, "modulo_id": mod["id"], "respuestas": correctas})
        self.assertTrue(r["aprobado"])
        self.assertEqual(r["puntaje"], 100)
        p = servicios.progreso_operario(self.con, 3)
        self.assertTrue(next(m for m in p["modulos"] if m["id"] == mod["id"])["aprobado"])

    def test_progreso_se_queda_con_el_mejor_intento(self):
        mod = conocimiento.MODULOS[0]
        bien = [p["correcta"] for p in mod["preguntas"]]
        mal = [(c + 1) % len(p["opciones"]) for c, p in zip(bien, mod["preguntas"])]
        servicios.registrar_progreso(self.con, {"operario_id": 3, "modulo_id": mod["id"], "respuestas": bien})
        r = servicios.registrar_progreso(self.con, {"operario_id": 3, "modulo_id": mod["id"], "respuestas": mal})
        self.assertFalse(r["aprobado"])
        p = servicios.progreso_operario(self.con, 3)
        self.assertTrue(next(m for m in p["modulos"] if m["id"] == mod["id"])["aprobado"])


class TestTableroYSync(unittest.TestCase):
    def setUp(self):
        self.con = base_nueva()

    def test_tablero_de_ejemplo_muestra_estado_mezclado(self):
        t = servicios.tablero(self.con)
        r = t["resumen"]
        self.assertEqual(r["maquinas_paradas"], 1)  # Autopropulsada 2 con pérdida en mangueras
        self.assertGreaterEqual(r["maquinas_atencion"], 2)  # sembradora con observaciones + service vencido
        self.assertEqual(r["checklists_hoy"], 2)
        textos = " ".join(a["texto"] for a in t["alertas"])
        self.assertIn("Service vencido", textos)
        self.assertIn("pastilla", textos)
        self.assertEqual(t["alertas"][0]["nivel"], "alta")  # ordenadas por gravedad

    def test_impacto_semana(self):
        imp = servicios.tablero(self.con)["impacto"]
        self.assertGreaterEqual(imp["salidas_frenadas"], 1)
        self.assertGreaterEqual(imp["calibraciones_fuera_de_rango"], 1)
        self.assertGreaterEqual(imp["checklists"], 15)  # depende de la hora; al menos 6 días completos

    def test_constancia_de_lote(self):
        c = servicios.constancia_lote(self.con, 4)  # lote donde hoy trabajó la sembradora
        self.assertEqual(c["lote"]["nombre"], "El Molino")
        self.assertTrue(c["labores"])
        self.assertEqual(c["labores"][0]["maquina"], "La Grande")
        self.assertTrue(c["labores"][0]["calibraciones"])  # calibró la sembradora ayer
        with self.assertRaises(servicios.ErrorDeDatos):
            servicios.constancia_lote(self.con, 999)

    def test_sync_procesa_lote_offline_sin_duplicar_y_aisla_errores(self):
        with mock.patch.dict(os.environ, {"COPILOTO_MOCK": "1"}):
            lote = [
                {"tipo": "checklist", "datos": {"uid": "off-1", "operario_id": 1, "maquina_id": 2,
                                                "items": todos_bien("cosechadora")}},
                {"tipo": "consulta", "datos": {"uid": "off-2", "operario_id": 1, "maquina_id": 2,
                                               "pregunta": "pierde grano por la cola",
                                               "respuesta_offline": "guía local", "guia_id": "cosecha_perdidas_cola"}},
                {"tipo": "checklist", "datos": {"uid": "off-3", "operario_id": 999, "maquina_id": 2, "items": {}}},
                {"tipo": "raro", "datos": {"uid": "off-4"}},
            ]
            r1 = servicios.sincronizar(self.con, lote)
            r2 = servicios.sincronizar(self.con, lote[:2])
        self.assertEqual(r1["procesadas"], 4)
        self.assertEqual(r1["ok"], 2)
        self.assertTrue(all(x["duplicado"] for x in r2["resultados"]))
        fila = self.con.execute("SELECT origen FROM checklists WHERE uid = 'off-1'").fetchone()
        self.assertEqual(fila["origen"], "offline")
        consulta = self.con.execute("SELECT modo, respuesta FROM consultas WHERE uid = 'off-2'").fetchone()
        self.assertEqual(consulta["modo"], "offline")
        self.assertEqual(consulta["respuesta"], "guía local")


if __name__ == "__main__":
    unittest.main()
