import pathlib
import re
import unittest

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.layout import NAVEGACAO


class NavegacaoTests(unittest.TestCase):
    def test_permissoes_apontam_para_vars_existentes(self) -> None:
        for rotulo, _, _, permissao, _ in NAVEGACAO:
            if permissao is None:
                continue
            with self.subTest(rotulo=rotulo):
                self.assertIn(permissao, AuthState.vars)

    def test_rotas_unicas_e_registradas_no_app(self) -> None:
        fonte = pathlib.Path("gestao_hospitalar/gestao_hospitalar.py").read_text(
            encoding="utf-8"
        )
        registradas = set(re.findall(r'route="([^"]+)"', fonte))
        rotas = [rota for _, rota, _, _, _ in NAVEGACAO]
        self.assertEqual(len(rotas), len(set(rotas)))
        for rota in rotas:
            with self.subTest(rota=rota):
                self.assertIn(rota, registradas)

    def test_painel_e_o_unico_item_sem_permissao(self) -> None:
        sem_permissao = [r for r, _, _, permissao, _ in NAVEGACAO if permissao is None]
        self.assertEqual(sem_permissao, ["Painel"])


if __name__ == "__main__":
    unittest.main()