"""Pagina de cadastro e consulta de medicos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


def formulario_medico() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar médico", size="5", color="#000000"),
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
            rx.center(
                rx.button("Cadastrar", on_click=AuthState.criar_medico, style=_BOTAO_COMPACTO),
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


def linha_medico(medico: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(medico["nome"], color="#000000", weight="bold"),
                    rx.text("CRM: ", medico["crm"], color="#000000"),
                    rx.text("Especialidade: ", medico["especialidade"], color="#000000"),
                    align="start",
                    flex="1",
                ),
                rx.button(
                    "Ver detalhes",
                    on_click=AuthState.consultar_medico(medico["id"]),
                    style=_BOTAO_COMPACTO,
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                AuthState.possui_medico_selecionado,
                rx.cond(
                    AuthState.medico_selecionado["id"] == medico["id"],
                    detalhe_medico(),
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


def detalhe_medico() -> rx.Component:
    return rx.cond(
        AuthState.possui_medico_selecionado,
        rx.box(
            rx.vstack(
            rx.heading("Detalhes do médico", size="5", color="#000000"),
            rx.text("Nome: ", AuthState.medico_selecionado["nome"], color="#000000"),
            rx.text("CRM: ", AuthState.medico_selecionado["crm"], color="#000000"),
                rx.text(
                    "Especialidade: ",
                    AuthState.medico_selecionado["especialidade"],
                    color="#000000",
                ),
                rx.text("Telefone: ", AuthState.medico_selecionado["telefone"], color="#000000"),
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


def medicos() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Médicos", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
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
                rx.text("Nenhum médico encontrado."),
            ),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )