"""Pagina de cadastro e consulta de convenios."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    grade_campos,
    acoes_tela,
    badge_status,
    botao_acao,
    botao_icone,
    confirmar,
    entrada,
    area_texto,
    grade_detalhes,
    item_detalhe,
    mensagem_erro,
    secao,
    secao_lista,
    selecao,
)
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import pagina


def formulario_convenio() -> rx.Component:
    return secao(
        rx.cond(AuthState.editando_convenio, "Editar convênio", "Cadastrar convênio"),
        "shield_check",
        grade_campos(
            entrada(
                "Nome do convênio",
                AuthState.nome_convenio,
                AuthState.set_nome_convenio,
                "Ex.: Saúde Total",
                obrigatorio=True,
                max_length=120,
            ),
            selecao(
                "Tipo de convênio",
                AuthState.tipos_convenio,
                AuthState.tipo_convenio,
                AuthState.set_tipo_convenio,
                "Selecione o tipo",
                obrigatorio=True,
            ),
            area_texto(
                "Cobertura",
                AuthState.cobertura_convenio,
                AuthState.set_cobertura_convenio,
                "Descreva a cobertura",
                obrigatorio=True,
                max_length=500,
            ),
        ),
        mensagem_erro(AuthState.erro_convenio),
        rx.hstack(
            botao_acao(
                rx.cond(AuthState.editando_convenio, "Atualizar convênio", "Cadastrar convênio"),
                AuthState.salvar_convenio,
                "salvar_convenio",
                "convenio",
                "save",
                flex="1",
            ),
            rx.cond(
                AuthState.editando_convenio,
                rx.button(
                    "Cancelar",
                    on_click=AuthState.cancelar_edicao_convenio,
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                    cursor="pointer",
                ),
            ),
            spacing="3",
            width="100%",
        ),
    )


def linha_convenio(convenio: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(rx.text(convenio["nome"], weight="bold")),
        rx.table.cell(badge_status(convenio["tipo"])),
        rx.table.cell(
            rx.text(convenio["cobertura"], size="2", color="var(--gh-muted)"),
            class_name="gh-celula-texto",
        ),
        rx.table.cell(
            rx.hstack(
                botao_icone(
                    "eye",
                    "Ver detalhes",
                    AuthState.consultar_convenio(convenio["id"]),
                    "ver_convenio_" + convenio["id"],
                    "convenio",
                    "teal",
                ),
                rx.cond(
                    AuthState.pode_cadastrar_convenios,
                    rx.hstack(
                        rx.tooltip(
                            rx.icon_button(
                                icone("pencil", 16),
                                on_click=AuthState.editar_convenio(convenio["id"]),
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
                            "Excluir convênio?",
                            "O convênio será removido da lista. Esta ação não pode ser desfeita.",
                            "Excluir",
                            AuthState.excluir_convenio(convenio["id"]),
                            "excluir_convenio_" + convenio["id"],
                            "convenio",
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


def detalhe_convenio() -> rx.Component:
    return rx.cond(
        AuthState.possui_convenio_selecionado,
        secao(
            "Detalhes do convênio",
            "file_text",
            grade_detalhes(
                item_detalhe("Nome", AuthState.convenio_selecionado["nome"]),
                item_detalhe("Tipo", AuthState.convenio_selecionado["tipo"]),
                item_detalhe("Cobertura", AuthState.convenio_selecionado["cobertura"]),
            ),
        ),
        rx.fragment(),
    )


def convenios() -> rx.Component:
    return pagina(
        "Convênios",
        "Planos e coberturas aceitas",
        "shield_check",
        "/convenios",
        (acoes_tela("convenios", AuthState.carregar_convenios, "convenio"),),
        rx.flex(
            rx.cond(
                AuthState.pode_cadastrar_convenios,
                rx.box(
                    formulario_convenio(),
                    class_name="gh-form-col",
                ),
            ),
            rx.vstack(
                secao_lista(
                    "Convênios cadastrados",
                    "shield_check",
                    AuthState.convenios_filtrados,
                    ["Nome", "Tipo", "Cobertura", ""],
                    linha_convenio,
                    "Nenhum convênio encontrado.",
                    "Os convênios cadastrados aparecerão aqui. Use Atualizar para consultar novamente.",
                    "Buscar por nome ou tipo",
                ),
                detalhe_convenio(),
                spacing="4",
                align="stretch",
                flex="2 1 640px",
                min_width="0",
            ),
            wrap="wrap",
            spacing="4",
            align="start",
            width="100%",
        ),
    )
