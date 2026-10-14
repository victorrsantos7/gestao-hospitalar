"""Estado de autenticação do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.authorization import (
    RECURSO_CADASTRO_PACIENTES,
    RECURSO_CONVENIOS,
    RECURSO_DASHBOARD,
    RECURSO_ATENDIMENTOS,
    RECURSO_DIAGNOSTICOS,
    RECURSO_INTERNACOES,
    RECURSO_LEITOS,
    RECURSO_HISTORICO,
    RECURSO_TRANSFERENCIAS,
    RECURSO_MEDICOS,
    RECURSO_PACIENTES,
    pode_acessar,
    tem_permissao,
)
from gestao_hospitalar.crm import crm_valido, formatar_crm, normalizar_crm
from gestao_hospitalar.cpf import cpf_valido, normalizar_cpf
from gestao_hospitalar.data_br import data_br_para_iso, formatar_data_br
from gestao_hospitalar.logging_config import get_logger
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
    XanoAuthenticationError,
    XanoClient,
    XanoConfig,
    XanoError,
    XanoValidationError,
)


logger = get_logger("auth_state")


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
    medico_selecionado: dict[str, str] = {}
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
            for paciente in self.pacientes
        ]

    @rx.var
    def opcoes_medicos_atendimento(self) -> list[str]:
        return [
            f"{medico.get('id', '')} - {medico.get('nome', '')}"
            for medico in self.medicos
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
    def set_nome_paciente(self, value: str):
        self.nome_paciente = formatar_nome(value)

    @rx.event
    def set_cpf_paciente(self, value: str):
        self.cpf_paciente = formatar_cpf(value)

    @rx.event
    def set_nascimento_paciente(self, value: str):
        self.nascimento_paciente = formatar_data_br(value)

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
        self.data_atendimento = formatar_data_br(value)

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
        self.data_diagnostico = formatar_data_br(value)

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
        self.data_entrada_internacao = formatar_data_br(value)

    @rx.event
    def set_data_saida_internacao(self, value: str):
        self.data_saida_internacao = formatar_data_br(value)

    @rx.event
    def selecionar_internacao_alta(self, internacao_id: str):
        if self.internacao_id_alta == internacao_id:
            self.internacao_id_alta = ""
            return
        self.internacao_id_alta = internacao_id
        self.data_saida_internacao = ""
        self.erro_internacao = ""

    @rx.event
    def selecionar_internacao_transferencia(self, internacao_id: str):
        if self.internacao_id_transferencia == internacao_id:
            self.internacao_id_transferencia = ""
            return
        self.internacao_id_transferencia = internacao_id
        self.data_transferencia = ""
        self.destino_transferencia = ""
        self.motivo_transferencia = ""
        self.erro_transferencia = ""
        self.sucesso_transferencia = ""
        self._carregar_transferencias(internacao_id)

    @rx.event
    def set_data_transferencia(self, value: str):
        self.data_transferencia = formatar_data_br(value)

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
        except XanoError:
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
        except XanoError:
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
        self.medico_selecionado = {}
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

    def _carregar_pacientes(self):
        """Executa a consulta de pacientes dentro de outro evento."""
        self.erro_paciente = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            self.erro_paciente = "Você não tem permissão para consultar pacientes."
            return

        try:
            registros = XanoClient(XanoConfig.from_env()).listar_pacientes(
                self._auth_token
            )
        except XanoError:
            logger.warning("patient_list_result status=xano_error role=%s", self.papel)
            self.erro_paciente = "Não foi possível carregar os pacientes."
            return

        self.pacientes = [
            {
                chave: str(valor)
                for chave, valor in registro.items()
                if chave != "contato_emergencia"
            }
            for registro in registros
        ]
        logger.info(
            "patient_list_result status=success role=%s count=%s",
            self.papel,
            len(self.pacientes),
        )

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

    def _carregar_medicos(self):
        """Executa a consulta de medicos dentro de outro evento."""
        self.erro_medico = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para consultar médicos."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_medicos(
                self._auth_token
            )
        except XanoError:
            logger.warning("doctor_list_result status=xano_error role=%s", self.papel)
            self.erro_medico = "Não foi possível carregar os médicos."
            return

        self.medicos = [
            {chave: str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]
        logger.info(
            "doctor_list_result status=success role=%s count=%s",
            self.papel,
            len(self.medicos),
        )

    @rx.event
    def consultar_medico(self, medico_id: str):
        """Carrega os dados detalhados de um medico autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para consultar médicos."
            return
        if self.medico_selecionado.get("id") == medico_id:
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
    def criar_medico(self):
        """Valida e cria um medico para recepcionista ou admin."""
        self.erro_medico = ""
        self.sucesso_medico = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_MEDICOS):
            self.erro_medico = "Você não tem permissão para cadastrar médicos."
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
            medicos_existentes = XanoClient(XanoConfig.from_env()).listar_medicos(
                self._auth_token
            )
        except XanoError:
            self.erro_medico = "Não foi possível validar o CRM."
            return
        if any(
            normalizar_crm(str(medico.get("crm", ""))) == crm
            for medico in medicos_existentes
        ):
            self.erro_medico = "O CRM já está cadastrado."
            return

        try:
            medico_id = XanoClient(XanoConfig.from_env()).criar_medico(
                self._auth_token,
                {
                    "nome": nome,
                    "crm": crm,
                    "especialidade": self.especialidade_medico.strip(),
                    "telefone": telefone,
                },
            )
        except XanoValidationError:
            self.erro_medico = "O CRM já está cadastrado."
            return
        except XanoError:
            self.erro_medico = "Não foi possível cadastrar o médico."
            return

        self.sucesso_medico = f"Médico cadastrado (#{medico_id})."
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
        except XanoError:
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
        if self.convenio_selecionado.get("id") == convenio_id:
            self.convenio_selecionado = {}
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
        except XanoError:
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
        if self.pode_cadastrar_atendimentos:
            self._carregar_medicos()
            self._carregar_convenios()
        self._carregar_atendimentos()

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
        except XanoError:
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
        if self.atendimento_selecionado.get("id") == atendimento_id:
            self.atendimento_selecionado = {}
            self.atendimento_id_diagnostico = ""
            self.diagnosticos = []
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
        except XanoError:
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
        if not data_diagnostico_valida(data_br_para_iso(self.data_diagnostico)):
            self.erro_diagnostico = "Informe uma data de diagnóstico válida."
            return

        try:
            diagnostico_id = XanoClient(XanoConfig.from_env()).criar_diagnostico(
                self._auth_token,
                {
                    "atendimento_id": int(self.atendimento_id_diagnostico),
                    "descricao": self.descricao_diagnostico.strip(),
                    "codigo_cid": self.codigo_cid_diagnostico.strip() or None,
                    "data_diagnostico": data_br_para_iso(self.data_diagnostico),
                },
            )
        except XanoValidationError:
            self.erro_diagnostico = "O atendimento informado é inválido."
            return
        except XanoError:
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
        except XanoError:
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
        except XanoError:
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
        except XanoError:
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
        except XanoError:
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
        if not data_internacao_valida(data_br_para_iso(self.data_entrada_internacao)):
            self.erro_internacao = "Informe uma data de entrada válida."
            return
        data_entrada_iso = data_br_para_iso(self.data_entrada_internacao)
        try:
            internacao_id = XanoClient(XanoConfig.from_env()).criar_internacao(
                self._auth_token,
                {
                    "atendimento_id": int(atendimento_id),
                    "leito_id": int(leito_id),
                    "data_entrada": data_entrada_iso,
                },
            )
        except XanoValidationError as error:
            self.erro_internacao = str(error)
            return
        except XanoError:
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
            data_br_para_iso(self.data_saida_internacao),
            internacao.get("data_entrada", ""),
        ):
            self.erro_internacao = "Informe uma data de saída válida."
            return
        try:
            XanoClient(XanoConfig.from_env()).registrar_alta(
                self._auth_token,
                int(self.internacao_id_alta),
                data_br_para_iso(self.data_saida_internacao),
            )
        except XanoValidationError:
            self.erro_internacao = "A internação não pode receber alta."
            return
        except XanoError:
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
        except XanoError:
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
        if not data_transferencia_valida(data_br_para_iso(self.data_transferencia)):
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
                    "data_transferencia": data_br_para_iso(self.data_transferencia),
                    "destino": self.destino_transferencia.strip(),
                    "motivo": self.motivo_transferencia.strip(),
                },
            )
        except XanoValidationError as error:
            self.erro_transferencia = str(error)
            return
        except XanoError:
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
        if not data_atendimento_valida(data_br_para_iso(self.data_atendimento)):
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
            "data_atendimento": data_br_para_iso(self.data_atendimento),
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
        except XanoError:
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
        if self.paciente_selecionado.get("id") == paciente_id:
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

        if not data_nascimento_valida(data_br_para_iso(self.nascimento_paciente)):
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
                    "data_nascimento": data_br_para_iso(self.nascimento_paciente),
                    "telefone": telefone,
                    "endereco": self.endereco_paciente.strip(),
                    "contato_emergencia": contato_emergencia,
                },
            )
        except XanoValidationError:
            self.erro_paciente = "O CPF já está cadastrado."
            return
        except XanoError:
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
