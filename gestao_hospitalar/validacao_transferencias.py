"""Validacoes dos dados de transferencia."""

from datetime import date


def referencia_transferencia_valida(referencia: str) -> bool:
    """Aceita somente identificadores inteiros positivos."""
    try:
        return int(referencia) > 0
    except (TypeError, ValueError):
        return False


def transferencia_texto_valida(valor: str) -> bool:
    """Exige texto nao vazio apos remover espacos."""
    return bool(valor.strip())


def data_transferencia_valida(data_texto: str) -> bool:
    """Valida uma data no formato ISO."""
    try:
        date.fromisoformat(data_texto)
    except (TypeError, ValueError):
        return False
    return True
