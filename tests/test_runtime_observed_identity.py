from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.application.finalization.service import FinalizationError, FinalizationService
from teo_reference.final_execution_provenance import attach_execution_provenance
from teo_reference.provider_adapter import ProviderExecutionResponse
from teo_reference.route_outcome import RouteOutcomeVersionContext, build_guarded_canary_route_outcome
from teo_reference.runtime_canary import CanaryRuntimeOutcome
from teo_reference.runtime_identity import (
    RuntimeIdentityError,
    RuntimeIdentityObservation,
    compare_runtime_identity,
)
from teo_reference.runtime_telemetry import RuntimeTelemetryEvent
from teo_reference.schemas import (
    DispatchRecord,
    ExecutionResult,
    ImplementationChoice,
    VerificationPlan,
    VerificationResult,
)


class _UnusedArtifactIntegrity:
    def revalidate(self, output_ref, verified_artifact, *, allowed_root):  # pragma: no cover
        raise AssertionError("artifact revalidation is not expected in these tests")


def _dispatch() -> DispatchRecord:
    executor = ImplementationChoice(
        agent="worker",
        model="executor-model",
        profile=None,
        provider_family="openai",
        availability="available",
        source="test",
        reasoning="medium",
    )
    verifier = ImplementationChoice(
        agent="checker",
        model="checker-model",
        profile=None,
        provider_family="anthropic",
        availability="available",
        source="test",
        reasoning="high",
    )
    return DispatchRecord(
        task_id="task-rmi6",
        dispatch_id="dispatch-rmi6",
        created_at="2026-08-23T06:00:00+00:00",
        task="Inspect the runtime identity contract.",
        task_type="high_volume_simple",
        risk_level="low",
        selected_team="engineering",
        selected_worker="worker",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["reasoning"],
        selected_implementation=executor,
        fallback_implementation=None,
        verification=VerificationPlan(
            team="verification",
            method=["independent_review"],
            implementation=verifier,
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=[],
        warnings=[],
    )


def _executor_identity(
    *,
    model: str = "executor-model",
    provider_family: str = "openai",
    model_observed: bool = True,
) -> RuntimeIdentityObservation:
    return RuntimeIdentityObservation(
        provider_family=provider_family,
        model=model,
        source="provider_response" if model_observed else "provider_adapter",
        model_observed=model_observed,
    )


def _verifier_identity(
    *,
    model: str = "checker-model",
    provider_family: str = "anthropic",
    model_observed: bool = True,
) -> RuntimeIdentityObservation:
    return RuntimeIdentityObservation(
        provider_family=provider_family,
        model=model,
        source="verifier_response" if model_observed else "verifier_adapter",
        model_observed=model_observed,
    )


def _provider_response(
    *,
    model: str = "executor-model",
    provider_family: str = "openai",
    model_observed: bool = True,
) -> ProviderExecutionResponse:
    return ProviderExecutionResponse(
        dispatch_id="dispatch-rmi6",
        status="succeeded",
        provider_family=provider_family,
        model=model,
        model_observed=model_observed,
        output_ref="file:///tmp/rmi6-output.txt",
        evidence=("provider_attempt:test",),
    )


def _telemetry(dispatch: DispatchRecord, response: ProviderExecutionResponse) -> RuntimeTelemetryEvent:
    return RuntimeTelemetryEvent.from_attempt(
        dispatch,
        response,
        role="primary",
        attempt_number=1,
        duration_seconds=0.125,
        recorded_at="2026-08-23T06:00:01+00:00",
    )


def _versions() -> RouteOutcomeVersionContext:
    return RouteOutcomeVersionContext(
        runtime_version="test-runtime",
        repository_revision="test-revision",
    )


def _canary(dispatch: DispatchRecord, response: ProviderExecutionResponse) -> CanaryRuntimeOutcome:
    return CanaryRuntimeOutcome(
        status="primary_executed",
        primary_dispatch=dispatch,
        primary_response=response,
        primary_attempts=1,
    )


def test_runtime_identity_comparison_distinguishes_match_mismatch_and_unconfirmed() -> None:
    assert compare_runtime_identity(
        expected_provider_family="openai",
        expected_model="executor-model",
        observed=_executor_identity(),
    ) == "match"
    assert compare_runtime_identity(
        expected_provider_family="openai",
        expected_model="executor-model",
        observed=_executor_identity(model="different-model"),
    ) == "mismatch"
    assert compare_runtime_identity(
        expected_provider_family="openai",
        expected_model="executor-model",
        observed=_executor_identity(provider_family="google"),
    ) == "mismatch"
    assert compare_runtime_identity(
        expected_provider_family="openai",
        expected_model="executor-model",
        observed=_executor_identity(model_observed=False),
    ) == "unconfirmed"
    assert compare_runtime_identity(
        expected_provider_family=None,
        expected_model="executor-model",
        observed=_executor_identity(),
    ) == "unconfirmed"


def test_configuration_identity_cannot_be_claimed_without_valid_attestation() -> None:
    with pytest.raises(RuntimeIdentityError, match="cannot be populated"):
        RuntimeIdentityObservation(
            provider_family="openai",
            model="executor-model",
            source="provider_response",
            model_observed=True,
            configuration_fingerprint="a" * 64,
            configuration_observed=False,
        )
    with pytest.raises(RuntimeIdentityError, match="lowercase SHA-256"):
        RuntimeIdentityObservation(
            provider_family="openai",
            model="executor-model",
            source="provider_response",
            model_observed=True,
            configuration_fingerprint="not-a-digest",
            configuration_observed=True,
        )


def test_provider_execution_result_retains_observed_identity() -> None:
    result = _provider_response(model="actual-model").to_execution_result()
    assert result.observed_identity is not None
    assert result.observed_identity.provider_family == "openai"
    assert result.observed_identity.model == "actual-model"
    assert result.observed_identity.model_observed is True
    assert result.observed_identity.configuration_observed is False


def test_runtime_telemetry_keeps_intended_and_observed_identity_separate() -> None:
    dispatch = _dispatch()
    event = _telemetry(dispatch, _provider_response(model="actual-model"))
    assert event.intended_provider_family == "openai"
    assert event.intended_model == "executor-model"
    assert event.provider_family == "openai"
    assert event.model == "actual-model"
    assert event.identity_status == "mismatch"
    assert event.model_observed is True
    assert event.configuration_identity_observed is False
    assert event.verifier_identity_source == "assigned"


def test_route_outcome_preserves_executor_mismatch_and_refuses_completed_disposition(tmp_path: Path) -> None:
    dispatch = _dispatch()
    response = _provider_response(model="actual-model")
    record = build_guarded_canary_route_outcome(
        _canary(dispatch, response),
        [_telemetry(dispatch, response)],
        repo_root=Path(__file__).parents[1],
        versions=_versions(),
        recorded_at="2026-08-23T06:00:02+00:00",
    ).to_dict()

    assert record["final_disposition"] == "identity_mismatch"
    assert record["primary_route"]["implementation"]["model"] == "executor-model"
    assert record["primary_route"]["implementation"]["observed_identity"]["model"] == "actual-model"
    assert record["primary_route"]["implementation"]["identity_status"] == "mismatch"
    assert record["provenance"]["executor_identity_status"] == "mismatch"
    assert record["provenance"]["configuration_identity_observed"] is False


def test_route_outcome_marks_missing_model_attestation_unconfirmed() -> None:
    dispatch = _dispatch()
    response = _provider_response(model_observed=False)
    record = build_guarded_canary_route_outcome(
        _canary(dispatch, response),
        [_telemetry(dispatch, response)],
        repo_root=Path(__file__).parents[1],
        versions=_versions(),
        recorded_at="2026-08-23T06:00:02+00:00",
    ).to_dict()

    assert record["final_disposition"] == "identity_unconfirmed"
    assert record["primary_route"]["implementation"]["identity_status"] == "unconfirmed"
    assert record["primary_route"]["implementation"]["observed_identity"]["model_observed"] is False


def test_route_outcome_preserves_checker_mismatch_as_integrity_failure() -> None:
    dispatch = _dispatch()
    response = _provider_response()
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="failed",
        verifier_model="checker-model",
        checks=["runtime_identity:mismatch"],
        evidence=["checker_attempt:test"],
        notes="observed_checker_identity:mismatch",
        observed_identity=_verifier_identity(model="different-checker"),
    )
    record = build_guarded_canary_route_outcome(
        _canary(dispatch, response),
        [_telemetry(dispatch, response)],
        repo_root=Path(__file__).parents[1],
        versions=_versions(),
        verification=verification,
        recorded_at="2026-08-23T06:00:02+00:00",
    ).to_dict()

    assert record["final_disposition"] == "identity_mismatch"
    assert record["primary_route"]["verifier"]["model"] == "checker-model"
    assert record["primary_route"]["verifier"]["observed_identity"]["model"] == "different-checker"
    assert record["primary_route"]["verifier"]["identity_status"] == "mismatch"
    assert record["provenance"]["verifier_identity_status"] == "mismatch"


def test_finalization_fails_closed_on_executor_or_checker_identity_drift() -> None:
    dispatch = _dispatch()
    service = FinalizationService(_UnusedArtifactIntegrity())
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model="checker-model",
        observed_identity=_verifier_identity(),
    )

    with pytest.raises(FinalizationError, match="executor runtime identity is mismatch"):
        service.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                observed_identity=_executor_identity(model="different-model"),
            ),
            verification,
        )

    with pytest.raises(FinalizationError, match="verifier runtime identity is mismatch"):
        service.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                observed_identity=_executor_identity(),
            ),
            VerificationResult(
                dispatch_id=dispatch.dispatch_id,
                status="failed",
                verifier_model="checker-model",
                observed_identity=_verifier_identity(model="different-checker"),
            ),
        )


def test_matching_observed_identity_reaches_final_provenance() -> None:
    dispatch = _dispatch()
    response = _provider_response()
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model="checker-model",
        evidence=["checker_attempt:test"],
        observed_identity=_verifier_identity(),
    )
    route_outcome = build_guarded_canary_route_outcome(
        _canary(dispatch, response),
        [_telemetry(dispatch, response)],
        repo_root=Path(__file__).parents[1],
        versions=_versions(),
        verification=verification,
        recorded_at="2026-08-23T06:00:02+00:00",
    )
    final = FinalizationService(_UnusedArtifactIntegrity()).finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            evidence=["provider_attempt:test"],
            observed_identity=_executor_identity(),
        ),
        verification,
    )
    final = attach_execution_provenance(
        final,
        route_outcome,
        repo_root=Path(__file__).parents[1],
    )

    assert final.status == "completed"
    assert final.execution_provenance is not None
    assert final.execution_provenance.provider_family == "openai"
    assert final.execution_provenance.model == "executor-model"
    assert final.execution_provenance.intended_provider_family == "openai"
    assert final.execution_provenance.intended_model == "executor-model"
    assert final.execution_provenance.executor_identity_status == "match"
    assert final.execution_provenance.observed_verifier_provider_family == "anthropic"
    assert final.execution_provenance.observed_verifier_model == "checker-model"
    assert final.execution_provenance.verifier_identity_status == "match"
    assert final.execution_provenance.configuration_identity_observed is False


def test_runtime_identity_contract_has_no_routing_or_connection_authority_imports() -> None:
    source = (
        Path(__file__).parents[1]
        / "reference/implementations/python/src/teo_reference/runtime_identity.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)

    forbidden = (
        "routing",
        "runtime_selection",
        "runtime_dispatch_binding",
        "provider_connection",
        "configuration",
    )
    assert not any(any(token in imported for token in forbidden) for imported in imports)
