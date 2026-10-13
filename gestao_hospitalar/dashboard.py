"""Página inicial protegida do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def dashboard() -> rx.Component:
    """Página interna protegida, destino após login bem-sucedido."""
    return rx.center(
        rx.vstack(
            rx.heading("Bem-vindo(a)!", size="8"),
            rx.text("Usuário: ", AuthState.login, " — papel: ", AuthState.papel),
            rx.cond(
                AuthState.pode_ver_pacientes,
                rx.button(
                    "Pacientes",
                    on_click=rx.redirect("/pacientes"),
                ),
            ),
            rx.cond(
                AuthState.pode_ver_medicos,
                rx.button(
                    "Medicos",
                    on_click=rx.redirect("/medicos"),
                ),
            ),
            rx.cond(
                AuthState.pode_ver_convenios,
                rx.button(
                    "Convenios",
                    on_click=rx.redirect("/convenios"),
                ),
            ),
            rx.cond(
                AuthState.pode_ver_atendimentos,
                rx.button(
                    "Atendimentos",
                    on_click=rx.redirect("/atendimentos"),
                ),
            ),
            rx.cond(
                AuthState.pode_ver_internacoes,
                rx.button(
                    "Internacoes e leitos",
                    on_click=rx.redirect("/internacoes"),
                ),
            ),
            rx.button("Sair", on_click=AuthState.do_logout),
            spacing="4",
            align="center",
        ),
        min_height="100vh",
    )
