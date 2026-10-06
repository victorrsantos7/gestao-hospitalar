"""Estado de autenticação do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.models import Usuario
from gestao_hospitalar.security import verificar_senha


class AuthState(rx.State):
    """Guarda a sessão do usuário autenticado e a lógica de login/logout."""

    usuario_id: int = 0
    papel: str = ""

    login: str = ""
    senha: str = ""
    erro: str = ""

    @rx.var
    def is_authenticated(self) -> bool:
        """Indica se há um usuário autenticado na sessão atual."""
        return self.usuario_id != 0

    @rx.event
    def set_login(self, value: str):
        """Atualiza o campo de login do formulário."""
        self.login = value

    @rx.event
    def set_senha(self, value: str):
        """Atualiza o campo de senha do formulário."""
        self.senha = value

    @rx.event
    def do_login(self):
        """Valida login e senha e estabelece a sessão em caso de sucesso."""
        with rx.session() as session:
            usuario = Usuario.buscar_por_login(session, self.login)

        if usuario is None or not verificar_senha(self.senha, usuario.senha_hash):
            self.erro = "Login ou senha inválidos."
            return

        self.usuario_id = usuario.id
        self.papel = usuario.papel
        self.erro = ""
        self.senha = ""
        return rx.redirect("/dashboard")

    @rx.event
    def do_logout(self):
        """Encerra a sessão do usuário autenticado."""
        self.usuario_id = 0
        self.papel = ""
        self.login = ""
        self.senha = ""
        return rx.redirect("/")

    @rx.event
    def check_auth(self):
        """Redireciona para o login quando não há sessão autenticada."""
        if not self.is_authenticated:
            return rx.redirect("/")
