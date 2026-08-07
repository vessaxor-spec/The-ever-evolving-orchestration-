from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import execute_guarded_canary
from teo_reference.runtime_retry import RetryPolicy
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def task() -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "task-retry",
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )


def sequence_connection(
    provider_family: str,
    calls: list[dict],
    responses: list[tuple[int, dict]],
) -> HeaderProviderConnection:
    queue = list(responses)

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
        if not queue:
            raise AssertionError("unexpected provider attempt")
        status, payload = queue.pop(0)
        return status, {"x-request-id": f"req_{provider_family}_{len(calls)}"}, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers={"authorization": "Bearer test-runtime-token"},
        transport=transport,
    )


def anthropic_overloaded() -> dict:
    return {
        "type": "error",
        "error": {"type": "api_error", "message": "temporary server failure"},
    }


def anthropic_success() -> dict:
    return {
        "id": "msg_retry_success",
        "model": "claude-haiku-4-5",
        "content": [{"type": "text", "text": "label_a\nlabel_b"}],
    }


def anthropic_provider_failure() -> dict:
    return {
        "type": "error",
        "error": {"type": "rate_limit_error", "message": "provider unavailable"},
    }


def gemini_success() -> dict:
    return {
        "id": "int_retry_fallback",
        "model": "gemini-3.6-flash",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [{"type": "text", "text": "label_a\nlabel_b"}],
            }
        ],
    }


def test_retry_policy_loads_as_two_attempt_transient_only_control() -> None:
    policy = RetryPolicy.load(REPO_ROOT)
    assert policy.eligible_failure_scopes == {"transient"}
    assert policy.max_attempts_per_dispatch == 2
    assert policy.initial_delay_seconds == 0.5
    assert policy.backoff_multiplier == 2.0
    assert policy.max_delay_seconds == 2.0
    assert policy.jitter_ratio == 0.2
    assert policy.fallback_after_transient_exhaustion is False


def test_transient_then_success_reuses_primary_dispatch_without_redispatch(tmp_path: Path) -> None:
    calls: list[dict] = []
    delays: list[float] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": sequence_connection(
                "anthropic",
                calls,
                [
                    (500, anthropic_overloaded()),
                    (200, anthropic_success()),
                ],
            )
        },
        artifact_root=tmp_path,
        sleeper=delays.append,
        random_source=lambda: 0.5,
    )

    assert outcome.status == "primary_executed"
    assert outcome.execution_succeeded is True
    assert outcome.primary_attempts == 2
    assert outcome.primary_retry_delays_seconds == (0.5,)
    assert delays == [0.5]
    assert outcome.fallback_dispatch is None
    assert len(calls) == 2
    assert calls[0]["body"] == calls[1]["body"]


def test_jitter_is_bounded_and_deterministic_when_source_is_injected(tmp_path: Path) -> None:
    calls: list[dict] = []
    delays: list[float] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": sequence_connection(
                "anthropic",
                calls,
                [
                    (500, anthropic_overloaded()),
                    (200, anthropic_success()),
                ],
            )
        },
        artifact_root=tmp_path,
        sleeper=delays.append,
        random_source=lambda: 1.0,
    )

    assert outcome.primary_retry_delays_seconds == (0.6,)
    assert delays == [0.6]


def test_non_transient_failure_is_never_retried(tmp_path: Path) -> None:
    calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": sequence_connection(
                "anthropic",
                calls,
                [(429, anthropic_provider_failure())],
            ),
            "google": sequence_connection(
                "google",
                google_calls,
                [(200, gemini_success())],
            ),
        },
        artifact_root=tmp_path,
        sleeper=lambda _: (_ for _ in ()).throw(AssertionError("non-transient failure slept")),
    )

    assert outcome.status == "fallback_executed"
    assert outcome.primary_attempts == 1
    assert len(calls) == 1
    assert len(google_calls) == 1


def test_transient_retry_can_surface_provider_failure_then_redispatch(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    outcome = execute_guarded_canary(
        engine(),
        task(),
        {
            "anthropic": sequence_connection(
                "anthropic",
                anthropic_calls,
                [
                    (500, anthropic_overloaded()),
                    (429, anthropic_provider_failure()),
                ],
            ),
            "google": sequence_connection(
                "google",
                google_calls,
                [(200, gemini_success())],
            ),
        },
        artifact_root=tmp_path,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
    )

    assert outcome.status == "fallback_executed"
    assert outcome.primary_attempts == 2
    assert outcome.fallback_trigger_scope == "provider"
    assert outcome.fallback_dispatch is not None
    assert outcome.fallback_dispatch.dispatch_id != outcome.primary_dispatch.dispatch_id
    assert len(anthropic_calls) == 2
    assert len(google_calls) == 1


def test_retry_policy_rejects_fallback_after_transient_exhaustion() -> None:
    policy = RetryPolicy(
        eligible_failure_scopes=frozenset({"transient"}),
        max_attempts_per_dispatch=2,
        initial_delay_seconds=0.5,
        backoff_multiplier=2.0,
        max_delay_seconds=2.0,
        jitter_ratio=0.2,
        fallback_after_transient_exhaustion=True,
    )
    with pytest.raises(ProviderAdapterContractError, match="cannot silently authorize fallback"):
        policy.validate()


def test_retry_policy_refuses_more_than_two_attempts() -> None:
    policy = RetryPolicy(
        eligible_failure_scopes=frozenset({"transient"}),
        max_attempts_per_dispatch=3,
        initial_delay_seconds=0.5,
        backoff_multiplier=2.0,
        max_delay_seconds=2.0,
        jitter_ratio=0.2,
        fallback_after_transient_exhaustion=False,
    )
    with pytest.raises(ProviderAdapterContractError, match="one or two attempts"):
        policy.validate()
