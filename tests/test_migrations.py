from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from alembic import command
from alembic.config import Config


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class MigrationTests(unittest.TestCase):
    def test_all_migrations_build_expected_local_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "migration-test.db"
            config = Config(str(REPOSITORY_ROOT / "alembic.ini"))
            config.set_main_option(
                "sqlalchemy.url",
                f"sqlite:///{database_path.as_posix()}",
            )

            command.upgrade(config, "head")

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

            self.assertIn("usuario", tables)
            self.assertIn("ix_usuario_login", indexes)
            self.assertEqual(revision, ("d21af3eecf55",))


if __name__ == "__main__":
    unittest.main()
