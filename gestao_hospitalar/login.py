"""Página de login do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def login() -> rx.Component:
    """Página de login — ponto de entrada da aplicação."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.image(
                    src="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80",
                    alt="",
                    width="100%",
                    object_fit="cover",
                    height="100%",
                ),
                rx.box(
                    rx.vstack(
                        rx.box(
                            rx.box(
                                position="absolute",
                                background_color="white",
                                border_radius="0.25em",
                                height="2.2em",
                                left="0.8em",
                                top="0",
                                width="0.6em",
                            ),
                            rx.box(
                                position="absolute",
                                background_color="white",
                                border_radius="0.25em",
                                height="0.6em",
                                left="0",
                                top="0.8em",
                                width="2.2em",
                            ),
                            height="2.2em",
                            position="relative",
                            width="2.2em",
                        ),
                        rx.heading("Gestão Hospitalar", size="6", color="white"),
                        rx.text(
                            "Mais controle, melhores decisões, uma saúde mais eficiente.",
                            color="#d9e8f4",
                            max_width="19em",
                        ),
                        align="start",
                        position="absolute",
                        bottom="7em",
                        left="3em",
                        spacing="2",
                    ),
                    background="linear-gradient(180deg, rgba(8, 38, 69, 0.08), rgba(8, 38, 69, 0.88))",
                    position="absolute",
                    inset="0",
                ),
                background_color="#12395f",
                border_radius="0",
                overflow="hidden",
                position="relative",
                width="50%",
            ),
            rx.box(
                rx.vstack(
                    rx.heading("Bem-vindo(a)!", size="7", color="#173b61"),
                    rx.text("Entre com seu login e senha", color="#111827"),
                    rx.input(
                        placeholder="Login",
                        value=AuthState.login,
                        on_change=AuthState.set_login,
                        background_color="white",
                        border="1px solid #c8d4df",
                        color="#111827",
                        font_weight="500",
                        style={"color": "#111827", "::placeholder": {"color": "#53677b", "opacity": "1"}},
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Senha",
                        type="password",
                        value=AuthState.senha,
                        on_change=AuthState.set_senha,
                        background_color="white",
                        border="1px solid #c8d4df",
                        color="#111827",
                        font_weight="500",
                        style={"color": "#111827", "::placeholder": {"color": "#53677b", "opacity": "1"}},
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
                    justify="center",
                ),
                background_color="#ffffff",
                border_radius="0",
                padding="clamp(2em, 5vw, 4em)",
                width="50%",
            ),
            align="stretch",
            border="1px solid #d7e1ea",
            border_radius="8px",
            flex_wrap="nowrap",
            height="36em",
            justify="center",
            max_width="64em",
            overflow="hidden",
            width="100%",
        ),
        background="#f4f7fa",
        display="flex",
        align_items="flex-start",
        justify_content="center",
        min_height="100vh",
        padding="2em 1em",
        width="100%",
    )
