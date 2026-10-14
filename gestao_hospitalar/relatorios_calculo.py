"""Calculos puros do relatorio de ocupacao de leitos e internacoes ativas.

Funcoes isoladas da camada de State para permitir testes sem depender do
Reflex, seguindo o mesmo padrao dos modulos ``validacao_*.py`` do projeto.
"""

from __future__ import annotations

from datetime import date


def contagem_leitos(leitos: list[dict]) -> dict:
    """Conta leitos livres, ocupados e o total a partir da lista carregada."""
    livres = sum(1 for leito in leitos if leito.get("status") == "livre")
    ocupados = sum(1 for leito in leitos if leito.get("status") == "ocupado")
    return {"livres": livres, "ocupados": ocupados, "total": len(leitos)}


def internacoes_ativas(
    internacoes: list[dict], hoje: date | None = None
) -> list[dict]:
    """Filtra internacoes com status "internado" e calcula dias internado.

    Internacoes com ``data_entrada`` ausente ou invalida sao ignoradas em
    vez de interromper o relatorio.
    """
    data_referencia = hoje or date.today()
    ativas = []
    for internacao in internacoes:
        if internacao.get("status") != "internado":
            continue
        try:
            data_entrada = date.fromisoformat(internacao.get("data_entrada", ""))
        except (TypeError, ValueError):
            continue
        dias_internado = (data_referencia - data_entrada).days
        ativas.append(
            {
                "id": internacao.get("id", ""),
                "leito_numero": internacao.get("leito_numero", ""),
                "data_entrada": internacao.get("data_entrada", ""),
                "dias_internado": dias_internado,
            }
        )
    return ativas
