"""Página de leitos e internações."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def formulario_leito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar leito", size="4"),
            rx.input(
                placeholder="Número do leito",
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
            rx.heading("Registrar internação", size="4"),
            rx.select(
                AuthState.opcoes_atendimentos_internaveis,
                value=AuthState.atendimento_id_internacao,
                on_change=AuthState.set_atendimento_id_internacao,
                placeholder="Atendimento elegível",
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
                "Registrar internação",
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
            rx.text("Internação #", internacao["id"], weight="bold"),
            rx.text("Atendimento: ", internacao["atendimento_id"]),
            rx.text("Paciente: ", internacao["paciente_id"]),
            rx.text("Leito: ", internacao["leito_numero"]),
            rx.text("Entrada: ", internacao["data_entrada"]),
            rx.text("Saída: ", internacao["data_saida"]),
            rx.text("Status: ", internacao["status"]),
            rx.cond(
                internacao["status"] == "internado",
                rx.button(
                    "Registrar alta",
                    on_click=AuthState.selecionar_internacao_alta(internacao["id"]),
                ),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.pode_ver_transferencias,
                rx.button(
                    "Ver transferências",
                    on_click=AuthState.selecionar_internacao_transferencia(
                        internacao["id"]
                    ),
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
                    placeholder="Data de saída",
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


def linha_transferencia(transferencia: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Transferência #", transferencia["id"], weight="bold"),
            rx.text("Data: ", transferencia["data_transferencia"]),
            rx.text("Destino: ", transferencia["destino"]),
            rx.text("Motivo: ", transferencia["motivo"]),
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
                rx.heading("Transferências", size="4"),
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
                    rx.text("Nenhuma transferência registrada."),
                ),
                rx.cond(
                    AuthState.internacao_transferencia_ativa,
                    rx.vstack(
                        rx.input(
                            placeholder="Data da transferência",
                            type="date",
                            value=AuthState.data_transferencia,
                            on_change=AuthState.set_data_transferencia,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Setor de destino (ex.: UTI)",
                            value=AuthState.destino_transferencia,
                            on_change=AuthState.set_destino_transferencia,
                            width="100%",
                        ),
                        rx.text_area(
                            placeholder="Motivo da transferência",
                            value=AuthState.motivo_transferencia,
                            on_change=AuthState.set_motivo_transferencia,
                            width="100%",
                        ),
                        rx.button(
                            "Registrar transferência",
                            on_click=AuthState.criar_transferencia,
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    rx.text("Internação encerrada; novas transferências bloqueadas."),
                ),
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
                rx.heading("Internações e leitos", size="7"),
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
            rx.heading("Internações", size="5"),
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
                rx.text("Nenhuma internação encontrada."),
            ),
            formulario_alta(),
            historico_transferencias(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )
