"""Validacao e formatacao dos campos cadastrais de pacientes."""

from __future__ import annotations

from datetime import date, datetime
import re


_NOME_RE = re.compile(r"[^\W\d_]+(?:[ '-][^\W\d_]+)*", re.UNICODE)


def apenas_digitos(valor: str, limite: int | None = None) -> str:
    """Retorna somente digitos, opcionalmente limitados ao tamanho informado."""
    digitos = re.sub(r"\D", "", valor)
    return digitos[:limite] if limite is not None else digitos


def normalizar_nome(valor: str) -> str:
    """Remove espacos nas extremidades e compacta separadores internos."""
    return " ".join(valor.strip().split())


def formatar_nome(valor: str) -> str:
    """Mantem letras, espacos, hifen e apostrofo na entrada visual."""
    filtrado = "".join(
        caractere
        for caractere in valor
        if caractere.isalpha() or caractere.isspace() or caractere in "-'"
    )
    return re.sub(r"\s{2,}", " ", filtrado.lstrip())


def nome_valido(valor: str) -> bool:
    """Aceita letras Unicode, espacos, hifen e apostrofo."""
    nome = normalizar_nome(valor)
    return bool(nome) and bool(_NOME_RE.fullmatch(nome))


def normalizar_telefone(valor: str) -> str:
    """Normaliza telefone brasileiro para digitos sem pontuacao."""
    return apenas_digitos(valor)


def telefone_valido(valor: str) -> bool:
    """Aceita telefones fixos ou celulares brasileiros."""
    return len(normalizar_telefone(valor)) in {10, 11}


def data_nascimento_valida(valor: str, hoje: date | None = None) -> bool:
    """Valida data ISO real e impede datas posteriores ao dia atual."""
    try:
        nascimento = datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return False
    return nascimento <= (hoje or date.today())


def formatar_cpf(valor: str) -> str:
    """Aplica a mascara visual de CPF sem ultrapassar 11 digitos."""
    digitos = apenas_digitos(valor, limite=11)
    if len(digitos) <= 3:
        return digitos
    if len(digitos) <= 6:
        return f"{digitos[:3]}.{digitos[3:]}"
    if len(digitos) <= 9:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:]}"
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def formatar_telefone(valor: str) -> str:
    """Aplica mascara de telefone fixo ou celular conforme os digitos."""
    digitos = apenas_digitos(valor, limite=11)
    if len(digitos) <= 2:
        return f"({digitos}"
    if len(digitos) <= 6:
        return f"({digitos[:2]}) {digitos[2:]}"
    if len(digitos) <= 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
