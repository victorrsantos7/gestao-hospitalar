"""Página de cadastro e consulta de pacientes."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


_FILTRAR_NOME = """(() => {
    const input = document.activeElement;
    const valor = input.value
        .replace(/[^\\p{L}\\s'-]/gu, '')
        .replace(/\\s+/g, ' ')
        .replace(/^\\s+/, '');
    input.value = valor;
    return valor;
})()"""

_FORMATAR_CPF = """(() => {
    const input = document.activeElement;
    const digitos = input.value.replace(/\\D/g, '').slice(0, 11);
    let valor = digitos;
    if (digitos.length > 3) valor = `${digitos.slice(0, 3)}.${digitos.slice(3)}`;
    if (digitos.length > 6) valor = `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6)}`;
    if (digitos.length > 9) valor = `${digitos.slice(0, 3)}.${digitos.slice(3, 6)}.${digitos.slice(6, 9)}-${digitos.slice(9)}`;
    input.value = valor;
    return valor;
})()"""

_FORMATAR_TELEFONE = """(() => {
    const input = document.activeElement;
    const digitos = input.value.replace(/\\D/g, '').slice(0, 11);
    let valor = digitos;
    if (digitos.length > 2) valor = `(${digitos.slice(0, 2)}) ${digitos.slice(2)}`;
    if (digitos.length > 6 && digitos.length <= 10) valor = `(${digitos.slice(0, 2)}) ${digitos.slice(2, 6)}-${digitos.slice(6)}`;
    if (digitos.length > 7 && digitos.length > 10) valor = `(${digitos.slice(0, 2)}) ${digitos.slice(2, 7)}-${digitos.slice(7)}`;
    input.value = valor;
    return valor;
})()"""


def formulario_paciente() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading(
                "Cadastrar paciente",
                size="5",
                color="#173b61",
                class_name="patient-form-title",
            ),
            rx.input(
                placeholder="Nome completo",
                value=AuthState.nome_paciente,
                on_change=rx.call_script(
                    _FILTRAR_NOME,
                    callback=AuthState.set_nome_paciente,
                ),
                max_length=120,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.input(
                placeholder="CPF: 000.000.000-00",
                type="tel",
                value=AuthState.cpf_paciente,
                on_change=rx.call_script(
                    _FORMATAR_CPF,
                    callback=AuthState.set_cpf_paciente,
                ),
                max_length=14,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.input(
                placeholder="Data de nascimento: dd/mm/aaaa",
                type="text",
                inputmode="numeric",
                value=AuthState.nascimento_paciente,
                on_change=AuthState.set_nascimento_paciente,
                max_length=10,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.input(
                placeholder="Telefone: (00) 00000-0000",
                type="tel",
                value=AuthState.telefone_paciente,
                on_change=rx.call_script(
                    _FORMATAR_TELEFONE,
                    callback=AuthState.set_telefone_paciente,
                ),
                max_length=15,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.input(
                placeholder="Endereço",
                value=AuthState.endereco_paciente,
                on_change=AuthState.set_endereco_paciente,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.input(
                placeholder="Contato de emergência: (00) 00000-0000",
                type="tel",
                value=AuthState.emergencia_paciente,
                on_change=rx.call_script(
                    _FORMATAR_TELEFONE,
                    callback=AuthState.set_emergencia_paciente,
                ),
                max_length=15,
                width="100%",
                class_name="paciente-form-field",
            ),
            rx.cond(
                AuthState.erro_paciente != "",
                rx.text(AuthState.erro_paciente, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_paciente != "",
                rx.text(AuthState.sucesso_paciente, color="green"),
            ),
            rx.center(
                rx.button(
                    "Cadastrar",
                    on_click=AuthState.criar_paciente,
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
        width="100%",
    )


def linha_paciente(paciente: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(paciente["nome"], color="#173b61", weight="bold"),
                    rx.text("Nascimento: ", paciente["data_nascimento"], color="#52677d"),
                    rx.text("Telefone: ", paciente["telefone"], color="#52677d"),
                    align="start",
                    flex="1",
                ),
                rx.button(
                    "Ver detalhes",
                    on_click=AuthState.consultar_paciente(paciente["id"]),
                    style=_BOTAO_COMPACTO,
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                AuthState.possui_paciente_selecionado,
                rx.cond(
                    AuthState.paciente_selecionado["id"] == paciente["id"],
                    detalhe_paciente(),
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


def detalhe_paciente() -> rx.Component:
    return rx.cond(
        AuthState.possui_paciente_selecionado,
        rx.box(
            rx.vstack(
                rx.heading(
                    "Detalhes do paciente",
                    size="5",
                    color="#173b61",
                    class_name="patient-details-title",
                ),
                rx.text("Nome: ", AuthState.paciente_selecionado["nome"], color="#52677d"),
                rx.text("CPF: ", AuthState.paciente_selecionado["cpf"], color="#52677d"),
                rx.text(
                    "Contato de emergência: ",
                    AuthState.paciente_selecionado["contato_emergencia"],
                    color="#52677d",
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


def pacientes() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Pacientes", size="7", color="#173b61"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_pacientes,
                formulario_paciente(),
                rx.text("Perfil com acesso somente para consulta."),
            ),
            rx.cond(
                AuthState.erro_paciente != "",
                rx.text(AuthState.erro_paciente, color="red"),
            ),
            rx.cond(
                AuthState.possui_pacientes,
                rx.foreach(AuthState.pacientes, linha_paciente),
                rx.text("Nenhum paciente encontrado."),
            ),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )
