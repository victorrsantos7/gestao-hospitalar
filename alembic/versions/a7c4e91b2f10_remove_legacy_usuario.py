"""Remove a tabela local legada de usuários.

Revision ID: a7c4e91b2f10
Revises: d21af3eecf55
Create Date: 2026-10-16 00:02:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = "a7c4e91b2f10"
down_revision: Union[str, Sequence[str], None] = "d21af3eecf55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_usuario_login", table_name="usuario")
    op.drop_table("usuario")


def downgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "login",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "senha_hash",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.Column(
            "papel",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_usuario_login",
        "usuario",
        ["login"],
        unique=True,
    )
