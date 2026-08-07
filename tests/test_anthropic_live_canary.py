from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping
from urllib.error import URLError

import pytest

from teo_reference.anthropic_adapter import (
    ANTHROPIC_MESSAGES_URL,
    ANTHROPIC_VERSION,
    execute_anthropic_canary_once,
)
from teo_reference.provider_adapter import ProviderAdapterContractError, ProviderExecutionRequest
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


def dispatch(
    *,
    task_type: str = "high_volume_simple",
    risk_level: str = "low",
    provider_family: str = "anthropic",
    model: str = "claude-haiku-4-5",
) -> DispatchRecord:
    selected = ImplementationChoice(
        agent="claude",
        model=model,
        profile="luna",
        provider_family=provider_family,
        availability="generally_available",
        source="policy/routing/routing.yaml",
    )
    verifier = ImplementationChoice(
        agent="agy",
        model="gemini-3.6-flash",
        profile="luna",
        provider_family="google",
        availability="stable",
        source="policy/routing/routing.yaml",
    )
    return DispatchRecord(
        task_id="task-canary",
        dispatch_id="dispatch-canary",
        created_at="2026-08-07T07:30:00+00:00",
        task="Classify these three records into supported categories.",
        task_type=task_type,
        risk_level=risk_level,  # type: ignore[arg-type]
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=selected,
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=verifier,
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def transport_response(
    status: int,
    payload: dict,
    *,
    response_headers: Mapping[str, str] | None = None,
    calls: list[dict] | None = None,
):
    def transport(
        url: str,
        method: str,
        body: bytes,
        request_headers: Mapping[str, str],
        timeout: float,
    ):
        if calls is not None:
            calls.append(
                {
                    "url": url,
                    "method": method,
                    "body": json.loads(body.decode("utf-8")),
                    "headers": dict(request_headers),
                    "timeout": timeout,
                }
            )
        return status, dict(response_headers or {}), json.dumps(payload).encode("utf-8")

    return transport


def connection(*, transport=None) -> HeaderProviderConnection:
    return HeaderProviderConnection(
        provider_family="anthropic",
        authorization_headers={"x-api-key": "test-secret-key"},
        transport=transport or transport_response(200, {}),
    )


def test_live_canary_performs_one_attempt_and_writes_normalized_artifact(tmp_path: Path) -> None:
    calls: list[dict] = []
    conn = connection(
        transport=transport_response(
            200,
            {
                "id": "msg_123",
                "type": "message",
                "model": "claude-haiku-4-5-20251001",
                "content": [
                    {"type": "text", "text": "category_a\ncategory_b\ncategory_c"},
                    {"type": "tool_use", "id": "tool_1", "name": "ignored", "input": {}},
                ],
            },
            response_headers={"request-id": "req_123"},
            calls=calls,
        )
    )
    response = execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)

    assert len(calls) == 1
    assert calls[0]["url"] == ANTHROPIC_MESSAGES_URL
    assert calls[0]["method"] == "POST"
    assert calls[0]["headers"]["anthropic-version"] == ANTHROPIC_VERSION
    assert calls[0]["headers"]["x-api-key"] == "test-secret-key"
    assert calls[0]["body"]["model"] == "claude-haiku-4-5"
    assert calls[0]["body"]["messages"] == [
        {"role": "user", "content": "Classify these three records into supported categories."}
    ]
    assert response.status == "succeeded"
    assert response.model == "claude-haiku-4-5"
    assert response.provider_family == "anthropic"
    assert "anthropic_request_id:req_123" in response.evidence
    artifact = Path(response.output_ref.removeprefix("file://"))
    assert artifact.read_text(encoding="utf-8") == "category_a\ncategory_b\ncategory_c\n"
    assert "test-secret-key" not in artifact.read_text(encoding="utf-8")


def test_connection_credentials_are_not_serialized_into_provider_request() -> None:
    request = ProviderExecutionRequest.from_dispatch(dispatch())
    serialized = json.dumps(request.to_dict(), sort_keys=True)
    assert "test-secret-key" not in serialized
    assert "x-api-key" not in serialized.lower()
    assert "authorization" not in serialized.lower()


def test_live_canary_refuses_non_canary_task_before_connection_invocation(tmp_path: Path) -> None:
    calls: list[dict] = []
    conn = connection(transport=transport_response(200, {}, calls=calls))
    with pytest.raises(ProviderAdapterContractError, match="high_volume_simple"):
        execute_anthropic_canary_once(
            dispatch(task_type="documentation"), conn, artifact_dir=tmp_path
        )
    assert calls == []


@pytest.mark.parametrize("risk", ["high", "critical"])
def test_live_canary_refuses_consequential_risk_before_connection_invocation(
    tmp_path: Path, risk: str
) -> None:
    calls: list[dict] = []
    conn = connection(transport=transport_response(200, {}, calls=calls))
    with pytest.raises(ProviderAdapterContractError, match="refuses high and critical"):
        execute_anthropic_canary_once(dispatch(risk_level=risk), conn, artifact_dir=tmp_path)
    assert calls == []


def test_live_canary_refuses_wrong_provider_connection_before_invocation(tmp_path: Path) -> None:
    calls: list[dict] = []
    wrong_connection = HeaderProviderConnection(
        provider_family="google",
        authorization_headers={"authorization": "Bearer token"},
        transport=transport_response(200, {}, calls=calls),
    )
    with pytest.raises(ProviderAdapterContractError, match="Anthropic provider connection"):
        execute_anthropic_canary_once(dispatch(), wrong_connection, artifact_dir=tmp_path)
    assert calls == []


def test_live_canary_refuses_non_haiku_model_before_invocation(tmp_path: Path) -> None:
    calls: list[dict] = []
    conn = connection(transport=transport_response(200, {}, calls=calls))
    with pytest.raises(ProviderAdapterContractError, match="Haiku 4.5"):
        execute_anthropic_canary_once(
            dispatch(model="claude-sonnet-5"), conn, artifact_dir=tmp_path
        )
    assert calls == []


def test_provider_error_is_normalized_without_retry(tmp_path: Path) -> None:
    calls: list[dict] = []
    conn = connection(
        transport=transport_response(
            429,
            {"type": "error", "error": {"type": "rate_limit_error", "message": "slow down"}},
            response_headers={"request-id": "req_rate"},
            calls=calls,
        )
    )
    response = execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)

    assert len(calls) == 1
    assert response.status == "failed"
    assert response.failure is not None
    assert response.failure.scope == "provider"
    assert response.failure.code == "rate_limit_error"
    assert response.output_ref is None
    assert response.evidence == ("anthropic_request_id:req_rate",)


def test_model_not_found_is_model_scoped(tmp_path: Path) -> None:
    conn = connection(
        transport=transport_response(
            404,
            {"type": "error", "error": {"type": "not_found_error", "message": "model unavailable"}},
        )
    )
    response = execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)
    assert response.failure is not None
    assert response.failure.scope == "model"


def test_request_too_large_is_capability_scoped(tmp_path: Path) -> None:
    conn = connection(
        transport=transport_response(
            413,
            {"type": "error", "error": {"type": "request_too_large", "message": "too large"}},
        )
    )
    response = execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)
    assert response.failure is not None
    assert response.failure.scope == "capability"


def test_connection_failure_is_transient_and_single_attempt(tmp_path: Path) -> None:
    calls = 0

    def failing_transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        nonlocal calls
        calls += 1
        raise URLError("offline")

    conn = connection(transport=failing_transport)
    response = execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)
    assert calls == 1
    assert response.status == "failed"
    assert response.failure is not None
    assert response.failure.scope == "transient"
    assert response.failure.code == "connection_error"


def test_provider_cannot_silently_report_different_model(tmp_path: Path) -> None:
    conn = connection(
        transport=transport_response(
            200,
            {
                "model": "claude-sonnet-5",
                "content": [{"type": "text", "text": "wrong model"}],
            },
        )
    )
    with pytest.raises(ProviderAdapterContractError, match="model outside"):
        execute_anthropic_canary_once(dispatch(), conn, artifact_dir=tmp_path)
