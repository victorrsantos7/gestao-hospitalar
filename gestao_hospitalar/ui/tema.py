"""Tema global e tokens visuais (os valores vivem em assets/styles.css)."""

import reflex as rx


def tema_app() -> rx.Component:
    """Tema Radix único do app: accent petróleo (escala em styles.css) e cinza frio."""
    return rx.theme(
        appearance="light",
        has_background=True,
        accent_color="teal",
        gray_color="slate",
        radius="medium",
        scaling="100%",
        panel_background="solid",
    )
