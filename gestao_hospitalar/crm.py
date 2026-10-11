"""Validacao e formatacao de CRM medico."""

from __future__ import annotations

import re


_CRM_RE = re.compile(r"^\s*(?:CRM\s*)?(\d{4,7})\s*[/ -]?\s*([A-Za-z]{2})\s*$")
_UFS_BRASIL = frozenset(
    {
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    }
)


def normalizar_crm(valor: str) -> str:
    """Normaliza CRM para quatro a sete digitos, barra e UF em maiusculas."""
    correspondencia = _CRM_RE.fullmatch(valor)
    if not correspondencia:
        return ""
    numero, uf = correspondencia.groups()
    uf_normalizada = uf.upper()
    if uf_normalizada not in _UFS_BRASIL:
        return ""
    return f"{numero}/{uf_normalizada}"


def crm_valido(valor: str) -> bool:
    """Indica se o CRM possui numero e UF validos."""
    return bool(normalizar_crm(valor))


def formatar_crm(valor: str) -> str:
    """Aplica mascara visual ao CRM sem ultrapassar sete digitos e duas letras."""
    partes = re.sub(r"[^0-9A-Za-z]", "", valor).upper()
    numero = re.sub(r"\D", "", partes)[:7]
    uf = re.sub(r"[^A-Z]", "", partes)[-2:]
    if not numero:
        return ""
    return f"{numero}/{uf}" if uf else numero