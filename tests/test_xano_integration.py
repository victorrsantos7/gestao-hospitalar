import os
import unittest

import httpx
from dotenv import load_dotenv


load_dotenv()
RUN_INTEGRATION = os.getenv("RUN_XANO_INTEGRATION") == "1"
BASE_URL = os.getenv("XANO_API_URL", "").strip().rstrip("/")
TIMEOUT = float(os.getenv("XANO_TIMEOUT_SECONDS", "10"))


class XanoIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not RUN_INTEGRATION:
            raise unittest.SkipTest(
                "Defina RUN_XANO_INTEGRATION=1 para testar o Xano real."
            )
        if not BASE_URL:
            raise unittest.SkipTest("XANO_API_URL nao configurada.")

    def _credentials(self, role: str) -> tuple[str, str]:
        prefix = f"XANO_TEST_{role.upper()}"
        login = os.getenv(f"{prefix}_LOGIN", "").strip()
        password = os.getenv(f"{prefix}_PASSWORD", "")
        if not login or not password:
            self.skipTest(f"Credenciais {prefix}_LOGIN/PASSWORD ausentes.")
        return login, password

    def _login(self, role: str) -> str:
        login, password = self._credentials(role)
        response = httpx.post(
            f"{BASE_URL}/auth/login",
            json={"login": login, "password": password},
            timeout=TIMEOUT,
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload.get("papel"), role)
        token = payload.get("authToken")
        self.assertIsInstance(token, str)
        self.assertTrue(token)
        return token

    def _get(self, path: str, token: str) -> httpx.Response:
        return httpx.get(
            f"{BASE_URL}{path}",
            headers={"Authorization": token},
            timeout=TIMEOUT,
        )

    def test_invalid_login_is_rejected(self) -> None:
        response = httpx.post(
            f"{BASE_URL}/auth/login",
            json={
                "login": "usuario-inexistente-smoke-test",
                "password": "senha-invalida-smoke-test",
            },
            timeout=TIMEOUT,
        )
        self.assertIn(response.status_code, {400, 401, 403})

    def test_invalid_token_is_rejected(self) -> None:
        response = self._get("/patients", "token-invalido-smoke-test")
        self.assertIn(response.status_code, {401, 403})

    def test_role_matrix_for_read_only_endpoints(self) -> None:
        cases = {
            "recepcionista": {
                200: ["/patients", "/doctors", "/convenios", "/atendimentos"],
                403: ["/internacoes", "/leitos"],
            },
            "medico": {
                200: ["/patients", "/atendimentos"],
                403: ["/doctors", "/convenios", "/internacoes", "/leitos"],
            },
            "enfermagem_gestao": {
                200: ["/internacoes", "/leitos"],
                403: ["/patients", "/doctors", "/convenios", "/atendimentos"],
            },
            "admin": {
                200: [
                    "/patients",
                    "/doctors",
                    "/convenios",
                    "/atendimentos",
                    "/internacoes",
                    "/leitos",
                ],
            },
        }

        for role, expectations in cases.items():
            token = self._login(role)
            for expected_status, paths in expectations.items():
                for path in paths:
                    with self.subTest(role=role, path=path):
                        response = self._get(path, token)
                        self.assertEqual(response.status_code, expected_status)

    def test_unknown_role_token_is_denied_when_configured(self) -> None:
        token = os.getenv("XANO_TEST_UNKNOWN_AUTH_TOKEN", "").strip()
        if not token:
            self.skipTest("XANO_TEST_UNKNOWN_AUTH_TOKEN ausente.")

        for path in ("/patients", "/doctors", "/convenios", "/internacoes"):
            with self.subTest(path=path):
                response = self._get(path, token)
                self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
