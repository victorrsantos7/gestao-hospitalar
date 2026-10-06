"""Página inicial pós-login (placeholder) do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def dashboard() -> rx.Component:
    """Página interna protegida, destino após login bem-sucedido."""
    return rx.center(
        rx.vstack(
            rx.heading("Bem-vindo(a)!", size="8"),
            rx.text("Usuário: ", AuthState.login, " — papel: ", AuthState.papel),
            rx.button("Sair", on_click=AuthState.do_logout),
            spacing="4",
            align="center",
        ),
        min_height="100vh",
    )
