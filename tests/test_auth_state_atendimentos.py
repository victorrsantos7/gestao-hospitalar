import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoValidationError


class AuthStateAtendimentosTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_medico_cannot_create_atendimento(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.id_atendimento_edicao = ""
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        state.salvar_atendimento()

        self.assertIn("permissão", state.erro_atendimento)

    def test_invalid_type_is_rejected_before_remote_call(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_atendimento_edicao = ""
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = ""
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "internacao"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.salvar_atendimento()

        self.assertIn("tipo", state.erro_atendimento)
        client_class.assert_not_called()

    def test_authorized_user_creates_attendance(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_atendimento_edicao = ""
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = "3 - Integral"
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "consulta"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        client = Mock()
        client.criar_atendimento.return_value = 41
        client.listar_atendimentos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_atendimento()

        client.criar_atendimento.assert_called_once_with(
            "",
            {
                "paciente_id": 1,
                "medico_id": 2,
                "convenio_id": 3,
                "data_atendimento": "2026-10-12",
                "motivo": "Dor abdominal",
                "tipo": "consulta",
            },
        )
        client.atualizar_atendimento.assert_not_called()
        self.assertIn("#41", state.sucesso_atendimento)
        self.assertEqual(state.id_atendimento_edicao, "")

    def test_editing_attendance_fills_form_from_list(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.atendimentos = [
            {
                "id": "41",
                "paciente_id": "1",
                "paciente_nome": "Ana",
                "medico_id": "2",
                "medico_nome": "Dra. Beatriz",
                "convenio_id": "3",
                "convenio_nome": "Integral",
                "data_atendimento": "2026-10-12",
                "motivo": "Dor abdominal",
                "tipo": "consulta",
            }
        ]
        state.erro_atendimento = ""

        state.editar_atendimento("41")

        self.assertEqual(state.id_atendimento_edicao, "41")
        self.assertEqual(state.paciente_id_atendimento, "1 - Ana")
        self.assertEqual(state.medico_id_atendimento, "2 - Dra. Beatriz")
        self.assertEqual(state.convenio_id_atendimento, "3 - Integral")
        self.assertEqual(state.data_atendimento, "12/10/2026")
        self.assertEqual(state.motivo_atendimento, "Dor abdominal")
        self.assertEqual(state.tipo_atendimento, "consulta")
        self.assertTrue(state.editando_atendimento)

    def test_editing_unknown_attendance_reports_error(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.atendimentos = []
        state.erro_atendimento = ""
        state.id_atendimento_edicao = ""

        state.editar_atendimento("999")

        self.assertIn("editar", state.erro_atendimento)
        self.assertFalse(state.editando_atendimento)

    def test_cancelling_edit_clears_form(self) -> None:
        state = self._state()
        state.id_atendimento_edicao = "41"
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = "3 - Integral"
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "consulta"

        state.cancelar_edicao_atendimento()

        self.assertEqual(state.id_atendimento_edicao, "")
        self.assertEqual(state.paciente_id_atendimento, "")
        self.assertEqual(state.medico_id_atendimento, "")
        self.assertEqual(state.convenio_id_atendimento, "")
        self.assertEqual(state.data_atendimento, "")
        self.assertEqual(state.motivo_atendimento, "")
        self.assertEqual(state.tipo_atendimento, "")
        self.assertFalse(state.editando_atendimento)

    def test_saving_with_edicao_id_updates_attendance(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_atendimento_edicao = "41"
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = "3 - Integral"
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "consulta"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        client = Mock()
        client.listar_atendimentos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_atendimento()

        client.atualizar_atendimento.assert_called_once_with(
            "",
            41,
            {
                "paciente_id": 1,
                "medico_id": 2,
                "convenio_id": 3,
                "data_atendimento": "2026-10-12",
                "motivo": "Dor abdominal",
                "tipo": "consulta",
            },
        )
        client.criar_atendimento.assert_not_called()
        self.assertIn("atualizado", state.sucesso_atendimento)
        self.assertEqual(state.id_atendimento_edicao, "")

    def test_saving_with_invalid_references_reports_error(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.id_atendimento_edicao = "41"
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = "3 - Integral"
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "consulta"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        client = Mock()
        client.atualizar_atendimento.side_effect = XanoValidationError(
            "Referências inválidas."
        )
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.salvar_atendimento()

        self.assertIn("referências", state.erro_atendimento)

    def test_deleting_attendance_without_permission_is_blocked(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.excluir_atendimento("41")

        self.assertIn("permissão", state.erro_atendimento)
        client_class.assert_not_called()

    def test_deleting_attendance_succeeds(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""
        state.atendimento_selecionado = {}
        state.id_atendimento_edicao = ""
        state.atendimentos = []

        client = Mock()
        client.listar_atendimentos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_atendimento("41")

        client.excluir_atendimento.assert_called_once_with("", 41)
        self.assertIn("excluído", state.sucesso_atendimento)

    def test_deleting_attendance_with_dependencies_surfaces_backend_message(
        self,
    ) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        client = Mock()
        client.excluir_atendimento.side_effect = XanoValidationError(
            "Não é possível excluir: atendimento possui internação vinculada."
        )
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.excluir_atendimento("41")

        self.assertIn("vinculada", state.erro_atendimento)


if __name__ == "__main__":
    unittest.main()
