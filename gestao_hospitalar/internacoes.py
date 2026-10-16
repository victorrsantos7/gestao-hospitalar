"""Página de leitos e internações."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.componentes import (
    grade_campos,
    bloqueado,
    acoes_tela,
    area_texto,
    badge_status,
    botao_acao,
    botao_icone,
    confirmar,
    data_br,
    entrada,
    estado_vazio,
    mensagem_erro,
    metrica,
    secao,
    secao_lista,
    selecao,
)
from gestao_hospitalar.ui.icones import icone
from gestao_hospitalar.ui.layout import pagina


def formulario_leito() -> rx.Component:
    return secao(
        "Cadastrar leito",
        "bed_double",
        entrada(
            "Número do leito",
            AuthState.numero_leito,
            AuthState.set_numero_leito,
            "Ex.: 101",
            obrigatorio=True,
        ),
        botao_acao(
            "Cadastrar leito",
            AuthState.criar_leito,
            "criar_leito",
            "leito",
            "plus",
            width="100%",
        ),
        mensagem_erro(AuthState.erro_leito),
    )


def tile_leito(leito: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.hstack(
            icone("bed_double", 20, color="var(--gh-muted)"),
            rx.spacer(),
            badge_status(leito["status"]),
            width="100%",
            align="center",
        ),
        rx.text("Leito ", leito["numero"], weight="bold", size="4"),
        class_name=rx.cond(
            leito["status"] == "livre",
            "gh-leito gh-leito--livre",
            "gh-leito gh-leito--ocupado",
        ),
    )


def painel_leitos() -> rx.Component:
    return secao(
        "Leitos",
        "bed_double",
        rx.cond(
            AuthState.possui_leitos,
            rx.grid(
                rx.foreach(AuthState.leitos, tile_leito),
                columns="repeat(auto-fill, minmax(160px, 1fr))",
                spacing="3",
                width="100%",
            ),
            estado_vazio(
                "bed_double",
                "Nenhum leito cadastrado.",
                "Cadastre o primeiro leito para começar a controlar a ocupação.",
            ),
        ),
        acao=rx.badge(
            AuthState.leitos.length(),
            variant="soft",
            radius="full",
            size="2",
        ),
    )


def formulario_internacao() -> rx.Component:
    return secao(
        "Registrar internação",
        "user_check",
        grade_campos(
            selecao(
                "Atendimento elegível",
                AuthState.opcoes_atendimentos_internaveis,
                AuthState.atendimento_id_internacao,
                AuthState.set_atendimento_id_internacao,
                "Selecione o atendimento",
                obrigatorio=True,
            ),
            selecao(
                "Leito livre",
                AuthState.opcoes_leitos_livres,
                AuthState.leito_id_internacao,
                AuthState.set_leito_id_internacao,
                "Selecione o leito",
                obrigatorio=True,
            ),
            entrada(
                "Data de entrada",
                AuthState.data_entrada_internacao,
                AuthState.set_data_entrada_internacao,
                obrigatorio=True,
                type="date",
            ),
        ),
        botao_acao(
            "Registrar internação",
            AuthState.criar_internacao,
            "criar_internacao",
            "internacao",
            "plus",
            width="100%",
        ),
    )


def linha_internacao(internacao: dict[str, str]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(rx.text("#", internacao["id"], weight="bold")),
        rx.table.cell(
            rx.vstack(
                rx.text("Paciente #", internacao["paciente_id"], weight="medium"),
                rx.text(
                    "Atendimento #",
                    internacao["atendimento_id"],
                    size="1",
                    color="var(--gh-muted)",
                ),
                spacing="0",
                align="start",
            )
        ),
        rx.table.cell(internacao["leito_numero"]),
        rx.table.cell(data_br(internacao["data_entrada"])),
        rx.table.cell(data_br(internacao["data_saida"])),
        rx.table.cell(badge_status(internacao["status"])),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    internacao["status"] == "internado",
                    rx.tooltip(
                        rx.icon_button(
                            icone("door_open", 16),
                            on_click=AuthState.selecionar_internacao_alta(internacao["id"]),
                            variant="soft",
                            color_scheme="green",
                            size="2",
                            cursor="pointer",
                            aria_label="Registrar alta",
                        ),
                        content="Registrar alta",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    AuthState.pode_ver_transferencias,
                    botao_icone(
                        "arrow_right_left",
                        "Ver transferências",
                        AuthState.selecionar_internacao_transferencia(internacao["id"]),
                        "ver_transferencias_" + internacao["id"],
                        "transferencia",
                        "teal",
                    ),
                    rx.fragment(),
                ),
                spacing="2",
                justify="end",
            ),
            justify="end",
        ),
    )


def formulario_alta() -> rx.Component:
    return rx.cond(
        AuthState.internacao_id_alta != "",
        secao(
            "Registrar alta",
            "door_open",
            rx.text("Internação #", AuthState.internacao_id_alta, weight="bold"),
            entrada(
                "Data de saída",
                AuthState.data_saida_internacao,
                AuthState.set_data_saida_internacao,
                obrigatorio=True,
                type="date",
            ),
            confirmar(
                rx.button(
                    icone("door_open", 16),
                    "Registrar alta",
                    size="2",
                    width="100%",
                    cursor="pointer",
                    disabled=bloqueado(),
                ),
                "Confirmar alta?",
                "A internação será encerrada e o leito liberado. Esta ação não pode ser desfeita.",
                "Confirmar alta",
                AuthState.registrar_alta,
                "registrar_alta",
                "internacao",
                "green",
            ),
        ),
        rx.fragment(),
    )


def linha_transferencia(transferencia: dict[str, str]) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.text("Transferência #", transferencia["id"], weight="bold"),
            rx.spacer(),
            rx.text(data_br(transferencia["data_transferencia"]), size="2", color="var(--gh-muted)"),
            width="100%",
        ),
        rx.text("Destino: ", transferencia["destino"], size="2", weight="medium"),
        rx.text(transferencia["motivo"], size="2", color="var(--gh-muted)"),
        padding="12px 14px",
        border="1px solid var(--gh-border)",
        border_radius="10px",
        width="100%",
    )


def historico_transferencias() -> rx.Component:
    return rx.cond(
        AuthState.internacao_id_transferencia != "",
        secao(
            "Transferências",
            "arrow_right_left",
            rx.text("Internação #", AuthState.internacao_id_transferencia, weight="bold"),
            mensagem_erro(AuthState.erro_transferencia),
            rx.cond(
                AuthState.possui_transferencias,
                rx.vstack(
                    rx.foreach(AuthState.transferencias, linha_transferencia),
                    spacing="2",
                    width="100%",
                ),
                estado_vazio(
                    "arrow_right_left",
                    "Nenhuma transferência registrada.",
                    "As transferências desta internação aparecerão aqui.",
                ),
            ),
            rx.cond(
                AuthState.internacao_transferencia_ativa,
                rx.vstack(
                    rx.divider(),
                    rx.heading("Nova transferência", size="2"),
                    entrada(
                        "Data da transferência",
                        AuthState.data_transferencia,
                        AuthState.set_data_transferencia,
                        obrigatorio=True,
                        type="date",
                    ),
                    entrada(
                        "Setor de destino",
                        AuthState.destino_transferencia,
                        AuthState.set_destino_transferencia,
                        "Ex.: UTI",
                        obrigatorio=True,
                    ),
                    area_texto(
                        "Motivo da transferência",
                        AuthState.motivo_transferencia,
                        AuthState.set_motivo_transferencia,
                        "Descreva o motivo",
                        obrigatorio=True,
                    ),
                    confirmar(
                        rx.button(
                            icone("arrow_right_left", 16),
                            "Registrar transferência",
                            size="2",
                            width="100%",
                            cursor="pointer",
                            disabled=bloqueado(),
                        ),
                        "Registrar transferência?",
                        "O paciente será transferido para o setor informado.",
                        "Confirmar transferência",
                        AuthState.criar_transferencia,
                        "criar_transferencia",
                        "transferencia",
                    ),
                    spacing="3",
                    width="100%",
                    align="stretch",
                ),
                rx.callout.root(
                    rx.callout.icon(icone("info", 16)),
                    rx.callout.text("Internação encerrada; novas transferências bloqueadas."),
                    color_scheme="gray",
                    variant="soft",
                    width="100%",
                ),
            ),
        ),
        rx.fragment(),
    )


def _aba_internacoes() -> rx.Component:
    return rx.flex(
        rx.cond(
            AuthState.pode_cadastrar_internacoes,
            rx.box(
                formulario_internacao(),
                class_name="gh-form-col",
            ),
        ),
        rx.vstack(
            secao_lista(
                "Internações",
                "bed_double",
                AuthState.internacoes_filtradas,
                ["Nº", "Paciente", "Leito", "Entrada", "Saída", "Status", ""],
                linha_internacao,
                "Nenhuma internação encontrada.",
                "As internações registradas aparecerão aqui. Use Atualizar para consultar novamente.",
                "Buscar por paciente, atendimento, leito ou status",
            ),
            formulario_alta(),
            historico_transferencias(),
            spacing="4",
            align="stretch",
            flex="2 1 760px",
            min_width="0",
        ),
        wrap="wrap",
        spacing="4",
        align="start",
        width="100%",
    )


def _aba_leitos() -> rx.Component:
    return rx.flex(
        rx.cond(
            AuthState.pode_cadastrar_leitos,
            rx.box(
                formulario_leito(),
                class_name="gh-form-col",
            ),
        ),
        rx.box(painel_leitos(), flex="2 1 460px", min_width="0"),
        wrap="wrap",
        spacing="4",
        align="start",
        width="100%",
    )


def internacoes() -> rx.Component:
    return pagina(
        "Internações e leitos",
        "Ocupação, altas e transferências",
        "bed_double",
        "/internacoes",
        (acoes_tela("internacoes", AuthState.carregar_internacoes, "internacao"),),
        rx.grid(
            metrica("Leitos livres", AuthState.total_leitos_livres, "bed_double", "green", "Disponíveis agora"),
            metrica("Leitos ocupados", AuthState.total_leitos_ocupados, "bed_double", "amber", "Em uso"),
            metrica("Internações ativas", AuthState.total_internacoes_ativas, "activity", "red", "Pacientes internados"),
            columns="repeat(auto-fit, minmax(300px, 1fr))",
            spacing="4",
            width="100%",
        ),
        mensagem_erro(AuthState.erro_internacao),
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Internações", value="internacoes"),
                rx.tabs.trigger("Leitos", value="leitos"),
                size="2",
            ),
            rx.tabs.content(_aba_internacoes(), value="internacoes", padding_top="20px"),
            rx.tabs.content(_aba_leitos(), value="leitos", padding_top="20px"),
            default_value="internacoes",
            width="100%",
        ),
    )
