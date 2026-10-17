import os

import reflex as rx

from gestao_hospitalar.configuracao import origens_cors
from gestao_hospitalar.ui.tema import tema_app

config = rx.Config(
    app_name="gestao_hospitalar",
    backend_host="127.0.0.1",
    env_file=".env",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(theme=tema_app()),
    ],
    # Local por padrão; na nuvem, GESTAO_CORS_ORIGINS informa o endereço do app.
    cors_allowed_origins=origens_cors(os.getenv("GESTAO_CORS_ORIGINS")),
)