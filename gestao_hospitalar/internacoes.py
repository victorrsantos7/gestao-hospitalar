"""Pagina de leitos e internacoes."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def formulario_leito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar leito", size="4"),
            rx.input(
                placeholder="Numero do leito",
                value=AuthState.numero_leito,
                on_change=AuthState.set_numero_leito,
                width="100%",
            ),
            rx.cond(
                AuthState.erro_leito != "",
                rx.text(AuthState.erro_leito, color="red"),
            ),
            rx.cond(
                AuthState.sucesso_leito != "",
                rx.text(AuthState.sucesso_leito, color="green"),
            ),
            rx.button("Cadastrar leito", on_click=AuthState.criar_leito),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_leito(leito: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.text("Leito ", leito["numero"], weight="bold"),
            rx.spacer(),
            rx.badge(leito["status"]),
            width="100%",
        ),
        width="100%",
    )


def formulario_internacao() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Registrar internacao", size="4"),
            rx.select(
                AuthState.opcoes_atendimentos_internaveis,
                value=AuthState.atendimento_id_internacao,
                on_change=AuthState.set_atendimento_id_internacao,
                placeholder="Atendimento elegivel",
                width="100%",
            ),
            rx.select(
                AuthState.opcoes_leitos_livres,
                value=AuthState.leito_id_internacao,
                on_change=AuthState.set_leito_id_internacao,
                placeholder="Leito livre",
                width="100%",
            ),
            rx.input(
                placeholder="Data de entrada",
                type="date",
                value=AuthState.data_entrada_internacao,
                on_change=AuthState.set_data_entrada_internacao,
                width="100%",
            ),
            rx.button(
                "Registrar internacao",
                on_click=AuthState.criar_internacao,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_internacao(internacao: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Internacao #", internacao["id"], weight="bold"),
            rx.text("Atendimento: ", internacao["atendimento_id"]),
            rx.text("Paciente: ", internacao["paciente_id"]),
            rx.text("Leito: ", internacao["leito_numero"]),
            rx.text("Entrada: ", internacao["data_entrada"]),
            rx.text("Saida: ", internacao["data_saida"]),
            rx.text("Status: ", internacao["status"]),
            rx.cond(
                internacao["status"] == "internado",
                rx.button(
                    "Registrar alta",
                    on_click=AuthState.selecionar_internacao_alta(internacao["id"]),
                ),
                rx.fragment(),
            ),
            align="start",
            width="100%",
        ),
        width="100%",
    )


def formulario_alta() -> rx.Component:
    return rx.cond(
        AuthState.internacao_id_alta != "",
        rx.card(
            rx.vstack(
                rx.heading("Registrar alta", size="4"),
                rx.input(
                    placeholder="Data de saida",
                    type="date",
                    value=AuthState.data_saida_internacao,
                    on_change=AuthState.set_data_saida_internacao,
                    width="100%",
                ),
                rx.cond(
                    AuthState.erro_internacao != "",
                    rx.text(AuthState.erro_internacao, color="red"),
                ),
                rx.button("Confirmar alta", on_click=AuthState.registrar_alta),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def internacoes() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Internacoes e leitos", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_leitos,
                formulario_leito(),
                rx.fragment(),
            ),
            rx.heading("Leitos", size="5"),
            rx.cond(
                AuthState.possui_leitos,
                rx.foreach(AuthState.leitos, linha_leito),
                rx.text("Nenhum leito cadastrado."),
            ),
            rx.cond(
                AuthState.pode_cadastrar_internacoes,
                formulario_internacao(),
                rx.fragment(),
            ),
            rx.heading("Internacoes", size="5"),
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
                rx.text("Nenhuma internacao encontrada."),
            ),
            formulario_alta(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )
