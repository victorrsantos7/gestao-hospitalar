import unittest

from rxconfig import config


class LocalReadinessTests(unittest.TestCase):
    def test_reflex_has_no_local_database(self) -> None:
        self.assertIsNone(config.db_url)

    def test_reflex_is_bound_to_loopback(self) -> None:
        self.assertEqual(config.backend_host, "127.0.0.1")

    def test_cors_allows_only_local_presentation_origins(self) -> None:
        self.assertEqual(
            set(config.cors_allowed_origins),
            {
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            },
        )
        self.assertTrue(
            all(
                origin.startswith(("http://localhost:", "http://127.0.0.1:"))
                for origin in config.cors_allowed_origins
            )
        )


if __name__ == "__main__":
    unittest.main()
