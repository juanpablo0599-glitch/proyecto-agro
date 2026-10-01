import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from copiloto import asistente  # noqa: E402


class TestModoMock(unittest.TestCase):
    def setUp(self):
        self.env = mock.patch.dict(os.environ, {"COPILOTO_MOCK": "1"})
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_encuentra_guia_de_siembra(self):
        r = asistente.responder("la sembradora me deja dobles y fallas", "sembradora")
        self.assertEqual(r["modo"], "mock")
        self.assertEqual(r["guia_id"], "siembra_dobles_fallas")
        self.assertIn("5 y 8 km/h", r["respuesta"])
        self.assertIn("Cuándo parar", r["respuesta"])

    def test_acentos_y_mayusculas(self):
        r = asistente.responder("PRESIÓN del manómetro sube y baja", "pulverizadora")
        self.assertEqual(r["guia_id"], "pulv_presion")

    def test_usa_tipo_de_maquina_para_desempatar(self):
        r = asistente.responder("tengo perdidas", "cosechadora")
        self.assertTrue(r["guia_id"].startswith("cosecha_"))

    def test_urgencia_siempre_escala_y_prioriza_seguridad(self):
        r = asistente.responder("hay humo saliendo del motor de la cosechadora", "cosechadora")
        self.assertTrue(r["escalar"])
        self.assertTrue(r["respuesta"].startswith("PRIMERO LA SEGURIDAD"))

    def test_no_recomienda_productos(self):
        r = asistente.responder("¿qué herbicida le echo al barbecho?", "pulverizadora")
        self.assertIn("marbete", r["respuesta"])
        self.assertIsNone(r["guia_id"])

    def test_sin_guia_deriva_al_encargado(self):
        r = asistente.responder("el aire acondicionado de la cabina no enfría", "tractor")
        self.assertIsNone(r["guia_id"])
        self.assertTrue(r["escalar"])

    def test_pregunta_vacia(self):
        r = asistente.responder("   ")
        self.assertFalse(r["escalar"])

    def test_perdida_de_cosecha_no_se_confunde_con_perdida_de_liquido(self):
        r = asistente.responder("cuanta perdida de grano es normal en soja", "cosechadora")
        self.assertFalse(r["escalar"])


class _BloqueTexto:
    type = "text"

    def __init__(self, text):
        self.text = text


class TestModoIA(unittest.TestCase):
    """Verifica el camino con IA usando un módulo `anthropic` falso (sin red ni key real)."""

    def _modulo_falso(self, respuesta=None, error=None):
        llamadas = []

        class Mensajes:
            def create(self, **kwargs):
                llamadas.append(kwargs)
                if error:
                    raise error
                return respuesta

        class Cliente:
            def __init__(self):
                self.beta = types.SimpleNamespace(messages=Mensajes())

        return types.SimpleNamespace(Anthropic=Cliente), llamadas

    def test_usa_ia_con_modelo_y_reglas(self):
        resp = types.SimpleNamespace(stop_reason="end_turn", content=[_BloqueTexto("1. Bajá la velocidad.")])
        falso, llamadas = self._modulo_falso(respuesta=resp)
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "x", "COPILOTO_MOCK": ""}), \
                mock.patch.dict(sys.modules, {"anthropic": falso}):
            r = asistente.responder("la sembradora deja dobles", "sembradora")
        self.assertEqual(r["modo"], "ia")
        self.assertEqual(r["respuesta"], "1. Bajá la velocidad.")
        kw = llamadas[0]
        self.assertEqual(kw["model"], "claude-opus-5-5")
        self.assertIn("NO recomiendes marcas", kw["system"])
        self.assertIn("Guía interna", kw["messages"][0]["content"])
        self.assertEqual(kw["fallbacks"], "default")

    def test_si_la_ia_falla_responde_con_la_base_local(self):
        falso, _ = self._modulo_falso(error=RuntimeError("sin red"))
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "x", "COPILOTO_MOCK": ""}), \
                mock.patch.dict(sys.modules, {"anthropic": falso}):
            r = asistente.responder("la sembradora deja dobles", "sembradora")
        self.assertEqual(r["modo"], "mock-respaldo")
        self.assertEqual(r["guia_id"], "siembra_dobles_fallas")

    def test_rechazo_de_la_ia_cae_en_respaldo(self):
        resp = types.SimpleNamespace(stop_reason="refusal", content=[])
        falso, _ = self._modulo_falso(respuesta=resp)
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "x", "COPILOTO_MOCK": ""}), \
                mock.patch.dict(sys.modules, {"anthropic": falso}):
            r = asistente.responder("el motor calienta", "tractor")
        self.assertEqual(r["modo"], "mock-respaldo")

    def test_urgencias_no_esperan_a_la_ia(self):
        falso, llamadas = self._modulo_falso(respuesta=None)
        with mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "x", "COPILOTO_MOCK": ""}), \
                mock.patch.dict(sys.modules, {"anthropic": falso}):
            r = asistente.responder("hubo un accidente con el cardan", "tractor")
        self.assertEqual(llamadas, [])
        self.assertTrue(r["escalar"])

    def test_sin_key_usa_mock(self):
        env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(asistente.ia_disponible())


if __name__ == "__main__":
    unittest.main()
