"""Página de relatórios: ocupação de leitos e internações ativas."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def card_resumo_leitos() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Ocupação de leitos", size="5", color="#000000"),
            rx.cond(
                AuthState.possui_leitos,
                rx.hstack(
                    rx.vstack(
                        rx.text("Livres", color="#6b7b8c"),
                        rx.text(
                            AuthState.resumo_leitos["livres"],
                            size="7",
                            weight="bold",
                            color="#1f7a4d",
                        ),
                        align="center",
                    ),
                    rx.vstack(
                        rx.text("Ocupados", color="#6b7b8c"),
                        rx.text(
                            AuthState.resumo_leitos["ocupados"],
                            size="7",
                            weight="bold",
                            color="#b4482b",
                        ),
                        align="center",
                    ),
                    rx.vstack(
                        rx.text("Total", color="#6b7b8c"),
                        rx.text(
                            AuthState.resumo_leitos["total"],
                            size="7",
                            weight="bold",
                            color="#173b61",
                        ),
                        align="center",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.text("Não há leitos cadastrados.", color="#000000"),
            ),
            align="start",
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


def linha_internacao_ativa(internacao: dict) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.text("Leito ", internacao["leito_numero"], weight="bold", color="#000000"),
            rx.spacer(),
            rx.text("Entrada: ", internacao["data_entrada"], color="#000000"),
            rx.spacer(),
            rx.badge(internacao["dias_internado"], " dia(s) internado"),
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        padding="1em",
        width="100%",
    )


def card_internacoes_ativas() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Internações ativas", size="5", color="#000000"),
            rx.cond(
                AuthState.possui_internacoes_ativas,
                rx.foreach(AuthState.lista_internacoes_ativas, linha_internacao_ativa),
                rx.text("Não há internações ativas no momento.", color="#000000"),
            ),
            align="start",
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


def relatorios() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Relatórios", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
                width="100%",
            ),
            card_resumo_leitos(),
            card_internacoes_ativas(),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )
