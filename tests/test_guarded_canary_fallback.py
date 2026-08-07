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


def anthropic_provider_failure() -> dict:
    return {
        "type": "error",
        "error": {"type": "rate_limit_error", "message": "provider unavailable"},
    }


def anthropic_model_failure() -> dict:
    return {
        "type": "error",
        "error": {"type": "not_found_error", "message": "model unavailable"},
    }


def gemini_success() -> dict:
    return {
        "id": "int_fallback",
        "model": "gemini-3.6-flash",
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
    connections = {
        "anthropic": connection(
            "anthropic", anthropic_calls, status=429, payload=anthropic_provider_failure()
        ),
        "google": connection("google", google_calls, status=200, payload=gemini_success()),
        "openai": connection("openai", openai_calls, status=200, payload={}),
    }

    outcome = execute_guarded_canary(
        engine(),
        task(),
        connections,
        artifact_root=tmp_path,
    )

    assert outcome.status == "fallback_executed"
    assert outcome.execution_succeeded is True
    assert outcome.fallback_trigger_scope == "provider"
    assert outcome.primary_dispatch.selected_implementation.model == "claude-haiku-4-5"
    assert outcome.primary_dispatch.fallback_implementation is not None
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_response is not None
    assert outcome.fallback_dispatch.dispatch_id != outcome.primary_dispatch.dispatch_id
    assert (
        outcome.fallback_dispatch.selected_implementation.model
        == outcome.primary_dispatch.fallback_implementation.model
        == "gemini-3.6-flash"
    )
    assert (
        outcome.fallback_dispatch.selected_implementation.provider_family
        != outcome.primary_dispatch.selected_implementation.provider_family
    )
    assert (
        outcome.fallback_dispatch.verification.implementation.model
        != outcome.fallback_dispatch.selected_implementation.model
    )
    assert (
        outcome.fallback_dispatch.verification.implementation.model
        != outcome.primary_dispatch.verification.implementation.model
    )
    assert len(anthropic_calls) == 1
    assert len(google_calls) == 1
    assert openai_calls == []


def test_model_failure_redispatches_with_failed_model_blocked(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": connection(
                "anthropic", anthropic_calls, status=404, payload=anthropic_model_failure()
            ),
            "google": connection("google", google_calls, status=200, payload=gemini_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "fallback_executed"
    assert outcome.fallback_trigger_scope == "model"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_dispatch.selected_implementation.model == "gemini-3.6-flash"
    assert len(anthropic_calls) == 1
    assert len(google_calls) == 1


def test_transient_failure_does_not_fallback_before_retry_policy_exists(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": connection("anthropic", anthropic_calls, fail_transport=True),
            "google": connection("google", google_calls, status=200, payload=gemini_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "execution_failed"
    assert outcome.primary_response.failure is not None
    assert outcome.primary_response.failure.scope == "transient"
    assert outcome.fallback_dispatch is None
    assert len(anthropic_calls) == 1
    assert google_calls == []


def test_request_failure_does_not_fallback(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": connection(
                "anthropic",
                anthropic_calls,
                status=400,
                payload={
                    "type": "error",
                    "error": {"type": "invalid_request_error", "message": "bad request"},
                },
            ),
            "google": connection("google", google_calls, status=200, payload=gemini_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "execution_failed"
    assert outcome.primary_response.failure is not None
    assert outcome.primary_response.failure.scope == "request"
    assert outcome.fallback_dispatch is None
    assert google_calls == []


def test_failed_fallback_does_not_chain_to_a_third_provider(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    openai_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": connection(
                "anthropic", anthropic_calls, status=429, payload=anthropic_provider_failure()
            ),
            "google": connection(
                "google",
                google_calls,
                status=503,
                payload={"error": {"status": "UNAVAILABLE", "message": "try later"}},
            ),
            "openai": connection("openai", openai_calls, status=200, payload={}),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "execution_failed"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_response is not None
    assert outcome.fallback_response.failure is not None
    assert len(anthropic_calls) == 1
    assert len(google_calls) == 1
    assert openai_calls == []


def test_original_task_constraints_are_not_mutated_by_redispatch(tmp_path: Path) -> None:
    original = task()
    original.constraints.blocked_implementations.append("unrelated-model")
    original.constraints.blocked_providers.append("local_ollama")
    original_models = list(original.constraints.blocked_implementations)
    original_providers = list(original.constraints.blocked_providers)

    outcome = execute_guarded_canary(
        engine(),
        original,
        {
            "anthropic": connection(
                "anthropic", [], status=429, payload=anthropic_provider_failure()
            ),
            "google": connection("google", [], status=200, payload=gemini_success()),
        },
        artifact_root=tmp_path,
    )

    assert outcome.status == "fallback_executed"
    assert original.constraints.blocked_implementations == original_models
    assert original.constraints.blocked_providers == original_providers


def test_guarded_fallback_requires_explicit_canary_task_type(tmp_path: Path) -> None:
    ambiguous = TaskRequest.from_dict(
        {"task": "Classify these bounded records into the supported labels."}
    )
    with pytest.raises(ProviderAdapterContractError, match="explicit high_volume_simple"):
        execute_guarded_canary(engine(), ambiguous, {}, artifact_root=tmp_path)
