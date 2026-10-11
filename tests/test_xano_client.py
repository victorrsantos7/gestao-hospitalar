import os
import logging
import unittest
from unittest.mock import patch

import httpx

from gestao_hospitalar.xano_client import (
    XanoAuthenticationError,
    XanoConfig,
    XanoConfigurationError,
    XanoClient,
    XanoResponseError,
    XanoUnavailableError,
    XanoValidationError,
)


class XanoClientTests(unittest.TestCase):
    def test_logs_do_not_include_credentials_or_patient_payload(self) -> None:
        records: list[str] = []

        class CaptureHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record.getMessage())

        handler = CaptureHandler()
        logger = logging.getLogger("gestao_hospitalar")
        logger.addHandler(handler)
        try:
            client = XanoClient(
                XanoConfig("https://example.xano.io/api:test", None, 5),
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(
                        200,
                        json={
                            "authToken": "remote-token",
                            "user_id": 7,
                            "papel": "admin",
                        },
                    )
                ),
            )

            client.login("usuario-real", "senha-secreta")

            texto = " ".join(records)
            self.assertNotIn("senha-secreta", texto)
            self.assertNotIn("remote-token", texto)
            self.assertNotIn("usuario-real", texto)
        finally:
            logger.removeHandler(handler)

    def test_login_returns_public_user_data(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/api:test/auth/login")
            self.assertEqual(request.headers["authorization"], "Bearer api-token")
            return httpx.Response(
                200,
                json={"authToken": "remote-token", "user_id": 7, "papel": "admin"},
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", "api-token", 5),
            transport=httpx.MockTransport(handler),
        )

        usuario = client.login("admin", "senha")

        self.assertEqual(usuario.usuario_id, 7)
        self.assertEqual(usuario.papel, "admin")
        self.assertEqual(usuario.auth_token, "remote-token")

    def test_patient_operations_use_session_token(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 12})
            if request.url.path.endswith("/12"):
                return httpx.Response(200, json={"id": 12, "nome": "Ana"})
            return httpx.Response(200, json={"items": [{"id": 12, "nome": "Ana"}]})

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        paciente_id = client.criar_paciente(
            "user-token",
            {"nome": "Ana", "cpf": "52998224725"},
        )
        pacientes = client.listar_pacientes("user-token")
        paciente = client.consultar_paciente("user-token", paciente_id)

        self.assertEqual(paciente_id, 12)
        self.assertEqual(pacientes[0]["nome"], "Ana")
        self.assertEqual(paciente["id"], 12)
        self.assertTrue(all(request.headers["authorization"] == "user-token" for request in requests))

    def test_patient_creation_maps_validation_error(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(409)
            ),
        )

        with self.assertRaises(XanoValidationError):
            client.criar_paciente("user-token", {"cpf": "52998224725"})

    def test_patient_creation_does_not_retry_unknown_write_result(self) -> None:
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            attempts += 1
            raise httpx.ReadTimeout("timeout")

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        with self.assertRaises(XanoUnavailableError):
            client.criar_paciente("user-token", {"cpf": "52998224725"})

        self.assertEqual(attempts, 1)

    def test_patient_list_matches_xano_curl_contract(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api:test/patients")
            self.assertEqual(request.url.query, b"")
            self.assertEqual(request.headers["authorization"], "session-token")
            return httpx.Response(
                200,
                json={
                    "itemsReceived": 1,
                    "curPage": 1,
                    "itemsTotal": 1,
                    "items": [
                        {
                            "id": 1,
                            "nome": "Victor Ribeiro Santos",
                            "data_nascimento": "2008-02-09",
                            "telefone": "11988437634",
                        }
                    ],
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        self.assertEqual(
            client.listar_pacientes("session-token"),
            [
                {
                    "id": 1,
                    "nome": "Victor Ribeiro Santos",
                    "data_nascimento": "2008-02-09",
                    "telefone": "11988437634",
                }
            ],
        )

    def test_doctor_operations_use_session_token(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 21})
            if request.url.path.endswith("/21"):
                return httpx.Response(200, json={"id": 21, "nome": "Dra. Ana"})
            return httpx.Response(200, json={"items": [{"id": 21, "nome": "Dra. Ana"}]})

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        medico_id = client.criar_medico(
            "doctor-token",
            {"nome": "Dra. Ana", "crm": "1234567/SP"},
        )
        medicos = client.listar_medicos("doctor-token")
        medico = client.consultar_medico("doctor-token", medico_id)

        self.assertEqual(medico_id, 21)
        self.assertEqual(medicos[0]["nome"], "Dra. Ana")
        self.assertEqual(medico["id"], 21)
        self.assertTrue(
            all(request.headers["authorization"] == "doctor-token" for request in requests)
        )
        self.assertEqual(requests[1].url.query, b"")

    def test_login_rejects_invalid_credentials(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(403)
            ),
        )

        with self.assertRaises(XanoAuthenticationError):
            client.login("admin", "senha")

    def test_login_rejects_invalid_response(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"user_id": 7})
            ),
        )

        with self.assertRaises(XanoResponseError):
            client.login("admin", "senha")

    def test_login_maps_timeout_to_unavailable_error(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timeout")

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        with self.assertRaises(XanoUnavailableError):
            client.login("admin", "senha")

    def test_config_requires_api_url(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(XanoConfigurationError):
                XanoConfig.from_env()


if __name__ == "__main__":
    unittest.main()
