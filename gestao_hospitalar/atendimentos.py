"""Pagina de cadastro e consulta de atendimentos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState


def formulario_atendimento() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar atendimento", size="5"),
            rx.select(
                AuthState.opcoes_pacientes_atendimento,
                value=AuthState.paciente_id_atendimento,
                on_change=AuthState.set_paciente_id_atendimento,
                placeholder="Paciente",
                width="100%",
            ),
            rx.select(
                AuthState.opcoes_medicos_atendimento,
                value=AuthState.medico_id_atendimento,
                on_change=AuthState.set_medico_id_atendimento,
                placeholder="Medico",
                width="100%",
            ),
            rx.select(
                AuthState.opcoes_convenios_atendimento,
                value=AuthState.convenio_id_atendimento,
                on_change=AuthState.set_convenio_id_atendimento,
                placeholder="Convenio (opcional)",
                width="100%",
            ),
            rx.input(
                placeholder="Data do atendimento",
                type="date",
                value=AuthState.data_atendimento,
                on_change=AuthState.set_data_atendimento,
                width="100%",
            ),
            rx.text_area(
                placeholder="Motivo do atendimento",
                value=AuthState.motivo_atendimento,
                on_change=AuthState.set_motivo_atendimento,
                max_length=500,
                width="100%",
            ),
            rx.select(
                AuthState.tipos_atendimento,
                value=AuthState.tipo_atendimento,
                on_change=AuthState.set_tipo_atendimento,
                placeholder="Tipo de atendimento",
                width="100%",
            ),
            rx.cond(
                AuthState.sucesso_atendimento != "",
                rx.text(AuthState.sucesso_atendimento, color="green"),
            ),
            rx.button(
                "Cadastrar",
                on_click=AuthState.criar_atendimento,
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
    )


def linha_atendimento(atendimento: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(
                    "Atendimento #",
                    atendimento["id"],
                    weight="bold",
                ),
                rx.text("Paciente: ", atendimento["paciente_nome"]),
                rx.text("Medico: ", atendimento["medico_nome"]),
                rx.text("Convenio: ", atendimento["convenio_nome"]),
                rx.text("Data: ", atendimento["data_atendimento"]),
                rx.text("Tipo: ", atendimento["tipo"]),
                align="start",
                flex="1",
            ),
            rx.button(
                "Ver detalhes",
                on_click=AuthState.consultar_atendimento(atendimento["id"]),
            ),
            width="100%",
            align="center",
        ),
        width="100%",
    )


def detalhe_atendimento() -> rx.Component:
    return rx.cond(
        AuthState.possui_atendimento_selecionado,
        rx.card(
            rx.vstack(
                rx.heading("Detalhes do atendimento", size="5"),
                rx.text("Paciente: ", AuthState.atendimento_selecionado["paciente_nome"]),
                rx.text("Medico: ", AuthState.atendimento_selecionado["medico_nome"]),
                rx.text("Convenio: ", AuthState.atendimento_selecionado["convenio_nome"]),
                rx.text(
                    "Data: ",
                    AuthState.atendimento_selecionado["data_atendimento"],
                ),
                rx.text("Tipo: ", AuthState.atendimento_selecionado["tipo"]),
                rx.text("Motivo: ", AuthState.atendimento_selecionado["motivo"]),
                align="start",
            ),
            width="100%",
        ),
        rx.fragment(),
    )


def atendimentos() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Atendimentos", size="7"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard")),
                width="100%",
            ),
            rx.cond(
                AuthState.pode_cadastrar_atendimentos,
                formulario_atendimento(),
                rx.fragment(),
            ),
            rx.cond(
                AuthState.erro_atendimento != "",
                rx.text(AuthState.erro_atendimento, color="red"),
            ),
            rx.cond(
                AuthState.possui_atendimentos,
                rx.foreach(AuthState.atendimentos, linha_atendimento),
                rx.text("Nenhum atendimento encontrado."),
            ),
            detalhe_atendimento(),
            spacing="4",
            width="min(100%, 56em)",
            padding="2em",
        ),
        min_height="100vh",
        width="100%",
    )
