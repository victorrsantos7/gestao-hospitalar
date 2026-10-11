"""Validacao e normalizacao de CPF."""

import re


def normalizar_cpf(cpf: str) -> str:
    """Retorna somente os digitos do CPF informado."""
    return re.sub(r"\D", "", cpf)


def cpf_valido(cpf: str) -> bool:
    """Valida quantidade, repeticao e digitos verificadores do CPF."""
    digitos = normalizar_cpf(cpf)
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False

    primeiro_digito = _calcular_digito(digitos[:9])
    segundo_digito = _calcular_digito(digitos[:9] + primeiro_digito)
    return digitos[-2:] == primeiro_digito + segundo_digito


def _calcular_digito(base: str) -> str:
    fator = len(base) + 1
    total = sum(int(digito) * (fator - indice) for indice, digito in enumerate(base))
    resto = total % 11
    return "0" if resto < 2 else str(11 - resto)
