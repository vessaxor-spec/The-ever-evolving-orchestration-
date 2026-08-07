from __future__ import annotations

from typing import Mapping

import pytest

from teo_reference.provider_connection import (
    HeaderProviderConnection,
    ProviderConnectionError,
    ProviderConnectionRequest,
)


def capture_transport(calls: list[dict]):
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        calls.append(
            {
                "url": url,
                "method": method,
                "body": body,
                "headers": dict(headers),
                "timeout": timeout,
            }
        )
        return 200, {"request-id": "req"}, b"{}"

    return transport


def request() -> ProviderConnectionRequest:
    return ProviderConnectionRequest(
        operation="responses.create",
        url="https://provider.example/v1/execute",
        method="POST",
        headers={"content-type": "application/json", "provider-version": "1"},
        body=b'{"model":"selected-model"}',
        timeout_seconds=30.0,
    )


@pytest.mark.parametrize(
    ("provider_family", "authorization_headers"),
    [
        ("openai", {"authorization": "Bearer delegated-openai-token"}),
        ("anthropic", {"x-api-key": "anthropic-key"}),
        ("google", {"authorization": "Bearer delegated-google-token"}),
    ],
)
def test_connection_mechanism_is_runtime_only_and_provider_route_stays_unchanged(
    provider_family: str, authorization_headers: dict[str, str]
) -> None:
    calls: list[dict] = []
    connection = HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers=authorization_headers,
        transport=capture_transport(calls),
    )
    result = connection.invoke(request())

    assert result.status_code == 200
    assert len(calls) == 1
    assert calls[0]["body"] == b'{"model":"selected-model"}'
    assert calls[0]["headers"]["content-type"] == "application/json"
    for key, value in authorization_headers.items():
        assert calls[0]["headers"][key] == value


def test_connection_cannot_override_provider_protocol_headers() -> None:
    connection = HeaderProviderConnection(
        provider_family="openai",
        authorization_headers={
            "authorization": "Bearer token",
            "provider-version": "wrong",
        },
        transport=capture_transport([]),
    )
    with pytest.raises(ProviderConnectionError, match="cannot override protocol header"):
        connection.invoke(request())


def test_connection_provider_family_is_required() -> None:
    with pytest.raises(ProviderConnectionError, match="provider_family"):
        HeaderProviderConnection(
            provider_family="",
            authorization_headers={"authorization": "Bearer token"},
        )


def test_connection_authorization_material_is_required() -> None:
    with pytest.raises(ProviderConnectionError, match="authorization headers"):
        HeaderProviderConnection(provider_family="google", authorization_headers={})
