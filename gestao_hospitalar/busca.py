"""Busca textual em listas já carregadas, sem consulta ao servidor."""

import unicodedata


def normalizar_busca(texto: str) -> str:
    """Remove acentos e diferença de caixa para comparação."""
    sem_acento = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.casefold().strip()


def filtrar_registros(
    registros: list[dict[str, str]],
    termo: str,
) -> list[dict[str, str]]:
    """Retorna os registros em que algum valor contém o termo."""
    alvo = normalizar_busca(termo)
    if not alvo:
        return registros
    return [
        registro
        for registro in registros
        if any(alvo in normalizar_busca(valor) for valor in registro.values())
    ]
