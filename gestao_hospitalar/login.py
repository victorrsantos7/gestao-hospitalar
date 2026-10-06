"""Página de login do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def login() -> rx.Component:
    """Página de login — ponto de entrada da aplicação."""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Gestão Hospitalar", size="6"),
                rx.text("Entre com seu login e senha", color="gray", text_align="center"),
                rx.input(
                    placeholder="Login",
                    value=AuthState.login,
                    on_change=AuthState.set_login,
                    width="100%",
                ),
                rx.input(
                    placeholder="Senha",
                    type="password",
                    value=AuthState.senha,
                    on_change=AuthState.set_senha,
                    width="100%",
                ),
                rx.cond(
                    AuthState.erro != "",
                    rx.text(AuthState.erro, color="red"),
                ),
                rx.button("Entrar", on_click=AuthState.do_login, width="100%"),
                spacing="4",
                width="100%",
                align="center",
            ),
            width="24em",
        ),
        min_height="100vh",
    )
