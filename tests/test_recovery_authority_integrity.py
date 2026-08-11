from __future__ import annotations

from pathlib import Path

from teo_reference.engine import OrchestrationEngine
from teo_reference.runtime_canary import _copy_task_for_redispatch
from teo_reference.runtime_circuit_breaker import (
    InMemoryCircuitStateStore,
    ProviderCircuitBreaker,
    ProviderCircuitPolicy,
    ProviderCircuitRecord,
)
from teo_reference.schemas import TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _critical_task_and_dispatch():
    task = TaskRequest.from_dict(
        {
            "task_id": "recovery-authority-critical-001",
            "task": "Implement a production credentials control requiring a critical authority gate.",
            "task_type": "daily_coding",
            "risk_level": "critical",
            "constraints": {"require_human_approval": True},
        }
    )
    dispatch = OrchestrationEngine.from_repo(str(REPO_ROOT)).dispatch(task)
    assert dispatch.risk_level == "critical"
    assert dispatch.verification.human_approval_required is True
    return task, dispatch


def test_failure_redispatch_preserves_risk_and_human_authority_requirement() -> None:
    task, dispatch = _critical_task_and_dispatch()

    prepared = _copy_task_for_redispatch(task, dispatch, "model")

    assert prepared.risk_level == dispatch.risk_level == "critical"
    assert prepared.task_type == dispatch.task_type
    assert prepared.constraints.require_human_approval is True
    assert dispatch.selected_implementation.model in prepared.constraints.blocked_implementations
    assert task.constraints.blocked_implementations == []


def test_circuit_recovery_only_adds_provider_blocks_without_lowering_authority() -> None:
    task, _ = _critical_task_and_dispatch()
    policy = ProviderCircuitPolicy.load(REPO_ROOT)
    store = InMemoryCircuitStateStore()
    store.save(
        ProviderCircuitRecord(
            provider_family="anthropic",
            state="open",
            opened_at=100.0,
            reopen_at=200.0,
            trip_count=1,
            last_transition_at=100.0,
        )
    )
    circuit = ProviderCircuitBreaker(policy, store, clock=lambda: 150.0)

    prepared = circuit.prepare_task(task)

    assert prepared.risk_level == task.risk_level == "critical"
    assert prepared.constraints.require_human_approval is True
    assert prepared.task_type == task.task_type
    assert "anthropic" in prepared.constraints.blocked_providers
    assert task.constraints.blocked_providers == []
