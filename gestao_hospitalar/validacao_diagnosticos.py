"""Validacoes dos dados de diagnostico."""

from datetime import date


def diagnostico_texto_valido(valor: str) -> bool:
    """Exige texto nao vazio apos remover espacos."""
    return bool(valor.strip())


def data_diagnostico_valida(data_texto: str) -> bool:
    """Valida uma data no formato ISO aceito pelo campo de data."""
    try:
        date.fromisoformat(data_texto)
    except (TypeError, ValueError):
        return False
    return True


def referencia_diagnostico_valida(referencia: str) -> bool:
    """Aceita somente identificadores inteiros positivos."""
    try:
        return int(referencia) > 0
    except (TypeError, ValueError):
        return False
