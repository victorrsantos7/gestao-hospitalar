"""Pagina de cadastro e consulta de pacientes."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


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
            rx.heading("Cadastrar paciente", size="5"),
            rx.input(
                placeholder="Nome completo",
                value=AuthState.nome_paciente,
                on_change=rx.call_script(
                    _FILTRAR_NOME,
                    callback=AuthState.set_nome_paciente,
                ),
                max_length=120,
                width="100%",
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
            ),
            rx.input(
                placeholder="Data de nascimento",
                type="date",
                value=AuthState.nascimento_paciente,
                on_change=AuthState.set_nascimento_paciente,
                width="100%",
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
            ),
            rx.input(
                placeholder="Endereco",
                value=AuthState.endereco_paciente,
                on_change=AuthState.set_endereco_paciente,
                width="100%",
            ),
            rx.input(
                placeholder="Contato de emergencia: (00) 00000-0000",
                type="tel",
                value=AuthState.emergencia_paciente,
                on_change=rx.call_script(
                    _FORMATAR_TELEFONE,
                    callback=AuthState.set_emergencia_paciente,
                ),
                max_length=15,
                width="100%",
            ),
            rx.cond(
                AuthState.erro_paciente != "",
                rx.text(AuthState.erro_paciente, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_paciente != "",
                rx.text(AuthState.sucesso_paciente, color="green"),
            ),
            rx.button("Cadastrar", on_click=AuthState.criar_paciente, width="100%"),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_paciente(paciente: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(paciente["nome"], weight="bold"),
                rx.text("Nascimento: ", paciente["data_nascimento"]),
                rx.text("Telefone: ", paciente["telefone"]),
                align="start",
                flex="1",
            ),
            rx.button(
                "Ver detalhes",
                on_click=AuthState.consultar_paciente(paciente["id"]),
            ),
            width="100%",
            align="center",
        ),
        width="100%",
    )


def detalhe_paciente() -> rx.Component:
    return rx.cond(
        AuthState.possui_paciente_selecionado,
        rx.card(
            rx.vstack(
                rx.heading("Detalhes do paciente", size="5"),
                rx.text("Nome: ", AuthState.paciente_selecionado["nome"]),
                rx.text("CPF: ", AuthState.paciente_selecionado["cpf"]),
                rx.text(
                    "Contato de emergencia: ",
                    AuthState.paciente_selecionado["contato_emergencia"],
                ),
                align="start",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def pacientes() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Pacientes", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
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
            detalhe_paciente(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )
