from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import execute_guarded_canary
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def task() -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "task-guarded-fallback",
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )


def connection(
    provider_family: str,
    calls: list[dict],
    *,
    status: int | None = None,
    payload: dict | None = None,
    fail_transport: bool = False,
) -> HeaderProviderConnection:
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
                "body": json.loads(body.decode("utf-8")),
                "headers": dict(headers),
                "timeout": timeout,
            }
        )
        if fail_transport:
            raise OSError("offline")
        return int(status or 200), {"x-request-id": f"req_{provider_family}"}, json.dumps(payload or {}).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers={"authorization": "Bearer test-runtime-token"},
        transport=transport,
    )


def anthropic_success() -> dict:
    return {
        "id": "msg_fallback",
        "model": "claude-haiku-4-5",
        "content": [{"type": "text", "text": "label_a\nlabel_b"}],
    }


def anthropic_transient_failure() -> dict:
    return {
        "type": "error",
        "error": {"type": "api_error", "message": "try later"},
    }


def gemini_provider_failure() -> dict:
    return {"error": {"status": "RESOURCE_EXHAUSTED", "message": "provider unavailable"}}


def gemini_model_failure() -> dict:
    return {"error": {"status": "NOT_FOUND", "message": "model unavailable"}}


def gemini_success() -> dict:
    return {
        "id": "int_fallback",
        "model": "gemini-3.7-flash",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [{"type": "text", "text": "label_a\nlabel_b"}],
            }
        ],
    }


def test_provider_failure_redispatches_to_declared_fallback_with_new_verifier(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    openai_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "google": connection("google", google_calls, status=429, payload=gemini_provider_failure()),
            "anthropic": connection("anthropic", anthropic_calls, status=200, payload=anthropic_success()),
            "openai": connection("openai", openai_calls, status=200, payload={}),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "fallback_executed"
    assert outcome.execution_succeeded is True
    assert outcome.fallback_trigger_scope == "provider"
    assert outcome.primary_dispatch.selected_implementation.model == "gemini-3.7-flash"
    assert outcome.primary_dispatch.verification.implementation.model == "claude-sonnet-5"
    assert outcome.primary_dispatch.fallback_implementation is not None
    assert outcome.primary_dispatch.fallback_implementation.model == "claude-haiku-4-5"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_dispatch.selected_implementation.model == "claude-haiku-4-5"
    assert outcome.fallback_dispatch.verification.implementation.model == "gpt-5.6-sol"
    assert outcome.fallback_dispatch.verification.implementation.model != outcome.primary_dispatch.verification.implementation.model
    assert outcome.primary_attempts == 1
    assert outcome.fallback_attempts == 1
    assert len(google_calls) == 1
    assert len(anthropic_calls) == 1
    assert openai_calls == []


def test_model_failure_redispatches_with_failed_model_blocked(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "google": connection("google", google_calls, status=404, payload=gemini_model_failure()),
            "anthropic": connection("anthropic", anthropic_calls, status=200, payload=anthropic_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "fallback_executed"
    assert outcome.fallback_trigger_scope == "model"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_dispatch.selected_implementation.model == "claude-haiku-4-5"
    assert outcome.fallback_dispatch.verification.implementation.model == "gpt-5.6-sol"
    assert len(google_calls) == 1
    assert len(anthropic_calls) == 1


def test_transient_failure_retries_same_dispatch_without_fallback(tmp_path: Path) -> None:
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "google": connection("google", google_calls, fail_transport=True),
            "anthropic": connection("anthropic", anthropic_calls, status=200, payload=anthropic_success()),
        },
        artifact_root=tmp_path,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    assert outcome.status == "execution_failed"
    assert outcome.primary_response.failure is not None
    assert outcome.primary_response.failure.scope == "transient"
    assert outcome.primary_attempts == 2
    assert outcome.primary_retry_delays_seconds == (0.5,)
    assert outcome.fallback_dispatch is None
    assert len(google_calls) == 2
    assert anthropic_calls == []


def test_request_failure_does_not_retry_or_fallback(tmp_path: Path) -> None:
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "google": connection(
                "google", google_calls, status=400,
                payload={"error": {"status": "INVALID_ARGUMENT", "message": "bad request"}},
            ),
            "anthropic": connection("anthropic", anthropic_calls, status=200, payload=anthropic_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "execution_failed"
    assert outcome.primary_response.failure is not None
    assert outcome.primary_response.failure.scope == "request"
    assert outcome.primary_attempts == 1
    assert outcome.fallback_dispatch is None
    assert len(google_calls) == 1
    assert anthropic_calls == []


def test_failed_fallback_does_not_chain_to_a_third_provider(tmp_path: Path) -> None:
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "google": connection("google", google_calls, status=429, payload=gemini_provider_failure()),
            "anthropic": connection("anthropic", anthropic_calls, status=503, payload=anthropic_transient_failure()),
            "openai": connection("openai", openai_calls, status=200, payload={}),
        },
        artifact_root=tmp_path,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    assert outcome.status == "execution_failed"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_response is not None
    assert outcome.fallback_response.failure is not None
    assert outcome.primary_attempts == 1
    assert outcome.fallback_attempts == 2
    assert outcome.fallback_retry_delays_seconds == (0.5,)
    assert len(google_calls) == 1
    assert len(anthropic_calls) == 2
    assert openai_calls == []

