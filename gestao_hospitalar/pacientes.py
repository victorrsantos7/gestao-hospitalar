"""Página de cadastro e consulta de pacientes."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    grade_campos,
    paginacao,
    acoes_tela,
    botao_acao,
    botao_icone,
    data_br,
    entrada,
    grade_detalhes,
    item_detalhe,
    mensagem_erro,
    secao,
    secao_lista,
)
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import pagina


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
    return secao(
        "Cadastrar paciente",
        "user_round_plus",
        grade_campos(
            entrada(
                "Nome completo",
                AuthState.nome_paciente,
                rx.call_script(_FILTRAR_NOME, callback=AuthState.set_nome_paciente),
                "Ex.: Maria da Silva",
                obrigatorio=True,
                max_length=120,
            ),
            entrada(
                "CPF",
                AuthState.cpf_paciente,
                rx.call_script(_FORMATAR_CPF, callback=AuthState.set_cpf_paciente),
                "000.000.000-00",
                obrigatorio=True,
                type="tel",
                max_length=14,
            ),
            entrada(
                "Data de nascimento",
                AuthState.nascimento_paciente,
                AuthState.set_nascimento_paciente,
                obrigatorio=True,
                type="date",
            ),
            entrada(
                "Telefone",
                AuthState.telefone_paciente,
                rx.call_script(_FORMATAR_TELEFONE, callback=AuthState.set_telefone_paciente),
                "(00) 00000-0000",
                obrigatorio=True,
                type="tel",
                max_length=15,
            ),
            entrada(
                "Endereço",
                AuthState.endereco_paciente,
                AuthState.set_endereco_paciente,
                "Rua, número e bairro",
                obrigatorio=True,
            ),
            entrada(
                "Contato de emergência",
                AuthState.emergencia_paciente,
                rx.call_script(_FORMATAR_TELEFONE, callback=AuthState.set_emergencia_paciente),
                "(00) 00000-0000",
                obrigatorio=True,
                type="tel",
                max_length=15,
            ),
        ),
        mensagem_erro(AuthState.erro_paciente),
        botao_acao(
            "Cadastrar paciente",
            AuthState.criar_paciente,
            "criar_paciente",
            "paciente",
            "plus",
            width="100%",
        ),
        descricao="Todos os campos são obrigatórios.",
    )


def linha_paciente(paciente: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(rx.text(paciente["nome"], weight="bold")),
        rx.table.cell(data_br(paciente["data_nascimento"])),
        rx.table.cell(paciente["telefone"]),
        rx.table.cell(
            botao_icone(
                "eye",
                "Ver detalhes",
                AuthState.consultar_paciente(paciente["id"]),
                "ver_paciente_" + paciente["id"],
                "paciente",
                "teal",
            ),
            justify="end",
        ),
    )


def detalhe_paciente() -> rx.Component:
    return rx.cond(
        AuthState.possui_paciente_selecionado,
        secao(
            "Detalhes do paciente",
            "id_card",
            grade_detalhes(
                item_detalhe("Nome", AuthState.paciente_selecionado["nome"]),
                item_detalhe("CPF", AuthState.paciente_selecionado["cpf"]),
                item_detalhe(
                    "Contato de emergência",
                    AuthState.paciente_selecionado["contato_emergencia"],
                ),
            ),
        ),
        rx.fragment(),
    )


def _somente_consulta() -> rx.Component:
    return rx.vstack(
        rx.callout.root(
            rx.callout.icon(icone("info", 16)),
            rx.callout.text("Perfil com acesso somente para consulta."),
            color_scheme="blue",
            variant="soft",
            width="100%",
        ),
        mensagem_erro(AuthState.erro_paciente),
        spacing="3",
        width="100%",
        align="stretch",
    )


def pacientes() -> rx.Component:
    return pagina(
        "Pacientes",
        "Cadastro e consulta de pacientes",
        "users",
        "/pacientes",
        (acoes_tela("pacientes", AuthState.carregar_pacientes, "paciente"),),
        rx.flex(
            rx.box(
                rx.cond(
                    AuthState.pode_cadastrar_pacientes,
                    formulario_paciente(),
                    _somente_consulta(),
                ),
                class_name="gh-form-col",
            ),
            rx.vstack(
                secao_lista(
                    "Pacientes cadastrados",
                    "users",
                    AuthState.pacientes_filtrados,
                    ["Nome", "Nascimento", "Telefone", ""],
                    linha_paciente,
                    "Nenhum paciente encontrado.",
                    "Os pacientes cadastrados aparecerão aqui. Use Atualizar para consultar novamente.",
                    "Buscar nesta página por nome ou telefone",
                    "A busca considera apenas os registros desta página.",
                    paginacao(
                        "pacientes",
                        "paciente",
                        AuthState.pagina_pacientes,
                        AuthState.total_paginas_pacientes,
                        AuthState.texto_paginacao_pacientes,
                    ),
                    AuthState.total_registros_pacientes,
                ),
                detalhe_paciente(),
                spacing="4",
                align="stretch",
                flex="2 1 600px",
                min_width="0",
            ),
            wrap="wrap",
            spacing="4",
            align="start",
            width="100%",
        ),
    )
