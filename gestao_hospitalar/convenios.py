"""Pagina de cadastro e consulta de convenios."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


def formulario_convenio() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                rx.cond(AuthState.editando_convenio, "Editar convênio", "Cadastrar convênio"),
                size="5",
                color="#000000",
            ),
            rx.input(
                placeholder="Nome do convênio",
                value=AuthState.nome_convenio,
                on_change=AuthState.set_nome_convenio,
                max_length=120,
                width="100%",
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Tipo de convênio",
                    width="100%",
                    style={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "border": "1px solid #d7dee6",
                        "textTransform": "capitalize",
                        "&[data-placeholder] .rt-SelectTriggerInner": {
                            "color": "#243b53 !important",
                            "textTransform": "none",
                        },
                    },
                ),
                rx.select.content(
                    rx.foreach(
                        AuthState.tipos_convenio,
                        lambda tipo: rx.select.item(
                            tipo,
                            value=tipo,
                            style={"textTransform": "capitalize"},
                        ),
                    ),
                ),
                value=AuthState.tipo_convenio,
                on_change=AuthState.set_tipo_convenio,
            ),
            rx.text_area(
                placeholder="Cobertura",
                value=AuthState.cobertura_convenio,
                on_change=AuthState.set_cobertura_convenio,
                max_length=500,
                width="100%",
                style={
                    "border": "1px solid #d7dee6",
                },
            ),
            rx.center(
                rx.hstack(
                    rx.button(
                        rx.cond(AuthState.editando_convenio, "Atualizar", "Cadastrar"),
                        on_click=AuthState.salvar_convenio,
                        style=_BOTAO_COMPACTO,
                    ),
                    rx.cond(
                        AuthState.editando_convenio,
                        rx.button(
                            "Cancelar",
                            on_click=AuthState.cancelar_edicao_convenio,
                            style=_BOTAO_COMPACTO,
                            variant="soft",
                        ),
                    ),
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
        width="100%",
    )


def linha_convenio(convenio: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(convenio["nome"], color="#000000", weight="bold"),
                    rx.text(
                        "Tipo: ",
                        convenio["tipo"],
                        color="#000000",
                        style={"textTransform": "capitalize"},
                    ),
                    rx.text("Cobertura: ", convenio["cobertura"], color="#000000"),
                    align="start",
                    flex="1",
                ),
                rx.vstack(
                    rx.button(
                        "Ver detalhes",
                        on_click=AuthState.consultar_convenio(convenio["id"]),
                        style=_BOTAO_COMPACTO,
                    ),
                    rx.cond(
                        AuthState.pode_cadastrar_convenios,
                        rx.hstack(
                            rx.icon_button(
                                rx.icon("pencil", size=16),
                                on_click=AuthState.editar_convenio(convenio["id"]),
                                variant="soft",
                                size="2",
                                radius="full",
                                title="Editar",
                            ),
                            rx.icon_button(
                                rx.icon("trash-2", size=16),
                                on_click=AuthState.excluir_convenio(convenio["id"]),
                                variant="soft",
                                color_scheme="red",
                                size="2",
                                radius="full",
                                title="Excluir",
                            ),
                            spacing="2",
                            justify="center",
                        ),
                    ),
                    spacing="2",
                    align="stretch",
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                AuthState.possui_convenio_selecionado,
                rx.cond(
                    AuthState.convenio_selecionado["id"] == convenio["id"],
                    detalhe_convenio(),
                    rx.fragment(),
                ),
                rx.fragment(),
            ),
            spacing="3",
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        padding="1em",
        width="100%",
    )


def detalhe_convenio() -> rx.Component:
    return rx.cond(
        AuthState.possui_convenio_selecionado,
        rx.box(
            rx.vstack(
            rx.heading("Detalhes do convênio", size="5", color="#000000"),
            rx.text("Nome: ", AuthState.convenio_selecionado["nome"], color="#000000"),
            rx.text(
                "Tipo: ",
                AuthState.convenio_selecionado["tipo"],
                color="#000000",
                style={"textTransform": "capitalize"},
            ),
                rx.text(
                    "Cobertura: ",
                    AuthState.convenio_selecionado["cobertura"],
                    color="#000000",
                ),
                align="start",
            ),
            background_color="#f4f8fb",
            border="1px solid #c8dbe9",
            border_left="4px solid #2d78b7",
            border_radius="8px",
            padding="1.25em",
            width="100%",
        ),
        rx.fragment(),
    )


def convenios() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Convênios", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_convenios,
                formulario_convenio(),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.erro_convenio != "",
                rx.text(AuthState.erro_convenio, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_convenio != "",
                rx.text(AuthState.sucesso_convenio, color="green"),
            ),
            rx.cond(
                AuthState.possui_convenios,
                rx.foreach(AuthState.convenios, linha_convenio),
                rx.text("Nenhum convênio encontrado."),
            ),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )