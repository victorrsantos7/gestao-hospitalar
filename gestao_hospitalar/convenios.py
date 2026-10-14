"""Pagina de cadastro e consulta de convenios."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def formulario_convenio() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                rx.cond(AuthState.editando_convenio, "Editar convênio", "Cadastrar convênio"),
                size="5",
            ),
            rx.input(
                placeholder="Nome do convênio",
                value=AuthState.nome_convenio,
                on_change=AuthState.set_nome_convenio,
                max_length=120,
                width="100%",
            ),
            rx.select(
                AuthState.tipos_convenio,
                value=AuthState.tipo_convenio,
                on_change=AuthState.set_tipo_convenio,
                placeholder="Tipo de convênio",
                width="100%",
            ),
            rx.text_area(
                placeholder="Cobertura",
                value=AuthState.cobertura_convenio,
                on_change=AuthState.set_cobertura_convenio,
                max_length=500,
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    rx.cond(AuthState.editando_convenio, "Atualizar", "Cadastrar"),
                    on_click=AuthState.salvar_convenio,
                ),
                rx.cond(
                    AuthState.editando_convenio,
                    rx.button(
                        "Cancelar",
                        on_click=AuthState.cancelar_edicao_convenio,
                    ),
                ),
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_convenio(convenio: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(convenio["nome"], weight="bold"),
                rx.text("Tipo: ", convenio["tipo"]),
                rx.text("Cobertura: ", convenio["cobertura"]),
                align="start",
                flex="1",
            ),
            rx.button(
                "Ver detalhes",
                on_click=AuthState.consultar_convenio(convenio["id"]),
            ),
            rx.cond(
                AuthState.pode_cadastrar_convenios,
                rx.vstack(
                    rx.button(
                        "Editar",
                        on_click=AuthState.editar_convenio(convenio["id"]),
                    ),
                    rx.button(
                        "Excluir",
                        on_click=AuthState.excluir_convenio(convenio["id"]),
                    ),
                ),
            ),
            width="100%",
            align="center",
        ),
        width="100%",
    )


def detalhe_convenio() -> rx.Component:
    return rx.cond(
        AuthState.possui_convenio_selecionado,
        rx.card(
            rx.vstack(
                rx.heading("Detalhes do convênio", size="5"),
                rx.text("Nome: ", AuthState.convenio_selecionado["nome"]),
                rx.text("Tipo: ", AuthState.convenio_selecionado["tipo"]),
                rx.text(
                    "Cobertura: ",
                    AuthState.convenio_selecionado["cobertura"],
                ),
                align="start",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def convenios() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Convênios", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
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
            detalhe_convenio(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )