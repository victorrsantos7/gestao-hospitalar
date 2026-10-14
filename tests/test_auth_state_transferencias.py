import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState


class AuthStateTransferenciasTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_medico_cannot_create_transfer(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.internacao_id_transferencia = "71"
        state.erro_transferencia = ""
        state.sucesso_transferencia = ""

        state.criar_transferencia()

        self.assertIn("permissão", state.erro_transferencia)

    def test_active_admission_creates_transfer(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.internacao_id_transferencia = "71"
        state.data_transferencia = "2026-10-13"
        state.destino_transferencia = "UTI"
        state.motivo_transferencia = "Acompanhamento medico"
        state.internacoes = [{"id": "71", "status": "internado"}]
        state.erro_transferencia = ""
        state.sucesso_transferencia = ""

        client = Mock()
        client.criar_transferencia.return_value = 81
        client.listar_transferencias.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_transferencia()

        client.criar_transferencia.assert_called_once_with(
            "",
            {
                "internacao_id": 71,
                "data_transferencia": "2026-10-13",
                "destino": "UTI",
                "motivo": "Acompanhamento medico",
            },
        )
        self.assertIn("#81", state.sucesso_transferencia)

    def test_closed_admission_cannot_receive_transfer(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "admin"
        state.internacao_id_transferencia = "71"
        state.data_transferencia = "2026-10-13"
        state.destino_transferencia = "UTI"
        state.motivo_transferencia = "Acompanhamento medico"
        state.internacoes = [{"id": "71", "status": "alta"}]
        state.erro_transferencia = ""
        state.sucesso_transferencia = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.criar_transferencia()

        self.assertIn("encerrada", state.erro_transferencia)
        client_class.assert_not_called()

    def test_transfer_history_keeps_multiple_records(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.transferencias = []
        client = Mock()
        client.listar_transferencias.return_value = [
            {"id": 81, "destino": "UTI"},
            {"id": 82, "destino": "Enfermaria"},
        ]
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state._carregar_transferencias("71")

        self.assertEqual([item["id"] for item in state.transferencias], ["81", "82"])


if __name__ == "__main__":
    unittest.main()
