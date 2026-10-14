"""Validações dos dados de atendimento."""

from datetime import date


TIPOS_ATENDIMENTO = ("consulta", "emergencia", "retorno")

# Rótulos acentuados usados apenas para exibição na interface; os valores
# salvos e validados continuam sendo os de TIPOS_ATENDIMENTO (compatíveis
# com o enum cadastrado no Xano).
ROTULOS_TIPO_ATENDIMENTO = {
    "consulta": "Consulta",
    "emergencia": "Emergência",
    "retorno": "Retorno",
}


def tipo_atendimento_valido(tipo: str) -> bool:
    """Indica se o tipo pertence ao conjunto aceito pelo sistema."""
    return tipo in TIPOS_ATENDIMENTO


def data_atendimento_valida(data_texto: str) -> bool:
    """Valida uma data no formato ISO aceito pelo campo de data."""
    try:
        date.fromisoformat(data_texto)
    except (TypeError, ValueError):
        return False
    return True


def motivo_atendimento_valido(motivo: str) -> bool:
    """Exige motivo textual nao vazio apos remover espacos."""
    return bool(motivo.strip())


def referencia_atendimento_valida(referencia: str) -> bool:
    """Aceita somente identificadores inteiros positivos."""
    try:
        return int(referencia) > 0
    except (TypeError, ValueError):
        return False