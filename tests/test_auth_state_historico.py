import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoError


class AuthStateHistoricoTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_recepcionista_cannot_consult_history(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.paciente_id_historico = "1 - Ana Ribeiro"
        state.erro_historico = ""
        state.historico_eventos = []

        state.consultar_historico()

        self.assertIn("permissao", state.erro_historico)

    def test_authorized_user_loads_and_orders_history(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.paciente_id_historico = "1 - Ana Ribeiro"
        state.erro_historico = ""
        state.historico_eventos = []
        client = Mock()
        client.consultar_historico.return_value = {
            "atendimentos": [
                {
                    "data_atendimento": "2026-10-13",
                    "tipo": "consulta",
                    "motivo": "Dor",
                    "diagnosticos": [],
                }
            ],
            "internacoes": [],
        }

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.consultar_historico()

        self.assertEqual(state.historico_eventos[0]["tipo"], "atendimento")
        client.consultar_historico.assert_called_once_with("", 1)

    def test_history_failure_does_not_keep_partial_events(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "admin"
        state.paciente_id_historico = "1 - Ana Ribeiro"
        state.historico_eventos = [{"tipo": "old"}]
        state.erro_historico = ""
        client = Mock()
        client.consultar_historico.side_effect = XanoError("remote")

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.consultar_historico()

        self.assertEqual(state.historico_eventos, [])


if __name__ == "__main__":
    unittest.main()
