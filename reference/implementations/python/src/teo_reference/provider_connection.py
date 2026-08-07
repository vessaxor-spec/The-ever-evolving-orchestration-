from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from .provider_adapter import ProviderAdapterContractError


class ProviderConnection(Protocol):
    """Runtime-owned connection strategy, independent from TEO model routing."""

    provider_family: str

    def authorize_headers(self, base_headers: Mapping[str, str]) -> Mapping[str, str]:
        """Return authorized request headers without exposing credentials to dispatch records."""
        ...


@dataclass(frozen=True, slots=True)
class HeaderProviderConnection:
    """Minimal connection strategy for tests and externally resolved credentials.

    The caller decides how credentials were obtained. They may originate from an API key,
    OAuth flow, delegated token broker, secret manager, workload identity, or another
    provider-supported mechanism. TEO routing never inspects or persists those credentials.
    """

    provider_family: str
    authorization_headers: Mapping[str, str]

    def __post_init__(self) -> None:
        if not self.provider_family.strip():
            raise ProviderAdapterContractError("connection provider_family is required")
        if not self.authorization_headers:
            raise ProviderAdapterContractError("connection authorization headers are required")
        for key, value in self.authorization_headers.items():
            if not str(key).strip() or not str(value).strip():
                raise ProviderAdapterContractError("connection authorization headers cannot be empty")

    def authorize_headers(self, base_headers: Mapping[str, str]) -> Mapping[str, str]:
        headers = dict(base_headers)
        headers.update({str(key): str(value) for key, value in self.authorization_headers.items()})
        return headers
