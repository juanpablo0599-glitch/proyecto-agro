import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copiloto import calculos  # noqa: E402


class TestPulverizadora(unittest.TestCase):
    def test_caudal_por_pastilla(self):
        # 100 L/ha a 20 km/h con picos a 52,5 cm -> 1,75 L/min
        r = calculos.caudal_por_pastilla(100, 20, 52.5)
        self.assertAlmostEqual(r["caudal_l_min"], 1.75, places=3)
        self.assertIn("1.75", r["texto"])

    def test_datos_invalidos(self):
        with self.assertRaises(calculos.DatoInvalido):
            calculos.caudal_por_pastilla(0, 20, 52.5)
        with self.assertRaises(calculos.DatoInvalido):
            calculos.caudal_por_pastilla("", 20, 52.5)

    def test_prueba_de_jarra_detecta_pastillas_fuera_de_rango(self):
        r = calculos.verificar_pastillas(1.26, [1.27, 1.25, 1.41, 1.10])
        self.assertEqual(r["a_revisar"], [3, 4])
        self.assertFalse(r["aprobada"])
        self.assertTrue(r["detalle"][0]["ok"])

    def test_prueba_de_jarra_ok(self):
        r = calculos.verificar_pastillas(1.0, [1.05, 0.95, 1.0])
        self.assertTrue(r["aprobada"])
        self.assertEqual(r["a_revisar"], [])

    def test_prueba_de_jarra_sin_mediciones(self):
        with self.assertRaises(calculos.DatoInvalido):
            calculos.verificar_pastillas(1.0, [])


class TestSembradora(unittest.TestCase):
    def test_semillas_por_metro_maiz(self):
        # 80.000 pl/ha a 52,5 cm = 4,2 pl/m; con PG 95% y logro 90% -> 4,91 sem/m
        r = calculos.semillas_por_metro(80000, 52.5, 95, 90)
        self.assertAlmostEqual(r["plantas_por_metro"], 4.2, places=2)
        self.assertAlmostEqual(r["semillas_por_metro"], 4.91, places=2)
        self.assertAlmostEqual(r["semillas_en_10_metros"], 49.1, places=1)

    def test_porcentaje_mayor_a_100_es_invalido(self):
        with self.assertRaises(calculos.DatoInvalido):
            calculos.semillas_por_metro(80000, 52.5, 120, 90)

    def test_kg_semilla_por_ha(self):
        # 30 semillas/m2 con P1000 de 180 g -> 54 kg/ha
        self.assertAlmostEqual(calculos.kg_semilla_por_ha(30, 180)["kg_ha"], 54.0)

    def test_verificar_siembra(self):
        r = calculos.verificar_siembra([49, 50, 40], 4.91)
        self.assertEqual(r["a_revisar"], [3])
        self.assertFalse(r["aprobada"])


class TestPerdidasCosecha(unittest.TestCase):
    def test_perdida_dentro_de_tolerancia_soja(self):
        # 40 granos/m2 x 170 g / 100 = 68 kg/ha < 75 (tolerancia INTA)
        r = calculos.perdidas_cosecha(40, 170, "soja")
        self.assertAlmostEqual(r["kg_ha"], 68.0)
        self.assertEqual(r["veredicto"], "ok")

    def test_perdida_alta_soja(self):
        r = calculos.perdidas_cosecha(84, 170, "soja")  # 142,8 kg/ha, el promedio que reporta el INTA
        self.assertEqual(r["veredicto"], "alta")
        self.assertIn("75", r["texto"])

    def test_cultivo_sin_tolerancia_verificada(self):
        r = calculos.perdidas_cosecha(30, 300, "maiz")
        self.assertEqual(r["veredicto"], "sin_tolerancia")
        self.assertIsNone(r["tolerancia_kg_ha"])

    def test_granos_negativos(self):
        with self.assertRaises(calculos.DatoInvalido):
            calculos.perdidas_cosecha(-1, 170)


if __name__ == "__main__":
    unittest.main()
