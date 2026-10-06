import reflex as rx

config = rx.Config(
    app_name="gestao_hospitalar",
    db_url="sqlite:///gestao_hospitalar.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)