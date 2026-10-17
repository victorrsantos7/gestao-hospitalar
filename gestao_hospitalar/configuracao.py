"""Configuração de implantação lida do ambiente (usada pelo rxconfig.py)."""

ORIGENS_LOCAIS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]


def origens_cors(valor: str | None) -> list[str]:
    """Origens permitidas pelo backend (CORS).

    Sem valor, só as portas locais de desenvolvimento. Com
    `GESTAO_CORS_ORIGINS` (lista separada por vírgulas, ou `*`), usa a lista
    informada, por exemplo o endereço do app publicado na nuvem.
    """
    if valor is None or not valor.strip():
        return list(ORIGENS_LOCAIS)
    origens = [item.strip().rstrip("/") for item in valor.split(",") if item.strip()]
    return origens or list(ORIGENS_LOCAIS)
