import subprocess
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class SecurityReadinessTests(unittest.TestCase):
    def test_sensitive_operational_files_are_not_tracked(self) -> None:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        tracked = {
            Path(line.strip()).as_posix()
            for line in result.stdout.splitlines()
            if line.strip()
        }
        forbidden = {
            path
            for path in tracked
            if (
                path == ".env"
                or path.endswith((".db", ".log"))
                or path.startswith(("backups/", ".xano-"))
            )
        }

        self.assertEqual(
            forbidden,
            set(),
            f"Arquivos operacionais sensiveis rastreados: {sorted(forbidden)}",
        )


if __name__ == "__main__":
    unittest.main()
