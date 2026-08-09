from pathlib import Path

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.provider_adapter import ProviderExecutionResponse, ProviderFailure
from teo_reference.runtime_circuit_breaker import (
    InMemoryCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
    ProviderCircuitRecord,
)
from teo_reference.schemas import ExecutionResult, TaskRequest, VerificationResult


REPO_ROOT = Path(__file__).resolve().parents[1]


def _engine() -> OrchestrationEngine:
    return OrchestrationEngine(ConfigBundle.load(REPO_ROOT))


def _dispatch():
    return _engine().dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "task-finalize-integrity",
                "task": "Classify these bounded records into the supported labels.",
                "task_type": "high_volume_simple",
                "risk_level": "low",
            }
        )
    )


def _execution(dispatch_id: str) -> ExecutionResult:
    return ExecutionResult(
        dispatch_id=dispatch_id,
        status="succeeded",
        output_ref="file:///tmp/teo-test-output.txt",
        evidence=["execution:test"],
    )


def _verification(dispatch_id: str, verifier_model: str) -> VerificationResult:
    return VerificationResult(
        dispatch_id=dispatch_id,
        status="passed",
        verifier_model=verifier_model,
        checks=["output_validation:pass"],
        evidence=["verification:test"],
    )


def test_finalize_rejects_records_from_another_dispatch() -> None:
    engine = _engine()
    dispatch = _dispatch()
    verification = _verification(
        dispatch.dispatch_id,
        dispatch.verification.implementation.model,
    )

    with pytest.raises(
        RoutingError,
        match="Execution and verification records must reference the dispatch being finalized",
    ):
        engine.finalize(
            dispatch,
            _execution("dispatch-not-active"),
            verification,
        )


def test_finalize_rejects_same_model_independent_verification() -> None:
    engine = _engine()
    dispatch = _dispatch()
    dispatch.verification.implementation.model = dispatch.selected_implementation.model

    with pytest.raises(
        RoutingError,
        match="Independent verification cannot use the selected execution model",
    ):
        engine.finalize(
            dispatch,
            _execution(dispatch.dispatch_id),
            _verification(dispatch.dispatch_id, dispatch.selected_implementation.model),
        )


def test_finalize_rejects_same_provider_family_independent_verification() -> None:
    engine = _engine()
    dispatch = _dispatch()
    dispatch.verification.implementation.provider_family = (
        dispatch.selected_implementation.provider_family
    )

    with pytest.raises(
        RoutingError,
        match="Independent verification cannot use the selected execution provider family",
    ):
        engine.finalize(
            dispatch,
            _execution(dispatch.dispatch_id),
            _verification(
                dispatch.dispatch_id,
                dispatch.verification.implementation.model,
            ),
        )


def test_abandoned_half_open_probe_claim_expires() -> None:
    now = [10.0]
    policy = ProviderCircuitPolicy.load(REPO_ROOT)
    store = InMemoryCircuitStateStore()
    store.save(
        ProviderCircuitRecord(
            provider_family="anthropic",
            state="half_open",
            trip_count=1,
            half_open_successes=0,
            probe_in_flight=True,
            probe_claimed_at=10.0,
            last_transition_at=10.0,
        )
    )
    breaker = ProviderCircuitBreaker(policy, store, clock=lambda: now[0])
    task = TaskRequest.from_dict(
        {
            "task": "Classify these bounded records into the supported labels.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )

    now[0] = 10.0 + policy.half_open_probe_lease_seconds - 0.001
    still_claimed = breaker.prepare_task(task)
    assert "anthropic" in still_claimed.constraints.blocked_providers

    now[0] = 10.0 + policy.half_open_probe_lease_seconds
    lease_expired = breaker.prepare_task(task)
    assert "anthropic" not in lease_expired.constraints.blocked_providers
    refreshed = store.load_all()["anthropic"]
    assert refreshed.state == "half_open"
    assert refreshed.probe_in_flight is False
    assert refreshed.probe_claimed_at is None


def test_half_open_non_service_health_failure_remains_inconclusive() -> None:
    now = [50.0]
    policy = ProviderCircuitPolicy.load(REPO_ROOT)
    store = InMemoryCircuitStateStore()
    store.save(
        ProviderCircuitRecord(
            provider_family="anthropic",
            state="half_open",
            trip_count=1,
            probe_in_flight=True,
            probe_claimed_at=50.0,
            last_transition_at=50.0,
        )
    )
    breaker = ProviderCircuitBreaker(policy, store, clock=lambda: now[0])
    dispatch = _dispatch()
    dispatch.selected_implementation.provider_family = "anthropic"
    response = ProviderExecutionResponse(
        dispatch_id=dispatch.dispatch_id,
        status="failed",
        provider_family="anthropic",
        model=dispatch.selected_implementation.model,
        failure=ProviderFailure(
            scope="transient",
            code="connection_error",
            message="local connection failed",
        ),
    )

    observed = breaker.observe(dispatch, response)
    assert policy.half_open_non_service_health_failure_behavior == "remain_half_open"
    assert observed.state == "half_open"
    assert observed.trip_count == 1
    assert observed.probe_in_flight is False
    assert observed.probe_claimed_at is None
