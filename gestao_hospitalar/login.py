"""Página de login do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import botao_acao, campo, mensagem_erro
from gestao_hospitalar.ui.icones import icone, marca, painel_login


def _destaque(nome_icone: str, texto: str) -> rx.Component:
    return rx.hstack(
        rx.center(
            icone(nome_icone, 16),
            width="32px",
            height="32px",
            border_radius="10px",
            background="rgba(255, 255, 255, 0.14)",
            flex_shrink="0",
        ),
        rx.text(texto, size="2", color="#d6eaf0"),
        spacing="3",
        align="center",
    )


def _painel() -> rx.Component:
    return rx.box(
        painel_login(),
        rx.hstack(
            marca(26),
            rx.text("Gestão Hospitalar", weight="bold", size="3", color="white"),
            spacing="2",
            align="center",
            class_name="gh-login-painel-compacta",
        ),
        rx.vstack(
            marca(52),
            rx.heading("Gestão Hospitalar", size="8", color="white", weight="bold"),
            rx.text(
                "Mais controle, melhores decisões, uma saúde mais eficiente.",
                size="4",
                color="#d6eaf0",
                max_width="26em",
            ),
            rx.vstack(
                _destaque("users", "Pacientes, médicos e convênios em um só lugar"),
                _destaque("bed_double", "Leitos, internações e transferências em tempo real"),
                _destaque("history", "Histórico consolidado de cada paciente"),
                spacing="3",
                align="start",
                margin_top="12px",
            ),
            spacing="3",
            align="start",
            class_name="gh-login-painel-texto",
        ),
        class_name="gh-login-painel",
    )


def _formulario() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            marca(34),
            rx.text("Gestão Hospitalar", weight="bold", size="3"),
            spacing="3",
            align="center",
            margin_bottom="8px",
            class_name="gh-login-form-marca",
        ),
        rx.vstack(
            rx.heading("Bem-vindo(a)!", size="6", class_name="gh-titulo-pagina"),
            rx.text("Entre com seu login e senha", size="2", color="var(--gh-muted)"),
            spacing="1",
            align="start",
        ),
        campo(
            "Login",
            rx.input(
                rx.input.slot(icone("user_round", 16)),
                placeholder="Seu login",
                value=AuthState.login,
                on_change=AuthState.set_login,
                on_key_down=AuthState.login_tecla,
                size="3",
                width="100%",
            ),
        ),
        campo(
            "Senha",
            rx.input(
                rx.input.slot(icone("lock", 16)),
                placeholder="Sua senha",
                type="password",
                value=AuthState.senha,
                on_change=AuthState.set_senha,
                on_key_down=AuthState.login_tecla,
                size="3",
                width="100%",
            ),
        ),
        mensagem_erro(AuthState.erro),
        botao_acao(
            "Entrar",
            AuthState.do_login,
            "login",
            "login",
            "log_in",
            size="3",
            width="100%",
        ),
        rx.text(
            "O acesso é restrito a profissionais autorizados.",
            size="1",
            color="var(--gh-muted)",
        ),
        spacing="3",
        align="stretch",
        width="100%",
        max_width="380px",
    )


def login() -> rx.Component:
    """Página de login — ponto de entrada da aplicação."""
    return rx.box(
        _painel(),
        rx.box(_formulario(), class_name="gh-login-form"),
        class_name="gh-login",
    )
