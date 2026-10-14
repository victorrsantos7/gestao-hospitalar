import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoValidationError


class AuthStatePacientesTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_consulting_same_patient_toggles_details_closed(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.paciente_selecionado = {"id": "1", "nome": "Ana Ribeiro"}
        state.erro_paciente = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.consultar_paciente("1")

        self.assertEqual(state.paciente_selecionado, {})
        client_class.assert_not_called()

    def test_editing_patient_fills_form_from_list(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.pacientes = [
            {
                "id": "7",
                "nome": "Ana Ribeiro",
                "cpf": "52998224725",
                "data_nascimento": "2008-02-09",
                "telefone": "11988887777",
                "endereco": "Rua A, 10",
                "contato_emergencia": "11999998888",
            }
        ]
        state.erro_paciente = ""

        state.editar_paciente("7")

        self.assertEqual(state.id_paciente_edicao, "7")
        self.assertEqual(state.nome_paciente, "Ana Ribeiro")
        self.assertEqual(state.cpf_paciente, "529.982.247-25")
        self.assertEqual(state.nascimento_paciente, "09/02/2008")
        self.assertEqual(state.telefone_paciente, "(11) 98888-7777")
        self.assertEqual(state.endereco_paciente, "Rua A, 10")
        self.assertEqual(state.emergencia_paciente, "(11) 99999-8888")
        self.assertTrue(state.editando_paciente)

    def test_editing_unknown_patient_reports_error(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.pacientes = []
        state.erro_paciente = ""
        state.id_paciente_edicao = ""

        state.editar_paciente("999")

        self.assertIn("editar", state.erro_paciente)
        self.assertFalse(state.editando_paciente)

    def test_cancelling_edit_clears_form(self) -> None:
        state = self._state()
        state.id_paciente_edicao = "7"
        state.nome_paciente = "Ana Ribeiro"
        state.cpf_paciente = "529.982.247-25"
        state.nascimento_paciente = "09/02/2008"
        state.telefone_paciente = "(11) 98888-7777"
        state.endereco_paciente = "Rua A, 10"
        state.emergencia_paciente = "(11) 99999-8888"

        state.cancelar_edicao_paciente()

        self.assertEqual(state.id_paciente_edicao, "")
        self.assertEqual(state.nome_paciente, "")
        self.assertEqual(state.cpf_paciente, "")
        self.assertEqual(state.nascimento_paciente, "")
        self.assertEqual(state.telefone_paciente, "")
        self.assertEqual(state.endereco_paciente, "")
        self.assertEqual(state.emergencia_paciente, "")
        self.assertFalse(state.editando_paciente)

    def test_saving_without_edicao_id_creates_patient(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_paciente_edicao = ""
        state.nome_paciente = "Ana Ribeiro"
        state.cpf_paciente = "529.982.247-25"
        state.nascimento_paciente = "09/02/2008"
        state.telefone_paciente = "(11) 98888-7777"
        state.endereco_paciente = "Rua A, 10"
        state.emergencia_paciente = "(11) 99999-8888"
        state.erro_paciente = ""
        state.sucesso_paciente = ""
        state.pacientes = []

        client = Mock()
        client.listar_pacientes.return_value = []
        client.criar_paciente.return_value = 9
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_paciente()

        client.criar_paciente.assert_called_once()
        client.atualizar_paciente.assert_not_called()
        self.assertIn("#9", state.sucesso_paciente)
        self.assertEqual(state.id_paciente_edicao, "")

    def test_saving_with_edicao_id_updates_patient(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_paciente_edicao = "7"
        state.nome_paciente = "Ana Ribeiro"
        state.cpf_paciente = "529.982.247-25"
        state.nascimento_paciente = "09/02/2008"
        state.telefone_paciente = "(11) 98888-7777"
        state.endereco_paciente = "Rua A, 10"
        state.emergencia_paciente = "(11) 99999-8888"
        state.erro_paciente = ""
        state.sucesso_paciente = ""
        state.pacientes = []

        client = Mock()
        client.listar_pacientes.return_value = [
            {"id": "7", "cpf": "52998224725"}
        ]
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_paciente()

        client.atualizar_paciente.assert_called_once_with(
            "",
            7,
            {
                "nome": "Ana Ribeiro",
                "cpf": "52998224725",
                "data_nascimento": "2008-02-09",
                "telefone": "11988887777",
                "endereco": "Rua A, 10",
                "contato_emergencia": "11999998888",
            },
        )
        client.criar_paciente.assert_not_called()
        self.assertIn("atualizado", state.sucesso_paciente)
        self.assertEqual(state.id_paciente_edicao, "")

    def test_saving_rejects_cpf_already_used_by_other_patient(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_paciente_edicao = "7"
        state.nome_paciente = "Ana Ribeiro"
        state.cpf_paciente = "529.982.247-25"
        state.nascimento_paciente = "09/02/2008"
        state.telefone_paciente = "(11) 98888-7777"
        state.endereco_paciente = "Rua A, 10"
        state.emergencia_paciente = "(11) 99999-8888"
        state.erro_paciente = ""
        state.sucesso_paciente = ""

        client = Mock()
        client.listar_pacientes.return_value = [
            {"id": "8", "cpf": "52998224725"}
        ]
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_paciente()

        self.assertIn("CPF", state.erro_paciente)
        client.atualizar_paciente.assert_not_called()

    def test_deleting_patient_without_permission_is_blocked(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.erro_paciente = ""
        state.sucesso_paciente = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.excluir_paciente("7")

        self.assertIn("permissão", state.erro_paciente)
        client_class.assert_not_called()

    def test_deleting_patient_succeeds(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_paciente = ""
        state.sucesso_paciente = ""
        state.paciente_selecionado = {"id": "7"}
        state.id_paciente_edicao = ""
        state.pacientes = []

        client = Mock()
        client.listar_pacientes.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_paciente("7")

        client.excluir_paciente.assert_called_once_with("", 7)
        self.assertIn("excluído", state.sucesso_paciente)
        self.assertEqual(state.paciente_selecionado, {})

    def test_deleting_patient_with_dependencies_surfaces_backend_message(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_paciente = ""
        state.sucesso_paciente = ""

        client = Mock()
        client.excluir_paciente.side_effect = XanoValidationError(
            "Não é possível excluir: paciente possui atendimentos vinculados."
        )
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_paciente("7")

        self.assertIn("vinculados", state.erro_paciente)


if __name__ == "__main__":
    unittest.main()
