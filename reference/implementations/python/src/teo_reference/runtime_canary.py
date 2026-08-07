from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from random import random
from time import sleep
from typing import Literal, Mapping

from .anthropic_adapter import execute_anthropic_canary_once
from .google_adapter import execute_gemini_canary_once
from .openai_adapter import execute_openai_canary_once
from .provider_adapter import (
    ProviderAdapterContractError,
    ProviderExecutionResponse,
)
from .provider_connection import ProviderConnection
from .runtime_circuit_breaker import (
    JsonFileCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
)
from .runtime_retry import (
    RandomSource,
    RetryExecution,
    RetryPolicy,
    Sleeper,
    execute_with_transient_retry,
)
from .schemas import DispatchRecord, TaskConstraints, TaskRequest
from .specialist_routing import SpecialistRoutingEngine

FALLBACK_ELIGIBLE_SCOPES = {"model", "provider"}
CanaryRuntimeStatus = Literal["primary_executed", "fallback_executed", "execution_failed"]


@dataclass(frozen=True, slots=True)
class CanaryRuntimeOutcome:
    """Execution-only canary outcome. Verification remains a separate required gate."""

    status: CanaryRuntimeStatus
    primary_dispatch: DispatchRecord
    primary_response: ProviderExecutionResponse
    primary_attempts: int = 1
    primary_retry_delays_seconds: tuple[float, ...] = ()
    fallback_dispatch: DispatchRecord | None = None
    fallback_response: ProviderExecutionResponse | None = None
    fallback_attempts: int = 0
    fallback_retry_delays_seconds: tuple[float, ...] = ()
    fallback_trigger_scope: str | None = None
    circuit_blocked_providers: tuple[str, ...] = ()
    primary_provider_circuit_state: str = "closed"
    fallback_provider_circuit_state: str | None = None

    @property
    def execution_succeeded(self) -> bool:
        if self.status == "primary_executed":
            return self.primary_response.status == "succeeded"
        if self.status == "fallback_executed" and self.fallback_response is not None:
            return self.fallback_response.status == "succeeded"
        return False



def _copy_task_for_redispatch(
    task: TaskRequest,
    dispatch: DispatchRecord,
    failure_scope: str,
) -> TaskRequest:
    constraints = TaskConstraints(
        contexts=list(task.constraints.contexts),
        required_capabilities=list(task.constraints.required_capabilities),
        blocked_implementations=list(task.constraints.blocked_implementations),
        blocked_providers=list(task.constraints.blocked_providers),
        require_human_approval=task.constraints.require_human_approval,
    )
    if failure_scope == "model":
        model = dispatch.selected_implementation.model
        if model not in constraints.blocked_implementations:
            constraints.blocked_implementations.append(model)
    elif failure_scope == "provider":
        provider = dispatch.selected_implementation.provider_family
        if not provider:
            raise ProviderAdapterContractError(
                "Provider-scoped canary failure cannot be redispatched without provider_family"
            )
        if provider not in constraints.blocked_providers:
            constraints.blocked_providers.append(provider)
    else:
        raise ProviderAdapterContractError(
            f"Failure scope {failure_scope} is not eligible for guarded canary fallback"
        )

    return TaskRequest(
        task=task.task,
        task_id=task.task_id,
        task_type=dispatch.task_type,
        risk_level=dispatch.risk_level,
        domain=task.domain,
        specialist=dispatch.selected_specialist or task.specialist,
        constraints=constraints,
    )


def _execute_dispatch(
    dispatch: DispatchRecord,
    connections: Mapping[str, ProviderConnection],
    artifact_root: str | Path,
) -> ProviderExecutionResponse:
    provider = dispatch.selected_implementation.provider_family
    if provider not in connections:
        raise ProviderAdapterContractError(
            f"No runtime connection is available for dispatch-selected provider {provider}"
        )
    connection = connections[provider]
    root = Path(artifact_root)
    if provider == "anthropic":
        return execute_anthropic_canary_once(
            dispatch,
            connection,
            artifact_dir=root / "anthropic",
        )
    if provider == "openai":
        return execute_openai_canary_once(
            dispatch,
            connection,
            artifact_dir=root / "openai",
        )
    if provider == "google":
        return execute_gemini_canary_once(
            dispatch,
            connection,
            artifact_dir=root / "google",
        )
    raise ProviderAdapterContractError(
        f"Guarded live canary has no adapter for provider {provider}"
    )


def _execute_with_retry(
    dispatch: DispatchRecord,
    connections: Mapping[str, ProviderConnection],
    artifact_root: str | Path,
    retry_policy: RetryPolicy,
    sleeper: Sleeper,
    random_source: RandomSource,
) -> RetryExecution:
    return execute_with_transient_retry(
        dispatch,
        connections,
        artifact_root,
        _execute_dispatch,
        retry_policy,
        sleeper=sleeper,
        random_source=random_source,
    )


def _circuit_block_delta(original: TaskRequest, prepared: TaskRequest) -> tuple[str, ...]:
    original_blocks = set(original.constraints.blocked_providers)
    return tuple(
        provider
        for provider in prepared.constraints.blocked_providers
        if provider not in original_blocks
    )


def execute_guarded_canary(
    engine: SpecialistRoutingEngine,
    task: TaskRequest,
    connections: Mapping[str, ProviderConnection],
    *,
    artifact_root: str | Path = ".teo/runtime/artifacts",
    retry_policy: RetryPolicy | None = None,
    circuit_breaker: ProviderCircuitBreaker | None = None,
    sleeper: Sleeper = sleep,
    random_source: RandomSource = random,
) -> CanaryRuntimeOutcome:
    """Execute one primary dispatch and at most one policy-driven redispatch fallback.

    Each dispatch may use bounded transient retry. Provider-family circuit state is applied
    before routing and observed only after the dispatch's retry sequence finishes. Adapters
    remain stateless and never own retry, fallback, or circuit-breaker authority.
    """
    if task.task_type != "high_volume_simple":
        raise ProviderAdapterContractError(
            "Guarded automatic fallback is authorized only for explicit high_volume_simple tasks"
        )

    policy = retry_policy or RetryPolicy.load(engine.config.root)
    policy.validate()
    root = Path(artifact_root)
    circuit = circuit_breaker or ProviderCircuitBreaker(
        ProviderCircuitPolicy.load(engine.config.root),
        JsonFileCircuitStateStore(root.parent / "provider-circuits.json"),
    )

    prepared_task = circuit.prepare_task(task)
    circuit_blocks = _circuit_block_delta(task, prepared_task)
    primary_dispatch = engine.dispatch(prepared_task)
    if primary_dispatch.risk_level not in {"low", "medium"}:
        raise ProviderAdapterContractError(
            "Guarded automatic fallback refuses high and critical risk dispatches"
        )
    circuit.claim_dispatch(primary_dispatch)

    primary_execution = _execute_with_retry(
        primary_dispatch,
        connections,
        artifact_root,
        policy,
        sleeper,
        random_source,
    )
    primary_response = primary_execution.response
    primary_circuit = circuit.observe(primary_dispatch, primary_response)
    if primary_response.status == "succeeded":
        return CanaryRuntimeOutcome(
            status="primary_executed",
            primary_dispatch=primary_dispatch,
            primary_response=primary_response,
            primary_attempts=primary_execution.attempts,
            primary_retry_delays_seconds=primary_execution.delays_seconds,
            circuit_blocked_providers=circuit_blocks,
            primary_provider_circuit_state=primary_circuit.state,
        )

    failure = primary_response.failure
    if failure is None or failure.scope not in FALLBACK_ELIGIBLE_SCOPES:
        return CanaryRuntimeOutcome(
            status="execution_failed",
            primary_dispatch=primary_dispatch,
            primary_response=primary_response,
            primary_attempts=primary_execution.attempts,
            primary_retry_delays_seconds=primary_execution.delays_seconds,
            circuit_blocked_providers=circuit_blocks,
            primary_provider_circuit_state=primary_circuit.state,
        )

    redispatch_task = _copy_task_for_redispatch(prepared_task, primary_dispatch, failure.scope)
    prepared_redispatch = circuit.prepare_task(redispatch_task)
    fallback_dispatch = engine.dispatch(prepared_redispatch)

    if fallback_dispatch.dispatch_id == primary_dispatch.dispatch_id:
        raise ProviderAdapterContractError("Fallback redispatch must create a new dispatch ID")
    if fallback_dispatch.selected_implementation.model == primary_dispatch.selected_implementation.model:
        raise ProviderAdapterContractError(
            "Fallback redispatch must not reuse the failed implementation model"
        )
    if (
        failure.scope == "provider"
        and fallback_dispatch.selected_implementation.provider_family
        == primary_dispatch.selected_implementation.provider_family
    ):
        raise ProviderAdapterContractError(
            "Provider-scoped failure must redispatch outside the failed provider family"
        )
    if (
        fallback_dispatch.verification.implementation.model
        == fallback_dispatch.selected_implementation.model
    ):
        raise ProviderAdapterContractError(
            "Fallback redispatch must assign an independent verifier"
        )
    if (
        fallback_dispatch.verification.implementation.model
        == primary_dispatch.verification.implementation.model
    ):
        raise ProviderAdapterContractError(
            "Fallback redispatch must assign a fresh verifier implementation"
        )
    circuit.claim_dispatch(fallback_dispatch)

    fallback_execution = _execute_with_retry(
        fallback_dispatch,
        connections,
        artifact_root,
        policy,
        sleeper,
        random_source,
    )
    fallback_response = fallback_execution.response
    fallback_circuit = circuit.observe(fallback_dispatch, fallback_response)
    return CanaryRuntimeOutcome(
        status=("fallback_executed" if fallback_response.status == "succeeded" else "execution_failed"),
        primary_dispatch=primary_dispatch,
        primary_response=primary_response,
        primary_attempts=primary_execution.attempts,
        primary_retry_delays_seconds=primary_execution.delays_seconds,
        fallback_dispatch=fallback_dispatch,
        fallback_response=fallback_response,
        fallback_attempts=fallback_execution.attempts,
        fallback_retry_delays_seconds=fallback_execution.delays_seconds,
        fallback_trigger_scope=failure.scope,
        circuit_blocked_providers=circuit_blocks,
        primary_provider_circuit_state=primary_circuit.state,
        fallback_provider_circuit_state=fallback_circuit.state,
    )
