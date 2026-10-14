import unittest

from gestao_hospitalar.auth_state import AuthState


class AuthStateRelatoriosTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        return state

    def test_enfermagem_gestao_pode_ver_relatorios(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        self.assertTrue(state.pode_ver_relatorios)

    def test_admin_pode_ver_relatorios(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "admin"
        self.assertTrue(state.pode_ver_relatorios)

    def test_recepcionista_nao_pode_ver_relatorios(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "recepcionista"
        self.assertFalse(state.pode_ver_relatorios)

    def test_medico_nao_pode_ver_relatorios(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "medico"
        self.assertFalse(state.pode_ver_relatorios)

    def test_resumo_leitos_reflete_leitos_carregados(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.leitos = [
            {"id": "1", "numero": "101", "status": "livre"},
            {"id": "2", "numero": "102", "status": "ocupado"},
        ]
        self.assertEqual(
            state.resumo_leitos, {"livres": 1, "ocupados": 1, "total": 2}
        )

    def test_lista_internacoes_ativas_reflete_internacoes_carregadas(self) -> None:
        state = self._state()
        state.usuario_id = 10
        state.papel = "enfermagem_gestao"
        state.internacoes = [
            {
                "id": "1",
                "status": "internado",
                "leito_numero": "101",
                "data_entrada": "2026-10-10",
            },
            {
                "id": "2",
                "status": "alta",
                "leito_numero": "102",
                "data_entrada": "2026-10-01",
            },
        ]
        resultado = state.lista_internacoes_ativas
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["leito_numero"], "101")


if __name__ == "__main__":
    unittest.main()
