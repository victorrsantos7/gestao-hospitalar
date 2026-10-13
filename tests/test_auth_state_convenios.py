import unittest

from gestao_hospitalar.auth_state import AuthState


class AuthStateConveniosTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_unauthorized_role_cannot_save_convenio(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        state.nome_convenio = "Saude Integral"
        state.tipo_convenio = "plano"
        state.cobertura_convenio = "Consultas"

        state.salvar_convenio()

        self.assertIn("permissao", state.erro_convenio)

    def test_invalid_type_is_rejected_before_remote_call(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.nome_convenio = "Saude Integral"
        state.tipo_convenio = "empresarial"
        state.cobertura_convenio = "Consultas"

        state.salvar_convenio()

        self.assertIn("tipo", state.erro_convenio)


if __name__ == "__main__":
    unittest.main()