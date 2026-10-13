"""Validacoes dos dados de leitos e internacoes."""

from datetime import date


STATUS_LEITO = ("livre", "ocupado")
STATUS_INTERNACAO = ("internado", "alta")


def numero_leito_valido(numero: str) -> bool:
    """Aceita somente numeros de leito inteiros positivos."""
    try:
        return int(numero) > 0
    except (TypeError, ValueError):
        return False


def status_leito_valido(status: str) -> bool:
    """Indica se o status do leito pertence ao contrato."""
    return status in STATUS_LEITO


def status_internacao_valido(status: str) -> bool:
    """Indica se o status da internacao pertence ao contrato."""
    return status in STATUS_INTERNACAO


def data_internacao_valida(data_texto: str) -> bool:
    """Valida uma data ISO de entrada ou saida."""
    try:
        date.fromisoformat(data_texto)
    except (TypeError, ValueError):
        return False
    return True


def data_saida_valida(data_saida: str, data_entrada: str) -> bool:
    """Exige alta no mesmo dia ou depois da entrada."""
    try:
        return date.fromisoformat(data_saida) >= date.fromisoformat(data_entrada)
    except (TypeError, ValueError):
        return False
