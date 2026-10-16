"""Componentes reutilizáveis: formulário, feedback, tabelas e cartões."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.icones import icone


def cadeia(handler, chave, dominio: str = "", atualizacao: bool = False):
    """Encadeia carregamento, evento de negócio e toast de resultado."""
    eventos = [AuthState.iniciar_acao(chave, dominio), handler]
    if dominio:
        eventos.append(
            AuthState.notificar_atualizacao(dominio)
            if atualizacao
            else AuthState.notificar_resultado(dominio)
        )
    eventos.append(AuthState.encerrar_acao)
    return eventos


def botao_acao(
    rotulo,
    handler,
    chave,
    dominio: str = "",
    icone_nome: str | None = None,
    atualizacao: bool = False,
    **props,
) -> rx.Component:
    """Botão com carregamento, bloqueio de duplo clique e toast de resultado."""
    filhos = [icone(icone_nome, 16)] if icone_nome else []
    props.setdefault("size", "2")
    return rx.button(
        *filhos,
        rotulo,
        loading=AuthState.acao_em_andamento == chave,
        disabled=bloqueado(),
        on_click=cadeia(handler, chave, dominio, atualizacao),
        cursor="pointer",
        **props,
    )


def acoes_tela(tela: str, atualizar, dominio: str) -> rx.Component:
    """Atualizar (recarrega do servidor) e Limpar (zera leitura, seleção e busca)."""
    return rx.hstack(
        botao_acao(
            "Atualizar",
            atualizar,
            "atualizar_" + tela,
            dominio,
            "refresh_cw",
            atualizacao=True,
            variant="soft",
        ),
        rx.button(
            icone("eraser", 16),
            "Limpar",
            on_click=AuthState.limpar_tela(tela),
            disabled=bloqueado(),
            variant="soft",
            color_scheme="gray",
            size="2",
            cursor="pointer",
        ),
        spacing="2",
    )


def botao_icone(
    icone_nome: str,
    dica: str,
    handler,
    chave,
    dominio: str = "",
    cor: str = "gray",
    desabilitado=False,
) -> rx.Component:
    """Botão de ícone para ações de linha, com dica e carregamento."""
    return rx.tooltip(
        rx.icon_button(
            icone(icone_nome, 16),
            loading=AuthState.acao_em_andamento == chave,
            disabled=bloqueado() | desabilitado,
            on_click=cadeia(handler, chave, dominio),
            variant="soft",
            color_scheme=cor,
            size="2",
            cursor="pointer",
            aria_label=dica,
        ),
        content=dica,
    )


def confirmar(
    gatilho: rx.Component,
    titulo: str,
    descricao: str,
    rotulo_confirmar: str,
    handler,
    chave,
    dominio: str = "",
    cor: str = "teal",
) -> rx.Component:
    """Diálogo de confirmação antes de uma ação irreversível."""
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(gatilho),
        rx.alert_dialog.content(
            rx.alert_dialog.title(titulo),
            rx.alert_dialog.description(descricao, size="2"),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button("Cancelar", variant="soft", color_scheme="gray", size="2")
                ),
                rx.alert_dialog.action(
                    rx.button(
                        rotulo_confirmar,
                        color_scheme=cor,
                        size="2",
                        on_click=cadeia(handler, chave, dominio),
                    )
                ),
                spacing="3",
                justify="end",
                margin_top="20px",
            ),
            max_width="440px",
        ),
    )


def campo(rotulo: str, controle: rx.Component, obrigatorio: bool = False) -> rx.Component:
    """Rótulo permanente associado ao controle (o placeholder é só exemplo)."""
    cabecalho = [rx.text(rotulo, size="2", weight="medium", class_name="gh-rotulo")]
    if obrigatorio:
        cabecalho.append(rx.text("*", size="2", color="var(--red-9)"))
    return rx.vstack(
        rx.hstack(*cabecalho, spacing="1", align="center"),
        controle,
        spacing="1",
        align="start",
        width="100%",
    )


def entrada(rotulo: str, valor, ao_mudar, placeholder: str = "", obrigatorio: bool = False, **props) -> rx.Component:
    return campo(
        rotulo,
        rx.input(
            value=valor,
            on_change=ao_mudar,
            placeholder=placeholder,
            size="2",
            width="100%",
            **props,
        ),
        obrigatorio,
    )


def selecao(rotulo: str, opcoes, valor, ao_mudar, placeholder: str = "Selecione", obrigatorio: bool = False) -> rx.Component:
    return campo(
        rotulo,
        rx.select(
            opcoes,
            value=valor,
            on_change=ao_mudar,
            placeholder=placeholder,
            size="2",
            width="100%",
        ),
        obrigatorio,
    )


def area_texto(rotulo: str, valor, ao_mudar, placeholder: str = "", obrigatorio: bool = False, **props) -> rx.Component:
    return campo(
        rotulo,
        rx.text_area(
            value=valor,
            on_change=ao_mudar,
            placeholder=placeholder,
            size="2",
            width="100%",
            rows="3",
            **props,
        ),
        obrigatorio,
    )


def mensagem_erro(texto) -> rx.Component:
    """Erro persistente junto ao formulário (some quando a próxima ação começa)."""
    return rx.cond(
        texto != "",
        rx.callout.root(
            rx.callout.icon(icone("circle_alert", 16)),
            rx.callout.text(texto),
            color_scheme="red",
            variant="soft",
            role="alert",
            width="100%",
        ),
    )


def secao(titulo: str, icone_nome: str, *filhos, descricao: str = "", acao: rx.Component | None = None, **props) -> rx.Component:
    """Cartão com cabeçalho padronizado."""
    titulos = [rx.heading(titulo, size="3", weight="bold", class_name="gh-titulo-secao")]
    if descricao:
        titulos.append(rx.text(descricao, size="2", color="var(--gh-muted)"))
    cabecalho = [
        rx.center(icone(icone_nome, 16), class_name="gh-icone-secao"),
        rx.vstack(*titulos, spacing="0", align="start"),
    ]
    if acao is not None:
        cabecalho.extend([rx.spacer(), acao])
    return rx.card(
        rx.vstack(
            rx.hstack(*cabecalho, spacing="3", align="center", width="100%"),
            *filhos,
            spacing="3",
            width="100%",
            align="stretch",
        ),
        class_name="gh-card",
        size="2",
        width="100%",
        **props,
    )


def cabecalho_pagina(titulo: str, descricao: str, icone_nome: str, *acoes) -> rx.Component:
    return rx.hstack(
        rx.center(icone(icone_nome, 20), class_name="gh-icone-pagina"),
        rx.vstack(
            rx.heading(titulo, size="6", weight="bold", class_name="gh-titulo-pagina"),
            rx.text(descricao, size="2", color="var(--gh-muted)"),
            spacing="0",
            align="start",
        ),
        rx.spacer(),
        *acoes,
        spacing="4",
        align="center",
        width="100%",
        wrap="wrap",
    )


def estado_vazio(icone_nome: str, titulo: str, texto: str) -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.center(icone(icone_nome, 20), class_name="gh-vazio-icone"),
            rx.text(titulo, weight="bold", size="3"),
            rx.text(texto, size="2", color="var(--gh-muted)", text_align="center"),
            spacing="2",
            align="center",
            max_width="320px",
        ),
        padding="20px 12px",
        width="100%",
    )


def badge_status(valor) -> rx.Component:
    """Badge com cor semântica por valor de status/tipo."""
    cor = rx.match(
        valor,
        ("livre", "green"),
        ("alta", "green"),
        ("SUS", "green"),
        ("ocupado", "amber"),
        ("internado", "blue"),
        ("plano", "blue"),
        ("consulta", "blue"),
        ("emergencia", "red"),
        ("retorno", "violet"),
        "gray",
    )
    return rx.badge(
        valor,
        color_scheme=cor,
        variant="soft",
        radius="full",
        size="2",
        class_name="gh-badge",
    )


def campo_busca(placeholder: str = "Buscar na lista") -> rx.Component:
    return rx.input(
        rx.input.slot(icone("search", 16)),
        value=AuthState.termo_busca,
        on_change=AuthState.set_termo_busca,
        placeholder=placeholder,
        size="2",
        width="100%",
        aria_label=placeholder,
    )


def tabela(colunas: list[str], corpo: rx.Component) -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(*[rx.table.column_header_cell(c) for c in colunas])
        ),
        rx.table.body(corpo),
        variant="ghost",
        size="2",
        width="100%",
        class_name="gh-tabela",
    )


def bloqueado():
    """Bloqueia ações durante qualquer operação ou antes de o estado ser hidratado."""
    return (AuthState.acao_em_andamento != "") | ~AuthState.is_hydrated


def _carregando():
    """Verdadeiro antes da hidratação do estado e durante o on_load da página."""
    return ~AuthState.is_hydrated | AuthState.carregando_pagina


def carregando_lista() -> rx.Component:
    """Esqueleto exibido enquanto a primeira leitura ainda não chegou."""
    return rx.vstack(
        rx.skeleton(height="36px", width="100%", loading=True),
        rx.skeleton(height="36px", width="100%", loading=True),
        rx.skeleton(height="36px", width="100%", loading=True),
        spacing="2",
        width="100%",
        padding_y="8px",
        aria_busy="true",
    )


def indicador_atualizando() -> rx.Component:
    """Aviso discreto enquanto uma leitura nova substitui a anterior."""
    return rx.cond(
        _carregando(),
        rx.hstack(
            rx.spinner(size="1"),
            rx.text("Atualizando", size="1", color="var(--gh-muted)"),
            spacing="2",
            align="center",
        ),
    )


def paginacao(tela: str, dominio: str, pagina, total_paginas, texto) -> rx.Component:
    """Rodapé de navegação das listas paginadas do Xano (oculto com uma só página)."""
    return rx.cond(
        total_paginas > 1,
        rx.hstack(
            rx.text(texto, size="2", color="var(--gh-muted)"),
            rx.spacer(),
            rx.text("Página ", pagina, " de ", total_paginas, size="2", weight="medium"),
            botao_icone(
                "chevron_left",
                "Página anterior",
                AuthState.mudar_pagina(tela, -1),
                "pag_" + tela + "_anterior",
                dominio,
                desabilitado=pagina <= 1,
            ),
            botao_icone(
                "chevron_right",
                "Próxima página",
                AuthState.mudar_pagina(tela, 1),
                "pag_" + tela + "_proxima",
                dominio,
                desabilitado=pagina >= total_paginas,
            ),
            spacing="3",
            align="center",
            width="100%",
            padding_top="4px",
        ),
        rx.text(texto, size="2", color="var(--gh-muted)"),
    )


def secao_lista(
    titulo: str,
    icone_nome: str,
    filtrados,
    colunas: list[str],
    render_linha,
    titulo_vazio: str,
    texto_vazio: str,
    placeholder_busca: str = "Buscar na lista",
    dica_busca: str = "",
    rodape: rx.Component | None = None,
    total=None,
) -> rx.Component:
    """Cartão com busca, tabela, estado vazio, esqueleto de carregamento e rodapé.

    `total` substitui a contagem do selo quando a lista é paginada no servidor.
    """
    filhos = [campo_busca(placeholder_busca)]
    filhos.append(
        rx.cond(
            filtrados.length() > 0,
            tabela(colunas, rx.foreach(filtrados, render_linha)),
            rx.cond(
                _carregando(),
                carregando_lista(),
                rx.cond(
                    AuthState.termo_busca != "",
                    estado_vazio(
                        "search_x",
                        "Nenhum resultado",
                        "Nenhum registro corresponde à busca. Tente outro termo."
                        + (" " + dica_busca if dica_busca else ""),
                    ),
                    estado_vazio(icone_nome, titulo_vazio, texto_vazio),
                ),
            ),
        )
    )
    if rodape is not None:
        filhos.append(rodape)
    return secao(
        titulo,
        icone_nome,
        *filhos,
        acao=rx.hstack(
            indicador_atualizando(),
            rx.badge(
                filtrados.length() if total is None else total,
                variant="soft",
                radius="full",
                size="2",
            ),
            spacing="3",
            align="center",
        ),
    )


def item_detalhe(rotulo: str, valor) -> rx.Component:
    return rx.vstack(
        rx.text(rotulo, size="1", weight="medium", color="var(--gh-muted)", class_name="gh-rotulo-detalhe"),
        rx.text(rx.cond(valor == "", "—", valor), size="2", weight="medium"),
        spacing="0",
        align="start",
    )


def grade_detalhes(*itens) -> rx.Component:
    return rx.grid(*itens, columns="repeat(auto-fit, minmax(200px, 1fr))", spacing="3", width="100%")


def data_br(valor) -> rx.Component:
    """Converte AAAA-MM-DD em DD/MM/AAAA; outros formatos ficam como recebidos."""
    return rx.cond(
        valor == "",
        "—",
        rx.cond(
            valor.length() == 10,
            valor[8:10] + "/" + valor[5:7] + "/" + valor[0:4],
            valor,
        ),
    )


def metrica(titulo: str, valor, icone_nome: str, cor: str = "teal", detalhe: str = "") -> rx.Component:
    filhos = [
        rx.hstack(
            rx.text(titulo, size="2", weight="medium", color="var(--gh-muted)"),
            rx.spacer(),
            rx.center(icone(icone_nome, 16), class_name="gh-metrica-icone", color=f"var(--{cor}-11)", background=f"var(--{cor}-3)"),
            width="100%",
            align="center",
        ),
        rx.cond(
            _carregando() & (valor <= 0),
            rx.skeleton(rx.heading("00", size="6"), loading=True),
            rx.heading(rx.cond(valor < 0, "—", valor), size="6", weight="bold", class_name="gh-metrica-valor"),
        ),
    ]
    if detalhe:
        filhos.append(rx.text(detalhe, size="1", color="var(--gh-muted)"))
    return rx.card(
        rx.vstack(*filhos, spacing="1", align="start", width="100%"),
        class_name="gh-card gh-metrica",
        size="2",
    )
