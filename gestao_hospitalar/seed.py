"""Seed do usuário administrador inicial de desenvolvimento.

Uso: python -m gestao_hospitalar.seed

Credenciais fixas apenas para ambiente de desenvolvimento local — ver README.
"""

import reflex as rx

from gestao_hospitalar.models import Usuario
from gestao_hospitalar.security import hash_senha

ADMIN_LOGIN = "admin"
ADMIN_SENHA = "admin"
ADMIN_PAPEL = "gestao"


def seed_admin() -> None:
    """Cria o usuário administrador inicial, se ainda não existir."""
    with rx.session() as session:
        if Usuario.buscar_por_login(session, ADMIN_LOGIN) is not None:
            print(f"Usuário '{ADMIN_LOGIN}' já existe, nada a fazer.")
            return

        session.add(
            Usuario(
                login=ADMIN_LOGIN,
                senha_hash=hash_senha(ADMIN_SENHA),
                papel=ADMIN_PAPEL,
            )
        )
        session.commit()
        print(f"Usuário administrador '{ADMIN_LOGIN}' criado com sucesso.")


if __name__ == "__main__":
    seed_admin()
