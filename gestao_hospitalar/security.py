"""Funções auxiliares de hash e verificação de senha."""

import bcrypt


def hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto plano."""
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto plano corresponde ao hash armazenado."""
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
