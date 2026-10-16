"""Página de relatórios de ocupação e internações ativas."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.relatorios_calculo import InternacaoAtiva
from gestao_hospitalar.ui.componentes import (
    acoes_tela,
    data_br,
    estado_vazio,
    metrica,
    secao,
)
from gestao_hospitalar.ui.layout import pagina


def linha_internacao_ativa(internacao: InternacaoAtiva) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text("Leito ", internacao["leito_numero"], weight="bold", size="2"),
            rx.text(
                "Entrada: ",
                data_br(internacao["data_entrada"]),
                size="2",
                color="var(--gh-muted)",
            ),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.badge(
            internacao["dias_internado"],
            " dia(s)",
            variant="soft",
            color_scheme="blue",
            radius="full",
        ),
        width="100%",
        align="center",
        padding="12px 14px",
        border="1px solid var(--gh-border)",
        border_radius="10px",
    )


def relatorios() -> rx.Component:
    return pagina(
        "Relatórios",
        "Ocupação de leitos e internações ativas",
        "chart_no_axes_combined",
        "/relatorios",
        (acoes_tela("relatorios", AuthState.carregar_relatorios, "relatorio"),),
        rx.grid(
            metrica(
                "Leitos livres",
                AuthState.resumo_leitos["livres"],
                "bed",
                "green",
            ),
            metrica(
                "Leitos ocupados",
                AuthState.resumo_leitos["ocupados"],
                "bed_double",
                "amber",
            ),
            metrica(
                "Total de leitos",
                AuthState.resumo_leitos["total"],
                "hospital",
                "teal",
            ),
            columns="repeat(auto-fit, minmax(180px, 1fr))",
            spacing="4",
            width="100%",
        ),
        secao(
            "Internações ativas",
            "activity",
            rx.cond(
                AuthState.possui_internacoes_ativas,
                rx.vstack(
                    rx.foreach(
                        AuthState.lista_internacoes_ativas,
                        linha_internacao_ativa,
                    ),
                    spacing="2",
                    width="100%",
                ),
                estado_vazio(
                    "bed_double",
                    "Nenhuma internação ativa.",
                    "As internações em andamento aparecerão aqui.",
                ),
            ),
        ),
    )
