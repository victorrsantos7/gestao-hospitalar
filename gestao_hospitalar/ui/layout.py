"""Layout compartilhado: barra lateral, barra superior e navegação por papel."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import cabecalho_pagina
from gestao_hospitalar.ui.icones import icone, marca

NAVEGACAO = (
    ("Painel", "/dashboard", "layout_dashboard", None, "Visão geral da operação."),
    ("Pacientes", "/pacientes", "users", "pode_ver_pacientes", "Cadastre e consulte pacientes."),
    ("Médicos", "/medicos", "stethoscope", "pode_ver_medicos", "Corpo clínico e especialidades."),
    ("Convênios", "/convenios", "shield_check", "pode_ver_convenios", "Planos e coberturas aceitas."),
    ("Atendimentos", "/atendimentos", "clipboard_list", "pode_ver_atendimentos", "Consultas, retornos e diagnósticos."),
    ("Internações e leitos", "/internacoes", "bed_double", "pode_ver_internacoes", "Ocupação, altas e transferências."),
    ("Histórico do paciente", "/historico", "history", "pode_ver_historico", "Linha do tempo consolidada."),
    ("Relatórios", "/relatorios", "chart_no_axes_combined", "pode_ver_relatorios", "Ocupação e internações ativas."),
)

def _item_nav(rotulo: str, rota: str, nome_icone: str, permissao: str | None, rota_atual: str) -> rx.Component:
    ativo = rota == rota_atual
    item = rx.link(
        icone(nome_icone, 18),
        rx.text(rotulo, size="2", weight="medium"),
        href=rota,
        underline="none",
        class_name="gh-nav-item gh-nav-item--ativo" if ativo else "gh-nav-item",
    )
    if permissao is None:
        return item
    return rx.cond(getattr(AuthState, permissao), item)


def rotulo_papel() -> rx.Component:
    return rx.match(
        AuthState.papel,
        ("recepcionista", "Recepção"),
        ("medico", "Médico(a)"),
        ("enfermagem_gestao", "Enfermagem e gestão"),
        ("admin", "Administrador(a)"),
        "—",
    )


def _usuario() -> rx.Component:
    return rx.hstack(
        rx.center(AuthState.iniciais_usuario, class_name="gh-avatar"),
        rx.vstack(
            rx.text(AuthState.login, size="2", weight="bold", class_name="gh-usuario-nome"),
            rx.text(rotulo_papel(), size="1", class_name="gh-usuario-papel"),
            spacing="0",
            align="start",
            min_width="0",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _conteudo_nav(rota_atual: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            marca(38),
            rx.vstack(
                rx.text("Gestão Hospitalar", weight="bold", size="3", class_name="gh-marca-nome"),
                rx.text("Jornada do paciente", size="1", class_name="gh-marca-sub"),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
        ),
        rx.text("MENU", class_name="gh-nav-secao"),
        rx.vstack(
            *[_item_nav(rotulo, rota, nome_icone, permissao, rota_atual) for rotulo, rota, nome_icone, permissao, _ in NAVEGACAO],
            spacing="1",
            width="100%",
            align="stretch",
        ),
        rx.spacer(),
        rx.box(class_name="gh-divisor"),
        _usuario(),
        rx.button(
            icone("log_out", 16),
            "Sair",
            on_click=AuthState.do_logout,
            variant="soft",
            size="3",
            width="100%",
            cursor="pointer",
            class_name="gh-btn-sair",
        ),
        spacing="4",
        align="start",
        height="100%",
        width="100%",
    )


def _barra_mobile(rota_atual: str) -> rx.Component:
    return rx.hstack(
        rx.drawer.root(
            rx.drawer.trigger(
                rx.icon_button(
                    icone("menu", 20),
                    variant="ghost",
                    size="3",
                    aria_label="Abrir menu",
                    cursor="pointer",
                )
            ),
            rx.drawer.overlay(z_index="40"),
            rx.drawer.portal(
                rx.drawer.content(
                    rx.box(_conteudo_nav(rota_atual), class_name="gh-drawer-conteudo"),
                    top="0",
                    left="0",
                    bottom="0",
                    height="100%",
                    width="280px",
                    z_index="50",
                    outline="none",
                )
            ),
            direction="left",
        ),
        marca(30),
        rx.text("Gestão Hospitalar", weight="bold", size="3"),
        rx.spacer(),
        rx.center(AuthState.iniciais_usuario, class_name="gh-avatar gh-avatar--claro"),
        spacing="3",
        align="center",
        class_name="gh-barra-mobile",
    )


def pagina(
    titulo: str,
    descricao: str,
    icone_nome: str,
    rota: str,
    acoes: tuple,
    *filhos,
) -> rx.Component:
    """Página interna: navegação persistente (item ativo estático), cabeçalho e conteúdo."""
    return rx.box(
        rx.box(_conteudo_nav(rota), class_name="gh-sidebar"),
        rx.box(
            _barra_mobile(rota),
            rx.vstack(
                cabecalho_pagina(titulo, descricao, icone_nome, *acoes),
                *filhos,
                spacing="4",
                align="stretch",
                width="100%",
                class_name="gh-conteudo",
            ),
            class_name="gh-main",
        ),
        class_name="gh-shell",
    )
