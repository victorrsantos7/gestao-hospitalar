"""Ajuda de uso em modal: botão flutuante (FAB) e diálogo com conteúdo por módulo."""

import reflex as rx

from gestao_hospitalar.ajuda import TOPICOS, Topico
from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.ui.icones import icone


def fab_ajuda() -> rx.Component:
    """Botão flutuante que abre a ajuda sem sair da tela."""
    return rx.tooltip(
        rx.icon_button(
            icone("circle_help", 22),
            on_click=AuthState.abrir_ajuda,
            aria_label="Abrir ajuda de uso",
            size="4",
            radius="full",
            cursor="pointer",
            class_name="gh-fab",
        ),
        content="Ajuda de uso",
    )


def _liberado(topico: Topico, componente: rx.Component) -> rx.Component:
    if topico.permissao is None:
        return componente
    return rx.cond(getattr(AuthState, topico.permissao), componente)


def _item_nav(topico: Topico) -> rx.Component:
    item = rx.el.button(
        icone(topico.icone, 16),
        rx.text(topico.titulo, size="2", weight="medium"),
        on_click=AuthState.selecionar_ajuda(topico.id),
        type="button",
        class_name=rx.cond(
            AuthState.ajuda_topico == topico.id,
            "gh-ajuda-item gh-ajuda-item--ativo",
            "gh-ajuda-item",
        ),
    )
    return _liberado(topico, item)


def _lista(titulo: str, itens: tuple[str, ...], numerada: bool) -> rx.Component:
    return rx.vstack(
        rx.text(titulo, size="1", weight="bold", class_name="gh-ajuda-rotulo"),
        rx.el.ol(
            *[rx.el.li(item) for item in itens],
            class_name="gh-ajuda-lista",
        )
        if numerada
        else rx.el.ul(
            *[rx.el.li(item) for item in itens],
            class_name="gh-ajuda-lista gh-ajuda-lista--dicas",
        ),
        spacing="1",
        align="stretch",
        width="100%",
    )


def _conteudo(topico: Topico) -> rx.Component:
    blocos = [
        rx.heading(topico.titulo, size="3", class_name="gh-titulo-secao"),
        rx.text(topico.resumo, size="2", color="var(--gh-muted)"),
    ]
    if topico.perfis:
        blocos.append(
            rx.callout.root(
                rx.callout.icon(icone("user_check", 16)),
                rx.callout.text(topico.perfis),
                size="1",
                variant="soft",
                width="100%",
            )
        )
    blocos.append(_lista("COMO USAR", topico.passos, numerada=True))
    if topico.dicas:
        blocos.append(_lista("DICAS", topico.dicas, numerada=False))
    return _liberado(
        topico,
        rx.cond(
            AuthState.ajuda_topico == topico.id,
            rx.vstack(*blocos, spacing="3", align="stretch", width="100%"),
        ),
    )


def modal_ajuda() -> rx.Component:
    """Diálogo da ajuda: lista de módulos à esquerda e instruções à direita."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.hstack(
                rx.center(icone("circle_help", 16), class_name="gh-icone-secao"),
                rx.vstack(
                    rx.dialog.title("Ajuda de uso", weight="bold"),
                    rx.dialog.description(
                        "Instruções por módulo, conforme o seu perfil.",
                        color="var(--gh-muted)",
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.dialog.close(
                    rx.icon_button(
                        icone("x", 15),
                        variant="ghost",
                        color_scheme="gray",
                        size="2",
                        aria_label="Fechar ajuda",
                        cursor="pointer",
                    )
                ),
                align="center",
                spacing="3",
                width="100%",
                class_name="gh-ajuda-cabecalho",
            ),
            rx.box(
                rx.box(
                    *[_item_nav(topico) for topico in TOPICOS],
                    class_name="gh-ajuda-nav",
                    role="navigation",
                    aria_label="Módulos da ajuda",
                ),
                rx.box(
                    *[_conteudo(topico) for topico in TOPICOS],
                    class_name="gh-ajuda-conteudo",
                ),
                class_name="gh-ajuda-corpo",
            ),
            class_name="gh-ajuda-dialogo",
            max_width="820px",
            width="calc(100vw - 24px)",
        ),
        open=AuthState.ajuda_aberta,
        on_open_change=AuthState.set_ajuda_aberta,
    )
