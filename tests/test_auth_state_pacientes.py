import unittest
from unittest.mock import patch

from gestao_hospitalar.auth_state import AuthState


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


if __name__ == "__main__":
    unittest.main()
