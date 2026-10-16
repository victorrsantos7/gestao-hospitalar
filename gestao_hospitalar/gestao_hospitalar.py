"""Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.atendimentos import atendimentos
from gestao_hospitalar.convenios import convenios
from gestao_hospitalar.dashboard import dashboard
from gestao_hospitalar.login import login
from gestao_hospitalar.medicos import medicos
from gestao_hospitalar.internacoes import internacoes
from gestao_hospitalar.historico import historico
from gestao_hospitalar.pacientes import pacientes
from gestao_hospitalar.relatorios import relatorios

def ao_carregar(carregador, *antes):
    """on_load que sinaliza carregamento enquanto o Xano responde."""
    return [
        *antes,
        AuthState.iniciar_acao("carregando"),
        carregador,
        AuthState.encerrar_acao,
    ]


app = rx.App(stylesheets=["styles.css"])
app.add_page(login, route="/", title="Login | Gestão Hospitalar")
app.add_page(
    dashboard,
    route="/dashboard",
    title="Painel | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_resumo, AuthState.check_auth),
)
app.add_page(
    pacientes,
    route="/pacientes",
    title="Pacientes | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_pacientes, AuthState.limpar_busca),
)
app.add_page(
    medicos,
    route="/medicos",
    title="Médicos | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_medicos, AuthState.limpar_busca),
)
app.add_page(
    convenios,
    route="/convenios",
    title="Convênios | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_convenios, AuthState.limpar_busca),
)
app.add_page(
    atendimentos,
    route="/atendimentos",
    title="Atendimentos | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_atendimentos, AuthState.limpar_busca),
)
app.add_page(
    internacoes,
    route="/internacoes",
    title="Internações e leitos | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_internacoes, AuthState.limpar_busca),
)
app.add_page(
    historico,
    route="/historico",
    title="Histórico do paciente | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_historico, AuthState.limpar_busca),
)
app.add_page(
    relatorios,
    route="/relatorios",
    title="Relatórios | Gestão Hospitalar",
    on_load=ao_carregar(AuthState.carregar_relatorios, AuthState.limpar_busca),
)
