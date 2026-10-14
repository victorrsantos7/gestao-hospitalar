"""Validacoes e normalizacao do historico do paciente."""

from datetime import date
from typing import Any


def referencia_historico_valida(referencia: str) -> bool:
    """Aceita somente identificadores inteiros positivos."""
    try:
        return int(referencia) > 0
    except (TypeError, ValueError):
        return False


def data_historico_valida(data_texto: str) -> bool:
    """Valida data ISO usada para ordenar eventos."""
    try:
        date.fromisoformat(data_texto)
    except (TypeError, ValueError):
        return False
    return True


def normalizar_historico(payload: dict[str, Any]) -> list[dict[str, str]]:
    """Converte os grupos retornados pelo Xano em uma linha do tempo unica."""
    eventos: list[dict[str, str]] = []
    for atendimento in payload.get("atendimentos", []):
        data = str(atendimento.get("data_atendimento", ""))
        eventos.append(
            {
                "tipo": "atendimento",
                "data": data,
                "titulo": f"Atendimento - {atendimento.get('tipo', '')}",
                "detalhes": str(atendimento.get("motivo", "")),
            }
        )
        for diagnostico in atendimento.get("diagnosticos") or []:
            eventos.append(
                {
                    "tipo": "diagnostico",
                    "data": str(diagnostico.get("data_diagnostico", data)),
                    "titulo": "Diagnostico",
                    "detalhes": str(diagnostico.get("descricao", "")),
                }
            )
    for internacao in payload.get("internacoes", []):
        entrada = str(internacao.get("data_entrada", ""))
        eventos.append(
            {
                "tipo": "internacao",
                "data": entrada,
                "titulo": f"Internacao - {internacao.get('status', '')}",
                "detalhes": f"Leito {internacao.get('leito_id', '')}",
            }
        )
        for transferencia in internacao.get("transferencias") or []:
            eventos.append(
                {
                    "tipo": "transferencia",
                    "data": str(transferencia.get("data_transferencia", entrada)),
                    "titulo": f"Transferencia - {transferencia.get('destino', '')}",
                    "detalhes": str(transferencia.get("motivo", "")),
                }
            )
    return sorted(eventos, key=lambda evento: evento["data"])
