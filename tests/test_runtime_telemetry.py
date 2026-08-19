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
    ProviderUsage,
)
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import execute_guarded_canary
from teo_reference.runtime_telemetry import (
    InMemoryRuntimeTelemetrySink,
    JsonlRuntimeTelemetrySink,
    RuntimeTelemetryEvent,
    RuntimeTelemetryPolicy,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, TaskRequest, VerificationPlan
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def choice(model: str, provider: str, reasoning: str | None = None) -> ImplementationChoice:
    return ImplementationChoice(
        agent="telemetry-test",
        model=model,
        profile="test",
        provider_family=provider,
        availability="current",
        source="test",
        reasoning=reasoning,
    )


def dispatch(task_id: str = "customer@example.test") -> DispatchRecord:
    return DispatchRecord(
        task_id=task_id,
        dispatch_id="dispatch-telemetry",
        created_at="2026-08-07T10:00:00+00:00",
        task="Sensitive text that must never enter telemetry.",
        task_type="high_volume_simple",
        risk_level="low",
        selected_team="research",
        selected_worker="documentation",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=choice("gpt-5.6-luna", "openai", "low"),
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice("claude-sonnet-5", "anthropic", "medium"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def task(task_id: str) -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": task_id,
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )


def sequence_connection(
    provider_family: str,
    calls: list[dict],
    responses: list[tuple[int, dict, dict[str, str]]],
) -> HeaderProviderConnection:
    queue = list(responses)

    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        calls.append({"url": url, "body": json.loads(body.decode("utf-8"))})
        if not queue:
            raise AssertionError("unexpected provider attempt")
        status, payload, response_headers = queue.pop(0)
        return status, response_headers, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider_family,
        authorization_headers={"authorization": "Bearer secret-test-token"},
        transport=transport,
    )


def gemini_transient() -> dict:
    return {"error": {"status": "INTERNAL", "message": "temporary"}}


def gemini_provider_failure() -> dict:
    return {"error": {"status": "RESOURCE_EXHAUSTED", "message": "limited"}}


def gemini_success() -> dict:
    return {
        "id": "int_telemetry",
        "model": "gemini-3.7-flash",
        "status": "completed",
        "steps": [{"type": "model_output", "content": [{"type": "text", "text": "label_b"}]}],
        "usage": {
            "total_input_tokens": 8,
            "total_output_tokens": 5,
            "total_cached_tokens": 2,
            "total_thought_tokens": 3,
            "total_tool_use_tokens": 1,
            "total_tokens": 17,
        },
    }


def anthropic_success() -> dict:
    return {
        "id": "msg_telemetry_fallback",
        "model": "claude-haiku-4-5",
        "content": [{"type": "text", "text": "label_a"}],
        "usage": {
            "input_tokens": 10,
            "cache_read_input_tokens": 2,
            "cache_creation_input_tokens": 1,
            "output_tokens": 4,
        },
    }


def clock_from(values: list[float]):
    iterator = iter(values)
    return lambda: next(iterator)


def test_telemetry_event_is_content_free_identifier_free_and_round_trips() -> None:
    response = ProviderExecutionResponse(
        dispatch_id="dispatch-telemetry",
        status="succeeded",
        provider_family="openai",
        model="gpt-5.6-luna",
        output_ref="file:///secret-output.txt",
        evidence=("openai_request_id:req_1",),
        usage=ProviderUsage(input_tokens=12, output_tokens=4, cached_input_tokens=2, total_tokens=16),
    )
    event = RuntimeTelemetryEvent.from_attempt(
        dispatch(),
        response,
        role="primary",
        attempt_number=1,
        duration_seconds=0.125,
        recorded_at="2026-08-07T10:01:00+00:00",
    )
    serialized = event.to_dict()

    assert serialized["duration_ms"] == 125.0
    assert serialized["provider_family"] == "openai"
    assert serialized["verifier_provider_family"] == "anthropic"
    assert serialized["usage"]["cached_input_tokens"] == 2
    forbidden = {
        "task_id",
        "task",
        "prompt",
        "input",
        "output",
        "output_ref",
        "evidence",
        "authorization",
        "connection",
        "user_id",
    }
    assert forbidden.isdisjoint(serialized)
    encoded = json.dumps(serialized)
    assert "Sensitive text" not in encoded
    assert "customer@example.test" not in encoded
    assert "secret-output" not in encoded
    assert "req_1" not in encoded
    assert RuntimeTelemetryEvent.from_dict(serialized).to_dict() == serialized


def test_telemetry_rejects_unknown_content_or_identifier_fields() -> None:
    event = RuntimeTelemetryEvent.from_attempt(
        dispatch(),
        ProviderExecutionResponse(
            dispatch_id="dispatch-telemetry",
            status="failed",
            provider_family="openai",
            model="gpt-5.6-luna",
            failure=ProviderFailure(scope="transient", code="timeout", message="temporary"),
        ),
        role="primary",
        attempt_number=1,
        duration_seconds=0.1,
        recorded_at="2026-08-07T10:01:00+00:00",
    ).to_dict()
    for field in ("prompt", "task_id", "user_id"):
        mutated = dict(event)
        mutated[field] = "should not be stored"
        with pytest.raises(ProviderAdapterContractError, match="unsupported fields"):
            RuntimeTelemetryEvent.from_dict(mutated)


def test_telemetry_policy_requires_fail_closed_persistence_and_no_identifiers() -> None:
    policy = RuntimeTelemetryPolicy.load(REPO_ROOT)
    assert policy.sink_failure_behavior == "fail_closed"
    assert policy.include_user_identifiers is False


def test_usage_rejects_negative_or_unknown_values() -> None:
    with pytest.raises(ProviderAdapterContractError, match="cannot be negative"):
        ProviderUsage(input_tokens=-1)
    with pytest.raises(ProviderAdapterContractError, match="unsupported fields"):
        ProviderUsage.from_dict({"input_tokens": 1, "price": 0.1})


def test_jsonl_sink_persists_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "telemetry.jsonl"
    response = ProviderExecutionResponse(
        dispatch_id="dispatch-telemetry",
        status="failed",
        provider_family="openai",
        model="gpt-5.6-luna",
        failure=ProviderFailure(scope="transient", code="timeout", message="temporary"),
        retry_after_seconds=2.0,
    )
    first = RuntimeTelemetryEvent.from_attempt(
        dispatch(), response, role="primary", attempt_number=1, duration_seconds=0.2
    )
    second = RuntimeTelemetryEvent.from_attempt(
        dispatch(), response, role="primary", attempt_number=2, duration_seconds=0.3
    )
    JsonlRuntimeTelemetrySink(path).append(first)
    JsonlRuntimeTelemetrySink(path).append(second)

    events = JsonlRuntimeTelemetrySink(path).read_all()
    assert [event.attempt_number for event in events] == [1, 2]
    assert [event.duration_ms for event in events] == [200.0, 300.0]


def test_jsonl_sink_failure_fails_closed(tmp_path: Path) -> None:
    blocking_file = tmp_path / "not-a-directory"
    blocking_file.write_text("blocked", encoding="utf-8")
    sink = JsonlRuntimeTelemetrySink(blocking_file / "telemetry.jsonl")
    response = ProviderExecutionResponse(
        dispatch_id="dispatch-telemetry",
        status="failed",
        provider_family="openai",
        model="gpt-5.6-luna",
        failure=ProviderFailure(scope="transient", code="timeout", message="temporary"),
    )
    event = RuntimeTelemetryEvent.from_attempt(
        dispatch(), response, role="primary", attempt_number=1, duration_seconds=0.1
    )
    with pytest.raises((ProviderAdapterContractError, FileExistsError, NotADirectoryError, OSError)):
        sink.append(event)


def test_retry_attempts_are_logged_immediately_under_same_dispatch(tmp_path: Path) -> None:
    calls: list[dict] = []
    sink = InMemoryRuntimeTelemetrySink()
    outcome = execute_guarded_canary(
        engine(),
        task("task-telemetry-retry"),
        {
            "google": sequence_connection(
                "google",
                calls,
                [
                    (500, gemini_transient(), {"x-request-id": "req_g1"}),
                    (200, gemini_success(), {"x-request-id": "req_g2"}),
                ],
            )
        },
        artifact_root=tmp_path,
        telemetry_sink=sink,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
        attempt_clock=clock_from([1.0, 1.1, 2.0, 2.25]),
    )

    assert outcome.status == "primary_executed"
    assert outcome.primary_dispatch.selected_implementation.model == "gemini-3.7-flash"
    assert outcome.primary_attempts == 2
    assert len(sink.events) == 2
    assert [event.role for event in sink.events] == ["primary", "primary"]
    assert [event.attempt_number for event in sink.events] == [1, 2]
    assert sink.events[0].dispatch_id == sink.events[1].dispatch_id == outcome.primary_dispatch.dispatch_id
    assert sink.events[0].status == "failed"
    assert sink.events[0].failure_scope == "transient"
    assert sink.events[1].status == "succeeded"
    assert sink.events[1].usage is not None
    assert sink.events[1].usage.input_tokens == 8
    assert sink.events[1].usage.cached_input_tokens == 2
    assert sink.events[1].usage.reasoning_output_tokens == 3
    assert sink.events[1].duration_ms == 250.0


def test_fallback_attempt_has_new_dispatch_and_fallback_role(tmp_path: Path) -> None:
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []
    sink = InMemoryRuntimeTelemetrySink()
    outcome = execute_guarded_canary(
        engine(),
        task("task-telemetry-fallback"),
        {
            "google": sequence_connection(
                "google",
                google_calls,
                [(429, gemini_provider_failure(), {"x-request-id": "req_g", "retry-after": "2"})],
            ),
            "anthropic": sequence_connection(
                "anthropic",
                anthropic_calls,
                [(200, anthropic_success(), {"request-id": "req_a"})],
            ),
        },
        artifact_root=tmp_path,
        telemetry_sink=sink,
        sleeper=lambda _: None,
        attempt_clock=clock_from([1.0, 1.05, 2.0, 2.2]),
    )

    assert outcome.status == "fallback_executed"
    assert len(sink.events) == 2
    primary, fallback = sink.events
    assert primary.role == "primary"
    assert fallback.role == "fallback"
    assert primary.dispatch_id == outcome.primary_dispatch.dispatch_id
    assert outcome.fallback_dispatch is not None
    assert fallback.dispatch_id == outcome.fallback_dispatch.dispatch_id
    assert fallback.dispatch_id != primary.dispatch_id
    assert fallback.provider_family == "anthropic"
    assert fallback.model == "claude-haiku-4-5"
    assert fallback.usage is not None
    assert fallback.usage.input_tokens == 13
    assert fallback.usage.cached_input_tokens == 2


def test_default_runtime_sink_persists_jsonl_without_content_or_caller_id(tmp_path: Path) -> None:
    calls: list[dict] = []
    caller_id = "customer-123@example.test"
    execute_guarded_canary(
        engine(),
        task(caller_id),
        {
            "google": sequence_connection(
                "google",
                calls,
                [(200, gemini_success(), {"x-request-id": "req_default"})],
            )
        },
        artifact_root=tmp_path,
        sleeper=lambda _: None,
    )

    path = tmp_path / "runtime-telemetry.jsonl"
    assert path.is_file()
    raw = path.read_text(encoding="utf-8")
    assert "Classify these bounded records" not in raw
    assert "label_b" not in raw
    assert caller_id not in raw
    events = JsonlRuntimeTelemetrySink(path).read_all()
    assert len(events) == 1
    assert events[0].role == "primary"
