"""Marca e ilustrações em SVG próprio (ícones de ação usam Lucide via rx.icon)."""

import reflex as rx


def _marca_svg(tamanho: int) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
        'viewBox="0 0 40 40" fill="none" aria-hidden="true">'
        '<defs><linearGradient id="gh-marca" x1="4" y1="2" x2="36" y2="38" '
        'gradientUnits="userSpaceOnUse"><stop stop-color="#1B8AA6"/>'
        '<stop offset="1" stop-color="#0A4A5E"/></linearGradient></defs>'
        '<rect width="40" height="40" rx="11" fill="url(#gh-marca)"/>'
        '<path d="M16.5 8h7v8.5H32v7h-8.5V32h-7v-8.5H8v-7h8.5z" fill="#fff"/>'
        '<path d="M6 20h8.5l2.5-5.5 4 11 2.7-5.5H34" stroke="#0E6179" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def marca(tamanho: int = 36) -> rx.Component:
    """Logotipo: cruz clínica com linha de pulso."""
    return rx.html(_marca_svg(tamanho), line_height="0", flex_shrink="0")


_PAINEL_LOGIN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" '
    'viewBox="0 0 800 900" preserveAspectRatio="xMidYMid slice" fill="none" '
    'aria-hidden="true"><defs>'
    '<linearGradient id="gh-fundo" x1="0" y1="0" x2="800" y2="900" '
    'gradientUnits="userSpaceOnUse"><stop stop-color="#0E6179"/>'
    '<stop offset="1" stop-color="#082B38"/></linearGradient>'
    '<pattern id="gh-cruzes" width="72" height="72" patternUnits="userSpaceOnUse">'
    '<path d="M33 24h6v9h9v6h-9v9h-6v-9h-9v-6h9z" fill="#fff" fill-opacity=".06"/>'
    '</pattern></defs>'
    '<rect width="800" height="900" fill="url(#gh-fundo)"/>'
    '<rect width="800" height="900" fill="url(#gh-cruzes)"/>'
    '<circle cx="690" cy="130" r="230" fill="#fff" fill-opacity=".05"/>'
    '<circle cx="120" cy="780" r="290" fill="#fff" fill-opacity=".05"/>'
    '<path d="M0 330h210l40-90 64 180 44-90h442" stroke="#7FD3E6" '
    'stroke-opacity=".55" stroke-width="5" stroke-linecap="round" '
    'stroke-linejoin="round"/></svg>'
)


def painel_login() -> rx.Component:
    """Fundo ilustrado do login, sem dependência de imagem externa."""
    return rx.html(
        _PAINEL_LOGIN,
        position="absolute",
        inset="0",
        line_height="0",
    )


def icone(nome: str, tamanho: int = 18, **props) -> rx.Component:
    """Ícone SVG Lucide padronizado."""
    return rx.icon(tag=nome, size=tamanho, **props)
