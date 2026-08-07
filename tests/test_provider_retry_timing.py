from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.anthropic_adapter import execute_anthropic_canary_once
from teo_reference.google_adapter import execute_gemini_canary_once
from teo_reference.openai_adapter import execute_openai_canary_once
from teo_reference.provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionResponse,
    ProviderFailure,
    retry_after_seconds_from_headers,
)
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_retry import RetryPolicy, execute_with_transient_retry
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


REPO_ROOT = Path(__file__).resolve().parents[1]


def choice(model: str, provider: str, reasoning: str | None = None) -> ImplementationChoice:
    return ImplementationChoice(
        agent="retry-timing-test",
        model=model,
        profile="luna",
        provider_family=provider,
        availability="current",
        source="test-route",
        reasoning=reasoning,
    )


def dispatch(provider: str = "anthropic") -> DispatchRecord:
    models = {
        "anthropic": ("claude-haiku-4-5", None),
        "openai": ("gpt-5.6-luna", "low"),
        "google": ("gemini-3.6-flash", "medium"),
    }
    model, reasoning = models[provider]
    verifier_provider = "google" if provider != "google" else "anthropic"
    verifier_model = "gemini-3.1-pro-preview" if verifier_provider == "google" else "claude-sonnet-5"
    return DispatchRecord(
        task_id=f"task-retry-{provider}",
        dispatch_id=f"dispatch-retry-{provider}",
        created_at="2026-08-07T10:00:00+00:00",
        task="Classify the bounded records and return the labels.",
        task_type="high_volume_simple",
        risk_level="low",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=choice(model, provider, reasoning),
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice(verifier_model, verifier_provider, "medium"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def connection(
    provider: str,
    *,
    status: int,
    headers: Mapping[str, str] | None = None,
    payload: dict | None = None,
) -> HeaderProviderConnection:
    def transport(url: str, method: str, body: bytes, request_headers: Mapping[str, str], timeout: float):
        return status, dict(headers or {}), json.dumps(payload or {}).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider,
        authorization_headers={"authorization": "Bearer test-runtime-token"},
        transport=transport,
    )


def transient_response(seconds: float | None) -> ProviderExecutionResponse:
    return ProviderExecutionResponse(
        dispatch_id="dispatch-retry-anthropic",
        status="failed",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        failure=ProviderFailure(
            scope="transient",
            code="api_error",
            message="temporary provider failure",
        ),
        retry_after_seconds=seconds,
    )


def success_response() -> ProviderExecutionResponse:
    return ProviderExecutionResponse(
        dispatch_id="dispatch-retry-anthropic",
        status="succeeded",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        output_ref="artifact://retry-success",
    )


def test_retry_after_header_is_normalized_case_insensitively() -> None:
    assert retry_after_seconds_from_headers({"Retry-After": "7"}) == 7.0
    assert retry_after_seconds_from_headers({"retry-after": "0.5"}) == 0.5
    assert retry_after_seconds_from_headers({"Retry-After": "not-a-number"}) is None
    assert retry_after_seconds_from_headers({"Retry-After": "-1"}) is None


def test_normalized_retry_timing_is_failure_only_and_non_negative() -> None:
    with pytest.raises(ProviderAdapterContractError, match="Successful execution cannot include retry timing"):
        ProviderExecutionResponse(
            dispatch_id="dispatch-x",
            status="succeeded",
            provider_family="anthropic",
            model="claude-haiku-4-5",
            output_ref="artifact://x",
            retry_after_seconds=1.0,
        )
    with pytest.raises(ProviderAdapterContractError, match="non-negative"):
        transient_response(-1.0)


def test_retry_controller_uses_provider_hint_as_minimum_wait() -> None:
    policy = RetryPolicy.load(REPO_ROOT)
    responses = [transient_response(5.0), success_response()]
    delays: list[float] = []

    def executor(active_dispatch, connections, artifact_root):
        return responses.pop(0)

    execution = execute_with_transient_retry(
        dispatch(),
        {},
        ".",
        executor,
        policy,
        sleeper=delays.append,
        random_source=lambda: 0.5,
    )
    assert execution.response.status == "succeeded"
    assert execution.attempts == 2
    assert execution.delays_seconds == (5.0,)
    assert delays == [5.0]


def test_provider_hint_cannot_create_an_unbounded_wait_or_extra_attempt() -> None:
    policy = RetryPolicy.load(REPO_ROOT)
    calls = 0
    delays: list[float] = []

    def executor(active_dispatch, connections, artifact_root):
        nonlocal calls
        calls += 1
        return transient_response(61.0)

    execution = execute_with_transient_retry(
        dispatch(),
        {},
        ".",
        executor,
        policy,
        sleeper=delays.append,
        random_source=lambda: 0.5,
    )
    assert calls == 1
    assert execution.attempts == 1
    assert execution.response.status == "failed"
    assert execution.delays_seconds == ()
    assert delays == []


def test_retry_hint_on_non_transient_failure_does_not_authorize_retry() -> None:
    policy = RetryPolicy.load(REPO_ROOT)
    calls = 0
    delays: list[float] = []

    def executor(active_dispatch, connections, artifact_root):
        nonlocal calls
        calls += 1
        return ProviderExecutionResponse(
            dispatch_id=active_dispatch.dispatch_id,
            status="failed",
            provider_family="anthropic",
            model="claude-haiku-4-5",
            failure=ProviderFailure(
                scope="provider",
                code="rate_limit_error",
                message="rate limited",
            ),
            retry_after_seconds=10.0,
        )

    execution = execute_with_transient_retry(
        dispatch(),
        {},
        ".",
        executor,
        policy,
        sleeper=delays.append,
    )
    assert calls == 1
    assert execution.attempts == 1
    assert delays == []


def test_anthropic_adapter_normalizes_retry_after_header(tmp_path: Path) -> None:
    response = execute_anthropic_canary_once(
        dispatch("anthropic"),
        connection(
            "anthropic",
            status=500,
            headers={"Retry-After": "7", "request-id": "req_anthropic"},
            payload={"type": "error", "error": {"type": "api_error", "message": "temporary"}},
        ),
        artifact_dir=tmp_path,
    )
    assert response.failure is not None
    assert response.failure.scope == "transient"
    assert response.retry_after_seconds == 7.0


def test_openai_adapter_normalizes_retry_after_header_when_present(tmp_path: Path) -> None:
    response = execute_openai_canary_once(
        dispatch("openai"),
        connection(
            "openai",
            status=503,
            headers={"retry-after": "3", "x-request-id": "req_openai"},
            payload={"error": {"type": "server_error", "message": "temporary"}},
        ),
        artifact_dir=tmp_path,
    )
    assert response.failure is not None
    assert response.failure.scope == "transient"
    assert response.retry_after_seconds == 3.0


def test_gemini_adapter_normalizes_standard_retry_info_when_present(tmp_path: Path) -> None:
    response = execute_gemini_canary_once(
        dispatch("google"),
        connection(
            "google",
            status=503,
            headers={"x-request-id": "req_google"},
            payload={
                "error": {
                    "status": "UNAVAILABLE",
                    "message": "temporary",
                    "details": [
                        {
                            "@type": "type.googleapis.com/google.rpc.RetryInfo",
                            "retryDelay": "4.5s",
                        }
                    ],
                }
            },
        ),
        artifact_dir=tmp_path,
    )
    assert response.failure is not None
    assert response.failure.scope == "transient"
    assert response.retry_after_seconds == 4.5
