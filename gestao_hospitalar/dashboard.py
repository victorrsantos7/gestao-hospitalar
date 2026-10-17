"""Página inicial protegida do Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.painel import PERIODOS
from gestao_hospitalar.ui.ajuda import fab_ajuda, modal_ajuda
from gestao_hospitalar.ui.componentes import (
    acoes_tela,
    badge_status,
    carregando,
    data_br,
    estado_vazio,
    icone_destaque,
    mensagem_erro,
    metrica,
    secao,
)
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import NAVEGACAO, pagina, rotulo_papel


def _boas_vindas() -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.heading("Bem-vindo(a)!", size="5", class_name="gh-titulo-pagina"),
            rx.text(
                "Usuário: ",
                AuthState.login,
                " — papel: ",
                AuthState.papel,
                size="2",
                color="var(--gh-muted)",
            ),
            rx.spacer(),
            rx.cond(
                AuthState.painel_atualizado_em != "",
                rx.text(
                    "Indicadores atualizados às ",
                    AuthState.painel_atualizado_em,
                    size="1",
                    color="var(--gh-muted)",
                ),
            ),
            rx.badge(rotulo_papel(), variant="soft", radius="full", size="2"),
            align="center",
            spacing="3",
            width="100%",
            wrap="wrap",
        ),
        class_name="gh-card",
        size="1",
    )


def _alerta(alerta: dict[str, str]) -> rx.Component:
    return rx.callout.root(
        rx.callout.icon(rx.cond(alerta["nivel"] == "blue", icone("info", 16), icone("triangle_alert", 16))),
        rx.callout.text(alerta["texto"]),
        color_scheme=alerta["nivel"],
        variant="soft",
        size="1",
        role="status",
        width="100%",
    )


def _alertas() -> rx.Component:
    return rx.cond(
        AuthState.painel_alertas.length() > 0,
        rx.vstack(
            rx.foreach(AuthState.painel_alertas, _alerta),
            spacing="2",
            width="100%",
        ),
    )


def _internacoes_ativas() -> rx.Component:
    return metrica(
        "Internações ativas",
        AuthState.painel_internacoes_ativas,
        "activity",
        "red",
        compacta=True,
    )


def _indicadores() -> rx.Component:
    return rx.cond(
        AuthState.pode_ver_pacientes | AuthState.pode_ver_medicos | AuthState.pode_ver_atendimentos,
        rx.grid(
            rx.cond(
                AuthState.pode_ver_pacientes,
                metrica(
                    "Pacientes",
                    AuthState.painel_pacientes,
                    "users",
                    "teal",
                    compacta=True,
                ),
            ),
            rx.cond(
                AuthState.pode_ver_medicos,
                metrica(
                    "Médicos",
                    AuthState.painel_medicos,
                    "stethoscope",
                    "blue",
                    compacta=True,
                ),
            ),
            rx.cond(
                AuthState.pode_ver_atendimentos,
                metrica(
                    "Atendimentos",
                    AuthState.painel_atendimentos,
                    "clipboard_list",
                    "violet",
                    compacta=True,
                ),
            ),
            rx.cond(
                AuthState.pode_ver_internacoes & AuthState.pode_ver_atendimentos,
                _internacoes_ativas(),
            ),
            columns="repeat(auto-fit, minmax(190px, 1fr))",
            spacing="3",
            width="100%",
        ),
    )


def _seletor_periodo() -> rx.Component:
    return rx.segmented_control.root(
        *[rx.segmented_control.item(rotulo, value=valor) for valor, rotulo in PERIODOS.items()],
        value=AuthState.painel_periodo,
        on_change=AuthState.set_painel_periodo,
        size="1",
    )


def _grafico_barras() -> rx.Component:
    return rx.recharts.bar_chart(
        rx.recharts.cartesian_grid(vertical=False, stroke_dasharray="3 3"),
        rx.recharts.x_axis(
            data_key="rotulo",
            tick_line=False,
            axis_line=False,
            interval="preserveStartEnd",
            min_tick_gap=12,
            tick={"fontSize": 11, "fill": "#5a7280"},
        ),
        rx.recharts.y_axis(
            allow_decimals=False,
            tick_line=False,
            axis_line=False,
            width=28,
            tick={"fontSize": 11, "fill": "#5a7280"},
        ),
        rx.recharts.graphing_tooltip(),
        rx.recharts.bar(
            data_key="atendimentos",
            name="Atendimentos",
            fill="var(--accent-9)",
            radius=[4, 4, 0, 0],
        ),
        data=AuthState.painel_grafico,
        width="100%",
        height=230,
    )


def _grafico() -> rx.Component:
    sem_serie = AuthState.painel_serie.length() == 0
    return secao(
        "Atendimentos por período",
        "chart_column",
        rx.cond(
            (carregando() | AuthState.painel_graficos_carregando) & sem_serie,
            rx.skeleton(height="230px", width="100%", loading=True),
            rx.cond(
                sem_serie,
                estado_vazio(
                    "chart_column",
                    "Sem dados para o gráfico.",
                    "Use Atualizar para carregar os atendimentos.",
                ),
                _grafico_barras(),
            ),
        ),
        rx.cond(
            AuthState.painel_amostra_parcial,
            rx.text(
                "Gráficos consideram ",
                AuthState.painel_amostra_atendimentos,
                " de ",
                AuthState.painel_atendimentos,
                " atendimentos.",
                size="1",
                color="var(--gh-muted)",
            ),
        ),
        acao=_seletor_periodo(),
    )


def _linha_tipo(item: dict[str, object]) -> rx.Component:
    cor = rx.match(item["tipo"], ("emergencia", "red"), ("retorno", "violet"), "blue")
    return rx.vstack(
        rx.hstack(
            badge_status(item["tipo"], rx.match(item["tipo"], ("emergencia", "Emergência"), ("consulta", "Consulta"), ("retorno", "Retorno"), item["tipo"])),
            rx.spacer(),
            rx.text(item["total"], size="2", weight="bold"),
            rx.text("(", item["pct"], "%)", size="1", color="var(--gh-muted)"),
            align="center",
            width="100%",
        ),
        rx.progress(value=item["pct"].to(int), max=100, size="1", color_scheme=cor, width="100%"),
        spacing="1",
        width="100%",
    )


def _tipos() -> rx.Component:
    sem_serie = AuthState.painel_serie.length() == 0
    return secao(
        "Atendimentos por tipo",
        "layers",
        rx.cond(
            sem_serie,
            rx.cond(
                carregando() | AuthState.painel_graficos_carregando,
                rx.skeleton(height="90px", width="100%", loading=True),
                rx.text("Sem dados no período.", size="2", color="var(--gh-muted)"),
            ),
            rx.vstack(
                rx.foreach(AuthState.painel_tipos, _linha_tipo),
                spacing="3",
                width="100%",
            ),
        ),
        acao=rx.badge(AuthState.painel_periodo_rotulo, variant="soft", radius="full", size="1"),
    )


def _ocupacao() -> rx.Component:
    taxa = AuthState.painel_taxa_ocupacao
    cor = rx.cond(taxa >= 90, "red", rx.cond(taxa >= 75, "amber", "teal"))
    return rx.card(
        rx.vstack(
            rx.hstack(
                icone_destaque("bed_double", "teal"),
                rx.vstack(
                    rx.cond(
                        carregando() & (taxa < 0),
                        rx.skeleton(rx.heading("00%", size="5"), loading=True),
                        rx.heading(
                            rx.cond(taxa < 0, "—", taxa.to_string() + "%"),
                            size="5",
                            weight="bold",
                            class_name="gh-metrica-valor",
                        ),
                    ),
                    rx.text("Ocupação de leitos", size="1", color="var(--gh-muted)"),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                align="center",
                width="100%",
            ),
            rx.progress(
                value=rx.cond(taxa < 0, 0, taxa),
                max=100,
                size="2",
                color_scheme=cor,
                width="100%",
            ),
            rx.cond(
                taxa < 0,
                rx.text("Sem dados de leitos.", size="1", color="var(--gh-muted)"),
                rx.hstack(
                    rx.text("Ocupados: ", AuthState.painel_leitos_ocupados, size="1", weight="medium"),
                    rx.text("Livres: ", AuthState.painel_leitos_livres, size="1", weight="medium"),
                    rx.text("Total: ", AuthState.painel_total_leitos, size="1", color="var(--gh-muted)"),
                    spacing="4",
                    wrap="wrap",
                ),
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        class_name="gh-card gh-metrica",
        size="1",
    )


def _analise() -> rx.Component:
    return rx.cond(
        AuthState.pode_ver_atendimentos,
        rx.box(
            _grafico(),
            rx.vstack(
                rx.cond(AuthState.pode_ver_leitos, _ocupacao()),
                _tipos(),
                spacing="3",
                width="100%",
                align="stretch",
            ),
            class_name="gh-grid-analise",
        ),
        rx.cond(
            AuthState.pode_ver_leitos,
            rx.box(
                _ocupacao(),
                rx.cond(AuthState.pode_ver_internacoes, _internacoes_ativas()),
                class_name="gh-grid-analise",
            ),
        ),
    )


def _evento(evento: dict[str, str]) -> rx.Component:
    return rx.hstack(
        badge_status(evento["tipo"]),
        rx.vstack(
            rx.text(evento["titulo"], size="2", weight="medium"),
            rx.text(evento["detalhe"], size="1", color="var(--gh-muted)"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        rx.text(data_br(evento["data"]), size="1", color="var(--gh-muted)"),
        align="center",
        spacing="3",
        width="100%",
        padding_y="8px",
        class_name="gh-evento",
    )


def _atividade() -> rx.Component:
    return secao(
        "Atividade recente",
        "history",
        rx.cond(
            AuthState.painel_atividade.length() > 0,
            rx.vstack(
                rx.foreach(AuthState.painel_atividade, _evento),
                spacing="0",
                width="100%",
            ),
            rx.cond(
                carregando() | AuthState.painel_graficos_carregando,
                rx.skeleton(height="120px", width="100%", loading=True),
                estado_vazio(
                    "history",
                    "Nenhuma atividade recente.",
                    "Atendimentos, internações e altas aparecerão aqui.",
                ),
            ),
        ),
    )


def _atalho(titulo: str, rota: str, nome_icone: str, permissao: str, texto: str) -> rx.Component:
    return rx.cond(
        getattr(AuthState, permissao),
        rx.link(
            rx.hstack(
                icone(nome_icone, 16, color="var(--accent-11)"),
                rx.text(titulo, size="2", weight="medium"),
                rx.spacer(),
                icone("chevron_right", 14, color="var(--gh-muted)"),
                align="center",
                spacing="3",
                width="100%",
            ),
            href=rota,
            title=texto,
            underline="none",
            class_name="gh-atalho",
        ),
    )


def _acessos() -> rx.Component:
    return secao(
        "Acessos",
        "layout_dashboard",
        rx.vstack(
            *[_atalho(*item) for item in NAVEGACAO[1:]],
            spacing="0",
            width="100%",
            align="stretch",
        ),
    )


def _base() -> rx.Component:
    return rx.cond(
        AuthState.pode_ver_atendimentos | AuthState.pode_ver_internacoes,
        rx.box(_atividade(), _acessos(), class_name="gh-grid-analise"),
        rx.box(_acessos(), max_width="420px", width="100%"),
    )


def dashboard() -> rx.Component:
    """Página interna protegida, destino após login bem-sucedido."""
    return pagina(
        "Painel",
        "Visão geral da operação",
        "layout_dashboard",
        "/dashboard",
        (acoes_tela("painel", AuthState.atualizar_resumo, "painel"),),
        _boas_vindas(),
        mensagem_erro(AuthState.erro_painel),
        _alertas(),
        _indicadores(),
        _analise(),
        _base(),
        modal_ajuda(),
        fab_ajuda(),
    )