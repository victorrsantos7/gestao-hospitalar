"""Pagina de cadastro e consulta de medicos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    grade_campos,
    paginacao,
    acoes_tela,
    botao_acao,
    botao_icone,
    confirmar,
    entrada,
    grade_detalhes,
    item_detalhe,
    mensagem_erro,
    secao,
    secao_lista,
)
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import pagina


def formulario_medico() -> rx.Component:
    return secao(
        "Cadastrar ou editar médico",
        "stethoscope",
        grade_campos(
            entrada(
                "Nome completo",
                AuthState.nome_medico,
                AuthState.set_nome_medico,
                "Ex.: Dr. João Pereira",
                obrigatorio=True,
                max_length=120,
            ),
            entrada(
                "CRM",
                AuthState.crm_medico,
                AuthState.set_crm_medico,
                "0000000/UF",
                obrigatorio=True,
                max_length=12,
            ),
            entrada(
                "Especialidade",
                AuthState.especialidade_medico,
                AuthState.set_especialidade_medico,
                "Ex.: Cardiologia",
                obrigatorio=True,
                max_length=80,
            ),
            entrada(
                "Telefone",
                AuthState.telefone_medico,
                AuthState.set_telefone_medico,
                "(00) 00000-0000",
                obrigatorio=True,
                type="tel",
                max_length=15,
            ),
        ),
        mensagem_erro(AuthState.erro_medico),
        botao_acao(
            rx.cond(AuthState.editando_medico, "Atualizar médico", "Cadastrar médico"),
            AuthState.salvar_medico,
            "salvar_medico",
            "medico",
            "save",
            width="100%",
        ),
        rx.cond(
            AuthState.editando_medico,
            rx.button(
                "Cancelar edição",
                on_click=AuthState.cancelar_edicao_medico,
                variant="soft",
                color_scheme="gray",
                width="100%",
                cursor="pointer",
            ),
        ),
        descricao="Todos os campos são obrigatórios.",
    )


def linha_medico(medico: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(rx.text(medico["nome"], weight="bold")),
        rx.table.cell(medico["crm"]),
        rx.table.cell(medico["especialidade"]),
        rx.table.cell(
            rx.hstack(
                botao_icone(
                    "eye",
                    "Ver detalhes",
                    AuthState.consultar_medico(medico["id"]),
                    "ver_medico_" + medico["id"],
                    "medico",
                    "teal",
                ),
                rx.cond(
                    AuthState.pode_cadastrar_medicos,
                    rx.hstack(
                        rx.tooltip(
                            rx.icon_button(
                                icone("pencil", 16),
                                on_click=AuthState.editar_medico(medico["id"]),
                                variant="soft",
                                color_scheme="gray",
                                size="2",
                                cursor="pointer",
                                aria_label="Editar",
                            ),
                            content="Editar",
                        ),
                        confirmar(
                            rx.icon_button(
                                icone("trash_2", 16),
                                variant="soft",
                                color_scheme="red",
                                size="2",
                                cursor="pointer",
                                aria_label="Excluir",
                            ),
                            "Excluir médico?",
                            "O médico será removido se não possuir atendimentos vinculados.",
                            "Excluir",
                            AuthState.excluir_medico(medico["id"]),
                            "excluir_medico_" + medico["id"],
                            "medico",
                            "red",
                        ),
                        spacing="2",
                    ),
                ),
                spacing="2",
                justify="end",
            ),
            justify="end",
        ),
    )


def detalhe_medico() -> rx.Component:
    return rx.cond(
        AuthState.possui_medico_selecionado,
        secao(
            "Detalhes do médico",
            "id_card",
            grade_detalhes(
                item_detalhe("Nome", AuthState.medico_selecionado["nome"]),
                item_detalhe("CRM", AuthState.medico_selecionado["crm"]),
                item_detalhe("Especialidade", AuthState.medico_selecionado["especialidade"]),
                item_detalhe("Telefone", AuthState.medico_selecionado["telefone"]),
            ),
        ),
        rx.fragment(),
    )


def medicos() -> rx.Component:
    return pagina(
        "Médicos",
        "Corpo clínico, CRM e especialidades",
        "stethoscope",
        "/medicos",
        (acoes_tela("medicos", AuthState.carregar_medicos, "medico"),),
        rx.flex(
            rx.cond(
                AuthState.pode_cadastrar_medicos,
                rx.box(
                    formulario_medico(),
                    class_name="gh-form-col",
                ),
            ),
            rx.vstack(
                secao_lista(
                    "Médicos cadastrados",
                    "stethoscope",
                    AuthState.medicos_filtrados,
                    ["Nome", "CRM", "Especialidade", ""],
                    linha_medico,
                    "Nenhum médico encontrado.",
                    "Os médicos cadastrados aparecerão aqui. Use Atualizar para consultar novamente.",
                    "Buscar nesta página por nome, CRM ou especialidade",
                    "A busca considera apenas os registros desta página.",
                    paginacao(
                        "medicos",
                        "medico",
                        AuthState.pagina_medicos,
                        AuthState.total_paginas_medicos,
                        AuthState.texto_paginacao_medicos,
                    ),
                    AuthState.total_registros_medicos,
                ),
                detalhe_medico(),
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
