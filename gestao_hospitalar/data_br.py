"""Mascara e conversao de datas no padrao brasileiro (dd/mm/aaaa).

O formato nativo do ``<input type="date">`` segue o idioma configurado no
navegador/sistema operacional do usuario, nao o idioma da pagina. Para
garantir que todos os usuarios vejam sempre dia/mes/ano (padrao brasileiro),
os campos de data usam um input de texto com mascara aplicada aqui, e o
valor e convertido para o formato ISO (aaaa-mm-dd) somente na hora de validar
e enviar os dados ao backend.
"""

from __future__ import annotations

import re


def apenas_digitos_data(valor: str) -> str:
    """Retorna somente digitos, limitados a 8 (ddmmaaaa)."""
    return re.sub(r"\D", "", valor or "")[:8]


def formatar_data_br(valor: str) -> str:
    """Aplica a mascara visual dd/mm/aaaa conforme o usuario digita."""
    digitos = apenas_digitos_data(valor)
    if len(digitos) <= 2:
        return digitos
    if len(digitos) <= 4:
        return f"{digitos[:2]}/{digitos[2:]}"
    return f"{digitos[:2]}/{digitos[2:4]}/{digitos[4:]}"


def data_br_para_iso(valor: str) -> str:
    """Converte dd/mm/aaaa para aaaa-mm-dd; retorna "" se incompleta/invalida."""
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", valor or ""):
        return ""
    dia, mes, ano = valor.split("/")
    return f"{ano}-{mes}-{dia}"


def data_iso_para_br(valor: str) -> str:
    """Converte aaaa-mm-dd para dd/mm/aaaa; retorna "" se incompleta/invalida."""
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor or ""):
        return ""
    ano, mes, dia = valor.split("-")
    return f"{dia}/{mes}/{ano}"
