"""Validacoes e normalizacao de dados de convenios."""

from gestao_hospitalar.validacao_pacientes import nome_valido, normalizar_nome


TIPOS_CONVENIO = ("particular", "plano", "SUS")


def tipo_convenio_valido(tipo: str) -> bool:
    """Indica se o tipo pertence ao conjunto de valores aceitos."""
    return tipo in TIPOS_CONVENIO


def normalizar_nome_convenio(nome: str) -> str:
    """Normaliza o nome para exibicao e comparacao de duplicidade."""
    return normalizar_nome(nome)


def nome_convenio_valido(nome: str) -> bool:
    """Valida o nome com as mesmas regras de nomes do sistema."""
    return nome_valido(normalizar_nome_convenio(nome))