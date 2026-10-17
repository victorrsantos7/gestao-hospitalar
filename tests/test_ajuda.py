import unittest
from pathlib import Path
try:  # caminho interno do Reflex: pode mudar em outra versão
    from reflex.components.lucide.icon import LUCIDE_ICON_LIST
except ImportError:
    LUCIDE_ICON_LIST = None

from gestao_hospitalar.ajuda import (
    TOPICO_INICIAL,
    TOPICOS,
    topico_por_id,
)
from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.layout import NAVEGACAO
from gestao_hospitalar.validacao_convenios import TIPOS_CONVENIO


class ConteudoDaAjudaTests(unittest.TestCase):
    def test_ids_sao_unicos_e_o_inicial_existe(self) -> None:
        ids = [topico.id for topico in TOPICOS]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn(TOPICO_INICIAL, ids)

    def test_todo_topico_tem_texto_e_passos(self) -> None:
        for topico in TOPICOS:
            with self.subTest(topico=topico.id):
                self.assertTrue(topico.titulo.strip())
                self.assertTrue(topico.resumo.strip())
                self.assertTrue(topico.passos)
                self.assertTrue(all(passo.strip() for passo in topico.passos))

    @unittest.skipIf(LUCIDE_ICON_LIST is None, "lista de ícones do Reflex indisponível")
    def test_icones_existem_no_lucide(self) -> None:
        for topico in TOPICOS:
            with self.subTest(topico=topico.id):
                self.assertTrue(topico.icone in LUCIDE_ICON_LIST, topico.icone)

    def test_permissoes_apontam_para_variaveis_do_estado(self) -> None:
        for topico in TOPICOS:
            if topico.permissao is not None:
                with self.subTest(topico=topico.id):
                    self.assertTrue(hasattr(AuthState, topico.permissao))

    def test_cada_modulo_do_menu_tem_seu_topico_com_a_mesma_permissao(self) -> None:
        for rotulo, _rota, _icone, permissao, _descricao in NAVEGACAO:
            if permissao is None:
                continue
            with self.subTest(modulo=rotulo):
                permissoes = {topico.permissao for topico in TOPICOS}
                self.assertIn(permissao, permissoes)

    def test_tipos_de_convenio_citados_batem_com_a_validacao(self) -> None:
        texto = " ".join(topico_por_id("convenios").passos)

        for tipo in TIPOS_CONVENIO:
            self.assertIn(tipo.lower(), texto.lower())

    def test_topico_desconhecido_nao_existe(self) -> None:
        self.assertIsNone(topico_por_id("nao-existe"))


PACOTE = Path(__file__).resolve().parent.parent / "gestao_hospitalar"

# Rótulos de botão citados na ajuda: cada um precisa existir no texto do tópico
# e no código da tela correspondente, para o texto não envelhecer em silêncio.
ROTULOS_POR_TOPICO = {
    "primeiros-passos": (("Entrar", "login.py"), ("Atualizar", "ui/componentes.py"), ("Limpar", "ui/componentes.py"), ("Sair", "ui/layout.py")),
    "painel": (("Atualizar", "ui/componentes.py"),),
    "pacientes": (("Cadastrar paciente", "pacientes.py"), ("Ver detalhes", "pacientes.py")),
    "medicos": (("Cadastrar médico", "medicos.py"), ("Editar", "medicos.py"), ("Atualizar médico", "medicos.py"), ("Cancelar edição", "medicos.py"), ("Excluir", "medicos.py")),
    "convenios": (("Cadastrar convênio", "convenios.py"), ("Editar", "convenios.py"), ("Atualizar convênio", "convenios.py"), ("Excluir", "convenios.py")),
    "atendimentos": (("Cadastrar atendimento", "atendimentos.py"), ("Ver detalhes", "atendimentos.py"), ("Cadastrar diagnóstico", "atendimentos.py")),
    "internacoes": (("Cadastrar leito", "internacoes.py"), ("Registrar alta", "internacoes.py"), ("Nova transferência", "internacoes.py")),
    "historico": (("Consultar histórico", "historico.py"),),
    "relatorios": (("Atualizar", "ui/componentes.py"),),
    "problemas": (("Tentar novamente", "ui/componentes.py"), ("Atualizar", "ui/componentes.py")),
}


class SincroniaComAInterfaceTests(unittest.TestCase):
    def test_rotulos_citados_existem_na_ajuda_e_na_interface(self) -> None:
        for topico_id, rotulos in ROTULOS_POR_TOPICO.items():
            topico = topico_por_id(topico_id)
            texto = " ".join(topico.passos + topico.dicas)
            for rotulo, arquivo in rotulos:
                with self.subTest(topico=topico_id, rotulo=rotulo):
                    self.assertIn(rotulo, texto)
                    codigo = (PACOTE / arquivo).read_text(encoding="utf-8")
                    self.assertIn(f'"{rotulo}"', codigo)

    def test_todo_topico_de_modulo_tem_rotulos_conferidos(self) -> None:
        sem_cobertura = [
            topico.id
            for topico in TOPICOS
            if topico.id not in ROTULOS_POR_TOPICO and topico.id != "perfis"
        ]

        self.assertEqual(sem_cobertura, [])


class _EstadoAjuda:
    def __init__(self) -> None:
        self.ajuda_aberta = False
        self.ajuda_topico = "painel"


class EstadoDaAjudaTests(unittest.TestCase):
    def test_abrir_volta_ao_topico_inicial(self) -> None:
        estado = _EstadoAjuda()

        AuthState.abrir_ajuda.fn(estado)

        self.assertTrue(estado.ajuda_aberta)
        self.assertEqual(estado.ajuda_topico, TOPICO_INICIAL)

    def test_fechar_pelo_dialogo(self) -> None:
        estado = _EstadoAjuda()
        estado.ajuda_aberta = True

        AuthState.set_ajuda_aberta.fn(estado, False)

        self.assertFalse(estado.ajuda_aberta)

    def test_selecionar_troca_o_topico_e_ignora_id_invalido(self) -> None:
        estado = _EstadoAjuda()

        AuthState.selecionar_ajuda.fn(estado, "pacientes")
        self.assertEqual(estado.ajuda_topico, "pacientes")

        AuthState.selecionar_ajuda.fn(estado, "<script>")
        self.assertEqual(estado.ajuda_topico, "pacientes")


if __name__ == "__main__":
    unittest.main()
