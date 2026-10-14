import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import AuthState


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
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        state.criar_atendimento()

        self.assertIn("permissão", state.erro_atendimento)

    def test_invalid_type_is_rejected_before_remote_call(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.paciente_id_atendimento = "1 - Ana"
        state.medico_id_atendimento = "2 - Dra. Beatriz"
        state.convenio_id_atendimento = ""
        state.data_atendimento = "12/10/2026"
        state.motivo_atendimento = "Dor abdominal"
        state.tipo_atendimento = "internacao"
        state.erro_atendimento = ""
        state.sucesso_atendimento = ""

        with patch("gestao_hospitalar.auth_state.XanoClient") as client_class:
            state.criar_atendimento()

        self.assertIn("tipo", state.erro_atendimento)
        client_class.assert_not_called()

    def test_authorized_user_creates_attendance(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
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
            state.criar_atendimento()

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
        self.assertIn("#41", state.sucesso_atendimento)


if __name__ == "__main__":
    unittest.main()
