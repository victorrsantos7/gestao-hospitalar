"""Pagina de cadastro e consulta de atendimentos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.estilos import BOTAO_COMPACTO as _BOTAO_COMPACTO


def _select_atendimento(
    opcoes,
    valor,
    on_change,
    placeholder: str,
    capitalizar: bool = False,
) -> rx.Component:
    item_style = {"textTransform": "capitalize"} if capitalizar else {}
    return rx.select.root(
        rx.select.trigger(
            placeholder=placeholder,
            width="100%",
            style={
                "backgroundColor": "white",
                "color": "#000000",
                "border": "1px solid #d7dee6",
                "textTransform": "capitalize" if capitalizar else "none",
                "&[data-placeholder] .rt-SelectTriggerInner": {
                    "color": "#243b53 !important",
                    "textTransform": "none",
                },
            },
        ),
        rx.select.content(
            rx.foreach(
                opcoes,
                lambda opcao: rx.select.item(opcao, value=opcao, style=item_style),
            ),
        ),
        value=valor,
        on_change=on_change,
    )


def formulario_atendimento() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar atendimento", size="5", color="#000000"),
            _select_atendimento(
                AuthState.opcoes_pacientes_atendimento,
                AuthState.paciente_id_atendimento,
                AuthState.set_paciente_id_atendimento,
                "Paciente",
            ),
            _select_atendimento(
                AuthState.opcoes_medicos_atendimento,
                AuthState.medico_id_atendimento,
                AuthState.set_medico_id_atendimento,
                "Médico",
            ),
            _select_atendimento(
                AuthState.opcoes_convenios_atendimento,
                AuthState.convenio_id_atendimento,
                AuthState.set_convenio_id_atendimento,
                "Convênio (opcional)",
            ),
            rx.input(
                placeholder="Data do atendimento: dd/mm/aaaa",
                type="text",
                inputmode="numeric",
                value=AuthState.data_atendimento,
                on_change=AuthState.set_data_atendimento,
                max_length=10,
                width="100%",
                color="#000000",
            ),
            rx.text_area(
                placeholder="Motivo do atendimento",
                value=AuthState.motivo_atendimento,
                on_change=AuthState.set_motivo_atendimento,
                max_length=500,
                width="100%",
                style={
                    "backgroundColor": "white",
                    "color": "#000000",
                    "border": "1px solid #d7dee6",
                },
            ),
            _select_atendimento(
                AuthState.tipos_atendimento,
                AuthState.tipo_atendimento,
                AuthState.set_tipo_atendimento,
                "Tipo de atendimento",
                capitalizar=True,
            ),
            rx.cond(
                AuthState.sucesso_atendimento != "",
                rx.text(AuthState.sucesso_atendimento, color="green"),
            ),
            rx.center(
                rx.button(
                    "Cadastrar",
                    on_click=AuthState.criar_atendimento,
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


def linha_atendimento(atendimento: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        "Atendimento #",
                        atendimento["id"],
                        color="#000000",
                        weight="bold",
                    ),
                    rx.text("Paciente: ", atendimento["paciente_nome"], color="#000000"),
                    rx.text("Médico: ", atendimento["medico_nome"], color="#000000"),
                    rx.text("Convênio: ", atendimento["convenio_nome"], color="#000000"),
                    rx.text("Data: ", atendimento["data_atendimento"], color="#000000"),
                    rx.text(
                        "Tipo: ",
                        atendimento["tipo"],
                        color="#000000",
                        style={"textTransform": "capitalize"},
                    ),
                    align="start",
                    flex="1",
                ),
                rx.button(
                    "Ver detalhes",
                    on_click=AuthState.consultar_atendimento(atendimento["id"]),
                    style=_BOTAO_COMPACTO,
                ),
                width="100%",
                align="center",
            ),
            rx.cond(
                AuthState.possui_atendimento_selecionado,
                rx.cond(
                    AuthState.atendimento_selecionado["id"] == atendimento["id"],
                    detalhe_atendimento(),
                    rx.fragment(),
                ),
                rx.fragment(),
            ),
            spacing="3",
            width="100%",
        ),
        background_color="white",
        border="1px solid #dce6ef",
        border_radius="10px",
        padding="1em",
        width="100%",
    )


def formulario_diagnostico() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Cadastrar diagnóstico", size="4", color="#000000"),
            rx.input(
                placeholder="Descrição",
                value=AuthState.descricao_diagnostico,
                on_change=AuthState.set_descricao_diagnostico,
                width="100%",
                color="#000000",
            ),
            rx.input(
                placeholder="Código CID (opcional)",
                value=AuthState.codigo_cid_diagnostico,
                on_change=AuthState.set_codigo_cid_diagnostico,
                width="100%",
                color="#000000",
            ),
            rx.input(
                placeholder="Data do diagnóstico: dd/mm/aaaa",
                type="text",
                inputmode="numeric",
                value=AuthState.data_diagnostico,
                on_change=AuthState.set_data_diagnostico,
                max_length=10,
                width="100%",
                color="#000000",
            ),
            rx.cond(
                AuthState.sucesso_diagnostico != "",
                rx.text(AuthState.sucesso_diagnostico, color="green"),
            ),
            rx.center(
                rx.button(
                    "Cadastrar diagnóstico",
                    on_click=AuthState.criar_diagnostico,
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


def linha_diagnostico(diagnostico: dict[str, str]) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Diagnóstico #", diagnostico["id"], weight="bold", color="#000000"),
            rx.text("Descrição: ", diagnostico["descricao"], color="#000000"),
            rx.text("Código CID: ", diagnostico["codigo_cid"], color="#000000"),
            rx.text("Data: ", diagnostico["data_diagnostico"], color="#000000"),
            align="start",
            width="100%",
        ),
        background_color="#f8fbfd",
        border="1px solid #dce6ef",
        border_radius="8px",
        padding="1em",
        width="100%",
    )


def diagnosticos_atendimento() -> rx.Component:
    return rx.cond(
        AuthState.pode_ver_diagnosticos,
        rx.vstack(
            rx.heading("Diagnósticos", size="4", color="#000000"),
            rx.cond(
                AuthState.erro_diagnostico != "",
                rx.text(AuthState.erro_diagnostico, color="red"),
            ),
            rx.cond(
                AuthState.possui_diagnosticos,
                rx.foreach(AuthState.diagnosticos, linha_diagnostico),
                    rx.text("Nenhum diagnóstico encontrado."),
            ),
            formulario_diagnostico(),
            align="start",
            width="100%",
        ),
        rx.fragment(),
    )


def detalhe_atendimento() -> rx.Component:
    return rx.cond(
        AuthState.possui_atendimento_selecionado,
        rx.box(
            rx.vstack(
            rx.heading("Detalhes do atendimento", size="5", color="#000000"),
            rx.text("Paciente: ", AuthState.atendimento_selecionado["paciente_nome"], color="#000000"),
            rx.text("Médico: ", AuthState.atendimento_selecionado["medico_nome"], color="#000000"),
            rx.text("Convênio: ", AuthState.atendimento_selecionado["convenio_nome"], color="#000000"),
                rx.text(
                    "Data: ",
                    AuthState.atendimento_selecionado["data_atendimento"],
                    color="#000000",
                ),
                rx.text(
                    "Tipo: ",
                    AuthState.atendimento_selecionado["tipo"],
                    color="#000000",
                    style={"textTransform": "capitalize"},
                ),
                rx.text("Motivo: ", AuthState.atendimento_selecionado["motivo"], color="#000000"),
                diagnosticos_atendimento(),
                align="start",
            ),
            background_color="#f4f8fb",
            border="1px solid #c8dbe9",
            border_left="4px solid #2d78b7",
            border_radius="8px",
            padding="1.25em",
            width="100%",
        ),
        rx.fragment(),
    )


def atendimentos() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(
                rx.heading("Atendimentos", size="7", color="#000000"),
                rx.spacer(),
                rx.button("Voltar", on_click=rx.redirect("/dashboard"), variant="outline"),
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
            spacing="4",
            width="min(100%, 64em)",
            padding="2em",
        ),
        background="#f4f8fb",
        min_height="100vh",
        width="100%",
    )
