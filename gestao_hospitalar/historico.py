"""Página de histórico consolidado do paciente."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def linha_evento(evento: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(evento["tipo"]),
                rx.text(evento["data"], weight="bold"),
                width="100%",
            ),
            rx.heading(evento["titulo"], size="4"),
            rx.text(evento["detalhes"]),
            align="start",
            width="100%",
        ),
        width="100%",
    )


def historico() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Histórico do paciente", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
                width="100%",
            ),
            rx.select(
                AuthState.opcoes_pacientes_historico,
                value=AuthState.paciente_id_historico,
                on_change=AuthState.set_paciente_id_historico,
                placeholder="Paciente",
                width="100%",
            ),
            rx.button(
                "Consultar histórico",
                on_click=AuthState.consultar_historico,
                width="100%",
            ),
            rx.cond(
                AuthState.erro_historico != "",
                rx.text(AuthState.erro_historico, color="red"),
            ),
            rx.cond(
                AuthState.possui_historico_eventos,
                rx.foreach(AuthState.historico_eventos, linha_evento),
                rx.text("Nenhum evento encontrado."),
            ),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )
