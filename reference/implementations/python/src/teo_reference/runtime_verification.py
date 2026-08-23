from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from .anthropic_verifier import AnthropicLiveVerifier
from .google_verifier import GoogleLiveVerifier
from .openai_verifier import OpenAILiveVerifier
from .provider_adapter import ProviderExecutionResponse, ProviderUsage
from .provider_connection import ProviderConnection
from .runtime_canary import CanaryRuntimeOutcome
from .runtime_identity import IdentityStatus, compare_runtime_identity
from .schemas import DispatchRecord, VerificationResult
from .specialist_routing import SpecialistRoutingEngine
from .verification_adapter import (
    LiveVerificationError,
    LiveVerificationRequest,
    read_execution_artifact,
)
from .verification_policy import LiveVerificationPolicy


@dataclass(frozen=True, slots=True)
class LiveVerificationExecution:
    """Verification result plus normalized provider and runtime-identity evidence."""

    result: VerificationResult
    provider_family: str
    model: str
    recorded_at: str
    usage: ProviderUsage | None
    identity_status: IdentityStatus


def active_execution_from_outcome(
    outcome: CanaryRuntimeOutcome,
) -> tuple[DispatchRecord, ProviderExecutionResponse]:
    if outcome.status == "primary_executed" and outcome.primary_response.status == "succeeded":
        dispatch, response = outcome.primary_dispatch, outcome.primary_response
    elif (
        outcome.status == "fallback_executed"
        and outcome.fallback_dispatch is not None
        and outcome.fallback_response is not None
        and outcome.fallback_response.status == "succeeded"
    ):
        dispatch, response = outcome.fallback_dispatch, outcome.fallback_response
    else:
        raise LiveVerificationError("Live verification requires a successful active execution")

    status = compare_runtime_identity(
        expected_provider_family=dispatch.selected_implementation.provider_family,
        expected_model=dispatch.selected_implementation.model,
        observed=response.observed_identity(),
    )
    if status != "match":
        raise LiveVerificationError(
            f"Live verification refuses execution with {status} observed runtime identity"
        )
    return dispatch, response


def execute_live_verification_with_evidence(
    engine: SpecialistRoutingEngine,
    dispatch: DispatchRecord,
    execution: ProviderExecutionResponse,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path,
    verification_policy: LiveVerificationPolicy | None = None,
) -> LiveVerificationExecution:
    """Execute the assigned verifier and preserve normalized identity and usage evidence."""
    policy = verification_policy or LiveVerificationPolicy.load(engine.config.root)
    policy.validate()

    if dispatch.task_type not in policy.task_types:
        raise LiveVerificationError("Dispatch is outside the active live verification task scope")
    if dispatch.risk_level not in policy.risk_levels:
        raise LiveVerificationError("Guarded live verification refuses high and critical risk")
    if execution.status != "succeeded" or not execution.output_ref:
        raise LiveVerificationError("Live verification requires a successful execution artifact")
    if execution.dispatch_id != dispatch.dispatch_id:
        raise LiveVerificationError("Execution artifact does not belong to the active dispatch")

    execution_identity_status = compare_runtime_identity(
        expected_provider_family=dispatch.selected_implementation.provider_family,
        expected_model=dispatch.selected_implementation.model,
        observed=execution.observed_identity(),
    )
    if execution_identity_status != "match":
        raise LiveVerificationError(
            f"Live verification refuses execution with {execution_identity_status} observed runtime identity"
        )
    if dispatch.verification.human_approval_required and policy.human_approval_satisfied_by_model_verifier:
        raise LiveVerificationError("Model verification cannot satisfy qualified-human approval")

    output_text, verified_artifact = read_execution_artifact(
        execution.output_ref,
        allowed_root=artifact_root,
        max_bytes=policy.max_output_bytes,
    )
    request = LiveVerificationRequest.from_execution(dispatch, output_text)
    if policy.require_provider_diversity and request.verifier_provider_family == execution.provider_family:
        raise LiveVerificationError(
            "Guarded live verification requires provider-diverse execution and verification"
        )

    if request.verifier_provider_family == "google":
        response = GoogleLiveVerifier(connections).verify(request)
    elif request.verifier_provider_family == "anthropic":
        response = AnthropicLiveVerifier(connections).verify(request)
    elif request.verifier_provider_family == "openai":
        response = OpenAILiveVerifier(connections).verify(request)
    else:
        raise LiveVerificationError(
            f"No guarded live verifier adapter exists for {request.verifier_provider_family}"
        )

    observed_identity = response.observed_identity()
    identity_status = compare_runtime_identity(
        expected_provider_family=request.verifier_provider_family,
        expected_model=request.verifier_model,
        observed=observed_identity,
    )

    if identity_status == "match":
        result = response.decision.to_verification_result(
            dispatch,
            evidence=list(response.evidence),
            verified_artifact=verified_artifact,
            observed_identity=observed_identity,
        )
    else:
        result = VerificationResult(
            dispatch_id=dispatch.dispatch_id,
            status="failed",
            verifier_model=dispatch.verification.implementation.model,
            checks=[f"runtime_identity:{identity_status}"],
            evidence=list(response.evidence),
            notes=f"observed_checker_identity:{identity_status}",
            verified_artifact=verified_artifact,
            observed_identity=observed_identity,
        )

    return LiveVerificationExecution(
        result=result,
        provider_family=response.provider_family,
        model=response.model,
        recorded_at=datetime.now(timezone.utc).isoformat(),
        usage=response.usage,
        identity_status=identity_status,
    )


def execute_live_verification(
    engine: SpecialistRoutingEngine,
    dispatch: DispatchRecord,
    execution: ProviderExecutionResponse,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path,
    verification_policy: LiveVerificationPolicy | None = None,
) -> VerificationResult:
    """Compatibility wrapper returning the canonical VerificationResult only."""
    return execute_live_verification_with_evidence(
        engine,
        dispatch,
        execution,
        connections,
        artifact_root=artifact_root,
        verification_policy=verification_policy,
    ).result


def verify_guarded_canary_outcome_with_evidence(
    engine: SpecialistRoutingEngine,
    outcome: CanaryRuntimeOutcome,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path,
    verification_policy: LiveVerificationPolicy | None = None,
) -> LiveVerificationExecution:
    """Run the active dispatch verifier and preserve normalized identity evidence."""
    dispatch, execution = active_execution_from_outcome(outcome)
    return execute_live_verification_with_evidence(
        engine,
        dispatch,
        execution,
        connections,
        artifact_root=artifact_root,
        verification_policy=verification_policy,
    )


def verify_guarded_canary_outcome(
    engine: SpecialistRoutingEngine,
    outcome: CanaryRuntimeOutcome,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path,
    verification_policy: LiveVerificationPolicy | None = None,
) -> VerificationResult:
    """Compatibility wrapper for the canonical guarded verification result."""
    return verify_guarded_canary_outcome_with_evidence(
        engine,
        outcome,
        connections,
        artifact_root=artifact_root,
        verification_policy=verification_policy,
    ).result