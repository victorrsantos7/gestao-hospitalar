"""Matriz fixa de autorizacao do sistema."""

from typing import Final

RECURSO_DASHBOARD = "dashboard"
RECURSO_PACIENTES = "pacientes"
RECURSO_CADASTRO_PACIENTES = "cadastro_pacientes"
RECURSO_MEDICOS = "medicos"
RECURSO_CONVENIOS = "convenios"
RECURSO_ATENDIMENTOS = "atendimentos"
RECURSO_DIAGNOSTICOS = "diagnosticos"
RECURSO_INTERNACOES = "internacoes"
RECURSO_LEITOS = "leitos"
RECURSO_TRANSFERENCIAS = "transferencias"
RECURSO_HISTORICO = "historico"
RECURSO_FINANCEIRO = "financeiro"
RECURSO_RELATORIOS = "relatorios"
RECURSO_USUARIOS = "usuarios"

PERMISSOES_POR_PAPEL: Final[dict[str, frozenset[str]]] = {
    "recepcionista": frozenset(
        {
            RECURSO_DASHBOARD,
            RECURSO_PACIENTES,
            RECURSO_CADASTRO_PACIENTES,
            RECURSO_MEDICOS,
            RECURSO_CONVENIOS,
            RECURSO_ATENDIMENTOS,
        }
    ),
    "medico": frozenset(
        {
            RECURSO_DASHBOARD,
            RECURSO_PACIENTES,
            RECURSO_ATENDIMENTOS,
            RECURSO_DIAGNOSTICOS,
        }
    ),
    "enfermagem_gestao": frozenset(
        {
            RECURSO_DASHBOARD,
            RECURSO_INTERNACOES,
            RECURSO_LEITOS,
            RECURSO_TRANSFERENCIAS,
            RECURSO_HISTORICO,
        }
    ),
    "admin": frozenset({"*"}),
}


def papel_conhecido(papel: str) -> bool:
    """Indica se o papel pertence a matriz fixa."""
    return papel in PERMISSOES_POR_PAPEL


def tem_permissao(papel: str, recurso: str) -> bool:
    """Verifica uma permissao usando negacao por padrao."""
    permissoes = PERMISSOES_POR_PAPEL.get(papel)
    if permissoes is None:
        return False
    return "*" in permissoes or recurso in permissoes


def pode_acessar(autenticado: bool, papel: str, recurso: str) -> bool:
    """Valida sessao e permissao antes de liberar um recurso."""
    return autenticado and papel_conhecido(papel) and tem_permissao(papel, recurso)
