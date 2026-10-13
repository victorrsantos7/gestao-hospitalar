import unittest

from gestao_hospitalar.authorization import (
    RECURSO_ATENDIMENTOS,
    RECURSO_CADASTRO_PACIENTES,
    RECURSO_CONVENIOS,
    RECURSO_DIAGNOSTICOS,
    RECURSO_INTERNACOES,
    RECURSO_PACIENTES,
    RECURSO_USUARIOS,
    pode_acessar,
    papel_conhecido,
    tem_permissao,
)
from gestao_hospitalar.auth_state import rota_pos_login, valores_sessao_encerrada


class AuthorizationTests(unittest.TestCase):
    def test_recepcionista_accesses_operational_registration(self) -> None:
        self.assertTrue(tem_permissao("recepcionista", RECURSO_PACIENTES))
        self.assertTrue(tem_permissao("recepcionista", RECURSO_CADASTRO_PACIENTES))
        self.assertTrue(tem_permissao("recepcionista", RECURSO_ATENDIMENTOS))
        self.assertFalse(tem_permissao("recepcionista", RECURSO_DIAGNOSTICOS))

    def test_medico_accesses_diagnosis_but_not_administration(self) -> None:
        self.assertTrue(tem_permissao("medico", RECURSO_DIAGNOSTICOS))
        self.assertFalse(tem_permissao("medico", RECURSO_CADASTRO_PACIENTES))
        self.assertFalse(tem_permissao("medico", RECURSO_USUARIOS))

    def test_medicos_are_available_to_receptionist_and_admin_only(self) -> None:
        self.assertTrue(tem_permissao("recepcionista", "medicos"))
        self.assertTrue(tem_permissao("admin", "medicos"))
        self.assertFalse(tem_permissao("medico", "medicos"))
        self.assertFalse(tem_permissao("enfermagem_gestao", "medicos"))

    def test_convenios_are_available_to_receptionist_and_admin_only(self) -> None:
        self.assertTrue(tem_permissao("recepcionista", RECURSO_CONVENIOS))
        self.assertTrue(tem_permissao("admin", RECURSO_CONVENIOS))
        self.assertFalse(tem_permissao("medico", RECURSO_CONVENIOS))
        self.assertFalse(tem_permissao("enfermagem_gestao", RECURSO_CONVENIOS))

    def test_enfermagem_gestao_accesses_admission_flow(self) -> None:
        self.assertTrue(tem_permissao("enfermagem_gestao", RECURSO_INTERNACOES))
        self.assertFalse(tem_permissao("enfermagem_gestao", RECURSO_PACIENTES))

    def test_admin_accesses_every_resource(self) -> None:
        self.assertTrue(tem_permissao("admin", RECURSO_USUARIOS))
        self.assertTrue(tem_permissao("admin", "recurso_futuro"))

    def test_unknown_role_and_unauthenticated_session_are_denied(self) -> None:
        self.assertFalse(papel_conhecido("papel_inexistente"))
        self.assertFalse(tem_permissao("papel_inexistente", RECURSO_PACIENTES))
        self.assertFalse(pode_acessar(False, "admin", RECURSO_USUARIOS))
        self.assertFalse(pode_acessar(True, "papel_inexistente", RECURSO_PACIENTES))

    def test_dashboard_navigation_is_available_to_all_known_roles(self) -> None:
        for papel in ("recepcionista", "medico", "enfermagem_gestao", "admin"):
            self.assertTrue(pode_acessar(True, papel, "dashboard"))

    def test_post_login_route_rejects_unknown_role(self) -> None:
        self.assertEqual(rota_pos_login("admin"), "/dashboard")
        self.assertIsNone(rota_pos_login("papel_inexistente"))

    def test_logout_values_clear_session_and_return_to_login(self) -> None:
        self.assertEqual(valores_sessao_encerrada(), (0, "", "", "", ""))


if __name__ == "__main__":
    unittest.main()
