from __future__ import annotations

from typing import Mapping

from .anthropic_verifier import AnthropicLiveVerifier
from .google_verifier import GoogleLiveVerifier
from .openai_verifier import OpenAILiveVerifier
from .provider_adapter import ProviderExecutionResponse
from .provider_connection import ProviderConnection
from .runtime_canary import CanaryRuntimeOutcome
from .schemas import DispatchRecord, VerificationResult
from .verification_adapter import (
    LiveVerificationError,
    LiveVerificationRequest,
    read_execution_output,
)


def active_execution_from_outcome(
    outcome: CanaryRuntimeOutcome,
) -> tuple[DispatchRecord, ProviderExecutionResponse]:
    if outcome.status == "primary_executed" and outcome.primary_response.status == "succeeded":
        return outcome.primary_dispatch, outcome.primary_response
    if (
        outcome.status == "fallback_executed"
        and outcome.fallback_dispatch is not None
        and outcome.fallback_response is not None
        and outcome.fallback_response.status == "succeeded"
    ):
        return outcome.fallback_dispatch, outcome.fallback_response
    raise LiveVerificationError("Live verification requires a successful active execution")


def execute_live_verification(
    dispatch: DispatchRecord,
    execution: ProviderExecutionResponse,
    connections: Mapping[str, ProviderConnection],
) -> VerificationResult:
    """Execute the verifier already assigned by the active TEO dispatch exactly once."""
    if dispatch.task_type != "high_volume_simple":
        raise LiveVerificationError(
            "Guarded live verification is authorized only for high_volume_simple"
        )
    if dispatch.risk_level not in {"low", "medium"}:
        raise LiveVerificationError("Guarded live verification refuses high and critical risk")
    if execution.status != "succeeded" or not execution.output_ref:
        raise LiveVerificationError("Live verification requires a successful execution artifact")
    if execution.dispatch_id != dispatch.dispatch_id:
        raise LiveVerificationError("Execution artifact does not belong to the active dispatch")
    if execution.provider_family != dispatch.selected_implementation.provider_family:
        raise LiveVerificationError("Execution provider does not match the active dispatch")
    if execution.model != dispatch.selected_implementation.model:
        raise LiveVerificationError("Execution model does not match the active dispatch")

    output_text = read_execution_output(execution.output_ref)
    request = LiveVerificationRequest.from_execution(dispatch, output_text)
    if request.verifier_provider_family == execution.provider_family:
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

    if response.provider_family != request.verifier_provider_family:
        raise LiveVerificationError("Live verifier changed the assigned provider family")
    if response.model != request.verifier_model:
        raise LiveVerificationError("Live verifier changed the assigned model")
    return response.decision.to_verification_result(
        dispatch,
        evidence=list(response.evidence),
    )


def verify_guarded_canary_outcome(
    outcome: CanaryRuntimeOutcome,
    connections: Mapping[str, ProviderConnection],
) -> VerificationResult:
    """Run the active dispatch's assigned independent verifier after guarded execution."""
    dispatch, execution = active_execution_from_outcome(outcome)
    return execute_live_verification(dispatch, execution, connections)
