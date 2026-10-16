import reflex as rx

from gestao_hospitalar.ui.tema import tema_app

config = rx.Config(
    app_name="gestao_hospitalar",
    db_url="sqlite:///gestao_hospitalar.db",
    backend_host="127.0.0.1",
    env_file=".env",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(theme=tema_app()),
    ],
    cors_allowed_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
)