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
        sentinels = {
            "senha": "SENHA_SENTINELA_9d60",
            "token": "TOKEN_SENTINELA_2f18",
            "cpf": "52998224725",
            "telefone": "11987654321",
            "endereco": "ENDERECO_SENTINELA_73ab",
            "contato": "CONTATO_SENTINELA_54ce",
        }

        class CaptureHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                records.append(record.getMessage())

        log_handler = CaptureHandler()
        logger = logging.getLogger("gestao_hospitalar")
        logger.addHandler(log_handler)
        try:
            def transport_handler(request: httpx.Request) -> httpx.Response:
                if request.url.path.endswith("/auth/login"):
                    return httpx.Response(
                        200,
                        json={
                            "authToken": sentinels["token"],
                            "user_id": 7,
                            "papel": "admin",
                        },
                    )
                return httpx.Response(201, json={"id": 12})

            client = XanoClient(
                XanoConfig(
                    "https://example.xano.io/api:test",
                    "api-token-secreto",
                    5,
                ),
                transport=httpx.MockTransport(transport_handler),
            )

            client.login("usuario-real", sentinels["senha"])
            client.criar_paciente(
                sentinels["token"],
                {
                    "nome": "Paciente Sentinela",
                    "cpf": sentinels["cpf"],
                    "data_nascimento": "1990-01-01",
                    "telefone": sentinels["telefone"],
                    "endereco": sentinels["endereco"],
                    "contato_emergencia": sentinels["contato"],
                },
            )

            texto = " ".join(records)
            for sentinel in sentinels.values():
                self.assertNotIn(sentinel, texto)
            self.assertNotIn("api-token-secreto", texto)
            self.assertNotIn("usuario-real", texto)
        finally:
            logger.removeHandler(log_handler)

    def test_login_returns_public_user_data(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url.path, "/api:test/auth/login")
            self.assertEqual(request.headers["authorization"], "api-token")
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
        pacientes, _ = client.listar_pacientes_pagina("user-token")
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
            client.listar_pacientes_pagina("session-token")[0],
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
        medicos, _ = client.listar_medicos_pagina("doctor-token")
        medico = client.consultar_medico("doctor-token", medico_id)

        self.assertEqual(medico_id, 21)
        self.assertEqual(medicos[0]["nome"], "Dra. Ana")
        self.assertEqual(medico["id"], 21)
        self.assertTrue(
            all(request.headers["authorization"] == "doctor-token" for request in requests)
        )
        self.assertEqual(requests[1].url.query, b"")

    def test_insurance_operations_use_session_token(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 31})
            if request.method == "PATCH":
                return httpx.Response(204)
            if request.method == "DELETE":
                return httpx.Response(204)
            if request.url.path.endswith("/31"):
                return httpx.Response(
                    200,
                    json={"id": 31, "nome": "Saude Integral"},
                )
            return httpx.Response(
                200,
                json={"items": [{"id": 31, "nome": "Saude Integral"}]},
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )
        dados = {
            "nome": "Saude Integral",
            "nome_normalizado": "saude integral",
            "tipo": "plano",
            "cobertura": "Consultas",
        }

        convenio_id = client.criar_convenio("insurance-token", dados)
        convenios = client.listar_convenios("insurance-token")
        convenio = client.consultar_convenio("insurance-token", convenio_id)
        client.atualizar_convenio("insurance-token", convenio_id, dados)
        client.excluir_convenio("insurance-token", convenio_id)

        self.assertEqual(convenio_id, 31)
        self.assertEqual(convenios[0]["nome"], "Saude Integral")
        self.assertEqual(convenio["id"], 31)
        self.assertTrue(
            all(
                request.headers["authorization"] == "insurance-token"
                for request in requests
            )
        )

    def test_insurance_creation_maps_validation_error(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(409)
            ),
        )

        with self.assertRaises(XanoValidationError):
            client.criar_convenio("user-token", {"nome": "Saude Integral"})

    def test_attendance_operations_use_session_token_and_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 41})
            if request.url.path.endswith("/41"):
                return httpx.Response(
                    200,
                    json={
                        "id": 41,
                        "tipo": "consulta",
                        "paciente_id": 1,
                        "medico_id": 2,
                        "paciente": {"nome": "Ana Ribeiro"},
                        "medico": {"nome": "Dra. Beatriz Lima"},
                        "convenio": {"nome": "Integral"},
                    },
                )
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 41,
                            "tipo": "consulta",
                            "paciente_id": 1,
                            "medico_id": 2,
                            "paciente": {"nome": "Ana Ribeiro"},
                            "medico": {"nome": "Dra. Beatriz Lima"},
                            "convenio": {"nome": "Integral"},
                        }
                    ]
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )
        dados = {
            "paciente_id": 1,
            "medico_id": 2,
            "convenio_id": None,
            "data_atendimento": "2026-10-12",
            "motivo": "Consulta de retorno",
            "tipo": "retorno",
        }

        atendimento_id = client.criar_atendimento("attendance-token", dados)
        atendimentos = client.listar_atendimentos("attendance-token")
        atendimento = client.consultar_atendimento("attendance-token", atendimento_id)

        self.assertEqual(atendimento_id, 41)
        self.assertEqual(atendimentos[0]["id"], 41)
        self.assertEqual(atendimentos[0]["paciente_nome"], "Ana Ribeiro")
        self.assertEqual(atendimentos[0]["medico_nome"], "Dra. Beatriz Lima")
        self.assertEqual(atendimentos[0]["convenio_nome"], "Integral")
        self.assertEqual(atendimento["tipo"], "consulta")
        self.assertEqual(atendimento["paciente_nome"], "Ana Ribeiro")
        self.assertTrue(
            all(
                request.headers["authorization"] == "attendance-token"
                for request in requests
            )
        )
        self.assertEqual(requests[0].url.path, "/api:test/atendimentos")
        self.assertEqual(requests[1].url.query, b"")

    def test_attendance_creation_maps_validation_error(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(400)
            ),
        )

        with self.assertRaises(XanoValidationError):
            client.criar_atendimento("user-token", {"tipo": "invalido"})

    def test_diagnosis_operations_use_session_token_and_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 51})
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 51,
                            "atendimento_id": 41,
                            "descricao": "Hipertensao",
                            "codigo_cid": "I10",
                            "data_diagnostico": "2026-10-13",
                        }
                    ]
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )
        dados = {
            "atendimento_id": 41,
            "descricao": "Hipertensao",
            "codigo_cid": "I10",
            "data_diagnostico": "2026-10-13",
        }

        diagnostico_id = client.criar_diagnostico("diagnosis-token", dados)
        diagnosticos = client.listar_diagnosticos("diagnosis-token", 41)

        self.assertEqual(diagnostico_id, 51)
        self.assertEqual(diagnosticos[0]["codigo_cid"], "I10")
        self.assertTrue(
            all(
                request.headers["authorization"] == "diagnosis-token"
                for request in requests
            )
        )
        self.assertEqual(requests[0].url.path, "/api:test/diagnosticos")
        self.assertEqual(requests[1].url.path, "/api:test/diagnosticos/41")

    def test_diagnosis_creation_maps_validation_error(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(400)
            ),
        )

        with self.assertRaises(XanoValidationError):
            client.criar_diagnostico("user-token", {"atendimento_id": 0})

    def test_admission_operations_use_session_token_and_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.url.path.endswith("/leitos") and request.method == "POST":
                return httpx.Response(201, json={"id": 61})
            if request.url.path.endswith("/internacoes") and request.method == "POST":
                return httpx.Response(201, json={"id": 71})
            if request.url.path.endswith("/alta"):
                return httpx.Response(200, json={"id": 71, "status": "alta"})
            if request.url.path.endswith("/leitos"):
                return httpx.Response(
                    200,
                    json={"items": [{"id": 61, "numero": 101, "status": "livre"}]},
                )
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 71,
                            "atendimento_id": 41,
                            "paciente_id": 1,
                            "leito_id": 61,
                            "data_entrada": "2026-10-13",
                            "data_saida": None,
                            "status": "internado",
                        }
                    ]
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        leito_id = client.criar_leito("admission-token", 101)
        leitos = client.listar_leitos("admission-token")
        internacao_id = client.criar_internacao(
            "admission-token",
            {
                "atendimento_id": 41,
                "leito_id": leito_id,
                "data_entrada": "2026-10-13",
            },
        )
        internacoes = client.listar_internacoes("admission-token")
        client.registrar_alta("admission-token", internacao_id, "2026-10-14")

        self.assertEqual(leitos[0]["status"], "livre")
        self.assertEqual(internacoes[0]["status"], "internado")
        self.assertTrue(
            all(
                request.headers["authorization"] == "admission-token"
                for request in requests
            )
        )
        self.assertEqual(requests[0].url.path, "/api:test/leitos")
        self.assertEqual(requests[2].url.path, "/api:test/internacoes")
        self.assertEqual(requests[4].url.path, "/api:test/internacoes/71/alta")

    def test_admission_creation_maps_validation_error(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(409)
            ),
        )

        with self.assertRaises(XanoValidationError):
            client.criar_internacao("user-token", {"leito_id": 61})

    def test_internable_attendance_options_hide_existing_admissions(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.path, "/api:test/atendimentos/opcoes-internacao")
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 2,
                            "paciente_id": 1,
                            "data_atendimento": "2026-10-13",
                            "motivo": "Febre",
                            "tipo": "emergencia",
                            "paciente": {"nome": "Ana Ribeiro"},
                            "internacao": {},
                        },
                        {
                            "id": 1,
                            "paciente_id": 1,
                            "data_atendimento": "2026-10-12",
                            "motivo": "Dor",
                            "tipo": "consulta",
                            "paciente": {"nome": "Ana Ribeiro"},
                            "internacao": {"id": 71, "status": "alta"},
                        },
                    ]
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        opcoes = client.listar_atendimentos_internaveis("admission-token")

        self.assertEqual(len(opcoes), 1)
        self.assertEqual(opcoes[0]["id"], 2)
        self.assertEqual(opcoes[0]["paciente_nome"], "Ana Ribeiro")

    def test_validation_error_preserves_xano_message(self) -> None:
        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    409,
                    json={"message": "Atendimento invalido."},
                )
            ),
        )

        with self.assertRaisesRegex(XanoValidationError, "Atendimento invalido"):
            client.criar_internacao("user-token", {"leito_id": 61})

    def test_transfer_operations_use_session_token_and_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.method == "POST":
                return httpx.Response(201, json={"id": 81})
            return httpx.Response(
                200,
                json={
                    "items": [
                        {
                            "id": 81,
                            "internacao_id": 71,
                            "data_transferencia": "2026-10-13",
                            "destino": "UTI",
                            "motivo": "Acompanhamento medico",
                        }
                    ]
                },
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )
        dados = {
            "internacao_id": 71,
            "data_transferencia": "2026-10-13",
            "destino": "UTI",
            "motivo": "Acompanhamento medico",
        }

        transferencia_id = client.criar_transferencia("transfer-token", dados)
        transferencias = client.listar_transferencias("transfer-token", 71)

        self.assertEqual(transferencia_id, 81)
        self.assertEqual(transferencias[0]["destino"], "UTI")
        self.assertTrue(
            all(
                request.headers["authorization"] == "transfer-token"
                for request in requests
            )
        )
        self.assertEqual(requests[0].url.path, "/api:test/transferencias")
        self.assertEqual(
            requests[1].url.path,
            "/api:test/internacoes/71/transferencias",
        )

    def test_history_operations_use_session_token_and_contract(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.url.path.endswith("/opcoes-historico"):
                return httpx.Response(
                    200,
                    json={"items": [{"id": 1, "nome": "Ana Ribeiro"}]},
                )
            return httpx.Response(
                200,
                json={"paciente": {"id": 1}, "atendimentos": [], "internacoes": []},
            )

        client = XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

        pacientes = client.listar_pacientes_historico("history-token")
        historico = client.consultar_historico("history-token", 1)

        self.assertEqual(pacientes[0]["nome"], "Ana Ribeiro")
        self.assertEqual(historico["atendimentos"], [])
        self.assertTrue(
            all(
                request.headers["authorization"] == "history-token"
                for request in requests
            )
        )

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


class XanoClientPaginacaoTests(unittest.TestCase):
    @staticmethod
    def _cliente(handler) -> XanoClient:
        return XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

    def test_pagina_devolve_registros_e_total(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.query, b"page=3&per_page=25")
            return httpx.Response(
                200, json={"itemsTotal": 140, "items": [{"id": 51}, {"id": 52}]}
            )

        registros, total = self._cliente(handler).listar_pacientes_pagina(
            "token", page=3
        )

        self.assertEqual(registros, [{"id": 51}, {"id": 52}])
        self.assertEqual(total, 140)

    def test_primeira_pagina_padrao_nao_envia_parametros(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            self.assertEqual(request.url.query, b"")
            return httpx.Response(200, json=[{"id": 1}])

        registros, total = self._cliente(handler).listar_medicos_pagina("token")

        self.assertEqual(registros, [{"id": 1}])
        self.assertIsNone(total)

    def test_todos_percorre_as_paginas_ate_o_total(self) -> None:
        paginas: list[bytes] = []

        def handler(request: httpx.Request) -> httpx.Response:
            paginas.append(request.url.query)
            pagina = int(request.url.params["page"])
            itens = {1: [{"id": 1}, {"id": 2}], 2: [{"id": 3}]}[pagina]
            return httpx.Response(200, json={"itemsTotal": 3, "items": itens})

        with patch("gestao_hospitalar.xano_client.POR_PAGINA_REFERENCIA", 2):
            todos = self._cliente(handler).listar_todos_medicos("token")

        self.assertEqual([r["id"] for r in todos], [1, 2, 3])
        self.assertEqual(paginas, [b"page=1&per_page=2", b"page=2&per_page=2"])

    def test_todos_com_lista_simples_nao_repete_registros(self) -> None:
        chamadas = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chamadas
            chamadas += 1
            return httpx.Response(200, json=[{"id": 1}, {"id": 2}, {"id": 3}])

        with patch("gestao_hospitalar.xano_client.POR_PAGINA_REFERENCIA", 2):
            todos = self._cliente(handler).listar_todos_pacientes("token")

        self.assertEqual([r["id"] for r in todos], [1, 2, 3])
        self.assertEqual(chamadas, 2)

    def test_todos_respeita_o_limite_de_seguranca(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            pagina = int(request.url.params["page"])
            return httpx.Response(
                200,
                json={
                    "itemsTotal": 10_000,
                    "items": [{"id": pagina * 10 + i} for i in range(2)],
                },
            )

        with patch("gestao_hospitalar.xano_client.POR_PAGINA_REFERENCIA", 2), patch(
            "gestao_hospitalar.xano_client.LIMITE_REGISTROS_REFERENCIA", 6
        ):
            todos = self._cliente(handler).listar_todos_pacientes("token")

        self.assertEqual(len(todos), 6)

    def test_todos_com_lista_vazia(self) -> None:
        cliente = self._cliente(lambda request: httpx.Response(200, json=[]))

        self.assertEqual(cliente.listar_todos_medicos("token"), [])

class XanoClientContagemTests(unittest.TestCase):
    @staticmethod
    def _cliente(handler) -> XanoClient:
        return XanoClient(
            XanoConfig("https://example.xano.io/api:test", None, 5),
            transport=httpx.MockTransport(handler),
        )

    def test_contagem_usa_total_da_paginacao_sem_baixar_a_lista(self) -> None:
        chamadas: list[bytes] = []

        def handler(request: httpx.Request) -> httpx.Response:
            chamadas.append(request.url.query)
            self.assertEqual(request.url.path, "/api:test/patients")
            self.assertEqual(request.headers["authorization"], "session-token")
            return httpx.Response(
                200,
                json={"itemsTotal": 140, "items": [{"id": 1}]},
            )

        total = self._cliente(handler).contar_pacientes("session-token")

        self.assertEqual(total, 140)
        self.assertEqual(chamadas, [b"page=1&per_page=1"])

    def test_contagem_com_lista_simples_que_ignora_paginacao(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=[{"id": 1}, {"id": 2}, {"id": 3}])

        self.assertEqual(self._cliente(handler).contar_atendimentos("token"), 3)

    def test_contagem_com_um_registro_confirma_na_lista_completa(self) -> None:
        consultas: list[bytes] = []

        def handler(request: httpx.Request) -> httpx.Response:
            consultas.append(request.url.query)
            if request.url.query:
                return httpx.Response(200, json=[{"id": 1}])
            return httpx.Response(200, json=[{"id": 1}, {"id": 2}])

        self.assertEqual(self._cliente(handler).contar_medicos("token"), 2)
        self.assertEqual(consultas, [b"page=1&per_page=1", b""])

    def test_contagem_propaga_erro_do_xano(self) -> None:
        cliente = self._cliente(lambda request: httpx.Response(401))

        with self.assertRaises(XanoAuthenticationError):
            cliente.contar_pacientes("token")

if __name__ == "__main__":
    unittest.main()
