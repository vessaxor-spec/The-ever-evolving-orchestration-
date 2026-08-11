from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from teo_reference.engine import OrchestrationEngine
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.qualified_human_approval import (
    build_qualified_human_approval_disposition,
    evaluate_qualified_human_finalization,
)
from teo_reference.runtime_canary import _copy_task_for_redispatch
from teo_reference.schemas import TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
HELPERS_PATH = REPO_ROOT / "tests" / "test_qualified_human_approval.py"


def _load_helpers():
    spec = importlib.util.spec_from_file_location(
        "teo_qualified_human_boundary_helpers",
        HELPERS_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load qualified-human approval test helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


helpers = _load_helpers()


def test_approval_is_expired_at_exact_expiry_instant() -> None:
    dispatch = helpers.critical_dispatch()
    outcome = helpers.awaiting_human_outcome(dispatch)
    request = helpers.approval_request(dispatch=dispatch, outcome=outcome)
    grant = helpers.authority_grant()
    approved = helpers.approved_disposition(request=request, grant=grant)

    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [approved],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at=helpers.APPROVAL_EXPIRES_AT,
    ).to_dict()

    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == "expired"
    assert finalization["block_reason"] == "expired"
    assert finalization["qualified_human_approval_satisfied"] is False


def test_request_rejects_human_disposition_at_exact_expiry_instant() -> None:
    request = helpers.approval_request()
    grant = helpers.authority_grant()

    with pytest.raises(ProviderAdapterContractError, match="approval request is expired"):
        build_qualified_human_approval_disposition(
            request,
            state="rejected",
            reason="Late human decision must not be accepted at the request expiry boundary.",
            evidence=["request expiry boundary probe"],
            actor_subject_ref=grant.to_dict()["subject_ref"],
            authority_grant=grant,
            repo_root=REPO_ROOT,
            effective_at=helpers.REQUEST_EXPIRES_AT,
        )


def test_authority_grant_rejects_disposition_at_valid_until_boundary() -> None:
    request = helpers.approval_request()
    grant = helpers.authority_grant(valid_until=helpers.APPROVED_AT)

    with pytest.raises(ProviderAdapterContractError, match="not valid at disposition time"):
        build_qualified_human_approval_disposition(
            request,
            state="rejected",
            reason="Authority must already be valid and not yet expired at decision time.",
            evidence=["authority valid_until boundary probe"],
            actor_subject_ref=grant.to_dict()["subject_ref"],
            authority_grant=grant,
            repo_root=REPO_ROOT,
            effective_at=helpers.APPROVED_AT,
        )


def test_fallback_redispatch_preserves_dispatch_elevated_effective_risk() -> None:
    task = TaskRequest.from_dict(
        {
            "task_id": "recovery-authority-elevated-risk-001",
            "task": "Implement a production credentials control while preserving the caller request.",
            "task_type": "daily_coding",
            "risk_level": "low",
        }
    )
    engine = OrchestrationEngine.from_repo(str(REPO_ROOT))
    dispatch = engine.dispatch(task)

    assert task.risk_level == "low"
    assert dispatch.risk_level == "critical"
    assert dispatch.verification.human_approval_required is True

    prepared = _copy_task_for_redispatch(task, dispatch, "model")

    assert prepared.risk_level == dispatch.risk_level == "critical"
    assert prepared.task_type == dispatch.task_type
    assert dispatch.selected_implementation.model in prepared.constraints.blocked_implementations
    assert task.constraints.blocked_implementations == []
