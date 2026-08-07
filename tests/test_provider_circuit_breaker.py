from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionResponse,
    ProviderFailure,
)
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import execute_guarded_canary
from teo_reference.runtime_circuit_breaker import (
    InMemoryCircuitStateStore,
    JsonFileCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
)
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def canary_task(task_id: str = "task-circuit") -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": task_id,
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )


def anthropic_error(error_type: str, message: str = "provider error") -> dict:
    return {"type": "error", "error": {"type": error_type, "message": message}}


def gemini_success() -> dict:
    return {
        "id": "int_circuit",
        "model": "gemini-3.6-flash",
        "status": "completed",
        "steps": [
            {
                "type": "model_output",
                "content": [{"type": "text", "text": "label_a\nlabel_b"}],
            }
        ],
    }


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
            raise AssertionError(f"No queued response for {provider_family}")
        status, payload = queue.pop(0)
        return status, {"x-request-id": f"req_{provider_family}_{len(calls)}"}, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers={"authorization": "Bearer test-runtime-token"},
        transport=transport,
    )


def policy() -> ProviderCircuitPolicy:
    return ProviderCircuitPolicy.load(REPO_ROOT)


def failed_response(provider: str, scope: str, code: str) -> ProviderExecutionResponse:
    return ProviderExecutionResponse(
        dispatch_id="dispatch-health",
        status="failed",
        provider_family=provider,
        model={"anthropic": "claude-haiku-4-5", "openai": "gpt-5.6-luna", "google": "gemini-3.6-flash"}[provider],
        failure=ProviderFailure(scope=scope, code=code, message="test failure"),  # type: ignore[arg-type]
    )


def test_policy_distinguishes_service_health_from_tenant_and_connection_failures() -> None:
    breaker = ProviderCircuitBreaker(policy(), InMemoryCircuitStateStore(), clock=lambda: 0.0)

    assert breaker.is_service_health_failure(failed_response("anthropic", "provider", "overloaded_error"))
    assert breaker.is_service_health_failure(failed_response("anthropic", "transient", "api_error"))
    assert breaker.is_service_health_failure(failed_response("google", "transient", "UNAVAILABLE"))
    assert breaker.is_service_health_failure(failed_response("openai", "transient", "server_error"))

    assert not breaker.is_service_health_failure(failed_response("anthropic", "provider", "rate_limit_error"))
    assert not breaker.is_service_health_failure(failed_response("google", "provider", "RESOURCE_EXHAUSTED"))
    assert not breaker.is_service_health_failure(failed_response("openai", "provider", "authentication_error"))
    assert not breaker.is_service_health_failure(failed_response("openai", "transient", "connection_error"))


def test_three_provider_overloads_persist_open_circuit_and_route_next_task_away(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    connections = {
        "anthropic": sequence_connection(
            "anthropic",
            anthropic_calls,
            [(529, anthropic_error("overloaded_error"))] * 3,
        ),
        "google": sequence_connection(
            "google",
            google_calls,
            [(200, gemini_success())] * 4,
        ),
    }

    for index in range(3):
        outcome = execute_guarded_canary(
            engine(),
            canary_task(f"task-overload-{index}"),
            connections,
            artifact_root=tmp_path / "artifacts",
            sleeper=lambda _: None,
        )
        assert outcome.status == "fallback_executed"
        assert outcome.primary_dispatch.selected_implementation.provider_family == "anthropic"

    state_path = tmp_path / "provider-circuits.json"
    persisted = JsonFileCircuitStateStore(state_path).load_all()["anthropic"]
    assert persisted.state == "open"
    assert persisted.trip_count == 1

    fourth = execute_guarded_canary(
        engine(),
        canary_task("task-after-open"),
        connections,
        artifact_root=tmp_path / "artifacts",
        sleeper=lambda _: None,
    )
    assert fourth.primary_dispatch.selected_implementation.provider_family == "google"
    assert "anthropic" in fourth.circuit_blocked_providers
    assert len(anthropic_calls) == 3
    assert len(google_calls) == 4


def test_repeated_rate_limits_do_not_open_global_provider_circuit(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    connections = {
        "anthropic": sequence_connection(
            "anthropic",
            anthropic_calls,
            [(429, anthropic_error("rate_limit_error", "organization rate limit"))] * 4,
        ),
        "google": sequence_connection(
            "google",
            google_calls,
            [(200, gemini_success())] * 4,
        ),
    }

    for index in range(4):
        outcome = execute_guarded_canary(
            engine(),
            canary_task(f"task-rate-limit-{index}"),
            connections,
            artifact_root=tmp_path / "artifacts",
            sleeper=lambda _: None,
        )
        assert outcome.primary_dispatch.selected_implementation.provider_family == "anthropic"
        assert "anthropic" not in outcome.circuit_blocked_providers

    record = JsonFileCircuitStateStore(tmp_path / "provider-circuits.json").load_all()["anthropic"]
    assert record.state == "closed"
    assert record.failure_count == 0
    assert len(anthropic_calls) == 4


def test_retry_exhausted_server_failures_trip_circuit_across_executions(tmp_path: Path) -> None:
    anthropic_calls: list[dict] = []
    google_calls: list[dict] = []
    connections = {
        "anthropic": sequence_connection(
            "anthropic",
            anthropic_calls,
            [(500, anthropic_error("api_error"))] * 6,
        ),
        "google": sequence_connection(
            "google",
            google_calls,
            [(200, gemini_success())],
        ),
    }

    for index in range(3):
        outcome = execute_guarded_canary(
            engine(),
            canary_task(f"task-api-error-{index}"),
            connections,
            artifact_root=tmp_path / "artifacts",
            sleeper=lambda _: None,
            random_source=lambda: 0.5,
        )
        assert outcome.status == "execution_failed"
        assert outcome.primary_attempts == 2

    assert len(anthropic_calls) == 6
    record = JsonFileCircuitStateStore(tmp_path / "provider-circuits.json").load_all()["anthropic"]
    assert record.state == "open"

    rerouted = execute_guarded_canary(
        engine(),
        canary_task("task-api-error-reroute"),
        connections,
        artifact_root=tmp_path / "artifacts",
        sleeper=lambda _: None,
    )
    assert rerouted.primary_dispatch.selected_implementation.provider_family == "google"
    assert "anthropic" in rerouted.circuit_blocked_providers


def test_half_open_requires_two_successful_probes_and_repeated_failure_extends_cooldown() -> None:
    now = [0.0]
    store = InMemoryCircuitStateStore()
    breaker = ProviderCircuitBreaker(policy(), store, clock=lambda: now[0])
    dispatch = engine().dispatch(canary_task("task-half-open"))

    failure = failed_response("anthropic", "provider", "overloaded_error")
    for _ in range(3):
        breaker.observe(dispatch, failure)
    opened = store.load_all()["anthropic"]
    assert opened.state == "open"
    assert opened.reopen_at == pytest.approx(60.0)

    now[0] = 60.0
    prepared = breaker.prepare_task(canary_task("task-probe-one"))
    assert "anthropic" not in prepared.constraints.blocked_providers
    probe_one = engine().dispatch(prepared)
    breaker.claim_dispatch(probe_one)
    success = ProviderExecutionResponse(
        dispatch_id=probe_one.dispatch_id,
        status="succeeded",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        output_ref="artifact://probe-one",
    )
    first = breaker.observe(probe_one, success)
    assert first.state == "half_open"
    assert first.half_open_successes == 1
    assert first.probe_in_flight is False

    probe_two = engine().dispatch(breaker.prepare_task(canary_task("task-probe-two")))
    breaker.claim_dispatch(probe_two)
    second_success = ProviderExecutionResponse(
        dispatch_id=probe_two.dispatch_id,
        status="succeeded",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        output_ref="artifact://probe-two",
    )
    closed = breaker.observe(probe_two, second_success)
    assert closed.state == "closed"

    for _ in range(3):
        breaker.observe(dispatch, failure)
    reopened = store.load_all()["anthropic"]
    assert reopened.trip_count == 2
    assert reopened.reopen_at == pytest.approx(now[0] + 120.0)


def test_json_store_fails_closed_on_corrupt_state(tmp_path: Path) -> None:
    path = tmp_path / "provider-circuits.json"
    path.write_text("{ definitely not json", encoding="utf-8")
    store = JsonFileCircuitStateStore(path)
    with pytest.raises(ProviderAdapterContractError, match="unreadable or corrupt"):
        store.load_all()
