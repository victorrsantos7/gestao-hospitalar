"""Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.atendimentos import atendimentos
from gestao_hospitalar.convenios import convenios
from gestao_hospitalar.dashboard import dashboard
from gestao_hospitalar.login import login
from gestao_hospitalar.medicos import medicos
from gestao_hospitalar.pacientes import pacientes

app = rx.App()
app.add_page(login, route="/", title="Login")
app.add_page(dashboard, route="/dashboard", title="Dashboard", on_load=AuthState.check_auth)
app.add_page(
	pacientes,
	route="/pacientes",
	title="Pacientes",
	on_load=AuthState.carregar_pacientes,
)
app.add_page(
	medicos,
	route="/medicos",
	title="Medicos",
	on_load=AuthState.carregar_medicos,
)
app.add_page(
	convenios,
	route="/convenios",
	title="Convenios",
	on_load=AuthState.carregar_convenios,
)
app.add_page(
	atendimentos,
	route="/atendimentos",
	title="Atendimentos",
	on_load=AuthState.carregar_atendimentos,
)
