"""Página de histórico consolidado do paciente."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


def linha_evento(evento: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(evento["tipo"]),
                rx.text(evento["data"], weight="bold", color="#000000"),
                width="100%",
            ),
            rx.heading(evento["titulo"], size="4", color="#000000"),
            rx.text(evento["detalhes"], color="#000000"),
            align="start",
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_left="4px solid #2d78b7",
        border_radius="10px",
        box_shadow="0 8px 24px rgba(18, 57, 95, 0.06)",
        padding="1em",
        width="100%",
    )


def formulario_historico() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Consultar histórico", size="5", color="#000000"),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Paciente",
                    width="100%",
                    style={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "border": "1px solid #d7dee6",
                        "&[data-placeholder] .rt-SelectTriggerInner": {
                            "color": "#243b53 !important",
                        },
                    },
                ),
                rx.select.content(
                    rx.foreach(
                        AuthState.opcoes_pacientes_historico,
                        lambda opcao: rx.select.item(opcao, value=opcao),
                    ),
                ),
                value=AuthState.paciente_id_historico,
                on_change=AuthState.set_paciente_id_historico,
            ),
            rx.cond(
                AuthState.erro_historico != "",
                rx.text(AuthState.erro_historico, color="red"),
            ),
            rx.center(
                rx.button(
                    "Consultar histórico",
                    on_click=AuthState.consultar_historico,
                    style=_BOTAO_COMPACTO,
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        box_shadow="0 8px 24px rgba(18, 57, 95, 0.06)",
        padding="1.25em",
        width="100%",
    )


def historico() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Histórico do paciente", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
                width="100%",
            ),
            formulario_historico(),
            rx.cond(
                AuthState.possui_historico_eventos,
                rx.foreach(AuthState.historico_eventos, linha_evento),
                rx.text("Nenhum evento encontrado.", color="#000000"),
            ),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )
