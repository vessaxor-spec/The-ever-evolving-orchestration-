from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping, Protocol
from urllib.error import HTTPError
from urllib.request import Request, urlopen


class ProviderConnectionError(RuntimeError):
    """Raised when a runtime connection cannot perform the authorized provider invocation."""


@dataclass(frozen=True, slots=True)
class ProviderConnectionRequest:
    """Ephemeral provider invocation details that are never part of TEO routing records."""

    operation: str
    url: str
    method: str
    headers: Mapping[str, str]
    body: bytes
    timeout_seconds: float


@dataclass(frozen=True, slots=True)
class ProviderConnectionResponse:
    status_code: int
    headers: Mapping[str, str]
    body: bytes


class ProviderConnection(Protocol):
    """Runtime-owned connection strategy, independent from TEO model routing."""

    provider_family: str

    def invoke(self, request: ProviderConnectionRequest) -> ProviderConnectionResponse:
        """Invoke the already-selected provider operation using any supported connection method."""
        ...


HttpTransport = Callable[
    [str, str, bytes, Mapping[str, str], float],
    tuple[int, Mapping[str, str], bytes],
]


def _default_http_transport(
    url: str,
    method: str,
    body: bytes,
    headers: Mapping[str, str],
    timeout_seconds: float,
) -> tuple[int, Mapping[str, str], bytes]:
    http_request = Request(url, data=body, headers=dict(headers), method=method)
    try:
        with urlopen(http_request, timeout=timeout_seconds) as response:
            return int(response.status), dict(response.headers.items()), response.read()
    except HTTPError as exc:
        response_headers = dict(exc.headers.items()) if exc.headers else {}
        return int(exc.code), response_headers, exc.read()


@dataclass(frozen=True, slots=True)
class HeaderProviderConnection:
    """HTTP connection strategy using externally resolved authorization headers.

    The caller decides how the authorization material was obtained. It may originate from
    an API key, OAuth flow, delegated identity, service account, credential broker, connector,
    or another provider-supported mechanism. TEO routing never inspects or persists it.
    """

    provider_family: str
    authorization_headers: Mapping[str, str]
    transport: HttpTransport = field(default=_default_http_transport, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.provider_family.strip():
            raise ProviderConnectionError("connection provider_family is required")
        if not self.authorization_headers:
            raise ProviderConnectionError("connection authorization headers are required")
        for key, value in self.authorization_headers.items():
            if not str(key).strip() or not str(value).strip():
                raise ProviderConnectionError("connection authorization headers cannot be empty")

    def invoke(self, request: ProviderConnectionRequest) -> ProviderConnectionResponse:
        headers = {str(key): str(value) for key, value in request.headers.items()}
        normalized_existing = {key.lower(): value for key, value in headers.items()}
        for key, value in self.authorization_headers.items():
            normalized_key = str(key).lower()
            if normalized_key in normalized_existing and normalized_existing[normalized_key] != str(value):
                raise ProviderConnectionError(
                    f"connection cannot override protocol header: {key}"
                )
            headers[str(key)] = str(value)

        try:
            status_code, response_headers, body = self.transport(
                request.url,
                request.method,
                request.body,
                headers,
                request.timeout_seconds,
            )
        except (TimeoutError, OSError) as exc:
            raise ProviderConnectionError(
                f"provider connection failed: {type(exc).__name__}"
            ) from exc

        return ProviderConnectionResponse(
            status_code=int(status_code),
            headers=dict(response_headers),
            body=bytes(body),
        )
