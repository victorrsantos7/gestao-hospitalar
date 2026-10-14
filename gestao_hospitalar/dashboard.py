"""Página inicial protegida do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def dashboard() -> rx.Component:
    """Página interna protegida, destino após login bem-sucedido."""
    return rx.hstack(
        rx.vstack(
            rx.hstack(
                rx.text("+", size="7", weight="bold", color="#7ec8ed"),
                rx.text("Gestão Hospitalar", weight="bold", color="white"),
                align="center",
                spacing="2",
            ),
            rx.divider(color="#28486b"),
            rx.text("Navegação", size="2", color="#9fb6cc"),
            rx.cond(
                AuthState.pode_ver_pacientes,
                rx.button("Pacientes", on_click=rx.redirect("/pacientes"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_medicos,
                rx.button("Médicos", on_click=rx.redirect("/medicos"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_convenios,
                rx.button("Convênios", on_click=rx.redirect("/convenios"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_atendimentos,
                rx.button("Atendimentos", on_click=rx.redirect("/atendimentos"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_internacoes,
                rx.button("Internações e leitos", on_click=rx.redirect("/internacoes"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_historico,
                rx.button("Histórico do paciente", on_click=rx.redirect("/historico"), width="100%"),
            ),
            rx.cond(
                AuthState.pode_ver_relatorios,
                rx.button("Relatórios", on_click=rx.redirect("/relatorios"), width="100%"),
            ),
            rx.spacer(),
            rx.button("Sair", on_click=AuthState.do_logout, width="100%"),
            align="start",
            background="#0f2f52",
            color="white",
            min_height="100vh",
            padding="2em 1em",
            spacing="3",
            width="16em",
        ),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Gestão Hospitalar", size="2", weight="bold", color="#2d6a8a"),
                    rx.heading("Bem-vindo(a)!", size="8", color="#173b61"),
                    rx.text("Usuário: ", AuthState.login, " — papel: ", AuthState.papel, color="#6b7b8c"),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.text(AuthState.papel, color="#6b7b8c"),
                align="center",
                width="100%",
            ),
            rx.divider(),
            rx.card(
                rx.vstack(
                    rx.text("Acessos disponíveis", size="4", weight="bold", color="#173b61"),
                    rx.text("Selecione uma área para continuar.", color="#6b7b8c"),
                    rx.divider(),
                    rx.text("Os módulos disponíveis para seu papel estão na navegação lateral.", color="#6b7b8c"),
                    align="start",
                    spacing="4",
                    width="100%",
                ),
                background_color="white",
                box_shadow="0 12px 30px rgba(18, 57, 95, 0.08)",
                width="100%",
            ),
            align="start",
            background="#f4f8fb",
            min_height="100vh",
            padding="clamp(1.5em, 4vw, 3em)",
            width="100%",
        ),
        align="stretch",
        min_height="100vh",
        width="100%",
    )
