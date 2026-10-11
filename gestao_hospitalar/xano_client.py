"""Cliente de persistencia para a API do Xano."""

from dataclasses import dataclass
import os
import time
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


class XanoValidationError(XanoError):
    """Entrada rejeitada pela API do Xano."""


@dataclass(frozen=True)
class XanoConfig:
    """Configuracao necessaria para consumir a API do Xano."""

    base_url: str
    api_token: str | None
    timeout_seconds: float

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

        api_token = os.getenv("XANO_API_TOKEN", "").strip() or None
        return cls(base_url, api_token, timeout_seconds)


@dataclass(frozen=True)
class UsuarioRemoto:
    """Dados publicos devolvidos pelo login do sistema."""

    usuario_id: int
    papel: str
    auth_token: str


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
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        return headers

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
        try:
            with httpx.Client(
                base_url=self.config.base_url,
                headers=self._headers(auth_token),
                timeout=self.config.timeout_seconds,
                transport=self.transport,
            ) as client:
                response = client.request(method, path, **kwargs)
                logger.info(
                    "xano_request_end method=%s path=%s status=%s elapsed_ms=%d",
                    method,
                    path,
                    response.status_code,
                    int((time.monotonic() - started_at) * 1000),
                )
                return response
        except httpx.TimeoutException as error:
            logger.warning(
                "xano_request_error method=%s path=%s error=timeout",
                method,
                path,
            )
            raise XanoUnavailableError("Xano temporariamente indisponivel.") from error
        except httpx.RequestError as error:
            logger.warning(
                "xano_request_error method=%s path=%s error=%s",
                method,
                path,
                type(error).__name__,
            )
            raise XanoUnavailableError("Xano temporariamente indisponivel.") from error

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code in {401, 403}:
            raise XanoAuthenticationError("Credenciais invalidas.")
        if response.status_code in {400, 409}:
            raise XanoValidationError("Dados rejeitados pelo Xano.")
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

    def listar_medicos(
        self,
        auth_token: str,
        page: int = 1,
        per_page: int = 25,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/doctors",
            auth_token=auth_token,
            params=(
                {"page": page, "per_page": per_page}
                if (page, per_page) != (1, 25)
                else None
            ),
        )
        self._raise_for_status(response)
        return self._extract_records(self._json(response))

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

    def listar_pacientes(
        self,
        auth_token: str,
        page: int = 1,
        per_page: int = 25,
    ) -> list[dict[str, Any]]:
        response = self._request(
            "GET",
            "/patients",
            auth_token=auth_token,
            params=(
                {"page": page, "per_page": per_page}
                if (page, per_page) != (1, 25)
                else None
            ),
        )
        self._raise_for_status(response)
        payload = self._json(response)
        records = self._extract_records(payload)
        logger.info(
            "xano_patient_list payload_type=%s record_count=%s",
            type(payload).__name__,
            len(records),
        )
        return records

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
