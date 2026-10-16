"""Pagina de cadastro e consulta de atendimentos."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    acoes_tela,
    area_texto,
    badge_status,
    botao_acao,
    botao_icone,
    data_br,
    entrada,
    estado_vazio,
    grade_detalhes,
    item_detalhe,
    mensagem_erro,
    secao,
    secao_lista,
    selecao,
)
from gestao_hospitalar.ui.layout import pagina


def formulario_atendimento() -> rx.Component:
    return secao(
        "Cadastrar atendimento",
        "clipboard_plus",
        selecao(
            "Paciente",
            AuthState.opcoes_pacientes_atendimento,
            AuthState.paciente_id_atendimento,
            AuthState.set_paciente_id_atendimento,
            "Selecione o paciente",
            obrigatorio=True,
        ),
        selecao(
            "Médico",
            AuthState.opcoes_medicos_atendimento,
            AuthState.medico_id_atendimento,
            AuthState.set_medico_id_atendimento,
            "Selecione o médico",
            obrigatorio=True,
        ),
        selecao(
            "Convênio",
            AuthState.opcoes_convenios_atendimento,
            AuthState.convenio_id_atendimento,
            AuthState.set_convenio_id_atendimento,
            "Convênio (opcional)",
        ),
        entrada(
            "Data do atendimento",
            AuthState.data_atendimento,
            AuthState.set_data_atendimento,
            obrigatorio=True,
            type="date",
        ),
        selecao(
            "Tipo de atendimento",
            AuthState.tipos_atendimento,
            AuthState.tipo_atendimento,
            AuthState.set_tipo_atendimento,
            "Selecione o tipo",
            obrigatorio=True,
        ),
        area_texto(
            "Motivo do atendimento",
            AuthState.motivo_atendimento,
            AuthState.set_motivo_atendimento,
            "Descreva o motivo",
            obrigatorio=True,
            max_length=500,
        ),
        mensagem_erro(AuthState.erro_atendimento),
        botao_acao(
            "Cadastrar atendimento",
            AuthState.criar_atendimento,
            "criar_atendimento",
            "atendimento",
            "plus",
            width="100%",
        ),
    )


def linha_atendimento(atendimento: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(rx.text("#", atendimento["id"], weight="bold")),
        rx.table.cell(atendimento["paciente_nome"]),
        rx.table.cell(atendimento["medico_nome"]),
        rx.table.cell(atendimento["convenio_nome"]),
        rx.table.cell(data_br(atendimento["data_atendimento"])),
        rx.table.cell(badge_status(atendimento["tipo"])),
        rx.table.cell(
            botao_icone(
                "eye",
                "Ver detalhes",
                AuthState.consultar_atendimento(atendimento["id"]),
                "ver_atendimento_" + atendimento["id"],
                "atendimento",
                "teal",
            ),
            justify="end",
        ),
    )


def formulario_diagnostico() -> rx.Component:
    return rx.vstack(
        rx.heading("Novo diagnóstico", size="2"),
        entrada(
            "Descrição",
            AuthState.descricao_diagnostico,
            AuthState.set_descricao_diagnostico,
            "Descreva o diagnóstico",
            obrigatorio=True,
        ),
        entrada(
            "Código CID",
            AuthState.codigo_cid_diagnostico,
            AuthState.set_codigo_cid_diagnostico,
            "Ex.: J06.9 (opcional)",
        ),
        entrada(
            "Data do diagnóstico",
            AuthState.data_diagnostico,
            AuthState.set_data_diagnostico,
            obrigatorio=True,
            type="date",
        ),
        botao_acao(
            "Cadastrar diagnóstico",
            AuthState.criar_diagnostico,
            "criar_diagnostico",
            "diagnostico",
            "plus",
            width="100%",
        ),
        spacing="3",
        width="100%",
        align="stretch",
    )


def linha_diagnostico(diagnostico: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text(diagnostico["descricao"], weight="bold", size="2"),
            rx.spacer(),
            rx.cond(
                diagnostico["codigo_cid"] != "",
                rx.badge(diagnostico["codigo_cid"], variant="soft", radius="full"),
            ),
            width="100%",
            align="center",
        ),
        rx.text(data_br(diagnostico["data_diagnostico"]), size="2", color="var(--gh-muted)"),
        padding="12px 14px",
        border="1px solid var(--gh-border)",
        border_radius="10px",
        width="100%",
    )


def diagnosticos_atendimento() -> rx.Component:
    return rx.cond(
        AuthState.pode_ver_diagnosticos,
        rx.vstack(
            rx.divider(),
            rx.heading("Diagnósticos", size="4"),
            mensagem_erro(AuthState.erro_diagnostico),
            rx.cond(
                AuthState.possui_diagnosticos,
                rx.vstack(
                    rx.foreach(AuthState.diagnosticos, linha_diagnostico),
                    spacing="2",
                    width="100%",
                ),
                estado_vazio(
                    "clipboard_list",
                    "Nenhum diagnóstico encontrado.",
                    "Cadastre o primeiro diagnóstico deste atendimento abaixo.",
                ),
            ),
            formulario_diagnostico(),
            spacing="4",
            width="100%",
            align="stretch",
        ),
        rx.fragment(),
    )


def detalhe_atendimento() -> rx.Component:
    return rx.cond(
        AuthState.possui_atendimento_selecionado,
        secao(
            "Detalhes do atendimento",
            "file_text",
            grade_detalhes(
                item_detalhe("Paciente", AuthState.atendimento_selecionado["paciente_nome"]),
                item_detalhe("Médico", AuthState.atendimento_selecionado["medico_nome"]),
                item_detalhe("Convênio", AuthState.atendimento_selecionado["convenio_nome"]),
                item_detalhe("Data", data_br(AuthState.atendimento_selecionado["data_atendimento"])),
                item_detalhe("Tipo", AuthState.atendimento_selecionado["tipo"]),
                item_detalhe("Motivo", AuthState.atendimento_selecionado["motivo"]),
            ),
            diagnosticos_atendimento(),
        ),
        rx.fragment(),
    )


def atendimentos() -> rx.Component:
    return pagina(
        "Atendimentos",
        "Consultas, retornos e diagnósticos",
        "clipboard_list",
        "/atendimentos",
        (acoes_tela("atendimentos", AuthState.carregar_atendimentos, "atendimento"),),
        rx.flex(
            rx.cond(
                AuthState.pode_cadastrar_atendimentos,
                rx.box(
                    formulario_atendimento(),
                    flex="1 1 300px",
                    max_width="340px",
                    min_width="0",
                ),
            ),
            rx.vstack(
                rx.cond(
                    AuthState.pode_cadastrar_atendimentos,
                    rx.fragment(),
                    mensagem_erro(AuthState.erro_atendimento),
                ),
                secao_lista(
                    "Atendimentos registrados",
                    "clipboard_list",
                    AuthState.atendimentos_filtrados,
                    ["Nº", "Paciente", "Médico", "Convênio", "Data", "Tipo", ""],
                    linha_atendimento,
                    "Nenhum atendimento encontrado.",
                    "Os atendimentos registrados aparecerão aqui. Use Atualizar para consultar novamente.",
                    "Buscar por paciente, médico ou data",
                ),
                detalhe_atendimento(),
                spacing="4",
                align="stretch",
                flex="2 1 520px",
                min_width="0",
            ),
            wrap="wrap",
            spacing="4",
            align="start",
            width="100%",
        ),
    )
