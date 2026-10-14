import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoValidationError


class AuthStateMedicosTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_editing_doctor_fills_form_from_list(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.medicos = [
            {
                "id": "3",
                "nome": "Joao Souza",
                "crm": "123456/SP",
                "especialidade": "Cardiologia",
                "telefone": "11988887777",
            }
        ]
        state.erro_medico = ""

        state.editar_medico("3")

        self.assertEqual(state.id_medico_edicao, "3")
        self.assertEqual(state.nome_medico, "Joao Souza")
        self.assertEqual(state.crm_medico, "123456/SP")
        self.assertEqual(state.especialidade_medico, "Cardiologia")
        self.assertEqual(state.telefone_medico, "(11) 98888-7777")
        self.assertTrue(state.editando_medico)

    def test_editing_unknown_doctor_reports_error(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.medicos = []
        state.erro_medico = ""
        state.id_medico_edicao = ""

        state.editar_medico("999")

        self.assertIn("editar", state.erro_medico)
        self.assertFalse(state.editando_medico)

    def test_cancelling_edit_clears_form(self) -> None:
        state = self._state()
        state.id_medico_edicao = "3"
        state.nome_medico = "Joao Souza"
        state.crm_medico = "123456/SP"
        state.especialidade_medico = "Cardiologia"
        state.telefone_medico = "(11) 98888-7777"

        state.cancelar_edicao_medico()

        self.assertEqual(state.id_medico_edicao, "")
        self.assertEqual(state.nome_medico, "")
        self.assertEqual(state.crm_medico, "")
        self.assertEqual(state.especialidade_medico, "")
        self.assertEqual(state.telefone_medico, "")
        self.assertFalse(state.editando_medico)

    def test_saving_without_edicao_id_creates_doctor(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_medico_edicao = ""
        state.nome_medico = "Joao Souza"
        state.crm_medico = "123456/SP"
        state.especialidade_medico = "Cardiologia"
        state.telefone_medico = "(11) 98888-7777"
        state.erro_medico = ""
        state.sucesso_medico = ""

        client = Mock()
        client.listar_medicos.return_value = []
        client.criar_medico.return_value = 4
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_medico()

        client.criar_medico.assert_called_once()
        client.atualizar_medico.assert_not_called()
        self.assertIn("#4", state.sucesso_medico)
        self.assertEqual(state.id_medico_edicao, "")

    def test_saving_with_edicao_id_updates_doctor(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_medico_edicao = "3"
        state.nome_medico = "Joao Souza"
        state.crm_medico = "123456/SP"
        state.especialidade_medico = "Cardiologia"
        state.telefone_medico = "(11) 98888-7777"
        state.erro_medico = ""
        state.sucesso_medico = ""

        client = Mock()
        client.listar_medicos.return_value = [{"id": "3", "crm": "123456/SP"}]
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_medico()

        client.atualizar_medico.assert_called_once_with(
            "",
            3,
            {
                "nome": "Joao Souza",
                "crm": "123456/SP",
                "especialidade": "Cardiologia",
                "telefone": "11988887777",
            },
        )
        client.criar_medico.assert_not_called()
        self.assertIn("atualizado", state.sucesso_medico)
        self.assertEqual(state.id_medico_edicao, "")

    def test_saving_rejects_crm_already_used_by_other_doctor(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_medico_edicao = "3"
        state.nome_medico = "Joao Souza"
        state.crm_medico = "123456/SP"
        state.especialidade_medico = "Cardiologia"
        state.telefone_medico = "(11) 98888-7777"
        state.erro_medico = ""
        state.sucesso_medico = ""

        client = Mock()
        client.listar_medicos.return_value = [{"id": "9", "crm": "123456/SP"}]
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_medico()

        self.assertIn("CRM", state.erro_medico)
        client.atualizar_medico.assert_not_called()

    def test_deleting_doctor_without_permission_is_blocked(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.erro_medico = ""
        state.sucesso_medico = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.excluir_medico("3")

        self.assertIn("permissão", state.erro_medico)
        client_class.assert_not_called()

    def test_deleting_doctor_succeeds(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_medico = ""
        state.sucesso_medico = ""
        state.medico_selecionado = {"id": "3"}
        state.id_medico_edicao = ""
        state.medicos = []

        client = Mock()
        client.listar_medicos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_medico("3")

        client.excluir_medico.assert_called_once_with("", 3)
        self.assertIn("excluído", state.sucesso_medico)
        self.assertEqual(state.medico_selecionado, {})

    def test_deleting_doctor_with_dependencies_surfaces_backend_message(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_medico = ""
        state.sucesso_medico = ""

        client = Mock()
        client.excluir_medico.side_effect = XanoValidationError(
            "Não é possível excluir: médico possui atendimentos vinculados."
        )
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_medico("3")

        self.assertIn("vinculados", state.erro_medico)


if __name__ == "__main__":
    unittest.main()
