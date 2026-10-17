"""Cliente de persistencia para a API do Xano."""

from dataclasses import dataclass
import os
import threading
import time
from collections import deque
from typing import Any
from urllib.parse import urlparse

import httpx

from gestao_hospitalar.logging_config import get_logger


logger = get_logger("xano_client")


class XanoError(Exception):
    """Erro base para falhas de comunicacao com o Xano."""


class XanoConfigurationError(XanoError):
    """Configuracao obrigatoria ausente ou invalida."""


class XanoAuthenticationError(XanoError):
    """Credencial rejeitada pelo Xano."""


class XanoUnavailableError(XanoError):
    """Xano indisponivel ou sem resposta dentro do timeout."""


class XanoResponseError(XanoError):
    """Resposta do Xano ausente ou em formato inesperado."""


class XanoSessionExpiredError(XanoAuthenticationError):
    """Token da sessao recusado (401): o usuario precisa entrar de novo."""


class XanoValidationError(XanoError):
    """Entrada rejeitada pela API do Xano."""


@dataclass(frozen=True)
class XanoConfig:
    """Configuracao necessaria para consumir a API do Xano."""

    base_url: str
    api_token: str | None
    timeout_seconds: float
    max_tentativas: int = 3
    # Limite do plano do Xano por janela de tempo (0 desliga o controle local).
    limite_requisicoes: int = 0
    janela_segundos: float = 20.0

    @classmethod
    def from_env(cls) -> "XanoConfig":
        base_url = os.getenv("XANO_API_URL", "").strip().rstrip("/")
        if not base_url:
            raise XanoConfigurationError("XANO_API_URL nao configurada.")

        parsed_url = urlparse(base_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise XanoConfigurationError("XANO_API_URL invalida.")

        timeout_text = os.getenv("XANO_TIMEOUT_SECONDS", "10").strip()
        try:
            timeout_seconds = float(timeout_text)
        except ValueError as error:
            raise XanoConfigurationError(
                "XANO_TIMEOUT_SECONDS invalido."
            ) from error
        if timeout_seconds <= 0:
            raise XanoConfigurationError(
                "XANO_TIMEOUT_SECONDS deve ser maior que zero."
            )

        tentativas_texto = os.getenv("XANO_MAX_TENTATIVAS", "3").strip()
        try:
            max_tentativas = int(tentativas_texto)
        except ValueError as error:
            raise XanoConfigurationError("XANO_MAX_TENTATIVAS invalido.") from error
        if not 1 <= max_tentativas <= 5:
            raise XanoConfigurationError(
                "XANO_MAX_TENTATIVAS deve estar entre 1 e 5."
            )

        limite_texto = os.getenv("XANO_LIMITE_REQUISICOES", "8").strip()
        janela_texto = os.getenv("XANO_JANELA_SEGUNDOS", "20").strip()
        try:
            limite_requisicoes = int(limite_texto)
            janela_segundos = float(janela_texto)
        except ValueError as error:
            raise XanoConfigurationError(
                "XANO_LIMITE_REQUISICOES ou XANO_JANELA_SEGUNDOS invalido."
            ) from error
        if not 0 <= limite_requisicoes <= 100:
            raise XanoConfigurationError(
                "XANO_LIMITE_REQUISICOES deve estar entre 0 e 100."
            )
        if not 1 <= janela_segundos <= 120:
            raise XanoConfigurationError(
                "XANO_JANELA_SEGUNDOS deve estar entre 1 e 120."
            )

        api_token = os.getenv("XANO_API_TOKEN", "").strip() or None
        return cls(
            base_url,
            api_token,
            timeout_seconds,
            max_tentativas,
            limite_requisicoes,
            janela_segundos,
        )


@dataclass(frozen=True)
class UsuarioRemoto:
    """Dados publicos devolvidos pelo login do sistema."""

    usuario_id: int
    papel: str
    auth_token: str


# Leituras repetidas apenas para GET (idempotente); escritas nunca se repetem.
STATUS_REPETIVEIS = {429, 502, 503, 504}
ESPERA_BASE_SEGUNDOS = 0.5
ESPERA_MAXIMA_SEGUNDOS = 5.0
# O 429 do Xano vem de uma janela de tempo: esperar pouco só gasta a cota de novo.
ESPERA_BASE_429_SEGUNDOS = 2.0
ESPERA_MAXIMA_429_SEGUNDOS = 30.0
TIMEOUT_CONEXAO_SEGUNDOS = 5.0
# O Xano limita requisicoes por janela de tempo (429); poucas em paralelo
# evitam as rajadas do painel, que le varios recursos de uma vez.
_LIMITE_CONCORRENCIA = threading.BoundedSemaphore(3)

# Uma conexao (e um TLS) reaproveitada entre as leituras, por endereco e timeout.
_CLIENTES_HTTP: dict[tuple[str, float], httpx.Client] = {}
_TRAVA_CLIENTES = threading.Lock()


def _dormir(segundos: float) -> None:
    time.sleep(segundos)


class _Limitador:
    """Janela deslizante de requisições, compartilhada por todas as threads.

    Cada requisição reserva a sua vez (sem laço de espera): o instante de envio
    respeita o limite por janela e uma pausa coordenada, aberta quando o Xano
    devolve 429, para que as demais threads também esperem em vez de insistir.
    """

    def __init__(self) -> None:
        self._trava = threading.Lock()
        self._envios: deque[float] = deque()
        self._pausa_ate = 0.0

    def esperar_vez(self, limite: int, janela: float, pausa: float = 0.0) -> None:
        with self._trava:
            agora = time.monotonic()
            meu_fim = 0.0
            if pausa > 0:
                meu_fim = agora + pausa
                self._pausa_ate = max(self._pausa_ate, meu_fim)
            espera = pausa if pausa > 0 else max(0.0, self._pausa_ate - agora)
            if limite > 0:
                while self._envios and self._envios[0] + janela <= agora:
                    self._envios.popleft()
                if len(self._envios) >= limite:
                    espera = max(espera, self._envios[-limite] + janela - agora)
                envio = max(agora + espera, self._envios[-1] if self._envios else 0.0)
                espera = envio - agora
                self._envios.append(envio)
        if espera > 0:
            _dormir(espera)
        if meu_fim:
            with self._trava:
                # a pausa já foi cumprida por quem a abriu: não repete para a mesma thread
                if self._pausa_ate == meu_fim:
                    self._pausa_ate = min(meu_fim, time.monotonic())


_LIMITADOR = _Limitador()


def _cliente_http(config: XanoConfig) -> httpx.Client:
    chave = (config.base_url, config.timeout_seconds)
    with _TRAVA_CLIENTES:
        cliente = _CLIENTES_HTTP.get(chave)
        if cliente is None or cliente.is_closed:
            cliente = httpx.Client(
                base_url=config.base_url,
                timeout=httpx.Timeout(
                    config.timeout_seconds,
                    connect=min(TIMEOUT_CONEXAO_SEGUNDOS, config.timeout_seconds),
                ),
            )
            _CLIENTES_HTTP[chave] = cliente
        return cliente


def _espera_da_tentativa(tentativa: int, response: httpx.Response | None) -> float:
    """Espera crescente (0,5 s, 1 s, 2 s...), respeitando o Retry-After do Xano."""
    limitado = response is not None and response.status_code == 429
    teto = ESPERA_MAXIMA_429_SEGUNDOS if limitado else ESPERA_MAXIMA_SEGUNDOS
    if response is not None:
        try:
            pedido = float(response.headers.get("Retry-After", ""))
        except ValueError:
            pedido = 0.0
        if pedido > 0:
            return min(pedido, teto)
    if limitado:
        return min(
            ESPERA_BASE_429_SEGUNDOS * (2 ** (tentativa - 1)), ESPERA_MAXIMA_429_SEGUNDOS
        )
    return min(ESPERA_BASE_SEGUNDOS * (2 ** (tentativa - 1)), ESPERA_MAXIMA_SEGUNDOS)


POR_PAGINA_PADRAO = 25
POR_PAGINA_REFERENCIA = 100
LIMITE_REGISTROS_REFERENCIA = 2000


class XanoClient:
    """Acesso aos endpoints do Xano sem acoplar o State ao transporte HTTP."""

    def __init__(
        self,
        config: XanoConfig,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport

    def _headers(self, auth_token: str | None = None) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if auth_token:
            headers["Authorization"] = auth_token
        elif self.config.api_token:
            headers["Authorization"] = self.config.api_token
        return headers

    def _enviar(
        self,
        method: str,
        path: str,
        auth_token: str | None,
        **kwargs: Any,
    ) -> httpx.Response:
        headers = self._headers(auth_token)
        if self.transport is not None:
            with httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
                transport=self.transport,
            ) as client:
                return client.request(method, path, headers=headers, **kwargs)
        return _cliente_http(self.config).request(
            method, path, headers=headers, **kwargs
        )

    def _request(
        self,
        method: str,
        path: str,
        *,
        auth_token: str | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        started_at = time.monotonic()
        logger.info(
            "xano_request_start method=%s path=%s auth=%s params=%s",
            method,
            path,
            bool(auth_token or self.config.api_token),
            sorted((kwargs.get("params") or {}).keys()),
        )
        # Só leituras são repetidas: uma escrita sem resposta pode ter sido gravada.
        limite = self.config.max_tentativas if method.upper() == "GET" else 1
        tentativa = 0
        while True:
            tentativa += 1
            response = None
            falha: Exception | None = None
            _LIMITADOR.esperar_vez(
                self.config.limite_requisicoes, self.config.janela_segundos
            )
            try:
                with _LIMITE_CONCORRENCIA:
                    response = self._enviar(method, path, auth_token, **kwargs)
            except httpx.TimeoutException as error:
                motivo = "timeout"
                # Timeout já gastou a espera inteira: repete no máximo uma vez.
                esgotou = tentativa >= min(limite, 2)
                falha = error
            except httpx.RequestError as error:
                motivo = type(error).__name__
                esgotou = tentativa >= limite
                falha = error
            else:
                motivo = f"status_{response.status_code}"
                esgotou = (
                    response.status_code not in STATUS_REPETIVEIS
                    or tentativa >= limite
                )

            if esgotou:
                if response is not None:
                    logger.info(
                        "xano_request_end method=%s path=%s status=%s elapsed_ms=%d attempts=%d",
                        method,
                        path,
                        response.status_code,
                        int((time.monotonic() - started_at) * 1000),
                        tentativa,
                    )
                    if auth_token and response.status_code == 401:
                        raise XanoSessionExpiredError("Sessao expirada.")
                    return response
                logger.warning(
                    "xano_request_error method=%s path=%s error=%s attempts=%d",
                    method,
                    path,
                    motivo,
                    tentativa,
                )
                raise XanoUnavailableError(
                    "Xano temporariamente indisponivel."
                ) from falha

            espera = _espera_da_tentativa(tentativa, response)
            logger.warning(
                "xano_request_retry method=%s path=%s reason=%s attempt=%d wait_ms=%d retry_after=%s",
                method,
                path,
                motivo,
                tentativa,
                int(espera * 1000),
                response.headers.get("Retry-After", "-") if response is not None else "-",
            )
            if response is not None and response.status_code == 429:
                # pausa coordenada: as outras threads também esperam a janela do Xano
                _LIMITADOR.esperar_vez(
                    self.config.limite_requisicoes,
                    self.config.janela_segundos,
                    pausa=espera,
                )
            else:
                _dormir(espera)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in {401, 403}:
            raise XanoAuthenticationError("Credenciais invalidas.")
        if response.status_code in {400, 409}:
            mensagem = "Dados rejeitados pelo Xano."
            try:
                payload = response.json()
            except ValueError:
                payload = None
            if isinstance(payload, dict):
                detalhe = payload.get("message") or payload.get("error")
                if isinstance(detalhe, str) and detalhe.strip():
                    mensagem = detalhe.strip()
            raise XanoValidationError(mensagem)
        if response.status_code == 429 or response.status_code >= 500:
            raise XanoUnavailableError("Xano temporariamente indisponivel.")
        if response.status_code >= 400:
            raise XanoError("Xano rejeitou a requisicao.")

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    @staticmethod
    def _extract_records(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list) and all(
            isinstance(item, dict) for item in payload
        ):
            return payload
        if isinstance(payload, dict) and "items" in payload:
            return XanoClient._extract_records(payload["items"])
        raise XanoResponseError("Resposta invalida do Xano.")

    def _listar_pagina(
        self,
        path: str,
        auth_token: str,
        page: int,
        per_page: int,
    ) -> tuple[list[dict[str, Any]], int | None]:
        """Uma página e o total do Xano (None se o endpoint não for paginado).

        A primeira página padrão não envia parâmetros, mantendo o contrato já
        validado com o Xano.
        """
        response = self._request(
            "GET",
            path,
            auth_token=auth_token,
            params=(
                {"page": page, "per_page": per_page}
                if (page, per_page) != (1, POR_PAGINA_PADRAO)
                else None
            ),
        )
        self._raise_for_status(response)
        payload = self._json(response)
        total = None
        if isinstance(payload, dict):
            valor = payload.get("itemsTotal")
            if isinstance(valor, int) and not isinstance(valor, bool):
                total = valor
        return self._extract_records(payload), total

    def _listar_todos(self, path: str, auth_token: str) -> list[dict[str, Any]]:
        """Percorre as páginas (limite de segurança) para listas de referência."""
        todos: list[dict[str, Any]] = []
        primeiro_anterior = None
        page = 1
        while len(todos) < LIMITE_REGISTROS_REFERENCIA:
            registros, total = self._listar_pagina(
                path, auth_token, page, POR_PAGINA_REFERENCIA
            )
            if not registros or registros[0] == primeiro_anterior:
                break
            todos.extend(registros)
            primeiro_anterior = registros[0]
            if total is not None:
                if len(todos) >= total:
                    break
            elif len(registros) < POR_PAGINA_REFERENCIA:
                break
            page += 1
        return todos[:LIMITE_REGISTROS_REFERENCIA]

    def _contar(self, path: str, auth_token: str) -> int:
        """Total de registros sem baixar a lista: usa o total da paginação do Xano.

        Se o endpoint não for paginado (ou ignorar per_page), cai na lista
        completa, que é a única forma de contar nesse caso.
        """
        registros, total = self._listar_pagina(path, auth_token, 1, 1)
        if total is not None:
            return total
        if len(registros) > 1:
            return len(registros)
        registros, _ = self._listar_pagina(path, auth_token, 1, POR_PAGINA_PADRAO)
        return len(registros)

    def contar_pacientes(self, auth_token: str) -> int:
        return self._contar("/patients", auth_token)

    def contar_medicos(self, auth_token: str) -> int:
        return self._contar("/doctors", auth_token)

    def contar_atendimentos(self, auth_token: str) -> int:
        return self._contar("/atendimentos", auth_token)

    def login(self, login: str, senha: str) -> UsuarioRemoto:
        response = self._request(
            "POST",
            "/auth/login",
            json={"login": login, "password": senha},
        )
        self._raise_for_status(response)

        try:
            payload: Any = self._json(response)
            usuario_id = int(payload["user_id"])
            papel = str(payload["papel"])
            auth_token = str(payload["authToken"])
        except (ValueError, KeyError, TypeError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

        if not papel or not auth_token:
            raise XanoResponseError("Resposta invalida do Xano.")
        return UsuarioRemoto(
            usuario_id=usuario_id,
            papel=papel,
            auth_token=auth_token,
        )

    def criar_paciente(
        self,
        auth_token: str,
        dados: dict[str, str],
    ) -> int:
        response = self._request(
            "POST",
            "/patients",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def criar_medico(
        self,
        auth_token: str,
        dados: dict[str, str],
    ) -> int:
        response = self._request(
            "POST",
            "/doctors",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def listar_medicos_pagina(
        self,
        auth_token: str,
        page: int = 1,
        per_page: int = POR_PAGINA_PADRAO,
    ) -> tuple[list[dict[str, Any]], int | None]:
        return self._listar_pagina("/doctors", auth_token, page, per_page)

    def listar_todos_medicos(self, auth_token: str) -> list[dict[str, Any]]:
        return self._listar_todos("/doctors", auth_token)

    def consultar_medico(
        self,
        auth_token: str,
        medico_id: int,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/doctors/{medico_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        if not isinstance(payload, dict):
            raise XanoResponseError("Resposta invalida do Xano.")
        return payload

    def criar_convenio(
        self,
        auth_token: str,
        dados: dict[str, str],
    ) -> int:
        response = self._request(
            "POST",
            "/convenios",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def listar_convenios(
        self,
        auth_token: str,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/convenios",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

    def consultar_convenio(
        self,
        auth_token: str,
        convenio_id: int,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/convenios/{convenio_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        if not isinstance(payload, dict):
            raise XanoResponseError("Resposta invalida do Xano.")
        return payload

    def atualizar_convenio(
        self,
        auth_token: str,
        convenio_id: int,
        dados: dict[str, str],
    ) -> None:
        response = self._request(
            "PATCH",
            f"/convenios/{convenio_id}",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)

    def excluir_convenio(
        self,
        auth_token: str,
        convenio_id: int,
    ) -> None:
        response = self._request(
            "DELETE",
            f"/convenios/{convenio_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)

    def listar_pacientes_pagina(
        self,
        auth_token: str,
        page: int = 1,
        per_page: int = POR_PAGINA_PADRAO,
    ) -> tuple[list[dict[str, Any]], int | None]:
        registros, total = self._listar_pagina("/patients", auth_token, page, per_page)
        logger.info(
            "xano_patient_list page=%s record_count=%s total=%s",
            page,
            len(registros),
            total,
        )
        return registros, total

    def listar_todos_pacientes(self, auth_token: str) -> list[dict[str, Any]]:
        return self._listar_todos("/patients", auth_token)

    def consultar_paciente(
        self,
        auth_token: str,
        paciente_id: int,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/patients/{paciente_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        if not isinstance(payload, dict):
            raise XanoResponseError("Resposta invalida do Xano.")
        return payload

    def criar_atendimento(
        self,
        auth_token: str,
        dados: dict[str, Any],
    ) -> int:
        response = self._request(
            "POST",
            "/atendimentos",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    @staticmethod
    def _normalizar_atendimento(registro: dict[str, Any]) -> dict[str, Any]:
        atendimento = {
            chave: valor
            for chave, valor in registro.items()
            if chave not in {"paciente", "medico", "convenio"}
        }
        paciente = registro.get("paciente")
        medico = registro.get("medico")
        convenio = registro.get("convenio")
        atendimento["paciente_nome"] = (
            str(paciente.get("nome", ""))
            if isinstance(paciente, dict)
            else f"#{atendimento.get('paciente_id', '')}"
        )
        atendimento["medico_nome"] = (
            str(medico.get("nome", ""))
            if isinstance(medico, dict)
            else f"#{atendimento.get('medico_id', '')}"
        )
        atendimento["convenio_nome"] = (
            str(convenio.get("nome", ""))
            if isinstance(convenio, dict)
            else "Nao informado"
        )
        return atendimento

    def listar_atendimentos(
        self,
        auth_token: str,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/atendimentos",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return [
            self._normalizar_atendimento(registro)
            for registro in self._extract_records(self._json(response))
        ]

    def listar_todos_atendimentos(self, auth_token: str) -> list[dict[str, Any]]:
        """Todos os atendimentos (percorre páginas, com limite), já normalizados."""
        return [
            self._normalizar_atendimento(registro)
            for registro in self._listar_todos("/atendimentos", auth_token)
        ]

    def consultar_atendimento(
        self,
        auth_token: str,
        atendimento_id: int,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/atendimentos/{atendimento_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        if not isinstance(payload, dict):
            raise XanoResponseError("Resposta invalida do Xano.")
        return self._normalizar_atendimento(payload)

    def listar_atendimentos_internaveis(
        self,
        auth_token: str,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/atendimentos/opcoes-internacao",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        opcoes: list[dict[str, Any]] = []
        for registro in self._extract_records(self._json(response)):
            internacao = registro.get("internacao")
            if isinstance(internacao, dict) and internacao.get("id"):
                continue
            paciente = registro.get("paciente")
            opcao = {
                chave: valor
                for chave, valor in registro.items()
                if chave not in {"paciente", "internacao"}
            }
            opcao["paciente_nome"] = (
                str(paciente.get("nome", ""))
                if isinstance(paciente, dict)
                else f"#{opcao.get('paciente_id', '')}"
            )
            opcoes.append(opcao)
        return opcoes

    def criar_diagnostico(
        self,
        auth_token: str,
        dados: dict[str, Any],
    ) -> int:
        response = self._request(
            "POST",
            "/diagnosticos",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    @staticmethod
    def _normalizar_diagnostico(registro: dict[str, Any]) -> dict[str, Any]:
        return {
            chave: valor
            for chave, valor in registro.items()
            if chave not in {"atendimento"}
        }

    def listar_diagnosticos(
        self,
        auth_token: str,
        atendimento_id: int,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            f"/diagnosticos/{atendimento_id}",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return [
            self._normalizar_diagnostico(registro)
            for registro in self._extract_records(self._json(response))
        ]

    def criar_leito(
        self,
        auth_token: str,
        numero: int,
    ) -> int:
        response = self._request(
            "POST",
            "/leitos",
            auth_token=auth_token,
            json={"numero": numero},
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def listar_leitos(self, auth_token: str) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/leitos",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

    def criar_internacao(
        self,
        auth_token: str,
        dados: dict[str, Any],
    ) -> int:
        response = self._request(
            "POST",
            "/internacoes",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def listar_internacoes(self, auth_token: str) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/internacoes",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

    def registrar_alta(
        self,
        auth_token: str,
        internacao_id: int,
        data_saida: str,
    ) -> None:
        response = self._request(
            "POST",
            f"/internacoes/{internacao_id}/alta",
            auth_token=auth_token,
            json={"data_saida": data_saida},
        )
        self._raise_for_status(response)

    def criar_transferencia(
        self,
        auth_token: str,
        dados: dict[str, Any],
    ) -> int:
        response = self._request(
            "POST",
            "/transferencias",
            auth_token=auth_token,
            json=dados,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        try:
            return int(payload["id"])
        except (KeyError, TypeError, ValueError) as error:
            raise XanoResponseError("Resposta invalida do Xano.") from error

    def listar_transferencias(
        self,
        auth_token: str,
        internacao_id: int,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            f"/internacoes/{internacao_id}/transferencias",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

    def listar_pacientes_historico(
        self,
        auth_token: str,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/patients/opcoes-historico",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

    def consultar_historico(
        self,
        auth_token: str,
        paciente_id: int,
    ) -> dict[str, Any]:
        response = self._request(
            "GET",
            f"/patients/{paciente_id}/historico",
            auth_token=auth_token,
        )
        self._raise_for_status(response)
        payload = self._json(response)
        if not isinstance(payload, dict):
            raise XanoResponseError("Resposta invalida do Xano.")
        return payload
