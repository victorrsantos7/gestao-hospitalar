"""Estado de autenticação do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.authorization import (
    RECURSO_CADASTRO_PACIENTES,
    RECURSO_CONVENIOS,
    RECURSO_DASHBOARD,
    RECURSO_ATENDIMENTOS,
    RECURSO_MEDICOS,
    RECURSO_PACIENTES,
    pode_acessar,
    tem_permissao,
)
from gestao_hospitalar.crm import crm_valido, formatar_crm, normalizar_crm
from gestao_hospitalar.cpf import cpf_valido, normalizar_cpf
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
    def carregar_convenios(self):
        """Carrega a listagem de convenios para papeis autorizados."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            return rx.redirect("/dashboard")
        self._carregar_convenios()

    def _carregar_convenios(self):
        self.erro_convenio = ""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Voce nao tem permissao para consultar convenios."
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_convenios(
                self._auth_token
            )
        except XanoError:
            self.erro_convenio = "Nao foi possivel carregar os convenios."
            return
        self.convenios = [
            {chave: str(valor) for chave, valor in registro.items()}
            for registro in registros
        ]

    @rx.event
    def consultar_convenio(self, convenio_id: str):
        """Carrega os dados detalhados de um convenio autorizado."""
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Voce nao tem permissao para consultar convenios."
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_convenio(
                self._auth_token,
                int(convenio_id),
            )
        except (ValueError, XanoError):
            self.erro_convenio = "Nao foi possivel consultar o convenio."
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
            self.erro_convenio = "Nao foi possivel editar o convenio."
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
            self.erro_convenio = "Voce nao tem permissao para manter convenios."
            return

        nome = normalizar_nome_convenio(self.nome_convenio)
        tipo = self.tipo_convenio.strip()
        cobertura = self.cobertura_convenio.strip()
        if not nome or not tipo or not cobertura:
            self.erro_convenio = "Preencha todos os campos do convenio."
            return
        if not nome_convenio_valido(nome):
            self.erro_convenio = "Informe um nome valido."
            return
        if not tipo_convenio_valido(tipo):
            self.erro_convenio = "Informe um tipo de convenio valido."
            return

        nome_normalizado = nome.casefold()
        try:
            existentes = XanoClient(XanoConfig.from_env()).listar_convenios(
                self._auth_token
            )
        except XanoError:
            self.erro_convenio = "Nao foi possivel validar o convenio."
            return
        if any(
            str(convenio.get("id")) != self.id_convenio_edicao
            and str(convenio.get("nome_normalizado", convenio.get("nome", ""))).casefold()
            == nome_normalizado
            for convenio in existentes
        ):
            self.erro_convenio = "O convenio ja esta cadastrado."
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
                mensagem = "Convenio atualizado."
            else:
                convenio_id = cliente.criar_convenio(self._auth_token, dados)
                mensagem = f"Convenio cadastrado (#{convenio_id})."
        except XanoValidationError:
            self.erro_convenio = "O convenio ja esta cadastrado."
            return
        except (ValueError, XanoError):
            self.erro_convenio = "Nao foi possivel salvar o convenio."
            return

        self.sucesso_convenio = mensagem
        self.cancelar_edicao_convenio()
        self._carregar_convenios()

    @rx.event
    def excluir_convenio(self, convenio_id: str):
        if not pode_acessar(self.is_authenticated, self.papel, RECURSO_CONVENIOS):
            self.erro_convenio = "Voce nao tem permissao para excluir convenios."
            return
        try:
            XanoClient(XanoConfig.from_env()).excluir_convenio(
                self._auth_token,
                int(convenio_id),
            )
        except (ValueError, XanoError):
            self.erro_convenio = "Nao foi possivel excluir o convenio."
            return
        self.sucesso_convenio = "Convenio excluido."
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
                "Voce nao tem permissao para consultar atendimentos."
            )
            return
        try:
            registros = XanoClient(XanoConfig.from_env()).listar_atendimentos(
                self._auth_token
            )
        except XanoError:
            self.erro_atendimento = "Nao foi possivel carregar os atendimentos."
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
                "Voce nao tem permissao para consultar atendimentos."
            )
            return
        try:
            registro = XanoClient(XanoConfig.from_env()).consultar_atendimento(
                self._auth_token,
                int(atendimento_id),
            )
        except (ValueError, XanoError):
            self.erro_atendimento = "Nao foi possivel consultar o atendimento."
            return
        self.atendimento_selecionado = {
            chave: str(valor) for chave, valor in registro.items()
        }

    @rx.event
    def criar_atendimento(self):
        """Valida e cria atendimento para recepcionista ou admin."""
        self.erro_atendimento = ""
        self.sucesso_atendimento = ""
        if not self.pode_cadastrar_atendimentos:
            self.erro_atendimento = (
                "Voce nao tem permissao para cadastrar atendimentos."
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
            self.erro_atendimento = "Informe um paciente valido."
            return
        if not referencia_atendimento_valida(medico_id):
            self.erro_atendimento = "Informe um medico valido."
            return
        if convenio_id and not referencia_atendimento_valida(convenio_id):
            self.erro_atendimento = "Informe um convenio valido."
            return
        if not data_atendimento_valida(self.data_atendimento):
            self.erro_atendimento = "Informe uma data de atendimento valida."
            return
        if not motivo_atendimento_valido(self.motivo_atendimento):
            self.erro_atendimento = "Informe o motivo do atendimento."
            return
        if not tipo_atendimento_valido(self.tipo_atendimento):
            self.erro_atendimento = "Informe um tipo de atendimento valido."
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
            self.erro_atendimento = "As referencias do atendimento sao invalidas."
            return
        except XanoError:
            self.erro_atendimento = "Nao foi possivel cadastrar o atendimento."
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
