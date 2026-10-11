"""Pagina de cadastro e consulta de medicos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def formulario_medico() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar medico", size="5"),
            rx.input(
                placeholder="Nome completo",
                value=AuthState.nome_medico,
                on_change=AuthState.set_nome_medico,
                max_length=120,
                width="100%",
            ),
            rx.input(
                placeholder="CRM: 0000000/UF",
                value=AuthState.crm_medico,
                on_change=AuthState.set_crm_medico,
                max_length=12,
                width="100%",
            ),
            rx.input(
                placeholder="Especialidade",
                value=AuthState.especialidade_medico,
                on_change=AuthState.set_especialidade_medico,
                max_length=80,
                width="100%",
            ),
            rx.input(
                placeholder="Telefone: (00) 00000-0000",
                type="tel",
                value=AuthState.telefone_medico,
                on_change=AuthState.set_telefone_medico,
                max_length=15,
                width="100%",
            ),
            rx.cond(
                AuthState.erro_medico != "",
                rx.text(AuthState.erro_medico, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_medico != "",
                rx.text(AuthState.sucesso_medico, color="green"),
            ),
            rx.button("Cadastrar", on_click=AuthState.criar_medico, width="100%"),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_medico(medico: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(medico["nome"], weight="bold"),
                rx.text("CRM: ", medico["crm"]),
                rx.text("Especialidade: ", medico["especialidade"]),
                align="start",
                flex="1",
            ),
            rx.button(
                "Ver detalhes",
                on_click=AuthState.consultar_medico(medico["id"]),
            ),
            width="100%",
            align="center",
        ),
        width="100%",
    )


def detalhe_medico() -> rx.Component:
    return rx.cond(
        AuthState.possui_medico_selecionado,
        rx.card(
            rx.vstack(
                rx.heading("Detalhes do medico", size="5"),
                rx.text("Nome: ", AuthState.medico_selecionado["nome"]),
                rx.text("CRM: ", AuthState.medico_selecionado["crm"]),
                rx.text(
                    "Especialidade: ",
                    AuthState.medico_selecionado["especialidade"],
                ),
                rx.text("Telefone: ", AuthState.medico_selecionado["telefone"]),
                align="start",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def medicos() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Medicos", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_medicos,
                formulario_medico(),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.possui_medicos,
                rx.foreach(AuthState.medicos, linha_medico),
                rx.text("Nenhum medico encontrado."),
            ),
            detalhe_medico(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )