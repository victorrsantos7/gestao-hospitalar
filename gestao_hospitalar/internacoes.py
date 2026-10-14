"""Página de leitos e internações."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


def formulario_leito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar leito", size="4", color="#000000"),
            rx.input(
                placeholder="Número do leito",
                value=AuthState.numero_leito,
                on_change=AuthState.set_numero_leito,
                width="100%",
                color="#000000",
            ),
            rx.cond(
                AuthState.erro_leito != "",
                rx.text(AuthState.erro_leito, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_leito != "",
                rx.text(AuthState.sucesso_leito, color="green"),
            ),
            rx.center(
                rx.button(
                    "Cadastrar leito",
                    on_click=AuthState.criar_leito,
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
        padding="1.25em",
        width="100%",
    )


def linha_leito(leito: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.text("Leito ", leito["numero"], weight="bold", color="#000000"),
            rx.spacer(),
            rx.badge(leito["status"]),
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        padding="1em",
        width="100%",
    )


def formulario_internacao() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Registrar internação", size="4", color="#000000"),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Atendimento elegível",
                    width="100%",
                    style={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "border": "1px solid #d7dee6",
                        "&[data-placeholder] .rt-SelectTriggerInner": {
                            "color": "#243b53 !important",
                        },
                    },
                ),
                rx.select.content(
                    rx.foreach(
                        AuthState.opcoes_atendimentos_internaveis,
                        lambda opcao: rx.select.item(opcao, value=opcao),
                    ),
                ),
                value=AuthState.atendimento_id_internacao,
                on_change=AuthState.set_atendimento_id_internacao,
            ),
            rx.select.root(
                rx.select.trigger(
                    placeholder="Leito livre",
                    width="100%",
                    style={
                        "backgroundColor": "white",
                        "color": "#111827",
                        "border": "1px solid #d7dee6",
                        "&[data-placeholder] .rt-SelectTriggerInner": {
                            "color": "#243b53 !important",
                        },
                    },
                ),
                rx.select.content(
                    rx.foreach(
                        AuthState.opcoes_leitos_livres,
                        lambda opcao: rx.select.item(opcao, value=opcao),
                    ),
                ),
                value=AuthState.leito_id_internacao,
                on_change=AuthState.set_leito_id_internacao,
            ),
            rx.input(
                placeholder="Data de entrada: dd/mm/aaaa",
                type="text",
                inputmode="numeric",
                value=AuthState.data_entrada_internacao,
                on_change=AuthState.set_data_entrada_internacao,
                max_length=10,
                width="100%",
                color="#000000",
            ),
            rx.center(
                rx.button(
                    "Registrar internação",
                    on_click=AuthState.criar_internacao,
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
        padding="1.25em",
        width="100%",
    )


def linha_internacao(internacao: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Internação #", internacao["id"], weight="bold", color="#000000"),
            rx.text("Atendimento: ", internacao["atendimento_id"], color="#000000"),
            rx.text("Paciente: ", internacao["paciente_id"], color="#000000"),
            rx.text("Leito: ", internacao["leito_numero"], color="#000000"),
            rx.text("Entrada: ", internacao["data_entrada"], color="#000000"),
            rx.text("Saída: ", internacao["data_saida"], color="#000000"),
            rx.text("Status: ", internacao["status"], color="#000000"),
            rx.cond(
                internacao["status"] == "internado",
                rx.button(
                    "Registrar alta",
                    on_click=AuthState.selecionar_internacao_alta(internacao["id"]),
                    style=_BOTAO_COMPACTO,
                ),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.internacao_id_alta == internacao["id"],
                formulario_alta(),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.pode_ver_transferencias,
                rx.button(
                    "Ver transferências",
                    on_click=AuthState.selecionar_internacao_transferencia(
                        internacao["id"]
                    ),
                    style=_BOTAO_COMPACTO,
                    variant="soft",
                ),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.internacao_id_transferencia == internacao["id"],
                historico_transferencias(),
                rx.fragment(),
            ),
            align="start",
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        padding="1em",
        width="100%",
    )


def formulario_alta() -> rx.Component:
    return rx.cond(
        AuthState.internacao_id_alta != "",
        rx.card(
            rx.vstack(
                rx.heading("Registrar alta", size="4", color="#000000"),
                rx.input(
                    placeholder="Data de saída: dd/mm/aaaa",
                    type="text",
                    inputmode="numeric",
                    value=AuthState.data_saida_internacao,
                    on_change=AuthState.set_data_saida_internacao,
                    max_length=10,
                    width="100%",
                    color="#000000",
                ),
                rx.cond(
                    AuthState.erro_internacao != "",
                    rx.text(AuthState.erro_internacao, color="red"),
                ),
                rx.center(
                    rx.button(
                        "Confirmar alta",
                        on_click=AuthState.registrar_alta,
                        style=_BOTAO_COMPACTO,
                    ),
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def linha_transferencia(transferencia: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Transferência #", transferencia["id"], weight="bold", color="#000000"),
            rx.text("Data: ", transferencia["data_transferencia"], color="#000000"),
            rx.text("Destino: ", transferencia["destino"], color="#000000"),
            rx.text("Motivo: ", transferencia["motivo"], color="#000000"),
            align="start",
            width="100%",
        ),
        width="100%",
    )


def historico_transferencias() -> rx.Component:
    return rx.cond(
        AuthState.internacao_id_transferencia != "",
        rx.card(
            rx.vstack(
                rx.heading("Transferências", size="4", color="#000000"),
                rx.cond(
                    AuthState.erro_transferencia != "",
                    rx.text(AuthState.erro_transferencia, color="red"),
                ),
                rx.cond(
                    AuthState.sucesso_transferencia != "",
                    rx.text(AuthState.sucesso_transferencia, color="green"),
                ),
                rx.cond(
                    AuthState.possui_transferencias,
                    rx.foreach(AuthState.transferencias, linha_transferencia),
                    rx.text("Nenhuma transferência registrada.", color="#000000"),
                ),
                rx.cond(
                    AuthState.internacao_transferencia_ativa,
                    rx.vstack(
                        rx.input(
                            placeholder="Data da transferência: dd/mm/aaaa",
                            type="text",
                            inputmode="numeric",
                            value=AuthState.data_transferencia,
                            on_change=AuthState.set_data_transferencia,
                            max_length=10,
                            width="100%",
                            color="#000000",
                        ),
                        rx.input(
                            placeholder="Setor de destino (ex.: UTI)",
                            value=AuthState.destino_transferencia,
                            on_change=AuthState.set_destino_transferencia,
                            width="100%",
                            color="#000000",
                        ),
                        rx.text_area(
                            placeholder="Motivo da transferência",
                            value=AuthState.motivo_transferencia,
                            on_change=AuthState.set_motivo_transferencia,
                            width="100%",
                            style={
                                "backgroundColor": "white",
                                "color": "#000000",
                                "border": "1px solid #d7dee6",
                            },
                        ),
                        rx.center(
                            rx.button(
                                "Registrar transferência",
                                on_click=AuthState.criar_transferencia,
                                style=_BOTAO_COMPACTO,
                            ),
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.text(
                        "Internação encerrada; novas transferências bloqueadas.",
                        color="#000000",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            background_color="white",
            border="1px solid #c8dbe9",
            border_left="4px solid #2d78b7",
            border_radius="10px",
            padding="1.25em",
            width="100%",
        ),
        rx.fragment(),
    )


def internacoes() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Internações e leitos", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_leitos,
                formulario_leito(),
                rx.fragment(),
            ),
            rx.heading("Leitos", size="5", color="#000000"),
            rx.cond(
                AuthState.possui_leitos,
                rx.foreach(AuthState.leitos, linha_leito),
                rx.text("Nenhum leito cadastrado.", color="#000000"),
            ),
            rx.cond(
                AuthState.pode_cadastrar_internacoes,
                formulario_internacao(),
                rx.fragment(),
            ),
            rx.heading("Internações", size="5", color="#000000"),
            rx.cond(
                AuthState.erro_internacao != "",
                rx.text(AuthState.erro_internacao, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_internacao != "",
                rx.text(AuthState.sucesso_internacao, color="green"),
            ),
            rx.cond(
                AuthState.possui_internacoes,
                rx.foreach(AuthState.internacoes, linha_internacao),
                rx.text("Nenhuma internação encontrada.", color="#000000"),
            ),
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )
