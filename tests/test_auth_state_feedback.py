import unittest
from unittest.mock import Mock, patch

from gestao_hospitalar.auth_state import (
    CAMPOS_FEEDBACK,
    CAMPOS_LIMPEZA,
    VALIDADE_PAINEL_SEGUNDOS,
    AuthState,
    paginas_do_total,
    texto_paginacao,
)
from gestao_hospitalar.xano_client import XanoError


class AuthStateFeedbackTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = "admin"
        state.acao_em_andamento = ""
        state.erro_paciente = ""
        state.sucesso_paciente = ""
        state.erro = ""
        return state

    def test_iniciar_acao_marca_e_limpa_mensagens_do_dominio(self) -> None:
        state = self._state()
        state.erro_paciente = "antigo"
        state.sucesso_paciente = "antigo"

        state.iniciar_acao("criar_paciente", "paciente")

        self.assertEqual(state.acao_em_andamento, "criar_paciente")
        self.assertEqual(state.erro_paciente, "")
        self.assertEqual(state.sucesso_paciente, "")

    def test_iniciar_acao_ignora_dominio_desconhecido(self) -> None:
        state = self._state()
        state.erro_paciente = "mantido"

        state.iniciar_acao("x", "dominio_inexistente")

        self.assertEqual(state.erro_paciente, "mantido")

    def test_carregando_pagina_reflete_acao_de_carga(self) -> None:
        state = self._state()
        self.assertFalse(state.carregando_pagina)
        state.iniciar_acao("carregando")
        self.assertTrue(state.carregando_pagina)
        state.encerrar_acao()
        self.assertFalse(state.carregando_pagina)

    def test_encerrar_acao_libera_botoes(self) -> None:
        state = self._state()
        state.acao_em_andamento = "criar_paciente"

        state.encerrar_acao()

        self.assertEqual(state.acao_em_andamento, "")

    def test_notificar_erro_mantem_mensagem_inline(self) -> None:
        state = self._state()
        state.erro_paciente = "Informe um CPF válido."

        resultado = state.notificar_resultado("paciente")

        self.assertIsNotNone(resultado)
        self.assertEqual(state.erro_paciente, "Informe um CPF válido.")

    def test_notificar_sucesso_limpa_mensagem(self) -> None:
        state = self._state()
        state.sucesso_paciente = "Paciente cadastrado (#1)."

        resultado = state.notificar_resultado("paciente")

        self.assertIsNotNone(resultado)
        self.assertEqual(state.sucesso_paciente, "")

    def test_notificar_sem_mensagem_nao_dispara_toast(self) -> None:
        state = self._state()

        self.assertIsNone(state.notificar_resultado("paciente"))
        self.assertIsNone(state.notificar_resultado("dominio_inexistente"))

    def test_dominios_apontam_para_campos_existentes(self) -> None:
        for dominio, (campo_erro, campo_sucesso) in CAMPOS_FEEDBACK.items():
            with self.subTest(dominio=dominio):
                self.assertIn(campo_erro, AuthState.vars)
                if campo_sucesso is not None:
                    self.assertIn(campo_sucesso, AuthState.vars)

    def test_login_tecla_ignora_outras_teclas(self) -> None:
        state = self._state()

        self.assertIsNone(state.login_tecla("a"))

    def test_login_tecla_enter_encadeia_login(self) -> None:
        state = self._state()

        eventos = state.login_tecla("Enter")

        self.assertEqual(len(eventos), 4)

    def test_login_tecla_enter_ignorado_durante_acao(self) -> None:
        state = self._state()
        state.acao_em_andamento = "login"

        self.assertIsNone(state.login_tecla("Enter"))


class AuthStateResumoTests(unittest.TestCase):
    @staticmethod
    def _state(papel: str) -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = papel
        state.painel_pacientes = -1
        state.painel_medicos = -1
        state.painel_atendimentos = -1
        state.painel_leitos_livres = -1
        state.painel_leitos_ocupados = -1
        state.painel_internacoes_ativas = -1
        state.painel_atualizado_em = ""
        state.erro_painel = ""
        object.__setattr__(state, "_backend_vars", {})
        state._painel_ts = 0.0
        return state

    @staticmethod
    def _cliente() -> Mock:
        cliente = Mock()
        cliente.contar_pacientes.return_value = 140
        cliente.contar_medicos.return_value = 12
        cliente.contar_atendimentos.return_value = 300
        cliente.listar_leitos.return_value = [
            {"status": "livre"},
            {"status": "ocupado"},
            {"status": "livre"},
        ]
        cliente.listar_internacoes.return_value = [
            {"status": "internado"},
            {"status": "alta"},
        ]
        return cliente

    def _executar(self, state: AuthState, cliente: Mock, evento: str = "carregar_resumo") -> None:
        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            getattr(state, evento)()

    def test_admin_le_todos_os_indicadores_sem_baixar_listas_de_pacientes(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()

        self._executar(state, cliente)

        self.assertEqual(state.painel_pacientes, 140)
        self.assertEqual(state.painel_medicos, 12)
        self.assertEqual(state.painel_atendimentos, 300)
        self.assertEqual(state.painel_leitos_livres, 2)
        self.assertEqual(state.painel_leitos_ocupados, 1)
        self.assertEqual(state.painel_internacoes_ativas, 1)
        self.assertNotEqual(state.painel_atualizado_em, "")
        cliente.listar_pacientes.assert_not_called()
        cliente.listar_medicos.assert_not_called()
        cliente.listar_atendimentos.assert_not_called()

    def test_recepcionista_nao_consulta_leitos_nem_internacoes(self) -> None:
        state = self._state("recepcionista")
        cliente = self._cliente()

        self._executar(state, cliente)

        cliente.contar_pacientes.assert_called_once()
        cliente.listar_leitos.assert_not_called()
        cliente.listar_internacoes.assert_not_called()
        self.assertEqual(state.painel_leitos_livres, -1)
        self.assertEqual(state.painel_internacoes_ativas, -1)

    def test_enfermagem_consulta_somente_leitos_e_internacoes(self) -> None:
        state = self._state("enfermagem_gestao")
        cliente = self._cliente()

        self._executar(state, cliente)

        cliente.contar_pacientes.assert_not_called()
        cliente.contar_medicos.assert_not_called()
        cliente.contar_atendimentos.assert_not_called()
        cliente.listar_leitos.assert_called_once()
        cliente.listar_internacoes.assert_called_once()

    def test_papel_desconhecido_nao_consulta_nada(self) -> None:
        state = self._state("invasor")
        cliente = self._cliente()

        self._executar(state, cliente)

        cliente.contar_pacientes.assert_not_called()
        cliente.listar_leitos.assert_not_called()
        self.assertEqual(state.painel_atualizado_em, "")

    def test_leitura_recente_e_reaproveitada(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()
        self._executar(state, cliente)

        self._executar(state, cliente)

        cliente.contar_pacientes.assert_called_once()

    def test_atualizar_forca_nova_leitura(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()
        self._executar(state, cliente)

        self._executar(state, cliente, "atualizar_resumo")

        self.assertEqual(cliente.contar_pacientes.call_count, 2)

    def test_leitura_expirada_e_refeita(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()
        self._executar(state, cliente)
        state._painel_ts -= VALIDADE_PAINEL_SEGUNDOS + 1

        self._executar(state, cliente)

        self.assertEqual(cliente.contar_pacientes.call_count, 2)

    def test_apos_limpar_o_painel_e_lido_novamente(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()
        self._executar(state, cliente)
        state.limpar_tela("painel")

        self._executar(state, cliente)

        self.assertEqual(cliente.contar_pacientes.call_count, 2)
        self.assertEqual(state.painel_pacientes, 140)

    def test_falha_parcial_mantem_demais_indicadores(self) -> None:
        state = self._state("admin")
        cliente = self._cliente()
        cliente.contar_medicos.side_effect = XanoError("falha")

        self._executar(state, cliente)

        self.assertEqual(state.painel_medicos, -1)
        self.assertEqual(state.painel_pacientes, 140)
        self.assertNotEqual(state.painel_atualizado_em, "")
        self.assertIn("indicadores", state.erro_painel)
        self.assertIsNotNone(state.notificar_atualizacao("painel"))

    def test_falha_total_nao_marca_leitura_como_recente(self) -> None:
        state = self._state("admin")
        cliente = Mock()
        for metodo in (
            "contar_pacientes",
            "contar_medicos",
            "contar_atendimentos",
            "listar_leitos",
            "listar_internacoes",
        ):
            getattr(cliente, metodo).side_effect = XanoError("falha")

        self._executar(state, cliente)

        self.assertEqual(state.painel_atualizado_em, "")
        self.assertNotEqual(state.erro_painel, "")

    def test_nova_leitura_com_sucesso_limpa_o_erro_anterior(self) -> None:
        state = self._state("admin")
        state.erro_painel = "antigo"
        cliente = self._cliente()

        self._executar(state, cliente, "atualizar_resumo")

        self.assertEqual(state.erro_painel, "")

    def test_limpar_painel_zera_erro_e_totais(self) -> None:
        state = self._state("admin")
        state.erro_painel = "x"
        state.painel_pacientes = 5

        state.limpar_tela("painel")

        self.assertEqual(state.erro_painel, "")
        self.assertEqual(state.painel_pacientes, -1)


class AuthStateLimpezaTests(unittest.TestCase):
    @staticmethod
    def _state() -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = "admin"
        state.pacientes = [{"id": "1", "nome": "Ana"}]
        state.paciente_selecionado = {"id": "1"}
        state.nome_paciente = "Ana"
        state.cpf_paciente = "111"
        state.nascimento_paciente = "2000-01-01"
        state.telefone_paciente = "1"
        state.endereco_paciente = "Rua"
        state.emergencia_paciente = "2"
        state.erro_paciente = "x"
        state.sucesso_paciente = "y"
        state.termo_busca = "ana"
        state.medicos = [{"id": "9"}]
        state.paciente_id_historico = "1 - Ana"
        state.historico_eventos = [{"tipo": "atendimento"}]
        state.pacientes_historico = [{"id": "1", "nome": "Ana"}]
        state.erro_historico = ""
        return state

    def test_limpar_pacientes_zera_leitura_selecao_busca_e_formulario(self) -> None:
        state = self._state()

        resultado = state.limpar_tela("pacientes")

        self.assertIsNotNone(resultado)
        self.assertEqual(state.pacientes, [])
        self.assertEqual(state.paciente_selecionado, {})
        self.assertEqual(state.nome_paciente, "")
        self.assertEqual(state.erro_paciente, "")
        self.assertEqual(state.termo_busca, "")

    def test_limpar_tela_nao_toca_em_outras_telas(self) -> None:
        state = self._state()

        state.limpar_tela("pacientes")

        self.assertEqual(state.medicos, [{"id": "9"}])

    def test_limpar_tela_desconhecida_nao_altera_nada(self) -> None:
        state = self._state()

        self.assertIsNone(state.limpar_tela("usuario_id"))
        self.assertEqual(state.usuario_id, 10)
        self.assertEqual(state.pacientes, [{"id": "1", "nome": "Ana"}])

    def test_limpar_historico_mantem_opcoes_de_pacientes(self) -> None:
        state = self._state()

        state.limpar_tela("historico")

        self.assertEqual(state.historico_eventos, [])
        self.assertEqual(state.paciente_id_historico, "")
        self.assertEqual(state.pacientes_historico, [{"id": "1", "nome": "Ana"}])

    def test_limpeza_nao_compartilha_listas_entre_chamadas(self) -> None:
        state = self._state()
        state.limpar_tela("pacientes")
        state.pacientes.append({"id": "2"})

        state.limpar_tela("pacientes")

        self.assertEqual(state.pacientes, [])
        self.assertEqual(CAMPOS_LIMPEZA["pacientes"]["pacientes"], [])

    def test_campos_de_limpeza_existem_no_estado(self) -> None:
        for tela, campos in CAMPOS_LIMPEZA.items():
            for campo in campos:
                with self.subTest(tela=tela, campo=campo):
                    self.assertIn(campo, AuthState.vars)

    def test_notificar_atualizacao_sucesso_e_erro(self) -> None:
        state = self._state()
        state.erro_paciente = ""
        self.assertIsNotNone(state.notificar_atualizacao("paciente"))
        state.erro_painel = ""
        self.assertIsNotNone(state.notificar_atualizacao("painel"))
        state.erro_paciente = "Não foi possível carregar os pacientes."
        self.assertIsNotNone(state.notificar_atualizacao("paciente"))
        self.assertIsNone(state.notificar_atualizacao("inexistente"))

    def _executar_atualizar_historico(self, state: AuthState) -> Mock:
        cliente = Mock()
        cliente.listar_pacientes_historico.return_value = [{"id": 1, "nome": "Ana"}]
        cliente.consultar_historico.return_value = {"atendimentos": [], "internacoes": []}
        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            state.atualizar_historico()
        return cliente

    def test_atualizar_historico_reconsulta_paciente_selecionado(self) -> None:
        state = self._state()
        state.papel = "enfermagem_gestao"
        state.pacientes_historico = []

        cliente = self._executar_atualizar_historico(state)

        cliente.listar_pacientes_historico.assert_called_once()
        cliente.consultar_historico.assert_called_once_with("", 1)
        self.assertEqual(state.pacientes_historico, [{"id": "1", "nome": "Ana"}])

    def test_atualizar_historico_sem_selecao_nao_consulta(self) -> None:
        state = self._state()
        state.papel = "enfermagem_gestao"
        state.paciente_id_historico = ""

        cliente = self._executar_atualizar_historico(state)

        cliente.listar_pacientes_historico.assert_called_once()
        cliente.consultar_historico.assert_not_called()


class AuthStateAtendimentosReferenciasTests(unittest.TestCase):
    def test_atendimentos_carrega_referencias_completas_para_o_formulario(self) -> None:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = "recepcionista"
        chamados: list[str] = []
        nomes = (
            "_carregar_pacientes_referencia",
            "_carregar_medicos_referencia",
            "_carregar_convenios",
            "_carregar_atendimentos",
        )
        patches = [
            patch.object(AuthState, nome, lambda *a, nome=nome: chamados.append(nome))
            for nome in nomes
        ]
        for aplicado in patches:
            aplicado.start()
        try:
            state.carregar_atendimentos()
        finally:
            for aplicado in patches:
                aplicado.stop()

        self.assertEqual(sorted(chamados), sorted(nomes))


class AuthStatePaginacaoTests(unittest.TestCase):
    @staticmethod
    def _state(papel: str = "recepcionista") -> AuthState:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = papel
        state.pacientes = []
        state.pagina_pacientes = 1
        state.total_paginas_pacientes = 1
        state.total_registros_pacientes = 0
        state.erro_paciente = ""
        state.medicos = []
        state.pagina_medicos = 1
        state.total_paginas_medicos = 1
        state.total_registros_medicos = 0
        state.erro_medico = ""
        state.termo_busca = "ana"
        state.erro_atendimento = ""
        state.pacientes_referencia = []
        state.medicos_referencia = []
        return state

    @staticmethod
    def _cliente(total: int = 140) -> Mock:
        cliente = Mock()

        def pagina(token, page, per_page):
            inicio = (page - 1) * per_page
            fim = min(inicio + per_page, total)
            return (
                [
                    {"id": i + 1, "nome": f"P{i + 1}", "contato_emergencia": "x"}
                    for i in range(inicio, fim)
                ],
                total,
            )

        cliente.listar_pacientes_pagina.side_effect = pagina
        cliente.listar_medicos_pagina.side_effect = pagina
        return cliente

    def _executar(self, state: AuthState, cliente: Mock, evento: str, *args) -> None:
        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            getattr(state, evento)(*args)

    def test_carga_inicial_define_total_e_paginas(self) -> None:
        state = self._state()

        self._executar(state, self._cliente(140), "carregar_pacientes")

        self.assertEqual(len(state.pacientes), 25)
        self.assertEqual(state.total_registros_pacientes, 140)
        self.assertEqual(state.total_paginas_pacientes, 6)
        self.assertEqual(state.texto_paginacao_pacientes, "1–25 de 140")
        self.assertNotIn("contato_emergencia", state.pacientes[0])

    def test_proxima_e_anterior_carregam_a_pagina_certa_e_zeram_a_busca(self) -> None:
        state = self._state()
        cliente = self._cliente(140)
        self._executar(state, cliente, "carregar_pacientes")

        self._executar(state, cliente, "mudar_pagina", "pacientes", 1)

        self.assertEqual(state.pagina_pacientes, 2)
        self.assertEqual(state.pacientes[0]["id"], "26")
        self.assertEqual(state.termo_busca, "")
        self.assertEqual(state.texto_paginacao_pacientes, "26–50 de 140")

        self._executar(state, cliente, "mudar_pagina", "pacientes", -1)
        self.assertEqual(state.pagina_pacientes, 1)

    def test_pagina_fica_dentro_dos_limites(self) -> None:
        state = self._state()
        cliente = self._cliente(60)
        self._executar(state, cliente, "carregar_pacientes")

        self._executar(state, cliente, "mudar_pagina", "pacientes", -1)
        self.assertEqual(state.pagina_pacientes, 1)
        for _ in range(5):
            self._executar(state, cliente, "mudar_pagina", "pacientes", 1)
        self.assertEqual(state.pagina_pacientes, 3)
        self.assertEqual(len(state.pacientes), 10)

    def test_pagina_vazia_volta_para_a_primeira(self) -> None:
        state = self._state()
        state.pagina_pacientes = 4
        cliente = Mock()
        cliente.listar_pacientes_pagina.side_effect = [
            ([], 10),
            ([{"id": 1, "nome": "Ana"}], 10),
        ]

        self._executar(state, cliente, "carregar_pacientes")

        self.assertEqual(state.pagina_pacientes, 1)
        self.assertEqual(len(state.pacientes), 1)

    def test_endpoint_sem_paginacao_vira_uma_pagina_com_todos(self) -> None:
        state = self._state()
        cliente = Mock()
        cliente.listar_medicos_pagina.return_value = (
            [{"id": i, "nome": f"M{i}"} for i in range(40)],
            None,
        )

        self._executar(state, cliente, "carregar_medicos")

        self.assertEqual(state.total_paginas_medicos, 1)
        self.assertEqual(state.total_registros_medicos, 40)
        self.assertEqual(state.texto_paginacao_medicos, "1–40 de 40")

    def test_mudar_pagina_ignora_tela_desconhecida(self) -> None:
        state = self._state()
        cliente = self._cliente()

        self._executar(state, cliente, "mudar_pagina", "usuario_id", 1)

        self.assertEqual(state.usuario_id, 10)
        cliente.listar_pacientes_pagina.assert_not_called()

    def test_papel_sem_permissao_nao_navega(self) -> None:
        state = self._state("enfermagem_gestao")
        cliente = self._cliente()

        self._executar(state, cliente, "mudar_pagina", "pacientes", 1)

        cliente.listar_pacientes_pagina.assert_not_called()
        self.assertIn("permissão", state.erro_paciente)

    def test_medicos_tem_paginacao_propria(self) -> None:
        state = self._state()
        cliente = self._cliente(60)
        self._executar(state, cliente, "carregar_medicos")

        self._executar(state, cliente, "mudar_pagina", "medicos", 1)

        self.assertEqual(state.pagina_medicos, 2)
        self.assertEqual(state.pagina_pacientes, 1)

    def test_referencias_guardam_somente_id_e_nome(self) -> None:
        state = self._state()
        cliente = Mock()
        cliente.listar_todos_pacientes.return_value = [
            {"id": 1, "nome": "Ana", "cpf": "111", "contato_emergencia": "x"}
        ]
        cliente.listar_todos_medicos.return_value = [
            {"id": 2, "nome": "Dr. João", "crm": "1", "telefone": "2"}
        ]

        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            state._carregar_pacientes_referencia()
            state._carregar_medicos_referencia()

        self.assertEqual(state.pacientes_referencia, [{"id": "1", "nome": "Ana"}])
        self.assertEqual(state.medicos_referencia, [{"id": "2", "nome": "Dr. João"}])

    def test_falha_nas_referencias_informa_erro_do_atendimento(self) -> None:
        state = self._state()
        cliente = Mock()
        cliente.listar_todos_pacientes.side_effect = XanoError("falha")

        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            state._carregar_pacientes_referencia()

        self.assertIn("pacientes", state.erro_atendimento)

    def test_limpar_zera_a_paginacao(self) -> None:
        state = self._state()
        state.pagina_pacientes = 3
        state.total_paginas_pacientes = 6
        state.total_registros_pacientes = 140
        state.pacientes = [{"id": "1"}]
        state.paciente_selecionado = {}
        for campo in ("nome", "cpf", "nascimento", "telefone", "endereco", "emergencia"):
            setattr(state, f"{campo}_paciente", "")
        state.sucesso_paciente = ""
        state.pacientes_referencia = [{"id": "1", "nome": "Ana"}]

        state.limpar_tela("pacientes")

        self.assertEqual(state.pagina_pacientes, 1)
        self.assertEqual(state.total_registros_pacientes, 0)
        self.assertEqual(state.pacientes_referencia, [{"id": "1", "nome": "Ana"}])


class TextoPaginacaoTests(unittest.TestCase):
    def test_textos(self) -> None:
        self.assertEqual(texto_paginacao(1, 0, 0), "Nenhum registro")
        self.assertEqual(texto_paginacao(1, 25, 25), "1–25 de 25")
        self.assertEqual(texto_paginacao(6, 140, 15), "126–140 de 140")

    def test_paginas_do_total(self) -> None:
        self.assertEqual(paginas_do_total(None, 40), 1)
        self.assertEqual(paginas_do_total(0, 0), 1)
        self.assertEqual(paginas_do_total(25, 25), 1)
        self.assertEqual(paginas_do_total(26, 25), 2)
        self.assertEqual(paginas_do_total(140, 25), 6)


class AuthStateCrmDuplicadoTests(unittest.TestCase):
    def test_duplicidade_de_crm_consulta_todas_as_paginas(self) -> None:
        state = object.__new__(AuthState)
        state.dirty_vars = set()
        state.usuario_id = 10
        state.papel = "recepcionista"
        state.erro_medico = ""
        state.sucesso_medico = ""
        state.id_medico_edicao = ""
        state.nome_medico = "Ana Souza"
        state.crm_medico = "1234567/SP"
        state.especialidade_medico = "Cardiologia"
        state.telefone_medico = "(11) 98765-4321"
        cliente = Mock()
        cliente.listar_todos_medicos.return_value = [{"crm": "1234567/SP"}]

        with patch(
            "gestao_hospitalar.auth_state.XanoClient", return_value=cliente
        ), patch(
            "gestao_hospitalar.auth_state.XanoConfig.from_env", return_value=Mock()
        ):
            state.criar_medico()

        cliente.listar_todos_medicos.assert_called_once()
        cliente.criar_medico.assert_not_called()
        self.assertIn("CRM", state.erro_medico)

if __name__ == "__main__":
    unittest.main()
