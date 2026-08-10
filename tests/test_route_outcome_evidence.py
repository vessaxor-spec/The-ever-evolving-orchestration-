from __future__ import annotations

import json
from pathlib import Path

import pytest

from teo_reference.provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionResponse,
    ProviderFailure,
    ProviderUsage,
)
from teo_reference.route_outcome import (
    JsonlRouteOutcomeSink,
    RouteOutcomeRecord,
    RouteOutcomeVersionContext,
    build_abandoned_route_outcome,
    build_guarded_canary_route_outcome,
)
from teo_reference.runtime_canary import CanaryRuntimeOutcome
from teo_reference.runtime_telemetry import RuntimeTelemetryEvent
from teo_reference.schemas import (
    DispatchRecord,
    ImplementationChoice,
    VerificationPlan,
    VerificationResult,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def choice(model: str, provider: str, reasoning: str = "low") -> ImplementationChoice:
    return ImplementationChoice(
        agent="route-outcome-test",
        model=model,
        profile="test",
        provider_family=provider,
        availability="current",
        source="test",
        reasoning=reasoning,
    )


def dispatch(
    dispatch_id: str,
    *,
    provider: str,
    model: str,
    verifier_provider: str,
    verifier_model: str,
    human_approval_required: bool = False,
) -> DispatchRecord:
    return DispatchRecord(
        task_id="customer@example.test",
        dispatch_id=dispatch_id,
        created_at="2026-08-10T15:00:00+00:00",
        task="Sensitive customer content that must not enter route-outcome evidence.",
        task_type="high_volume_simple",
        risk_level="low",
        selected_team="research",
        selected_worker="documentation",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["classification"],
        selected_implementation=choice(model, provider),
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice(verifier_model, verifier_provider, "medium"),
            independent=True,
            human_approval_required=human_approval_required,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def event(
    active_dispatch: DispatchRecord,
    *,
    role: str,
    attempt_number: int,
    status: str,
    duration_ms: float,
    failure_scope: str | None = None,
    failure_code: str | None = None,
    usage: ProviderUsage | None = None,
) -> RuntimeTelemetryEvent:
    return RuntimeTelemetryEvent(
        recorded_at=f"2026-08-10T15:00:0{attempt_number}+00:00",
        dispatch_id=active_dispatch.dispatch_id,
        task_type=active_dispatch.task_type,
        risk_level=active_dispatch.risk_level,
        role=role,  # type: ignore[arg-type]
        attempt_number=attempt_number,
        provider_family=active_dispatch.selected_implementation.provider_family or "",
        model=active_dispatch.selected_implementation.model,
        reasoning_effort=active_dispatch.selected_implementation.reasoning,
        verifier_provider_family=active_dispatch.verification.implementation.provider_family,
        verifier_model=active_dispatch.verification.implementation.model,
        status=status,
        failure_scope=failure_scope,
        failure_code=failure_code,
        duration_ms=duration_ms,
        retry_after_seconds=None,
        usage=usage,
    )


def versions() -> RouteOutcomeVersionContext:
    return RouteOutcomeVersionContext(
        runtime_version="1.0.1.dev0",
        repository_revision="test-revision",
        routing_policy_revision="test-policy-revision",
        registry_revision="test-registry-revision",
        tool_versions={"provider-adapter": "1"},
    )


def passed(dispatch_id: str, verifier_model: str) -> VerificationResult:
    return VerificationResult(
        dispatch_id=dispatch_id,
        status="passed",
        verifier_model=verifier_model,
        checks=["output_validation"],
        evidence=["verification:test"],
    )


def test_primary_success_joins_route_attempt_verifier_and_versions_without_content() -> None:
    primary = dispatch(
        "dispatch-primary",
        provider="google",
        model="gemini-3.5-flash-lite",
        verifier_provider="anthropic",
        verifier_model="claude-sonnet-5",
    )
    response = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="succeeded",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        output_ref="file:///sensitive-output.txt",
        evidence=("google_request_id:secret",),
        usage=ProviderUsage(input_tokens=8, output_tokens=5, total_tokens=13),
    )
    telemetry = [
        event(
            primary,
            role="primary",
            attempt_number=1,
            status="succeeded",
            duration_ms=125.0,
            usage=ProviderUsage(input_tokens=8, output_tokens=5, total_tokens=13),
        )
    ]
    outcome = CanaryRuntimeOutcome(
        status="primary_executed",
        primary_dispatch=primary,
        primary_response=response,
        primary_attempts=1,
    )
    record = build_guarded_canary_route_outcome(
        outcome,
        telemetry,
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=passed(primary.dispatch_id, "claude-sonnet-5"),
        recorded_at="2026-08-10T15:01:00+00:00",
    ).to_dict()

    assert record["final_disposition"] == "completed"
    assert record["active_route_role"] == "primary"
    assert record["primary_route"]["attempt_count"] == 1
    assert record["primary_route"]["attempts"][0]["usage"]["total_tokens"] == 13
    assert record["versions"]["runtime_version"] == "1.0.1.dev0"
    assert record["cost"] == {
        "status": "unknown",
        "amount": None,
        "currency": None,
        "source": None,
    }
    encoded = json.dumps(record)
    for forbidden in (
        "customer@example.test",
        "Sensitive customer content",
        "sensitive-output",
        "google_request_id",
    ):
        assert forbidden not in encoded


def test_fallback_success_is_distinct_from_primary_success() -> None:
    primary = dispatch(
        "dispatch-failed-primary",
        provider="google",
        model="gemini-3.5-flash-lite",
        verifier_provider="openai",
        verifier_model="gpt-5.6-sol",
    )
    fallback = dispatch(
        "dispatch-fallback",
        provider="anthropic",
        model="claude-haiku-4-5",
        verifier_provider="openai",
        verifier_model="gpt-5.6-terra",
    )
    primary_response = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="failed",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        failure=ProviderFailure(
            scope="provider",
            code="resource_exhausted",
            message="limited",
        ),
    )
    fallback_response = ProviderExecutionResponse(
        dispatch_id=fallback.dispatch_id,
        status="succeeded",
        provider_family="anthropic",
        model="claude-haiku-4-5",
        output_ref="file:///fallback.txt",
    )
    telemetry = [
        event(
            primary,
            role="primary",
            attempt_number=1,
            status="failed",
            duration_ms=80.0,
            failure_scope="provider",
            failure_code="resource_exhausted",
        ),
        event(
            fallback,
            role="fallback",
            attempt_number=1,
            status="succeeded",
            duration_ms=120.0,
        ),
    ]
    outcome = CanaryRuntimeOutcome(
        status="fallback_executed",
        primary_dispatch=primary,
        primary_response=primary_response,
        fallback_dispatch=fallback,
        fallback_response=fallback_response,
        fallback_trigger_scope="provider",
        primary_attempts=1,
        fallback_attempts=1,
    )
    record = build_guarded_canary_route_outcome(
        outcome,
        telemetry,
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=passed(fallback.dispatch_id, "gpt-5.6-terra"),
    ).to_dict()

    assert record["final_disposition"] == "completed"
    assert record["active_route_role"] == "fallback"
    assert record["fallback_assisted"] is True
    assert record["primary_route"]["execution_status"] == "failed"
    assert record["primary_route"]["failure_scope"] == "provider"
    assert record["fallback_route"]["execution_status"] == "succeeded"
    assert record["provenance"]["source_dispatch_ids"] == [
        primary.dispatch_id,
        fallback.dispatch_id,
    ]


def test_retry_assistance_is_preserved_without_collapsing_attempts() -> None:
    primary = dispatch(
        "dispatch-retry",
        provider="google",
        model="gemini-3.5-flash-lite",
        verifier_provider="anthropic",
        verifier_model="claude-sonnet-5",
    )
    response = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="succeeded",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        output_ref="file:///retry.txt",
    )
    telemetry = [
        event(
            primary,
            role="primary",
            attempt_number=1,
            status="failed",
            duration_ms=50.0,
            failure_scope="transient",
            failure_code="timeout",
        ),
        event(
            primary,
            role="primary",
            attempt_number=2,
            status="succeeded",
            duration_ms=70.0,
        ),
    ]
    outcome = CanaryRuntimeOutcome(
        status="primary_executed",
        primary_dispatch=primary,
        primary_response=response,
        primary_attempts=2,
        primary_retry_delays_seconds=(0.25,),
    )
    record = build_guarded_canary_route_outcome(
        outcome,
        telemetry,
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=passed(primary.dispatch_id, "claude-sonnet-5"),
    ).to_dict()

    assert record["retry_assisted"] is True
    assert record["primary_route"]["retry_used"] is True
    assert [item["attempt_number"] for item in record["primary_route"]["attempts"]] == [1, 2]


def test_missing_verification_and_execution_failure_remain_explicit() -> None:
    primary = dispatch(
        "dispatch-unverified",
        provider="google",
        model="gemini-3.5-flash-lite",
        verifier_provider="anthropic",
        verifier_model="claude-sonnet-5",
    )
    success = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="succeeded",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        output_ref="file:///unverified.txt",
    )
    success_event = event(
        primary,
        role="primary",
        attempt_number=1,
        status="succeeded",
        duration_ms=50.0,
    )
    unverified = build_guarded_canary_route_outcome(
        CanaryRuntimeOutcome(
            status="primary_executed",
            primary_dispatch=primary,
            primary_response=success,
        ),
        [success_event],
        repo_root=REPO_ROOT,
        versions=versions(),
    ).to_dict()
    assert unverified["final_disposition"] == "verification_missing"
    assert unverified["verification_status"] is None

    failure = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="failed",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        failure=ProviderFailure(scope="request", code="invalid_request", message="bad"),
    )
    failure_event = event(
        primary,
        role="primary",
        attempt_number=1,
        status="failed",
        duration_ms=20.0,
        failure_scope="request",
        failure_code="invalid_request",
    )
    failed = build_guarded_canary_route_outcome(
        CanaryRuntimeOutcome(
            status="execution_failed",
            primary_dispatch=primary,
            primary_response=failure,
        ),
        [failure_event],
        repo_root=REPO_ROOT,
        versions=versions(),
    ).to_dict()
    assert failed["final_disposition"] == "execution_failed"
    assert failed["active_route_role"] is None


def test_abandoned_outcome_is_first_class_and_requires_reason() -> None:
    primary = dispatch(
        "dispatch-abandoned",
        provider="openai",
        model="gpt-5.6-luna",
        verifier_provider="anthropic",
        verifier_model="claude-sonnet-5",
    )
    telemetry = [
        event(
            primary,
            role="primary",
            attempt_number=1,
            status="failed",
            duration_ms=25.0,
            failure_scope="transient",
            failure_code="connection_reset",
        )
    ]
    record = build_abandoned_route_outcome(
        primary,
        telemetry,
        repo_root=REPO_ROOT,
        versions=versions(),
        reason="process_interrupted",
    ).to_dict()
    assert record["final_disposition"] == "abandoned"
    assert record["abandonment_reason"] == "process_interrupted"
    assert record["primary_route"]["execution_status"] == "abandoned"

    with pytest.raises(ProviderAdapterContractError, match="abandonment_reason"):
        build_abandoned_route_outcome(
            primary,
            telemetry,
            repo_root=REPO_ROOT,
            versions=versions(),
            reason="",
        )


def test_schema_and_integrity_fail_closed_on_mutation() -> None:
    primary = dispatch(
        "dispatch-integrity",
        provider="google",
        model="gemini-3.5-flash-lite",
        verifier_provider="anthropic",
        verifier_model="claude-sonnet-5",
    )
    response = ProviderExecutionResponse(
        dispatch_id=primary.dispatch_id,
        status="succeeded",
        provider_family="google",
        model="gemini-3.5-flash-lite",
        output_ref="file:///integrity.txt",
    )
    telemetry = [
        event(
            primary,
            role="primary",
            attempt_number=1,
            status="succeeded",
            duration_ms=10.0,
        )
    ]
    original = build_guarded_canary_route_outcome(
        CanaryRuntimeOutcome(
            status="primary_executed",
            primary_dispatch=primary,
            primary_response=response,
        ),
        telemetry,
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=passed(primary.dispatch_id, "claude-sonnet-5"),
    ).to_dict()

    unknown = dict(original)
    unknown["task"] = "must not be accepted"
    with pytest.raises(ProviderAdapterContractError, match="schema validation"):
        RouteOutcomeRecord.from_dict(unknown, repo_root=REPO_ROOT)

    tampered = json.loads(json.dumps(original))
    tampered["task_type"] = "documentation"
    with pytest.raises(ProviderAdapterContractError, match="integrity hash"):
        RouteOutcomeRecord.from_dict(tampered, repo_root=REPO_ROOT)


def test_jsonl_sink_round_trips_validated_records(tmp_path: Path) -> None:
    fixture_path = REPO_ROOT / "reference" / "datasets" / "route-outcomes" / "route-outcomes-v1.jsonl"
    first_payload = json.loads(fixture_path.read_text(encoding="utf-8").splitlines()[0])
    first = RouteOutcomeRecord.from_dict(first_payload, repo_root=REPO_ROOT)

    sink = JsonlRouteOutcomeSink(tmp_path / "route-outcomes.jsonl", repo_root=REPO_ROOT)
    sink.append(first)
    loaded = sink.read_all()
    assert len(loaded) == 1
    assert loaded[0].to_dict() == first.to_dict()


def test_reproducible_route_outcome_fixtures_are_schema_and_integrity_valid() -> None:
    fixture_path = REPO_ROOT / "reference" / "datasets" / "route-outcomes" / "route-outcomes-v1.jsonl"
    records = [
        RouteOutcomeRecord.from_dict(json.loads(line), repo_root=REPO_ROOT)
        for line in fixture_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert [record.to_dict()["final_disposition"] for record in records] == [
        "completed",
        "completed",
        "abandoned",
    ]
    assert records[1].to_dict()["fallback_assisted"] is True
