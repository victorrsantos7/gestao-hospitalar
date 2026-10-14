import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoError


class AuthStateDiagnosticosTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_recepcionista_cannot_create_diagnosis(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_diagnostico = ""
        state.sucesso_diagnostico = ""

        state.criar_diagnostico()

        self.assertIn("permissão", state.erro_diagnostico)

    def test_invalid_diagnosis_is_rejected_before_remote_call(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.atendimento_id_diagnostico = "41"
        state.descricao_diagnostico = ""
        state.codigo_cid_diagnostico = "I10"
        state.data_diagnostico = "13/10/2026"
        state.erro_diagnostico = ""
        state.sucesso_diagnostico = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.criar_diagnostico()

        self.assertIn("descrição", state.erro_diagnostico)
        client_class.assert_not_called()

    def test_authorized_user_creates_diagnosis(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.atendimento_id_diagnostico = "41"
        state.descricao_diagnostico = "Hipertensao"
        state.codigo_cid_diagnostico = "I10"
        state.data_diagnostico = "13/10/2026"
        state.erro_diagnostico = ""
        state.sucesso_diagnostico = ""

        client = Mock()
        client.criar_diagnostico.return_value = 51
        client.listar_diagnosticos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_diagnostico()

        client.criar_diagnostico.assert_called_once_with(
            "",
            {
                "atendimento_id": 41,
                "descricao": "Hipertensao",
                "codigo_cid": "I10",
                "data_diagnostico": "2026-10-13",
            },
        )
        self.assertIn("#51", state.sucesso_diagnostico)

    def test_authorized_user_can_create_diagnosis_without_cid(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.atendimento_id_diagnostico = "41"
        state.descricao_diagnostico = "Hipertensao"
        state.codigo_cid_diagnostico = ""
        state.data_diagnostico = "13/10/2026"
        state.erro_diagnostico = ""
        state.sucesso_diagnostico = ""

        client = Mock()
        client.criar_diagnostico.return_value = 52
        client.listar_diagnosticos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_diagnostico()

        self.assertEqual(
            client.criar_diagnostico.call_args.args[1]["codigo_cid"],
            None,
        )
        self.assertIn("#52", state.sucesso_diagnostico)

    def test_diagnosis_list_failure_keeps_session(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.atendimento_id_diagnostico = "41"
        state.diagnosticos = []
        state.erro_diagnostico = ""
        client = Mock()
        client.listar_diagnosticos.side_effect = XanoError("remote")

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state._carregar_diagnosticos("41")

        self.assertEqual(state.usuario_id, 10)
        self.assertIn("carregar", state.erro_diagnostico)


if __name__ == "__main__":
    unittest.main()
