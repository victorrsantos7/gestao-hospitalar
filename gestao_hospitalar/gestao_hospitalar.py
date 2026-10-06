"""Sistema de Gestão Hospitalar."""

import reflex as rx

from gestao_hospitalar.auth_state import AuthState
from gestao_hospitalar.dashboard import dashboard
from gestao_hospitalar.login import login
from gestao_hospitalar.models import Usuario  # noqa: F401 - registra o modelo para migrações

app = rx.App()
app.add_page(login, route="/", title="Login")
app.add_page(dashboard, route="/dashboard", title="Dashboard", on_load=AuthState.check_auth)
