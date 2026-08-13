from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from teo_reference.final_execution_provenance import attach_execution_provenance
from teo_reference.provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionResponse,
    ProviderFailure,
)
from teo_reference.route_outcome import (
    RouteOutcomeVersionContext,
    build_guarded_canary_route_outcome,
)
from teo_reference.runtime_canary import CanaryRuntimeOutcome
from teo_reference.runtime_telemetry import RuntimeTelemetryEvent
from teo_reference.schemas import (
    DispatchRecord,
    FinalOutcome,
    ImplementationChoice,
    VerificationPlan,
    VerificationResult,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def choice(model: str, provider: str, reasoning: str = "low") -> ImplementationChoice:
    return ImplementationChoice(
        agent="final-provenance-test",
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
) -> DispatchRecord:
    return DispatchRecord(
        task_id="task-final-provenance",
        dispatch_id=dispatch_id,
        created_at="2026-08-13T05:00:00+00:00",
        task="Synthetic provenance test",
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
            human_approval_required=False,
        ),
        routing_explanation=["test"],
        warnings=[],
    )


def event(active_dispatch: DispatchRecord, *, role: str, status: str) -> RuntimeTelemetryEvent:
    return RuntimeTelemetryEvent(
        recorded_at="2026-08-13T05:00:01+00:00",
        dispatch_id=active_dispatch.dispatch_id,
        task_type=active_dispatch.task_type,
        risk_level=active_dispatch.risk_level,
        role=role,  # type: ignore[arg-type]
        attempt_number=1,
        provider_family=active_dispatch.selected_implementation.provider_family or "",
        model=active_dispatch.selected_implementation.model,
        reasoning_effort=active_dispatch.selected_implementation.reasoning,
        verifier_provider_family=active_dispatch.verification.implementation.provider_family,
        verifier_model=active_dispatch.verification.implementation.model,
        status=status,
        failure_scope=None if status == "succeeded" else "provider",
        failure_code=None if status == "succeeded" else "unavailable",
        duration_ms=10.0,
        retry_after_seconds=None,
        usage=None,
    )


def versions() -> RouteOutcomeVersionContext:
    return RouteOutcomeVersionContext(
        runtime_version="1.0.1.dev0",
        repository_revision="final-provenance-test",
        routing_policy_revision="policy-test",
        registry_revision="registry-test",
        tool_versions={"provider-adapter": "1"},
    )


def verification(active_dispatch: DispatchRecord, status: str = "passed") -> VerificationResult:
    return VerificationResult(
        dispatch_id=active_dispatch.dispatch_id,
        status=status,  # type: ignore[arg-type]
        verifier_model=active_dispatch.verification.implementation.model,
        checks=["output_validation"],
        evidence=["verification:test"],
    )


def final_outcome(active_dispatch: DispatchRecord, *, status: str = "completed", verification_status: str = "passed") -> FinalOutcome:
    return FinalOutcome(
        dispatch_id=active_dispatch.dispatch_id,
        task_id=active_dispatch.task_id,
        completed_at="2026-08-13T05:00:02+00:00",
        status=status,  # type: ignore[arg-type]
        execution_status="succeeded",
        verification_status=verification_status,  # type: ignore[arg-type]
        selected_model=active_dispatch.selected_implementation.model,
        verifier_model=active_dispatch.verification.implementation.model,
        evidence=["execution:test", "verification:test"],
        failed_attempts=0,
        escalation_used=False,
        notes=["test"],
    )


def primary_record():
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
        model=primary.selected_implementation.model,
        output_ref="file:///synthetic.txt",
    )
    record = build_guarded_canary_route_outcome(
        CanaryRuntimeOutcome(
            status="primary_executed",
            primary_dispatch=primary,
            primary_response=response,
        ),
        [event(primary, role="primary", status="succeeded")],
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=verification(primary),
        recorded_at="2026-08-13T05:00:03+00:00",
    )
    return primary, record


def fallback_record():
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
        model=primary.selected_implementation.model,
        failure=ProviderFailure(scope="provider", code="unavailable", message="unavailable"),
    )
    fallback_response = ProviderExecutionResponse(
        dispatch_id=fallback.dispatch_id,
        status="succeeded",
        provider_family="anthropic",
        model=fallback.selected_implementation.model,
        output_ref="file:///fallback.txt",
    )
    record = build_guarded_canary_route_outcome(
        CanaryRuntimeOutcome(
            status="fallback_executed",
            primary_dispatch=primary,
            primary_response=primary_response,
            fallback_dispatch=fallback,
            fallback_response=fallback_response,
            fallback_trigger_scope="provider",
            primary_attempts=1,
            fallback_attempts=1,
        ),
        [
            event(primary, role="primary", status="failed"),
            event(fallback, role="fallback", status="succeeded"),
        ],
        repo_root=REPO_ROOT,
        versions=versions(),
        verification=verification(fallback),
        recorded_at="2026-08-13T05:00:03+00:00",
    )
    return primary, fallback, record


def test_legacy_final_outcome_serialization_omits_optional_provenance() -> None:
    primary, _ = primary_record()
    encoded = final_outcome(primary).to_dict()
    assert "execution_provenance" not in encoded


def test_primary_projection_uses_observed_active_execution_provider_not_verifier() -> None:
    primary, record = primary_record()
    projected = attach_execution_provenance(final_outcome(primary), record, repo_root=REPO_ROOT)

    assert projected.execution_provenance is not None
    assert projected.execution_provenance.active_route_role == "primary"
    assert projected.execution_provenance.provider_family == "google"
    assert projected.execution_provenance.model == "gemini-3.5-flash-lite"
    assert projected.execution_provenance.provider_family != primary.verification.implementation.provider_family
    assert projected.execution_provenance.route_outcome_integrity_sha256 == record.to_dict()["integrity_sha256"]


def test_fallback_projection_reports_successful_fallback_not_failed_primary() -> None:
    primary, fallback, record = fallback_record()
    projected = attach_execution_provenance(final_outcome(fallback), record, repo_root=REPO_ROOT)

    assert projected.execution_provenance is not None
    assert projected.execution_provenance.active_route_role == "fallback"
    assert projected.execution_provenance.provider_family == "anthropic"
    assert projected.execution_provenance.model == fallback.selected_implementation.model
    assert projected.execution_provenance.provider_family != primary.selected_implementation.provider_family
    assert projected.execution_provenance.fallback_assisted is True


def test_tampered_route_outcome_is_rejected_before_projection() -> None:
    primary, record = primary_record()
    tampered = record.to_dict()
    tampered["primary_route"]["implementation"]["provider_family"] = "openai"

    with pytest.raises(ProviderAdapterContractError, match="integrity|attempt provider"):
        attach_execution_provenance(final_outcome(primary), tampered, repo_root=REPO_ROOT)


def test_active_dispatch_mismatch_cannot_project_planned_primary_as_executed() -> None:
    primary, fallback, record = fallback_record()

    with pytest.raises(ProviderAdapterContractError, match="active dispatch"):
        attach_execution_provenance(final_outcome(primary), record, repo_root=REPO_ROOT)

    assert fallback.dispatch_id != primary.dispatch_id


def test_selected_model_mismatch_is_rejected() -> None:
    primary, record = primary_record()
    outcome = final_outcome(primary)
    outcome.selected_model = "not-the-active-model"

    with pytest.raises(ProviderAdapterContractError, match="active model"):
        attach_execution_provenance(outcome, record, repo_root=REPO_ROOT)


def test_verifier_model_mismatch_is_rejected() -> None:
    primary, record = primary_record()
    outcome = final_outcome(primary)
    outcome.verifier_model = "not-the-route-verifier"

    with pytest.raises(ProviderAdapterContractError, match="verifier model"):
        attach_execution_provenance(outcome, record, repo_root=REPO_ROOT)


def test_final_status_must_match_route_outcome_disposition() -> None:
    primary, record = primary_record()
    outcome = final_outcome(primary, status="failed")

    with pytest.raises(ProviderAdapterContractError, match="status"):
        attach_execution_provenance(outcome, record, repo_root=REPO_ROOT)


def test_verification_status_must_match_route_outcome() -> None:
    primary, record = primary_record()
    outcome = final_outcome(primary, status="failed", verification_status="failed")

    with pytest.raises(ProviderAdapterContractError, match="verification status"):
        attach_execution_provenance(outcome, record, repo_root=REPO_ROOT)


def test_different_existing_provenance_cannot_be_silently_replaced() -> None:
    primary, record = primary_record()
    projected = attach_execution_provenance(final_outcome(primary), record, repo_root=REPO_ROOT)
    assert projected.execution_provenance is not None
    projected.execution_provenance = replace(
        projected.execution_provenance,
        provider_family="tampered-provider",
    )

    with pytest.raises(ProviderAdapterContractError, match="cannot be replaced"):
        attach_execution_provenance(projected, record, repo_root=REPO_ROOT)


def test_projected_final_outcome_passes_strict_schema() -> None:
    primary, record = primary_record()
    projected = attach_execution_provenance(final_outcome(primary), record, repo_root=REPO_ROOT).to_dict()
    schema = json.loads((REPO_ROOT / "reference/schemas/final-outcome.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(projected))
    assert errors == []
