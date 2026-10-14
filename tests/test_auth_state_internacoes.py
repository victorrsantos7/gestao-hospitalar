import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.xano_client import XanoValidationError


class AuthStateInternacoesTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_medico_cannot_create_bed(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.numero_leito = "101"
        state.erro_leito = ""
        state.sucesso_leito = ""

        state.criar_leito()

        self.assertIn("permissão", state.erro_leito)

    def test_medico_cannot_create_admission(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.atendimento_id_internacao = "41"
        state.leito_id_internacao = "1 - Leito 101"
        state.data_entrada_internacao = "2026-10-13"
        state.erro_internacao = ""
        state.sucesso_internacao = ""

        state.criar_internacao()

        self.assertIn("permissão", state.erro_internacao)

    def test_nursing_user_creates_bed_as_free(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.numero_leito = "101"
        state.erro_leito = ""
        state.sucesso_leito = ""

        client = Mock()
        client.criar_leito.return_value = 61
        client.listar_leitos.return_value = []
        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_leito()

        client.criar_leito.assert_called_once_with("", 101)
        self.assertIn("#61", state.sucesso_leito)

    def test_duplicate_bed_is_reported(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "admin"
        state.numero_leito = "101"
        state.erro_leito = ""
        state.sucesso_leito = ""
        client = Mock()
        client.criar_leito.side_effect = XanoValidationError(
            "Numero de leito ja cadastrado."
        )

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_leito()

        self.assertIn("ja cadastrado", state.erro_leito)

    def test_nursing_user_creates_admission(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.atendimento_id_internacao = "41"
        state.leito_id_internacao = "61 - Leito 101"
        state.data_entrada_internacao = "2026-10-13"
        state.erro_internacao = ""
        state.sucesso_internacao = ""
        client = Mock()
        client.criar_internacao.return_value = 71
        client.listar_leitos.return_value = []
        client.listar_internacoes.return_value = []
        client.listar_atendimentos_internaveis.return_value = []

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.criar_internacao()

        client.criar_internacao.assert_called_once_with(
            "",
            {
                "atendimento_id": 41,
                "leito_id": 61,
                "data_entrada": "2026-10-13",
            },
        )
        self.assertIn("#71", state.sucesso_internacao)

    def test_internable_attendance_options_include_context(self) -> None:
        state = self._state()
        state.atendimentos_internaveis = [
            {
                "id": "2",
                "paciente_nome": "Ana Ribeiro",
                "data_atendimento": "2026-10-13",
                "tipo": "emergencia",
                "motivo": "Febre",
            }
        ]

        self.assertEqual(
            state.opcoes_atendimentos_internaveis,
            ["2 - Ana Ribeiro - 2026-10-13 - emergencia - Febre"],
        )

    def test_admission_rejects_invalid_discharge_before_remote_call(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "admin"
        state.internacao_id_alta = "71"
        state.data_saida_internacao = "2026-10-12"
        state.internacoes = [
            {
                "id": "71",
                "data_entrada": "2026-10-13",
                "status": "internado",
            }
        ]
        state.erro_internacao = ""
        state.sucesso_internacao = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.registrar_alta()

        self.assertIn("data de saída", state.erro_internacao)
        client_class.assert_not_called()

    def test_valid_discharge_releases_bed_in_state(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.internacao_id_alta = "71"
        state.data_saida_internacao = "2026-10-14"
        state.internacoes = [
            {
                "id": "71",
                "data_entrada": "2026-10-13",
                "status": "internado",
            }
        ]
        state.erro_internacao = ""
        state.sucesso_internacao = ""
        client = Mock()
        client.listar_leitos.return_value = []
        client.listar_internacoes.return_value = []

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state.registrar_alta()

        client.registrar_alta.assert_called_once_with("", 71, "2026-10-14")
        self.assertIn("liberado", state.sucesso_internacao)

    def test_admission_display_uses_bed_number_instead_of_internal_id(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.leitos = [{"id": "1", "numero": "101", "status": "ocupado"}]
        state.internacoes = []
        state.erro_internacao = ""
        client = Mock()
        client.listar_internacoes.return_value = [
            {
                "id": 71,
                "atendimento_id": 41,
                "paciente_id": 1,
                "leito_id": 1,
                "data_entrada": "2026-10-13",
                "data_saida": None,
                "status": "internado",
            }
        ]

        with patch(
            "gestao_hospitalar.auth_state.XanoClient",
            return_value=client,
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env",
            return_value=Mock(),
        ):
            state._carregar_internacoes()

        self.assertEqual(state.internacoes[0]["leito_numero"], "101")


if __name__ == "__main__":
    unittest.main()
