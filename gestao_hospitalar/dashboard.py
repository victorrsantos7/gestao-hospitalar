"""Página inicial protegida do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import acoes_tela, mensagem_erro, metrica, secao
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import NAVEGACAO, pagina, rotulo_papel

def _atalho(titulo: str, rota: str, nome_icone: str, permissao: str, texto: str) -> rx.Component:
    return rx.cond(
        getattr(AuthState, permissao),
        rx.link(
            rx.card(
                rx.hstack(
                    rx.center(icone(nome_icone, 20), class_name="gh-icone-secao"),
                    rx.vstack(
                        rx.text(titulo, weight="bold", size="2"),
                        rx.text(texto, size="2", color="var(--gh-muted)"),
                        spacing="0",
                        align="start",
                    ),
                    rx.spacer(),
                    icone("chevron_right", 18, color="var(--gh-muted)"),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                class_name="gh-card gh-metrica",
                size="2",
            ),
            href=rota,
            underline="none",
            color="inherit",
        ),
    )


def _indicadores() -> rx.Component:
    return rx.grid(
        rx.cond(AuthState.pode_ver_pacientes, metrica("Pacientes", AuthState.painel_pacientes, "users", "teal", "Cadastrados")),
        rx.cond(AuthState.pode_ver_medicos, metrica("Médicos", AuthState.painel_medicos, "stethoscope", "blue", "No corpo clínico")),
        rx.cond(AuthState.pode_ver_atendimentos, metrica("Atendimentos", AuthState.painel_atendimentos, "clipboard_list", "violet", "Registrados")),
        rx.cond(AuthState.pode_ver_leitos, metrica("Leitos livres", AuthState.painel_leitos_livres, "bed_double", "green", "Disponíveis agora")),
        rx.cond(AuthState.pode_ver_leitos, metrica("Leitos ocupados", AuthState.painel_leitos_ocupados, "bed_double", "amber", "Em uso")),
        rx.cond(AuthState.pode_ver_internacoes, metrica("Internações ativas", AuthState.painel_internacoes_ativas, "activity", "red", "Pacientes internados")),
        columns="repeat(auto-fit, minmax(300px, 1fr))",
        spacing="4",
        width="100%",
    )


def dashboard() -> rx.Component:
    """Página interna protegida, destino após login bem-sucedido."""
    return pagina(
        "Painel",
        "Visão geral da operação",
        "layout_dashboard",
        "/dashboard",
        (acoes_tela("painel", AuthState.atualizar_resumo, "painel"),),
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.heading("Bem-vindo(a)!", size="7", class_name="gh-titulo-pagina"),
                    rx.text(
                        "Usuário: ",
                        AuthState.login,
                        " — papel: ",
                        AuthState.papel,
                        size="2",
                        color="var(--gh-muted)",
                    ),
                    rx.cond(
                        AuthState.painel_atualizado_em != "",
                        rx.text(
                            "Indicadores atualizados às ",
                            AuthState.painel_atualizado_em,
                            size="1",
                            color="var(--gh-muted)",
                        ),
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(rotulo_papel(), variant="soft", radius="full", size="2"),
                align="center",
                width="100%",
                wrap="wrap",
            ),
            class_name="gh-card",
            size="2",
        ),
        mensagem_erro(AuthState.erro_painel),
        _indicadores(),
        secao(
            "Acessos disponíveis",
            "layout_dashboard",
            rx.grid(
                *[_atalho(*item) for item in NAVEGACAO[1:]],
                columns="repeat(auto-fit, minmax(300px, 1fr))",
                spacing="3",
                width="100%",
            ),
            descricao="Os módulos exibidos dependem do seu papel.",
        ),
    )
