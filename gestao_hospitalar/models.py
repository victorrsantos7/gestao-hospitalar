"""Modelos de dados do Sistema de Gestão Hospitalar."""

import sqlmodel


class Usuario(sqlmodel.SQLModel, table=True):
    """Usuário do sistema (funcionário do hospital) com credenciais de acesso."""

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
    login: str = sqlmodel.Field(unique=True, index=True)
    senha_hash: str
    papel: str

    @classmethod
    def buscar_por_login(
        cls, session: sqlmodel.Session, login: str
    ) -> "Usuario | None":
        """Busca um usuário pelo login, ou None se não existir."""
        return session.exec(
            sqlmodel.select(cls).where(cls.login == login)
        ).first()
