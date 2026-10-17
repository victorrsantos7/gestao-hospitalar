"""Estado de autenticação do Sistema de Gestão Hospitalar."""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Any

import reflex as rx

from gestao_hospitalar.ajuda import TOPICO_INICIAL, topico_por_id
from gestao_hospitalar.authorization import (
    RECURSO_CADASTRO_PACIENTES,
    RECURSO_CONVENIOS,
    RECURSO_DASHBOARD,
    RECURSO_ATENDIMENTOS,
    RECURSO_DIAGNOSTICOS,
    RECURSO_INTERNACOES,
    RECURSO_LEITOS,
    RECURSO_HISTORICO,
    RECURSO_RELATORIOS,
    RECURSO_TRANSFERENCIAS,
    RECURSO_MEDICOS,
    RECURSO_PACIENTES,
    pode_acessar,
    tem_permissao,
)
from gestao_hospitalar.busca import filtrar_registros
from gestao_hospitalar.crm import crm_valido, formatar_crm, normalizar_crm
from gestao_hospitalar.cpf import cpf_valido, normalizar_cpf
from gestao_hospitalar.logging_config import get_logger
from gestao_hospitalar.painel import (
    PERIODOS,
    calcular_alertas,
    emergencias_de_hoje,
    eventos_atendimentos,
    eventos_internacoes,
    grafico,
    mesclar_atividade,
    serie_diaria,
    totais_por_tipo,
)
from gestao_hospitalar.relatorios_calculo import (
    InternacaoAtiva,
    contagem_leitos,
    internacoes_ativas as calcular_internacoes_ativas,
)
from gestao_hospitalar.validacao_convenios import (
    TIPOS_CONVENIO,
    nome_convenio_valido,
    normalizar_nome_convenio,
    tipo_convenio_valido,
)
from gestao_hospitalar.validacao_atendimentos import (
    TIPOS_ATENDIMENTO,
    data_atendimento_valida,
    motivo_atendimento_valido,
    referencia_atendimento_valida,
    tipo_atendimento_valido,
)
from gestao_hospitalar.validacao_diagnosticos import (
    data_diagnostico_valida,
    diagnostico_texto_valido,
    referencia_diagnostico_valida,
)
from gestao_hospitalar.validacao_internacoes import (
    data_internacao_valida,
    data_saida_valida,
    numero_leito_valido,
    status_internacao_valido,
)
from gestao_hospitalar.validacao_transferencias import (
    data_transferencia_valida,
    referencia_transferencia_valida,
    transferencia_texto_valida,
)
from gestao_hospitalar.validacao_historico import (
    normalizar_historico,
    referencia_historico_valida,
)
from gestao_hospitalar.validacao_pacientes import (
    data_nascimento_valida,
    formatar_cpf,
    formatar_nome,
    formatar_telefone,
    nome_valido,
    normalizar_nome,
    normalizar_telefone,
    telefone_valido,
)
from gestao_hospitalar.xano_client import (
    POR_PAGINA_PADRAO,
    XanoAuthenticationError,
    XanoSessionExpiredError,
    XanoClient,
    XanoConfig,
    XanoError,
    XanoValidationError,
)


logger = get_logger("auth_state")

VALIDADE_PAINEL_SEGUNDOS = 60


CAMPOS_FEEDBACK: dict[str, tuple[str, str | None]] = {
    "login": ("erro", None),
    "paciente": ("erro_paciente", "sucesso_paciente"),
    "medico": ("erro_medico", "sucesso_medico"),
    "convenio": ("erro_convenio", "sucesso_convenio"),
    "atendimento": ("erro_atendimento", "sucesso_atendimento"),
    "diagnostico": ("erro_diagnostico", "sucesso_diagnostico"),
    "leito": ("erro_leito", "sucesso_leito"),
    "internacao": ("erro_internacao", "sucesso_internacao"),
    "transferencia": ("erro_transferencia", "sucesso_transferencia"),
    "historico": ("erro_historico", None),
    "painel": ("erro_painel", None),
    "relatorio": ("erro_internacao", None),
}

CAMPOS_LIMPEZA: dict[str, dict[str, object]] = {
    "painel": {
        "painel_pacientes": -1,
        "painel_medicos": -1,
        "painel_atendimentos": -1,
        "painel_leitos_livres": -1,
        "painel_leitos_ocupados": -1,
        "painel_internacoes_ativas": -1,
        "painel_atualizado_em": "",
        "erro_painel": "",
        "painel_serie": [],
        "painel_ev_atendimentos": [],
        "painel_ev_internacoes": [],
        "painel_amostra_atendimentos": -1,
        "painel_periodo": "30",
        "painel_graficos_carregando": False,
        "painel_graficos_carregado": False,
    },
    "pacientes": {
        "pacientes": [],
        "paciente_selecionado": {},
        "nome_paciente": "",
        "cpf_paciente": "",
        "pagina_pacientes": 1,
        "total_paginas_pacientes": 1,
        "total_registros_pacientes": 0,
        "nascimento_paciente": "",
        "telefone_paciente": "",
        "endereco_paciente": "",
        "emergencia_paciente": "",
        "erro_paciente": "",
        "sucesso_paciente": "",
        "termo_busca": "",
    },
    "medicos": {
        "medicos": [],
        "medico_selecionado": {},
        "id_medico_edicao": "",
        "pagina_medicos": 1,
        "total_paginas_medicos": 1,
        "total_registros_medicos": 0,
        "nome_medico": "",
        "crm_medico": "",
        "especialidade_medico": "",
        "telefone_medico": "",
        "erro_medico": "",
        "sucesso_medico": "",
        "termo_busca": "",
    },
    "convenios": {
        "convenios": [],
        "convenio_selecionado": {},
        "id_convenio_edicao": "",
        "nome_convenio": "",
        "tipo_convenio": "",
        "cobertura_convenio": "",
        "erro_convenio": "",
        "sucesso_convenio": "",
        "termo_busca": "",
    },
    "atendimentos": {
        "atendimentos": [],
        "atendimento_selecionado": {},
        "diagnosticos": [],
        "paciente_id_atendimento": "",
        "medico_id_atendimento": "",
        "convenio_id_atendimento": "",
        "data_atendimento": "",
        "motivo_atendimento": "",
        "tipo_atendimento": "",
        "erro_atendimento": "",
        "sucesso_atendimento": "",
        "atendimento_id_diagnostico": "",
        "descricao_diagnostico": "",
        "codigo_cid_diagnostico": "",
        "data_diagnostico": "",
        "erro_diagnostico": "",
        "sucesso_diagnostico": "",
        "termo_busca": "",
    },
    "internacoes": {
        "leitos": [],
        "internacoes": [],
        "atendimentos_internaveis": [],
        "atendimento_id_internacao": "",
        "leito_id_internacao": "",
        "data_entrada_internacao": "",
        "internacao_id_alta": "",
        "data_saida_internacao": "",
        "erro_internacao": "",
        "sucesso_internacao": "",
        "transferencias": [],
        "internacao_id_transferencia": "",
        "data_transferencia": "",
        "destino_transferencia": "",
        "motivo_transferencia": "",
        "erro_transferencia": "",
        "sucesso_transferencia": "",
        "numero_leito": "",
        "erro_leito": "",
        "sucesso_leito": "",
        "termo_busca": "",
    },
    "historico": {
        "paciente_id_historico": "",
        "historico_eventos": [],
        "erro_historico": "",
    },
    "relatorios": {
        "leitos": [],
        "internacoes": [],
        "erro_internacao": "",
        "termo_busca": "",
    },
}


def texto_paginacao(pagina: int, total: int, exibidos: int) -> str:
    """Ex.: '26–50 de 140'; sem registros, 'Nenhum registro'."""
    if total <= 0 or exibidos <= 0:
        return "Nenhum registro"
    inicio = (pagina - 1) * POR_PAGINA_PADRAO + 1
    return f"{inicio}–{inicio + exibidos - 1} de {total}"


def paginas_do_total(total: int | None, exibidos: int) -> int:
    """Número de páginas; endpoint sem paginação (total None) conta como uma."""
    if total is None or exibidos == 0:
        return 1
    return max(1, -(-total // POR_PAGINA_PADRAO))


def rota_pos_login(papel: str) -> str | None:
    """Retorna a home permitida para o papel ou nega a sessão."""
    if pode_acessar(True, papel, RECURSO_DASHBOARD):
        return "/dashboard"
    return None


def valores_sessao_encerrada() -> tuple[int, str, str, str, str]:
    """Valores públicos e privados após o logout."""
    return 0, "", "", "", ""


class AuthState(rx.State):
    """Guarda a sessão do usuário autenticado e a lógica de login/logout."""

    usuario_id: int = 0
    papel: str = ""
    _auth_token: str = ""

    login: str = ""
    senha: str = ""
    erro: str = ""

    pacientes: list[dict[str, str]] = []
    pagina_pacientes: int = 1
    total_paginas_pacientes: int = 1
    total_registros_pacientes: int = 0
    pacientes_referencia: list[dict[str, str]] = []
    paciente_selecionado: dict[str, str] = {}
    nome_paciente: str = ""
    cpf_paciente: str = ""
    nascimento_paciente: str = ""
    telefone_paciente: str = ""
    endereco_paciente: str = ""
    emergencia_paciente: str = ""
    erro_paciente: str = ""
    sucesso_paciente: str = ""

    medicos: list[dict[str, str]] = []
    pagina_medicos: int = 1
    total_paginas_medicos: int = 1
    total_registros_medicos: int = 0
    medicos_referencia: list[dict[str, str]] = []
    medico_selecionado: dict[str, str] = {}
    id_medico_edicao: str = ""
    nome_medico: str = ""
    crm_medico: str = ""
    especialidade_medico: str = ""
    telefone_medico: str = ""
    erro_medico: str = ""
    sucesso_medico: str = ""

    convenios: list[dict[str, str]] = []
    convenio_selecionado: dict[str, str] = {}
    id_convenio_edicao: str = ""
    nome_convenio: str = ""
    tipo_convenio: str = ""
    cobertura_convenio: str = ""
    erro_convenio: str = ""
    sucesso_convenio: str = ""

    atendimentos: list[dict[str, str]] = []
    atendimento_selecionado: dict[str, str] = {}
    paciente_id_atendimento: str = ""
    medico_id_atendimento: str = ""
    convenio_id_atendimento: str = ""
    data_atendimento: str = ""
    motivo_atendimento: str = ""
    tipo_atendimento: str = ""
    erro_atendimento: str = ""
    sucesso_atendimento: str = ""

    diagnosticos: list[dict[str, str]] = []
    atendimento_id_diagnostico: str = ""
    descricao_diagnostico: str = ""
    codigo_cid_diagnostico: str = ""
    data_diagnostico: str = ""
    erro_diagnostico: str = ""
    sucesso_diagnostico: str = ""

    leitos: list[dict[str, str]] = []
    numero_leito: str = ""
    erro_leito: str = ""
    sucesso_leito: str = ""

    internacoes: list[dict[str, str]] = []
    atendimentos_internaveis: list[dict[str, str]] = []
    atendimento_id_internacao: str = ""
    leito_id_internacao: str = ""
    data_entrada_internacao: str = ""
    internacao_id_alta: str = ""
    data_saida_internacao: str = ""
    erro_internacao: str = ""
    sucesso_internacao: str = ""

    transferencias: list[dict[str, str]] = []
    internacao_id_transferencia: str = ""
    data_transferencia: str = ""
    destino_transferencia: str = ""
    motivo_transferencia: str = ""
    erro_transferencia: str = ""
    sucesso_transferencia: str = ""

    pacientes_historico: list[dict[str, str]] = []
    paciente_id_historico: str = ""
    historico_eventos: list[dict[str, str]] = []
    erro_historico: str = ""

    acao_em_andamento: str = ""
    termo_busca: str = ""
    ajuda_aberta: bool = False
    ajuda_topico: str = TOPICO_INICIAL
    # Última leitura falhou (mostra "Tentar novamente"); sessão recusada pelo Xano.
    leitura_falhou: bool = False
    _sessao_expirada: bool = False

    painel_pacientes: int = -1
    painel_medicos: int = -1
    painel_atendimentos: int = -1
    painel_leitos_livres: int = -1
    painel_leitos_ocupados: int = -1
    painel_internacoes_ativas: int = -1
    painel_atualizado_em: str = ""
    erro_painel: str = ""
    _painel_ts: float = 0.0
    painel_periodo: str = "30"
    painel_serie: list[dict[str, str]] = []
    painel_ev_atendimentos: list[dict[str, str]] = []
    painel_ev_internacoes: list[dict[str, str]] = []
    painel_amostra_atendimentos: int = -1
    painel_graficos_carregando: bool = False
    painel_graficos_carregado: bool = False
    _graficos_ts: float = 0.0
    _graficos_versao: int = 0

    @rx.var
    def is_authenticated(self) -> bool:
        """Indica se há um usuário autenticado na sessão atual."""
        return self.usuario_id != 0

    @rx.var
    def possui_paciente_selecionado(self) -> bool:
        return bool(self.paciente_selecionado)

    @rx.var
    def possui_pacientes(self) -> bool:
        return bool(self.pacientes)

    @rx.var
    def pode_ver_pacientes(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_PACIENTES)

    @rx.var
    def pode_cadastrar_pacientes(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_CADASTRO_PACIENTES)

    @rx.var
    def possui_medico_selecionado(self) -> bool:
        return bool(self.medico_selecionado)

    @rx.var
    def possui_medicos(self) -> bool:
        return bool(self.medicos)

    @rx.var
    def pode_ver_medicos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_MEDICOS)

    @rx.var
    def pode_cadastrar_medicos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_MEDICOS)

    @rx.var
    def editando_medico(self) -> bool:
        return bool(self.id_medico_edicao)

    @rx.var
    def possui_convenio_selecionado(self) -> bool:
        return bool(self.convenio_selecionado)

    @rx.var
    def possui_convenios(self) -> bool:
        return bool(self.convenios)

    @rx.var
    def possui_atendimento_selecionado(self) -> bool:
        return bool(self.atendimento_selecionado)

    @rx.var
    def possui_atendimentos(self) -> bool:
        return bool(self.atendimentos)

    @rx.var
    def pode_ver_atendimentos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_ATENDIMENTOS)

    @rx.var
    def pode_cadastrar_atendimentos(self) -> bool:
        return self.is_authenticated and self.papel in {"recepcionista", "admin"}

    @rx.var
    def possui_diagnosticos(self) -> bool:
        return bool(self.diagnosticos)

    @rx.var
    def pode_ver_diagnosticos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_DIAGNOSTICOS)

    @rx.var
    def possui_leitos(self) -> bool:
        return bool(self.leitos)

    @rx.var
    def pode_ver_leitos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_LEITOS)

    @rx.var
    def pode_cadastrar_leitos(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_LEITOS)

    @rx.var
    def possui_internacoes(self) -> bool:
        return bool(self.internacoes)

    @rx.var
    def pode_ver_internacoes(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_INTERNACOES)

    @rx.var
    def pode_ver_relatorios(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_RELATORIOS)

    @rx.var
    def resumo_leitos(self) -> dict[str, int]:
        return contagem_leitos(self.leitos)

    @rx.var
    def lista_internacoes_ativas(self) -> list[InternacaoAtiva]:
        return calcular_internacoes_ativas(self.internacoes)

    @rx.var
    def possui_internacoes_ativas(self) -> bool:
        return bool(self.lista_internacoes_ativas)

    @rx.var
    def pode_cadastrar_internacoes(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_INTERNACOES)

    @rx.var
    def pode_ver_transferencias(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_TRANSFERENCIAS)

    @rx.var
    def possui_transferencias(self) -> bool:
        return bool(self.transferencias)

    @rx.var
    def internacao_transferencia_ativa(self) -> bool:
        return any(
            registro.get("id") == self.internacao_id_transferencia
            and registro.get("status") == "internado"
            for registro in self.internacoes
        )

    @rx.var
    def pode_ver_historico(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_HISTORICO)

    @rx.var
    def possui_historico_eventos(self) -> bool:
        return bool(self.historico_eventos)

    @rx.var
    def opcoes_pacientes_historico(self) -> list[str]:
        return [
            f"{paciente.get('id', '')} - {paciente.get('nome', '')}"
            for paciente in self.pacientes_historico
        ]

    @rx.var
    def opcoes_leitos_livres(self) -> list[str]:
        return [
            f"{leito.get('id', '')} - Leito {leito.get('numero', '')}"
            for leito in self.leitos
            if leito.get("status") == "livre"
        ]

    @rx.var
    def opcoes_atendimentos_internaveis(self) -> list[str]:
        return [
            (
                f"{atendimento.get('id', '')} - "
                f"{atendimento.get('paciente_nome', '')} - "
                f"{atendimento.get('data_atendimento', '')} - "
                f"{atendimento.get('tipo', '')} - "
                f"{atendimento.get('motivo', '')}"
            )
            for atendimento in self.atendimentos_internaveis
        ]

    @rx.var
    def tipos_atendimento(self) -> list[str]:
        return list(TIPOS_ATENDIMENTO)

    @rx.var
    def opcoes_pacientes_atendimento(self) -> list[str]:
        return [
            f"{paciente.get('id', '')} - {paciente.get('nome', '')}"
            for paciente in self.pacientes_referencia
        ]

    @rx.var
    def opcoes_medicos_atendimento(self) -> list[str]:
        return [
            f"{medico.get('id', '')} - {medico.get('nome', '')}"
            for medico in self.medicos_referencia
        ]

    @rx.var
    def opcoes_convenios_atendimento(self) -> list[str]:
        return [
            f"{convenio.get('id', '')} - {convenio.get('nome', '')}"
            for convenio in self.convenios
        ]

    @rx.var
    def pode_ver_convenios(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_CONVENIOS)

    @rx.var
    def pode_cadastrar_convenios(self) -> bool:
        return self._pode_acessar_recurso(RECURSO_CONVENIOS)

    @rx.var
    def editando_convenio(self) -> bool:
        return bool(self.id_convenio_edicao)

    @rx.var
    def tipos_convenio(self) -> list[str]:
        return list(TIPOS_CONVENIO)

    @rx.var
    def painel_grafico(self) -> list[dict[str, Any]]:
        return grafico(self.painel_serie, self.painel_periodo)

    @rx.var
    def painel_tipos(self) -> list[dict[str, Any]]:
        if not self.painel_serie:
            return []
        return totais_por_tipo(self.painel_serie, self.painel_periodo)

    @rx.var
    def painel_periodo_rotulo(self) -> str:
        return PERIODOS.get(self.painel_periodo, "")

    @rx.var
    def painel_emergencias_hoje(self) -> int:
        return emergencias_de_hoje(self.painel_serie)

    @rx.var
    def painel_atividade(self) -> list[dict[str, str]]:
        return mesclar_atividade(self.painel_ev_atendimentos, self.painel_ev_internacoes)

    @rx.var
    def painel_alertas(self) -> list[dict[str, str]]:
        return calcular_alertas(
            self.painel_taxa_ocupacao,
            self.painel_leitos_livres,
            self.painel_emergencias_hoje,
        )

    @rx.var
    def painel_amostra_parcial(self) -> bool:
        """Verdadeiro quando os gráficos usam menos atendimentos que o total."""
        return 0 <= self.painel_amostra_atendimentos < self.painel_atendimentos

    @rx.var
    def painel_total_leitos(self) -> int:
        if self.painel_leitos_livres < 0 or self.painel_leitos_ocupados < 0:
            return -1
        return self.painel_leitos_livres + self.painel_leitos_ocupados

    @rx.var
    def painel_taxa_ocupacao(self) -> int:
        total = self.painel_total_leitos
        if total <= 0:
            return -1
        return round(100 * self.painel_leitos_ocupados / total)

    @rx.var
    def texto_paginacao_pacientes(self) -> str:
        return texto_paginacao(
            self.pagina_pacientes, self.total_registros_pacientes, len(self.pacientes)
        )

    @rx.var
    def texto_paginacao_medicos(self) -> str:
        return texto_paginacao(
            self.pagina_medicos, self.total_registros_medicos, len(self.medicos)
        )

    @rx.var
    def carregando_pagina(self) -> bool:
        return self.acao_em_andamento == "carregando"

    @rx.var
    def iniciais_usuario(self) -> str:
        return (self.login.strip()[:2] or "?").upper()

    @rx.var
    def pacientes_filtrados(self) -> list[dict[str, str]]:
        return filtrar_registros(self.pacientes, self.termo_busca)

    @rx.var
    def medicos_filtrados(self) -> list[dict[str, str]]:
        return filtrar_registros(self.medicos, self.termo_busca)

    @rx.var
    def convenios_filtrados(self) -> list[dict[str, str]]:
        return filtrar_registros(self.convenios, self.termo_busca)

    @rx.var
    def atendimentos_filtrados(self) -> list[dict[str, str]]:
        return filtrar_registros(self.atendimentos, self.termo_busca)

    @rx.var
    def internacoes_filtradas(self) -> list[dict[str, str]]:
        return filtrar_registros(self.internacoes, self.termo_busca)

    @rx.var
    def total_leitos_livres(self) -> int:
        return sum(1 for leito in self.leitos if leito.get("status") == "livre")

    @rx.var
    def total_leitos_ocupados(self) -> int:
        return sum(1 for leito in self.leitos if leito.get("status") == "ocupado")

    @rx.var
    def total_internacoes_ativas(self) -> int:
        return sum(
            1 for internacao in self.internacoes if internacao.get("status") == "internado"
        )

    def _pode_acessar_recurso(self, recurso: str) -> bool:
        return pode_acessar(self.is_authenticated, self.papel, recurso)

    @rx.event
    def set_login(self, value: str):
        """Atualiza o campo de login do formulário."""
        self.login = value

    @rx.event
    def set_senha(self, value: str):
        """Atualiza o campo de senha do formulário."""
        self.senha = value

    @rx.event
    def set_termo_busca(self, value: str):
        self.termo_busca = value

    @rx.event
    def limpar_busca(self):
        self.termo_busca = ""

    @rx.event
    def iniciar_acao(self, chave: str, dominio: str = ""):
        """Marca a ação em andamento e limpa mensagens antigas do domínio."""
        self.acao_em_andamento = chave[:60]
        self.leitura_falhou = False
        campos = CAMPOS_FEEDBACK.get(dominio)
        if campos is None:
            return
        for campo in campos:
            if campo is not None:
                setattr(self, campo, "")

    @rx.event
    def abrir_ajuda(self):
        """Abre o modal de ajuda no tópico inicial."""
        self.ajuda_topico = TOPICO_INICIAL
        self.ajuda_aberta = True

    @rx.event
    def set_ajuda_aberta(self, aberta: bool):
        self.ajuda_aberta = bool(aberta)

    @rx.event
    def selecionar_ajuda(self, topico: str):
        """Troca o módulo exibido; ignora ids desconhecidos."""
        if topico_por_id(topico) is not None:
            self.ajuda_topico = topico

    @rx.event
    def encerrar_acao(self):
        """Fim comum das cadeias (leitura, cadastro, login): confere a sessão."""
        self.acao_em_andamento = ""
        if self._sessao_expirada:
            return AuthState.verificar_sessao

    def _registrar_falha(self, error: Exception, leitura: bool = True):
        """Anota o tipo da falha: sessão expirada leva ao login; leitura oferece repetir."""
        if isinstance(error, XanoSessionExpiredError):
            self._sessao_expirada = True
        elif leitura:
            self.leitura_falhou = True

    @rx.event
    def verificar_sessao(self):
        """Se o Xano recusou o token da sessão, volta ao login com aviso."""
        if not self._sessao_expirada:
            return
        self._sessao_expirada = False
        logger.warning("session_expired user_id=%s", self.usuario_id)
        return [
            rx.toast.warning(
                "Sua sessão expirou. Entre novamente.",
                close_button=True,
                duration=6000,
            ),
            AuthState.do_logout,
        ]

    @rx.event
    def tentar_novamente(self):
        """Repete a leitura da tela atual (botão do aviso de falha de leitura)."""
        carregador = {
            "/dashboard": AuthState.atualizar_resumo,
            "/pacientes": AuthState.carregar_pacientes,
            "/medicos": AuthState.carregar_medicos,
            "/convenios": AuthState.carregar_convenios,
            "/atendimentos": AuthState.carregar_atendimentos,
            "/internacoes": AuthState.carregar_internacoes,
            "/historico": AuthState.carregar_historico,
            "/relatorios": AuthState.carregar_relatorios,
        }.get(self.router.url.path.rstrip("/") or "/")
        if carregador is None:
            return
        return [
            AuthState.iniciar_acao("carregando"),
            carregador,
            AuthState.encerrar_acao,
        ]

    @rx.event
    def notificar_resultado(self, dominio: str):
        """Exibe toast com o resultado do último evento do domínio."""
        campos = CAMPOS_FEEDBACK.get(dominio)
        if campos is None:
            return
        campo_erro, campo_sucesso = campos
        erro = getattr(self, campo_erro)
        if erro:
            return rx.toast.error(erro, close_button=True, duration=6000)
        if campo_sucesso is None:
            return
        sucesso = getattr(self, campo_sucesso)
        if sucesso:
            setattr(self, campo_sucesso, "")
            return rx.toast.success(sucesso, close_button=True, duration=4000)

    @rx.event
    def notificar_atualizacao(self, dominio: str):
        """Confirma com toast que a leitura foi atualizada (ou mostra o erro)."""
        campos = CAMPOS_FEEDBACK.get(dominio)
        if campos is None:
            return
        erro = getattr(self, campos[0])
        if erro:
            return rx.toast.error(erro, close_button=True, duration=6000)
        return rx.toast.success("Dados atualizados.", duration=2500)

    @rx.event
    def limpar_tela(self, tela: str):
        """Limpa leituras, seleções, busca e formulários de uma tela (lista fixa)."""
        campos = CAMPOS_LIMPEZA.get(tela)
        if campos is None:
            return
        if tela == "painel":
            self._invalidar_graficos()
        for campo, valor in campos.items():
            setattr(
                self,
                campo,
                type(valor)() if isinstance(valor, (list, dict)) else valor,
            )
        return rx.toast.info("Tela limpa.", duration=2500)

    @rx.event
    def atualizar_historico(self):
        """Recarrega os pacientes e, se houver um selecionado, o histórico dele."""
        destino = self.carregar_historico()
        if destino is not None:
            return destino
        if self.paciente_id_historico:
            self.consultar_historico()

    @rx.event
    def login_tecla(self, tecla: str):
        """Permite enviar o login com a tecla Enter."""
        if tecla != "Enter" or self.acao_em_andamento:
            return
        return [
            AuthState.iniciar_acao("login", "login"),
            AuthState.do_login,
            AuthState.notificar_resultado("login"),
            AuthState.encerrar_acao,
        ]

    @rx.event
    def carregar_resumo(self):
        """Carrega os indicadores do painel, reaproveitando uma leitura recente."""
        recente = (
            self.painel_atualizado_em != ""
            and time.time() - self._painel_ts < VALIDADE_PAINEL_SEGUNDOS
        )
        if not recente:
            self._ler_resumo()

    @rx.event
    def atualizar_resumo(self):
        """Releitura forçada dos indicadores e, depois, dos gráficos (botão Atualizar)."""
        self._ler_resumo()
        return AuthState.carregar_graficos(True)

    def _ler_resumo(self):
        """Lê só totais, em paralelo e sem guardar listas de pacientes no estado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_DASHBOARD):
            return
        try:
            cliente = XanoClient(XanoConfig.from_env())
        except XanoError:
            logger.warning("summary_result status=config_error role=%s", self.papel)
            return
        token = self._auth_token
        tarefas = {}
        if self.pode_ver_pacientes:
            tarefas["pacientes"] = lambda: cliente.contar_pacientes(token)
        if self.pode_ver_medicos:
            tarefas["medicos"] = lambda: cliente.contar_medicos(token)
        if self.pode_ver_atendimentos:
            tarefas["atendimentos"] = lambda: cliente.contar_atendimentos(token)
        if self.pode_ver_leitos:
            tarefas["leitos"] = lambda: cliente.listar_leitos(token)
        if self.pode_ver_internacoes:
            tarefas["internacoes"] = lambda: cliente.listar_internacoes(token)
        if not tarefas:
            return

        with ThreadPoolExecutor(max_workers=len(tarefas)) as pool:
            futuros = {chave: pool.submit(tarefa) for chave, tarefa in tarefas.items()}
        resultados = {}
        falhas = []
        for chave, futuro in futuros.items():
            try:
                resultados[chave] = futuro.result()
            except XanoError as error:
                self._registrar_falha(error)
                falhas.append(chave)
                logger.warning(
                    "summary_result status=xano_error resource=%s role=%s",
                    chave,
                    self.papel,
                )

        self.erro_painel = (
            "Não foi possível atualizar todos os indicadores." if falhas else ""
        )
        if "pacientes" in resultados:
            self.painel_pacientes = resultados["pacientes"]
        if "medicos" in resultados:
            self.painel_medicos = resultados["medicos"]
        if "atendimentos" in resultados:
            self.painel_atendimentos = resultados["atendimentos"]
        if "leitos" in resultados:
            status = [str(leito.get("status", "")) for leito in resultados["leitos"]]
            self.painel_leitos_livres = status.count("livre")
            self.painel_leitos_ocupados = status.count("ocupado")
        if "internacoes" in resultados:
            self.painel_internacoes_ativas = sum(
                1
                for internacao in resultados["internacoes"]
                if internacao.get("status") == "internado"
            )
            self.painel_ev_internacoes = eventos_internacoes(resultados["internacoes"])
        if resultados:
            self._painel_ts = time.time()
            self.painel_atualizado_em = time.strftime("%H:%M")

    @rx.event
    def set_painel_periodo(self, value: str | list[str]):
        escolhido = value[0] if isinstance(value, list) and value else value
        if isinstance(escolhido, str) and escolhido in PERIODOS:
            self.painel_periodo = escolhido

    def _invalidar_graficos(self):
        """Descarta leituras em curso e invalida o cache dos gráficos."""
        self._graficos_versao += 1
        self._graficos_ts = 0.0
        self.painel_graficos_carregando = False
        self.painel_graficos_carregado = False

    @rx.event(background=True)
    async def carregar_graficos(self, forcar: bool = False):
        """Lê os atendimentos fora da fila de eventos e agrega série, tipos e atividade.

        Roda em segundo plano para que indicadores e navegação não esperem a leitura
        completa dos atendimentos (a fila de eventos do usuário fica livre).
        """
        async with self:
            if not self.is_authenticated or not self.pode_ver_atendimentos:
                return
            recente = (
                self.painel_graficos_carregado
                and time.time() - self._graficos_ts < VALIDADE_PAINEL_SEGUNDOS
            )
            if not forcar and (recente or self.painel_graficos_carregando):
                return
            token = self._auth_token
            self._graficos_versao += 1
            versao = self._graficos_versao
            self.painel_graficos_carregando = True

        registros = None
        falha = None
        try:
            cliente = XanoClient(XanoConfig.from_env())
            registros = await asyncio.to_thread(cliente.listar_todos_atendimentos, token)
        except XanoError as error:
            falha = error
            logger.warning("summary_result status=xano_error resource=atendimentos_graficos")
        except Exception:
            # Tarefa sem usuário esperando: o erro vai ao log e ao aviso do painel,
            # e o indicador de carregamento nunca fica preso.
            logger.exception("summary_result status=unexpected_error resource=atendimentos_graficos")

        async with self:
            if versao != self._graficos_versao:
                return
            try:
                if self.is_authenticated and token == self._auth_token:
                    if falha is not None:
                        self._registrar_falha(falha)
                    self._aplicar_graficos(registros)
            finally:
                self.painel_graficos_carregando = False
        if isinstance(falha, XanoSessionExpiredError):
            return AuthState.verificar_sessao

    def _aplicar_graficos(self, registros: list[dict[str, Any]] | None):
        """Guarda só agregados e os 8 eventos mais recentes (não a lista completa)."""
        if registros is None:
            self.erro_painel = "Não foi possível carregar os gráficos."
            return
        self.painel_serie = serie_diaria(registros, date.today())
        self.painel_ev_atendimentos = eventos_atendimentos(registros)
        self.painel_amostra_atendimentos = len(registros)
        self.painel_graficos_carregado = True
        self._graficos_ts = time.time()

    @rx.event
    def set_nome_paciente(self, value: str):
        self.nome_paciente = formatar_nome(value)

    @rx.event
    def set_cpf_paciente(self, value: str):
        self.cpf_paciente = formatar_cpf(value)

    @rx.event
    def set_nascimento_paciente(self, value: str):
        self.nascimento_paciente = value

    @rx.event
    def set_telefone_paciente(self, value: str):
        self.telefone_paciente = formatar_telefone(value)

    @rx.event
    def set_endereco_paciente(self, value: str):
        self.endereco_paciente = value

    @rx.event
    def set_emergencia_paciente(self, value: str):
        self.emergencia_paciente = formatar_telefone(value)

    @rx.event
    def set_nome_medico(self, value: str):
        self.nome_medico = formatar_nome(value)

    @rx.event
    def set_crm_medico(self, value: str):
        self.crm_medico = formatar_crm(value)

    @rx.event
    def set_especialidade_medico(self, value: str):
        self.especialidade_medico = value

    @rx.event
    def set_telefone_medico(self, value: str):
        self.telefone_medico = formatar_telefone(value)

    @rx.event
    def set_nome_convenio(self, value: str):
        self.nome_convenio = value

    @rx.event
    def set_tipo_convenio(self, value: str):
        self.tipo_convenio = value

    @rx.event
    def set_cobertura_convenio(self, value: str):
        self.cobertura_convenio = value

    @rx.event
    def set_paciente_id_atendimento(self, value: str):
        self.paciente_id_atendimento = value

    @rx.event
    def set_medico_id_atendimento(self, value: str):
        self.medico_id_atendimento = value

    @rx.event
    def set_convenio_id_atendimento(self, value: str):
        self.convenio_id_atendimento = value

    @rx.event
    def set_data_atendimento(self, value: str):
        self.data_atendimento = value

    @rx.event
    def set_motivo_atendimento(self, value: str):
        self.motivo_atendimento = value

    @rx.event
    def set_tipo_atendimento(self, value: str):
        self.tipo_atendimento = value

    @rx.event
    def set_descricao_diagnostico(self, value: str):
        self.descricao_diagnostico = value

    @rx.event
    def set_codigo_cid_diagnostico(self, value: str):
        self.codigo_cid_diagnostico = value

    @rx.event
    def set_data_diagnostico(self, value: str):
        self.data_diagnostico = value

    @rx.event
    def set_numero_leito(self, value: str):
        self.numero_leito = value

    @rx.event
    def set_atendimento_id_internacao(self, value: str):
        self.atendimento_id_internacao = value

    @rx.event
    def set_leito_id_internacao(self, value: str):
        self.leito_id_internacao = value

    @rx.event
    def set_data_entrada_internacao(self, value: str):
        self.data_entrada_internacao = value

    @rx.event
    def set_data_saida_internacao(self, value: str):
        self.data_saida_internacao = value

    @rx.event
    def selecionar_internacao_alta(self, internacao_id: str):
        self.internacao_id_alta = internacao_id
        self.data_saida_internacao = ""
        self.erro_internacao = ""

    @rx.event
    def selecionar_internacao_transferencia(self, internacao_id: str):
        self.internacao_id_transferencia = internacao_id
        self.data_transferencia = ""
        self.destino_transferencia = ""
        self.motivo_transferencia = ""
        self.erro_transferencia = ""
        self.sucesso_transferencia = ""
        self._carregar_transferencias(internacao_id)

    @rx.event
    def set_data_transferencia(self, value: str):
        self.data_transferencia = value

    @rx.event
    def set_destino_transferencia(self, value: str):
        self.destino_transferencia = value

    @rx.event
    def set_motivo_transferencia(self, value: str):
        self.motivo_transferencia = value

    @rx.event
    def set_paciente_id_historico(self, value: str):
        self.paciente_id_historico = value

    @rx.event
    def consultar_historico(self):
        paciente_id = self.paciente_id_historico.split(" - ", 1)[0].strip()
        self.erro_historico = ""
        self.historico_eventos = []
        if not self.pode_ver_historico:
            self.erro_historico = "Você não tem permissão para consultar histórico."
            return
        if not referencia_historico_valida(paciente_id):
            self.erro_historico = "Selecione um paciente válido."
            return
        try:
            payload = XanoClient(XanoConfig.from_env()).consultar_historico(
                self._auth_token,
                int(paciente_id),
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_historico = "Não foi possível carregar o histórico."
            return
        self.historico_eventos = normalizar_historico(payload)

    @rx.event
    def carregar_historico(self):
        if not self.pode_ver_historico:
            return rx.redirect("/dashboard")
        self.erro_historico = ""
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_pacientes_historico(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_historico = "Não foi possível carregar os pacientes."
            return
        self.pacientes_historico = [
            {chave: "" if valor is None else str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]

    @rx.event
    def do_login(self):
        """Valida login e senha e estabelece a sessão em caso de sucesso."""
        logger.info("frontend_event name=do_login")
        try:
            usuario = XanoClient(XanoConfig.from_env()).login(
                self.login,
                self.senha,
            )
        except XanoAuthenticationError:
            logger.warning("login_result status=authentication_error")
            self.erro = "Login ou senha inválidos."
            return
        except XanoError:
            logger.warning("login_result status=xano_error")
            self.erro = "Não foi possível acessar o serviço de autenticação."
            return

        self.usuario_id = usuario.usuario_id
        self.papel = usuario.papel
        self._auth_token = usuario.auth_token
        destino = rota_pos_login(self.papel)
        if destino is None:
            logger.warning("login_result status=unknown_role role=%s", self.papel)
            self.usuario_id = 0
            self.papel = ""
            self._auth_token = ""
            self.erro = "Seu papel não possui acesso ao sistema."
            return rx.redirect("/")
        self.erro = ""
        self.senha = ""
        logger.info(
            "login_result status=success user_id=%s role=%s",
            self.usuario_id,
            self.papel,
        )
        return rx.redirect(destino)

    @rx.event
    def do_logout(self):
        """Encerra a sessão do usuário autenticado."""
        logger.info("frontend_event name=do_logout user_id=%s", self.usuario_id)
        (
            self.usuario_id,
            self.papel,
            self._auth_token,
            self.login,
            self.senha,
        ) = valores_sessao_encerrada()
        self.pacientes = []
        self.pagina_pacientes = 1
        self.total_paginas_pacientes = 1
        self.total_registros_pacientes = 0
        self.pacientes_referencia = []
        self.paciente_selecionado = {}
        self.nome_paciente = ""
        self.cpf_paciente = ""
        self.nascimento_paciente = ""
        self.telefone_paciente = ""
        self.endereco_paciente = ""
        self.emergencia_paciente = ""
        self.erro_paciente = ""
        self.sucesso_paciente = ""
        self.medicos = []
        self.pagina_medicos = 1
        self.total_paginas_medicos = 1
        self.total_registros_medicos = 0
        self.medicos_referencia = []
        self.medico_selecionado = {}
        self.id_medico_edicao = ""
        self.nome_medico = ""
        self.crm_medico = ""
        self.especialidade_medico = ""
        self.telefone_medico = ""
        self.erro_medico = ""
        self.sucesso_medico = ""
        self.convenios = []
        self.convenio_selecionado = {}
        self.id_convenio_edicao = ""
        self.nome_convenio = ""
        self.tipo_convenio = ""
        self.cobertura_convenio = ""
        self.erro_convenio = ""
        self.sucesso_convenio = ""
        self.atendimentos = []
        self.atendimento_selecionado = {}
        self.paciente_id_atendimento = ""
        self.medico_id_atendimento = ""
        self.convenio_id_atendimento = ""
        self.data_atendimento = ""
        self.motivo_atendimento = ""
        self.tipo_atendimento = ""
        self.erro_atendimento = ""
        self.sucesso_atendimento = ""
        self.diagnosticos = []
        self.atendimento_id_diagnostico = ""
        self.descricao_diagnostico = ""
        self.codigo_cid_diagnostico = ""
        self.data_diagnostico = ""
        self.erro_diagnostico = ""
        self.sucesso_diagnostico = ""
        self.leitos = []
        self.numero_leito = ""
        self.erro_leito = ""
        self.sucesso_leito = ""
        self.internacoes = []
        self.atendimentos_internaveis = []
        self.atendimento_id_internacao = ""
        self.leito_id_internacao = ""
        self.data_entrada_internacao = ""
        self.internacao_id_alta = ""
        self.data_saida_internacao = ""
        self.erro_internacao = ""
        self.sucesso_internacao = ""
        self.transferencias = []
        self.internacao_id_transferencia = ""
        self.data_transferencia = ""
        self.destino_transferencia = ""
        self.motivo_transferencia = ""
        self.erro_transferencia = ""
        self.sucesso_transferencia = ""
        self.pacientes_historico = []
        self.paciente_id_historico = ""
        self.historico_eventos = []
        self.erro_historico = ""
        self.acao_em_andamento = ""
        self.termo_busca = ""
        self.painel_pacientes = -1
        self.painel_medicos = -1
        self.painel_atendimentos = -1
        self.painel_leitos_livres = -1
        self.painel_leitos_ocupados = -1
        self.painel_internacoes_ativas = -1
        self.painel_atualizado_em = ""
        self.erro_painel = ""
        self._painel_ts = 0.0
        self.painel_serie = []
        self.painel_ev_atendimentos = []
        self.painel_ev_internacoes = []
        self.painel_amostra_atendimentos = -1
        self.painel_periodo = "30"
        self.leitura_falhou = False
        self._sessao_expirada = False
        self.ajuda_aberta = False
        self.ajuda_topico = TOPICO_INICIAL
        self._invalidar_graficos()
        return rx.redirect("/")

    @rx.event
    def carregar_pacientes(self):
        """Carrega a listagem resumida para papeis autorizados."""
        logger.info(
            "frontend_event name=carregar_pacientes authenticated=%s role=%s",
            self.is_authenticated,
            self.papel,
        )
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            logger.warning("patient_list_result status=forbidden role=%s", self.papel)
            return rx.redirect("/dashboard")
        self._carregar_pacientes()

    def _carregar_pacientes(self, nova_tentativa: bool = True):
        """Carrega a página atual de pacientes dentro de outro evento."""
        self.erro_paciente = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            self.erro_paciente = "Você não tem permissão para consultar pacientes."
            return

        try:
            registros, total = XanoClient(XanoConfig.from_env()).listar_pacientes_pagina(
                self._auth_token,
                self.pagina_pacientes,
                POR_PAGINA_PADRAO,
            )
        except XanoError as error:
            self._registrar_falha(error)
            logger.warning("patient_list_result status=xano_error role=%s", self.papel)
            self.erro_paciente = "Não foi possível carregar os pacientes."
            return

        if not registros and self.pagina_pacientes > 1 and nova_tentativa:
            self.pagina_pacientes = 1
            self._carregar_pacientes(nova_tentativa=False)
            return

        self.pacientes = [
            {
                chave: str(valor)
                for chave, valor in registro.items()
                if chave != "contato_emergencia"
            }
            for registro in registros
        ]
        self.total_registros_pacientes = total if total is not None else len(registros)
        self.total_paginas_pacientes = paginas_do_total(total, len(registros))
        logger.info(
            "patient_list_result status=success role=%s count=%s page=%s",
            self.papel,
            len(self.pacientes),
            self.pagina_pacientes,
        )

    def _carregar_pacientes_referencia(self):
        """Todos os pacientes (só id e nome) para o seletor de atendimentos."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            self.pacientes_referencia = []
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_todos_pacientes(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_atendimento = "Não foi possível carregar os pacientes."
            return
        self.pacientes_referencia = [
            {"id": str(r.get("id", "")), "nome": str(r.get("nome", ""))}
            for r in registros
        ]

    @rx.event
    def carregar_medicos(self):
        """Carrega a listagem de medicos para papeis autorizados."""
        logger.info(
            "frontend_event name=carregar_medicos authenticated=%s role=%s",
            self.is_authenticated,
            self.papel,
        )
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            logger.warning("doctor_list_result status=forbidden role=%s", self.papel)
            return rx.redirect("/dashboard")
        self._carregar_medicos()

    def _carregar_medicos(self, nova_tentativa: bool = True):
        """Carrega a página atual de médicos dentro de outro evento."""
        self.erro_medico = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para consultar médicos."
            return

        try:
            registros, total = XanoClient(XanoConfig.from_env()).listar_medicos_pagina(
                self._auth_token,
                self.pagina_medicos,
                POR_PAGINA_PADRAO,
            )
        except XanoError as error:
            self._registrar_falha(error)
            logger.warning("doctor_list_result status=xano_error role=%s", self.papel)
            self.erro_medico = "Não foi possível carregar os médicos."
            return

        if not registros and self.pagina_medicos > 1 and nova_tentativa:
            self.pagina_medicos = 1
            self._carregar_medicos(nova_tentativa=False)
            return

        self.medicos = [
            {chave: str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]
        self.total_registros_medicos = total if total is not None else len(registros)
        self.total_paginas_medicos = paginas_do_total(total, len(registros))
        logger.info(
            "doctor_list_result status=success role=%s count=%s page=%s",
            self.papel,
            len(self.medicos),
            self.pagina_medicos,
        )

    def _carregar_medicos_referencia(self):
        """Todos os médicos (só id e nome) para o seletor de atendimentos."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.medicos_referencia = []
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_todos_medicos(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_atendimento = "Não foi possível carregar os médicos."
            return
        self.medicos_referencia = [
            {"id": str(r.get("id", "")), "nome": str(r.get("nome", ""))}
            for r in registros
        ]

    @rx.event
    def mudar_pagina(self, tela: str, delta: int):
        """Navega nas listas paginadas (pacientes e médicos); a busca é por página."""
        if tela == "pacientes":
            self.pagina_pacientes = min(
                max(1, self.pagina_pacientes + delta), self.total_paginas_pacientes
            )
            self.termo_busca = ""
            self._carregar_pacientes()
        elif tela == "medicos":
            self.pagina_medicos = min(
                max(1, self.pagina_medicos + delta), self.total_paginas_medicos
            )
            self.termo_busca = ""
            self._carregar_medicos()

    @rx.event
    def consultar_medico(self, medico_id: str):
        """Carrega os dados detalhados de um medico autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para consultar médicos."
            return
        if self.medico_selecionado.get("id") == str(medico_id):
            self.medico_selecionado = {}
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_medico(
                self._auth_token,
                int(medico_id),
            )
        except (ValueError, XanoError):
            self.erro_medico = "Não foi possível consultar o médico."
            return
        self.medico_selecionado = {
            chave: str(valor) for chave, valor in registro.items()
        }

    @rx.event
    def editar_medico(self, medico_id: str):
        """Preenche o formulário com os dados do médico selecionado."""
        try:
            registro = next(
                medico
                for medico in self.medicos
                if medico.get("id") == str(medico_id)
            )
        except StopIteration:
            self.erro_medico = "Não foi possível editar o médico."
            return
        self.erro_medico = ""
        self.id_medico_edicao = str(medico_id)
        self.nome_medico = registro.get("nome", "")
        self.crm_medico = formatar_crm(registro.get("crm", ""))
        self.especialidade_medico = registro.get("especialidade", "")
        self.telefone_medico = formatar_telefone(registro.get("telefone", ""))

    @rx.event
    def cancelar_edicao_medico(self):
        self.id_medico_edicao = ""
        self.nome_medico = ""
        self.crm_medico = ""
        self.especialidade_medico = ""
        self.telefone_medico = ""

    def _salvar_medico(self):
        """Valida e cria ou atualiza um médico para recepcionista ou admin."""
        self.erro_medico = ""
        self.sucesso_medico = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para manter médicos."
            return

        campos = [
            self.nome_medico,
            self.crm_medico,
            self.especialidade_medico,
            self.telefone_medico,
        ]
        if not all(campo.strip() for campo in campos):
            self.erro_medico = "Preencha todos os campos do médico."
            return

        nome = normalizar_nome(self.nome_medico)
        crm = normalizar_crm(self.crm_medico)
        telefone = normalizar_telefone(self.telefone_medico)
        if not nome_valido(nome):
            self.erro_medico = "Informe um nome válido."
            return
        if not crm_valido(crm):
            self.erro_medico = "Informe um CRM válido."
            return
        if not telefone_valido(telefone):
            self.erro_medico = "Informe um telefone válido."
            return

        try:
            medicos_existentes = XanoClient(XanoConfig.from_env()).listar_todos_medicos(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_medico = "Não foi possível validar o CRM."
            return
        if any(
            (
                not self.id_medico_edicao
                or str(medico.get("id", "")) != self.id_medico_edicao
            )
            and normalizar_crm(str(medico.get("crm", ""))) == crm
            for medico in medicos_existentes
        ):
            self.erro_medico = "O CRM já está cadastrado."
            return

        dados = {
            "nome": nome,
            "crm": crm,
            "especialidade": self.especialidade_medico.strip(),
            "telefone": telefone,
        }
        try:
            cliente = XanoClient(XanoConfig.from_env())
            if self.id_medico_edicao:
                cliente.atualizar_medico(
                    self._auth_token,
                    int(self.id_medico_edicao),
                    dados,
                )
                mensagem = "Médico atualizado."
            else:
                medico_id = cliente.criar_medico(self._auth_token, dados)
                mensagem = f"Médico cadastrado (#{medico_id})."
        except XanoValidationError:
            self.erro_medico = "O CRM já está cadastrado."
            return
        except (ValueError, XanoError):
            self.erro_medico = "Não foi possível salvar o médico."
            return

        self.sucesso_medico = mensagem
        self.id_medico_edicao = ""
        self.nome_medico = ""
        self.crm_medico = ""
        self.especialidade_medico = ""
        self.telefone_medico = ""
        self._carregar_medicos()

    @rx.event
    def criar_medico(self):
        """Mantém compatibilidade com o evento de cadastro existente."""
        self._salvar_medico()

    @rx.event
    def salvar_medico(self):
        self._salvar_medico()

    @rx.event
    def excluir_medico(self, medico_id: str):
        self.erro_medico = ""
        self.sucesso_medico = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para excluir médicos."
            return
        try:
            XanoClient(XanoConfig.from_env()).excluir_medico(
                self._auth_token,
                int(medico_id),
            )
        except XanoValidationError as error:
            self.erro_medico = str(error)
            return
        except (ValueError, XanoError):
            self.erro_medico = "Não foi possível excluir o médico."
            return
        self.sucesso_medico = "Médico excluído."
        self.medico_selecionado = {}
        if self.id_medico_edicao == str(medico_id):
            self.id_medico_edicao = ""
            self.nome_medico = ""
            self.crm_medico = ""
            self.especialidade_medico = ""
            self.telefone_medico = ""
        self._carregar_medicos()

    @rx.event
    def carregar_convenios(self):
        """Carrega a listagem de convenios para papeis autorizados."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            return rx.redirect("/dashboard")
        self._carregar_convenios()

    def _carregar_convenios(self):
        self.erro_convenio = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Você não tem permissão para consultar convênios."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_convenios(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_convenio = "Não foi possível carregar os convênios."
            return
        self.convenios = [
            {chave: str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]

    @rx.event
    def consultar_convenio(self, convenio_id: str):
        """Carrega os dados detalhados de um convenio autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Você não tem permissão para consultar convênios."
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_convenio(
                self._auth_token,
                int(convenio_id),
            )
        except (ValueError, XanoError):
            self.erro_convenio = "Não foi possível consultar o convênio."
            return
        self.convenio_selecionado = {
            chave: str(valor) for chave, valor in registro.items()
        }

    @rx.event
    def editar_convenio(self, convenio_id: str):
        try:
            registro = next(
                convenio for convenio in self.convenios
                if convenio.get("id") == str(int(convenio_id))
            )
        except (StopIteration, ValueError):
            self.erro_convenio = "Não foi possível editar o convênio."
            return
        self.id_convenio_edicao = str(convenio_id)
        self.nome_convenio = registro.get("nome", "")
        self.tipo_convenio = registro.get("tipo", "")
        self.cobertura_convenio = registro.get("cobertura", "")

    @rx.event
    def cancelar_edicao_convenio(self):
        self.id_convenio_edicao = ""
        self.nome_convenio = ""
        self.tipo_convenio = ""
        self.cobertura_convenio = ""

    @rx.event
    def salvar_convenio(self):
        """Cria ou atualiza um convenio conforme o modo do formulario."""
        self.erro_convenio = ""
        self.sucesso_convenio = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Você não tem permissão para manter convênios."
            return

        nome = normalizar_nome_convenio(self.nome_convenio)
        tipo = self.tipo_convenio.strip()
        cobertura = self.cobertura_convenio.strip()
        if not nome or not tipo or not cobertura:
            self.erro_convenio = "Preencha todos os campos do convênio."
            return
        if not nome_convenio_valido(nome):
            self.erro_convenio = "Informe um nome válido."
            return
        if not tipo_convenio_valido(tipo):
            self.erro_convenio = "Informe um tipo de convênio válido."
            return

        nome_normalizado = nome.casefold()
        try:
            existentes = XanoClient(XanoConfig.from_env()).listar_convenios(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_convenio = "Não foi possível validar o convênio."
            return
        if any(
            str(convenio.get("id")) != self.id_convenio_edicao
            and str(convenio.get("nome_normalizado", convenio.get("nome", ""))).casefold()
            == nome_normalizado
            for convenio in existentes
        ):
            self.erro_convenio = "O convênio já está cadastrado."
            return

        dados = {
            "nome": nome,
            "nome_normalizado": nome_normalizado,
            "tipo": tipo,
            "cobertura": cobertura,
        }
        try:
            cliente = XanoClient(XanoConfig.from_env())
            if self.id_convenio_edicao:
                cliente.atualizar_convenio(
                    self._auth_token,
                    int(self.id_convenio_edicao),
                    dados,
                )
                mensagem = "Convênio atualizado."
            else:
                convenio_id = cliente.criar_convenio(self._auth_token, dados)
                mensagem = f"Convênio cadastrado (#{convenio_id})."
        except XanoValidationError:
            self.erro_convenio = "O convênio já está cadastrado."
            return
        except (ValueError, XanoError):
            self.erro_convenio = "Não foi possível salvar o convênio."
            return

        self.sucesso_convenio = mensagem
        self.cancelar_edicao_convenio()
        self._carregar_convenios()

    @rx.event
    def excluir_convenio(self, convenio_id: str):
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Você não tem permissão para excluir convênios."
            return
        try:
            XanoClient(XanoConfig.from_env()).excluir_convenio(
                self._auth_token,
                int(convenio_id),
            )
        except (ValueError, XanoError):
            self.erro_convenio = "Não foi possível excluir o convênio."
            return
        self.sucesso_convenio = "Convênio excluído."
        self.convenio_selecionado = {}
        self._carregar_convenios()

    @rx.event
    def carregar_atendimentos(self):
        """Carrega referencias e atendimentos conforme o papel."""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_ATENDIMENTOS,
        ):
            return rx.redirect("/dashboard")
        self._carregar_atendimentos()
        if self.pode_cadastrar_atendimentos:
            self._carregar_pacientes_referencia()
            self._carregar_medicos_referencia()
            self._carregar_convenios()

    def _carregar_atendimentos(self):
        self.erro_atendimento = ""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_ATENDIMENTOS,
        ):
            self.erro_atendimento = (
                "Você não tem permissão para consultar atendimentos."
            )
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_atendimentos(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_atendimento = "Não foi possível carregar os atendimentos."
            return
        self.atendimentos = [
            {chave: str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]

    @rx.event
    def consultar_atendimento(self, atendimento_id: str):
        """Carrega os dados detalhados de um atendimento autorizado."""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_ATENDIMENTOS,
        ):
            self.erro_atendimento = (
                "Você não tem permissão para consultar atendimentos."
            )
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_atendimento(
                self._auth_token,
                int(atendimento_id),
            )
        except (ValueError, XanoError):
            self.erro_atendimento = "Não foi possível consultar o atendimento."
            return
        self.atendimento_selecionado = {
            chave: str(valor) for chave, valor in registro.items()
        }
        self.atendimento_id_diagnostico = str(self.atendimento_selecionado.get("id", ""))
        self.diagnosticos = []
        if self.pode_ver_diagnosticos:
            self._carregar_diagnosticos(self.atendimento_id_diagnostico)

    def _carregar_diagnosticos(self, atendimento_id: str):
        self.erro_diagnostico = ""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_DIAGNOSTICOS,
        ):
            self.diagnosticos = []
            return
        if not referencia_diagnostico_valida(atendimento_id):
            self.erro_diagnostico = "Não foi possível consultar os diagnósticos."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_diagnosticos(
                self._auth_token,
                int(atendimento_id),
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_diagnostico = "Não foi possível carregar os diagnósticos."
            return
        self.diagnosticos = [
            {
                chave: "" if valor is None else str(valor)
                for chave, valor in registro.items()
            }
            for registro in registros
        ]

    @rx.event
    def criar_diagnostico(self):
        """Valida e cria diagnostico para medico ou admin."""
        self.erro_diagnostico = ""
        self.sucesso_diagnostico = ""
        if not self.pode_ver_diagnosticos:
            self.erro_diagnostico = (
                "Você não tem permissão para cadastrar diagnósticos."
            )
            return
        if not referencia_diagnostico_valida(self.atendimento_id_diagnostico):
            self.erro_diagnostico = "Informe um atendimento válido."
            return
        if not diagnostico_texto_valido(self.descricao_diagnostico):
            self.erro_diagnostico = "Informe a descrição do diagnóstico."
            return
        if not data_diagnostico_valida(self.data_diagnostico):
            self.erro_diagnostico = "Informe uma data de diagnóstico válida."
            return

        try:
            diagnostico_id = XanoClient(XanoConfig.from_env()).criar_diagnostico(
                self._auth_token,
                {
                    "atendimento_id": int(self.atendimento_id_diagnostico),
                    "descricao": self.descricao_diagnostico.strip(),
                    "codigo_cid": self.codigo_cid_diagnostico.strip() or None,
                    "data_diagnostico": self.data_diagnostico,
                },
            )
        except XanoValidationError:
            self.erro_diagnostico = "O atendimento informado é inválido."
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_diagnostico = "Não foi possível cadastrar o diagnóstico."
            return

        self.sucesso_diagnostico = f"Diagnóstico cadastrado (#{diagnostico_id})."
        self.descricao_diagnostico = ""
        self.codigo_cid_diagnostico = ""
        self.data_diagnostico = ""
        self._carregar_diagnosticos(self.atendimento_id_diagnostico)

    @rx.event
    def carregar_leitos(self):
        """Carrega leitos para papeis autorizados."""
        if not self.pode_ver_leitos:
            return rx.redirect("/dashboard")
        self._carregar_leitos()

    def _carregar_leitos(self):
        self.erro_leito = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_LEITOS):
            self.erro_leito = "Você não tem permissão para consultar leitos."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_leitos(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_leito = "Não foi possível carregar os leitos."
            return
        self.leitos = [
            {chave: "" if valor is None else str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]

    @rx.event
    def criar_leito(self):
        """Valida e cria leito livre para enfermagem/gestao ou admin."""
        self.erro_leito = ""
        self.sucesso_leito = ""
        if not self.pode_cadastrar_leitos:
            self.erro_leito = "Você não tem permissão para cadastrar leitos."
            return
        numero = self.numero_leito.strip()
        if not numero_leito_valido(numero):
            self.erro_leito = "Informe um número de leito válido."
            return
        try:
            leito_id = XanoClient(XanoConfig.from_env()).criar_leito(
                self._auth_token,
                int(numero),
            )
        except XanoValidationError as error:
            self.erro_leito = str(error)
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_leito = "Não foi possível cadastrar o leito."
            return
        self.sucesso_leito = f"Leito cadastrado (#{leito_id})."
        self.numero_leito = ""
        self._carregar_leitos()

    @rx.event
    def carregar_internacoes(self):
        """Carrega leitos e internacoes para papeis autorizados."""
        if not self.pode_ver_internacoes:
            return rx.redirect("/dashboard")
        self._carregar_leitos()
        self._carregar_atendimentos_internaveis()
        self._carregar_internacoes()

    @rx.event
    def carregar_relatorios(self):
        """Carrega apenas os dados necessários aos relatórios autorizados."""
        if not self.pode_ver_relatorios:
            return rx.redirect("/dashboard")
        self._carregar_leitos()
        self._carregar_internacoes()

    def _carregar_atendimentos_internaveis(self):
        self.erro_internacao = ""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_INTERNACOES,
        ):
            self.atendimentos_internaveis = []
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_atendimentos_internaveis(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_internacao = "Não foi possível carregar os atendimentos elegíveis."
            return
        self.atendimentos_internaveis = [
            {
                chave: "" if valor is None else str(valor)
                for chave, valor in registro.items()
            }
            for registro in registros
        ]

    def _carregar_internacoes(self):
        self.erro_internacao = ""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_INTERNACOES,
        ):
            self.erro_internacao = "Você não tem permissão para consultar internações."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_internacoes(
                self._auth_token
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_internacao = "Não foi possível carregar as internações."
            return
        numeros_por_id = {
            leito.get("id", ""): leito.get("numero", "")
            for leito in self.leitos
        }
        self.internacoes = []
        for registro in registros:
            internacao = {
                chave: "" if valor is None else str(valor)
                for chave, valor in registro.items()
            }
            internacao["leito_numero"] = numeros_por_id.get(
                internacao.get("leito_id", ""),
                internacao.get("leito_id", ""),
            )
            self.internacoes.append(internacao)

    @rx.event
    def criar_internacao(self):
        """Valida e cria internacao em leito livre."""
        self.erro_internacao = ""
        self.sucesso_internacao = ""
        if not self.pode_cadastrar_internacoes:
            self.erro_internacao = "Você não tem permissão para cadastrar internações."
            return
        atendimento_id = self.atendimento_id_internacao.split(" - ", 1)[0].strip()
        leito_id = self.leito_id_internacao.split(" - ", 1)[0].strip()
        if not referencia_atendimento_valida(atendimento_id):
            self.erro_internacao = "Informe um atendimento válido."
            return
        if not numero_leito_valido(leito_id):
            self.erro_internacao = "Informe um leito válido."
            return
        if not data_internacao_valida(self.data_entrada_internacao):
            self.erro_internacao = "Informe uma data de entrada válida."
            return
        try:
            internacao_id = XanoClient(XanoConfig.from_env()).criar_internacao(
                self._auth_token,
                {
                    "atendimento_id": int(atendimento_id),
                    "leito_id": int(leito_id),
                    "data_entrada": self.data_entrada_internacao,
                },
            )
        except XanoValidationError as error:
            self.erro_internacao = str(error)
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_internacao = "Não foi possível cadastrar a internação."
            return
        self.sucesso_internacao = f"Internação cadastrada (#{internacao_id})."
        self.atendimento_id_internacao = ""
        self.leito_id_internacao = ""
        self.data_entrada_internacao = ""
        self._carregar_atendimentos_internaveis()
        self._carregar_leitos()
        self._carregar_internacoes()

    @rx.event
    def registrar_alta(self):
        """Registra alta e libera o leito da internacao."""
        self.erro_internacao = ""
        self.sucesso_internacao = ""
        if not self.pode_cadastrar_internacoes:
            self.erro_internacao = "Você não tem permissão para registrar alta."
            return
        if not referencia_atendimento_valida(self.internacao_id_alta):
            self.erro_internacao = "Selecione uma internação válida."
            return
        internacao = next(
            (
                registro
                for registro in self.internacoes
                if registro.get("id") == self.internacao_id_alta
            ),
            None,
        )
        if internacao is None:
            self.erro_internacao = "Internação não encontrada."
            return
        if not status_internacao_valido(internacao.get("status", "")):
            self.erro_internacao = "Status de internação inválido."
            return
        if internacao.get("status") != "internado":
            self.erro_internacao = "Internação já encerrada."
            return
        if not data_saida_valida(
            self.data_saida_internacao,
            internacao.get("data_entrada", ""),
        ):
            self.erro_internacao = "Informe uma data de saída válida."
            return
        try:
            XanoClient(XanoConfig.from_env()).registrar_alta(
                self._auth_token,
                int(self.internacao_id_alta),
                self.data_saida_internacao,
            )
        except XanoValidationError:
            self.erro_internacao = "A internação não pode receber alta."
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_internacao = "Não foi possível registrar a alta."
            return
        self.sucesso_internacao = "Alta registrada e leito liberado."
        self.internacao_id_alta = ""
        self.data_saida_internacao = ""
        self._carregar_leitos()
        self._carregar_internacoes()

    def _carregar_transferencias(self, internacao_id: str):
        self.erro_transferencia = ""
        if not pode_acessar(
            self.is_authenticated,
            self.papel,
            RECURSO_TRANSFERENCIAS,
        ):
            self.transferencias = []
            return
        if not referencia_transferencia_valida(internacao_id):
            self.erro_transferencia = "Informe uma internação válida."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_transferencias(
                self._auth_token,
                int(internacao_id),
            )
        except XanoError as error:
            self._registrar_falha(error)
            self.erro_transferencia = "Não foi possível carregar as transferências."
            return
        self.transferencias = [
            {
                chave: "" if valor is None else str(valor)
                for chave, valor in registro.items()
            }
            for registro in registros
        ]

    @rx.event
    def criar_transferencia(self):
        """Valida e cria transferencia em internacao ativa."""
        self.erro_transferencia = ""
        self.sucesso_transferencia = ""
        if not self.pode_ver_transferencias:
            self.erro_transferencia = "Você não tem permissão para transferências."
            return
        if not referencia_transferencia_valida(self.internacao_id_transferencia):
            self.erro_transferencia = "Selecione uma internação válida."
            return
        internacao = next(
            (
                registro
                for registro in self.internacoes
                if registro.get("id") == self.internacao_id_transferencia
            ),
            None,
        )
        if internacao is None:
            self.erro_transferencia = "Internação não encontrada."
            return
        if internacao.get("status") != "internado":
            self.erro_transferencia = "Internação encerrada."
            return
        if not data_transferencia_valida(self.data_transferencia):
            self.erro_transferencia = "Informe uma data de transferência válida."
            return
        if not transferencia_texto_valida(self.destino_transferencia):
            self.erro_transferencia = "Informe o destino da transferência."
            return
        if not transferencia_texto_valida(self.motivo_transferencia):
            self.erro_transferencia = "Informe o motivo da transferência."
            return
        try:
            transferencia_id = XanoClient(XanoConfig.from_env()).criar_transferencia(
                self._auth_token,
                {
                    "internacao_id": int(self.internacao_id_transferencia),
                    "data_transferencia": self.data_transferencia,
                    "destino": self.destino_transferencia.strip(),
                    "motivo": self.motivo_transferencia.strip(),
                },
            )
        except XanoValidationError as error:
            self.erro_transferencia = str(error)
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_transferencia = "Não foi possível cadastrar a transferência."
            return
        self.sucesso_transferencia = (
            f"Transferência cadastrada (#{transferencia_id})."
        )
        self.data_transferencia = ""
        self.destino_transferencia = ""
        self.motivo_transferencia = ""
        self._carregar_transferencias(self.internacao_id_transferencia)

    @rx.event
    def criar_atendimento(self):
        """Valida e cria atendimento para recepcionista ou admin."""
        self.erro_atendimento = ""
        self.sucesso_atendimento = ""
        if not self.pode_cadastrar_atendimentos:
            self.erro_atendimento = (
                "Você não tem permissão para cadastrar atendimentos."
            )
            return

        paciente_id = self.paciente_id_atendimento.split(" - ", 1)[0]
        medico_id = self.medico_id_atendimento.split(" - ", 1)[0]
        convenio_id = self.convenio_id_atendimento.split(" - ", 1)[0]
        campos_obrigatorios = [
            paciente_id,
            medico_id,
            self.data_atendimento,
            self.motivo_atendimento,
            self.tipo_atendimento,
        ]
        if not all(campo.strip() for campo in campos_obrigatorios):
            self.erro_atendimento = "Preencha todos os campos do atendimento."
            return
        if not referencia_atendimento_valida(paciente_id):
            self.erro_atendimento = "Informe um paciente válido."
            return
        if not referencia_atendimento_valida(medico_id):
            self.erro_atendimento = "Informe um médico válido."
            return
        if convenio_id and not referencia_atendimento_valida(convenio_id):
            self.erro_atendimento = "Informe um convênio válido."
            return
        if not data_atendimento_valida(self.data_atendimento):
            self.erro_atendimento = "Informe uma data de atendimento válida."
            return
        if not motivo_atendimento_valido(self.motivo_atendimento):
            self.erro_atendimento = "Informe o motivo do atendimento."
            return
        if not tipo_atendimento_valido(self.tipo_atendimento):
            self.erro_atendimento = "Informe um tipo de atendimento válido."
            return

        dados: dict[str, int | str | None] = {
            "paciente_id": int(paciente_id),
            "medico_id": int(medico_id),
            "convenio_id": int(convenio_id) if convenio_id else None,
            "data_atendimento": self.data_atendimento,
            "motivo": self.motivo_atendimento.strip(),
            "tipo": self.tipo_atendimento,
        }
        try:
            atendimento_id = XanoClient(XanoConfig.from_env()).criar_atendimento(
                self._auth_token,
                dados,
            )
        except XanoValidationError:
            self.erro_atendimento = "As referências do atendimento são inválidas."
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_atendimento = "Não foi possível cadastrar o atendimento."
            return

        self.sucesso_atendimento = f"Atendimento cadastrado (#{atendimento_id})."
        self.paciente_id_atendimento = ""
        self.medico_id_atendimento = ""
        self.convenio_id_atendimento = ""
        self.data_atendimento = ""
        self.motivo_atendimento = ""
        self.tipo_atendimento = ""
        self._carregar_atendimentos()

    @rx.event
    def consultar_paciente(self, paciente_id: str):
        """Carrega os dados detalhados de um paciente autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            self.erro_paciente = "Você não tem permissão para consultar pacientes."
            return
        if self.paciente_selecionado.get("id") == str(paciente_id):
            self.paciente_selecionado = {}
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_paciente(
                self._auth_token,
                int(paciente_id),
            )
        except (ValueError, XanoError):
            self.erro_paciente = "Não foi possível consultar o paciente."
            return
        self.paciente_selecionado = {
            chave: str(valor) for chave, valor in registro.items()
        }

    @rx.event
    def criar_paciente(self):
        """Valida e cria um paciente para recepcionista ou admin."""
        self.erro_paciente = ""
        self.sucesso_paciente = ""
        if not self.is_authenticated or not tem_permissao(
            self.papel,
            RECURSO_CADASTRO_PACIENTES,
        ):
            self.erro_paciente = "Você não tem permissão para cadastrar pacientes."
            return

        campos = [
            self.nome_paciente,
            self.cpf_paciente,
            self.nascimento_paciente,
            self.telefone_paciente,
            self.endereco_paciente,
            self.emergencia_paciente,
        ]
        if not all(campo.strip() for campo in campos):
            self.erro_paciente = "Preencha todos os campos do paciente."
            return

        cpf = normalizar_cpf(self.cpf_paciente)
        if not cpf_valido(cpf):
            self.erro_paciente = "Informe um CPF válido."
            return

        nome = normalizar_nome(self.nome_paciente)
        if not nome_valido(nome):
            self.erro_paciente = "Informe um nome válido."
            return

        if not data_nascimento_valida(self.nascimento_paciente):
            self.erro_paciente = "Informe uma data de nascimento válida."
            return

        telefone = normalizar_telefone(self.telefone_paciente)
        if not telefone_valido(telefone):
            self.erro_paciente = "Informe um telefone válido."
            return

        contato_emergencia = normalizar_telefone(self.emergencia_paciente)
        if not telefone_valido(contato_emergencia):
            self.erro_paciente = "Informe um contato de emergência válido."
            return

        try:
            paciente_id = XanoClient(XanoConfig.from_env()).criar_paciente(
                self._auth_token,
                {
                    "nome": nome,
                    "cpf": cpf,
                    "data_nascimento": self.nascimento_paciente,
                    "telefone": telefone,
                    "endereco": self.endereco_paciente.strip(),
                    "contato_emergencia": contato_emergencia,
                },
            )
        except XanoValidationError:
            self.erro_paciente = "O CPF já está cadastrado."
            return
        except XanoError as error:
            self._registrar_falha(error, leitura=False)
            self.erro_paciente = "Não foi possível cadastrar o paciente."
            return

        self.sucesso_paciente = f"Paciente cadastrado (#{paciente_id})."
        self.nome_paciente = ""
        self.cpf_paciente = ""
        self.nascimento_paciente = ""
        self.telefone_paciente = ""
        self.endereco_paciente = ""
        self.emergencia_paciente = ""
        self._carregar_pacientes()

    @rx.event
    def check_auth(self):
        """Protege o dashboard contra sessao ausente ou papel sem acesso."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_DASHBOARD):
            self.usuario_id = 0
            self.papel = ""
            self._auth_token = ""
            return rx.redirect("/")
