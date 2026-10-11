"""Estado de autenticação do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.authorization import (
    RECURSO_CADASTRO_PACIENTES,
    RECURSO_DASHBOARD,
    RECURSO_MEDICOS,
    RECURSO_PACIENTES,
    pode_acessar,
    tem_permissao,
)
from gestao_hospitalar.crm import crm_valido, formatar_crm, normalizar_crm
from gestao_hospitalar.cpf import cpf_valido, normalizar_cpf
from gestao_hospitalar.logging_config import get_logger
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
            self.erro = "Seu papel nao possui acesso ao sistema."
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
            self.erro_paciente = "Voce nao tem permissao para consultar pacientes."
            return

        try:
            registros = XanoClient(XanoConfig.from_env()).listar_pacientes(
                self._auth_token
            )
        except XanoError:
            logger.warning("patient_list_result status=xano_error role=%s", self.papel)
            self.erro_paciente = "Nao foi possivel carregar os pacientes."
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
            self.erro_medico = "Voce nao tem permissao para consultar medicos."
            return

        try:
            registros = XanoClient(XanoConfig.from_env()).listar_medicos(
                self._auth_token
            )
        except XanoError:
            logger.warning("doctor_list_result status=xano_error role=%s", self.papel)
            self.erro_medico = "Nao foi possivel carregar os medicos."
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
            self.erro_medico = "Voce nao tem permissao para consultar medicos."
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_medico(
                self._auth_token,
                int(medico_id),
            )
        except (ValueError, XanoError):
            self.erro_medico = "Nao foi possivel consultar o medico."
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
            self.erro_medico = "Voce nao tem permissao para cadastrar medicos."
            return

        campos = [
            self.nome_medico,
            self.crm_medico,
            self.especialidade_medico,
            self.telefone_medico,
        ]
        if not all(campo.strip() for campo in campos):
            self.erro_medico = "Preencha todos os campos do medico."
            return

        nome = normalizar_nome(self.nome_medico)
        crm = normalizar_crm(self.crm_medico)
        telefone = normalizar_telefone(self.telefone_medico)
        if not nome_valido(nome):
            self.erro_medico = "Informe um nome valido."
            return
        if not crm_valido(crm):
            self.erro_medico = "Informe um CRM valido."
            return
        if not telefone_valido(telefone):
            self.erro_medico = "Informe um telefone valido."
            return

        try:
            medicos_existentes = XanoClient(XanoConfig.from_env()).listar_medicos(
                self._auth_token
            )
        except XanoError:
            self.erro_medico = "Nao foi possivel validar o CRM."
            return
        if any(
            normalizar_crm(str(medico.get("crm", ""))) == crm
            for medico in medicos_existentes
        ):
            self.erro_medico = "O CRM ja esta cadastrado."
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
            self.erro_medico = "O CRM ja esta cadastrado."
            return
        except XanoError:
            self.erro_medico = "Nao foi possivel cadastrar o medico."
            return

        self.sucesso_medico = f"Medico cadastrado (#{medico_id})."
        self.nome_medico = ""
        self.crm_medico = ""
        self.especialidade_medico = ""
        self.telefone_medico = ""
        self._carregar_medicos()

    @rx.event
    def consultar_paciente(self, paciente_id: str):
        """Carrega os dados detalhados de um paciente autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_PACIENTES):
            self.erro_paciente = "Voce nao tem permissao para consultar pacientes."
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_paciente(
                self._auth_token,
                int(paciente_id),
            )
        except (ValueError, XanoError):
            self.erro_paciente = "Nao foi possivel consultar o paciente."
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
            self.erro_paciente = "Voce nao tem permissao para cadastrar pacientes."
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
            self.erro_paciente = "Informe um CPF valido."
            return

        nome = normalizar_nome(self.nome_paciente)
        if not nome_valido(nome):
            self.erro_paciente = "Informe um nome valido."
            return

        if not data_nascimento_valida(self.nascimento_paciente):
            self.erro_paciente = "Informe uma data de nascimento valida."
            return

        telefone = normalizar_telefone(self.telefone_paciente)
        if not telefone_valido(telefone):
            self.erro_paciente = "Informe um telefone valido."
            return

        contato_emergencia = normalizar_telefone(self.emergencia_paciente)
        if not telefone_valido(contato_emergencia):
            self.erro_paciente = "Informe um contato de emergencia valido."
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
            self.erro_paciente = "O CPF ja esta cadastrado."
            return
        except XanoError:
            self.erro_paciente = "Nao foi possivel cadastrar o paciente."
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
