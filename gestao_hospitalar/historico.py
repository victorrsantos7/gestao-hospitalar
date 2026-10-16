"""Página de histórico consolidado do paciente."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    acoes_tela,
    botao_acao,
    data_br,
    estado_vazio,
    mensagem_erro,
    secao,
    selecao,
)
from gestao_hospitalar.ui.layout import pagina


def linha_evento(evento: dict[str, str]) -> rx.Component:
    cor = rx.match(
        evento["tipo"],
        ("atendimento", "blue"),
        ("diagnóstico", "violet"),
        ("internação", "amber"),
        ("transferência", "cyan"),
        "gray",
    )
    return rx.box(
        rx.box(class_name="gh-timeline-ponto"),
        rx.vstack(
            rx.hstack(
                rx.badge(evento["tipo"], color_scheme=cor, variant="soft", radius="full", class_name="gh-badge"),
                rx.text(data_br(evento["data"]), size="2", weight="medium", color="var(--gh-muted)"),
                spacing="3",
                align="center",
            ),
            rx.heading(evento["titulo"], size="2"),
            rx.text(evento["detalhes"], size="2", color="var(--gh-muted)"),
            spacing="1",
            align="start",
        ),
        class_name="gh-timeline-item",
    )


def historico() -> rx.Component:
    return pagina(
        "Histórico do paciente",
        "Linha do tempo consolidada de atendimentos, internações e transferências",
        "history",
        "/historico",
        (acoes_tela("historico", AuthState.atualizar_historico, "historico"),),
        secao(
            "Consultar histórico",
            "user_round_search",
            selecao(
                "Paciente",
                AuthState.opcoes_pacientes_historico,
                AuthState.paciente_id_historico,
                AuthState.set_paciente_id_historico,
                "Selecione o paciente",
                obrigatorio=True,
            ),
            mensagem_erro(AuthState.erro_historico),
            botao_acao(
                "Consultar histórico",
                AuthState.consultar_historico,
                "consultar_historico",
                "historico",
                "search",
                width="100%",
            ),
            max_width="640px",
        ),
        rx.cond(
            AuthState.possui_historico_eventos,
            secao(
                "Linha do tempo",
                "history",
                rx.box(
                    rx.foreach(AuthState.historico_eventos, linha_evento),
                    class_name="gh-timeline",
                ),
                acao=rx.badge(
                    AuthState.historico_eventos.length(),
                    variant="soft",
                    radius="full",
                    size="2",
                ),
            ),
            rx.card(
                estado_vazio(
                    "history",
                    "Nenhum evento encontrado.",
                    "Selecione um paciente e consulte o histórico para ver a linha do tempo.",
                ),
                class_name="gh-card",
                size="2",
            ),
        ),
    )
