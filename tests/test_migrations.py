from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LEGACY_REVISION = "d21af3eecf55"
CURRENT_REVISION = "a7c4e91b2f10"


class MigrationTests(unittest.TestCase):
    @staticmethod
    def _config(database_path: Path) -> Config:
        config = Config(str(REPOSITORY_ROOT / "alembic.ini"))
        config.set_main_option(
            "sqlalchemy.url",
            f"sqlite:///{database_path.as_posix()}",
        )
        return config

    def _assert_legacy_user_table_removed(self, database_path: Path) -> None:
        with closing(sqlite3.connect(database_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            indexes = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index'"
                )
            }
            revision = connection.execute(
                "SELECT version_num FROM alembic_version"
            ).fetchone()

        self.assertNotIn("usuario", tables)
        self.assertNotIn("ix_usuario_login", indexes)
        self.assertEqual(revision, (CURRENT_REVISION,))

    def test_all_migrations_build_expected_local_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "migration-test.db"
            config = self._config(database_path)
            command.upgrade(config, "head")
            self._assert_legacy_user_table_removed(database_path)

    def test_upgrade_removes_existing_legacy_user_without_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "migration-upgrade-test.db"
            config = self._config(database_path)
            command.upgrade(config, LEGACY_REVISION)
            with closing(sqlite3.connect(database_path)) as connection:
                connection.execute(
                    """
                    INSERT INTO usuario (id, login, senha_hash, papel)
                    VALUES (1, 'legado', 'hash-descartado', 'admin')
                    """
                )
                connection.commit()

            command.upgrade(config, "head")
            self._assert_legacy_user_table_removed(database_path)


if __name__ == "__main__":
    unittest.main()
