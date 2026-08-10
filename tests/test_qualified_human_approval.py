from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from teo_reference.engine import OrchestrationEngine as BaseOrchestrationEngine
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.qualified_human_approval import (
    JsonlQualifiedHumanApprovalLedger,
    QualifiedHumanApprovalDispositionRecord,
    QualifiedHumanApprovalRequestRecord,
    QualifiedHumanFinalizationRecord,
    build_qualified_human_approval_disposition,
    build_qualified_human_approval_request,
    build_qualified_human_authority_grant,
    evaluate_qualified_human_finalization,
)
from teo_reference.route_outcome import RouteOutcomeRecord
from teo_reference.schemas import TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUESTED_AT = "2026-08-10T20:05:00+00:00"
REQUEST_EXPIRES_AT = "2026-08-10T21:30:00+00:00"
GRANT_ISSUED_AT = "2026-08-10T19:00:00+00:00"
GRANT_VALID_UNTIL = "2026-08-10T22:00:00+00:00"
APPROVED_AT = "2026-08-10T20:10:00+00:00"
APPROVAL_EXPIRES_AT = "2026-08-10T21:00:00+00:00"
FINALIZED_AT = "2026-08-10T20:20:00+00:00"


def canonical_hash(payload: dict) -> str:
    data = dict(payload)
    data.pop("integrity_sha256", None)
    encoded = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def critical_dispatch():
    engine = BaseOrchestrationEngine.from_repo(str(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "human-approval-critical-001",
                "task": "Implement a production credentials control requiring a critical authority gate.",
                "task_type": "daily_coding",
                "risk_level": "critical",
            }
        )
    )
    assert dispatch.risk_level == "critical"
    assert dispatch.verification.human_approval_required is True
    return dispatch


def routine_dispatch():
    engine = BaseOrchestrationEngine.from_repo(str(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "human-approval-routine-001",
                "task": "Implement a small local documentation helper.",
                "task_type": "daily_coding",
                "risk_level": "low",
            }
        )
    )
    assert dispatch.verification.human_approval_required is False
    return dispatch


def awaiting_human_outcome(dispatch=None) -> RouteOutcomeRecord:
    dispatch = dispatch or critical_dispatch()
    provider = dispatch.selected_implementation.provider_family
    verifier_provider = dispatch.verification.implementation.provider_family
    seed = hashlib.sha256(dispatch.dispatch_id.encode("utf-8")).hexdigest()[:20]
    payload = {
        "route_outcome_version": "1",
        "record_type": "route_outcome",
        "recorded_at": "2026-08-10T20:04:00+00:00",
        "outcome_id": f"outcome-{seed}",
        "task_type": dispatch.task_type,
        "risk_level": dispatch.risk_level,
        "primary_route": {
            "dispatch_id": dispatch.dispatch_id,
            "role": "primary",
            "selected_team": dispatch.selected_team,
            "selected_worker": dispatch.selected_worker,
            "selected_specialist": dispatch.selected_specialist,
            "required_capabilities": list(dispatch.required_capabilities),
            "implementation": {
                "provider_family": provider,
                "model": dispatch.selected_implementation.model,
                "reasoning_effort": dispatch.selected_implementation.reasoning,
            },
            "verifier": {
                "provider_family": verifier_provider,
                "model": dispatch.verification.implementation.model,
            },
            "attempts": [
                {
                    "recorded_at": "2026-08-10T20:03:00+00:00",
                    "attempt_number": 1,
                    "provider_family": provider,
                    "model": dispatch.selected_implementation.model,
                    "reasoning_effort": dispatch.selected_implementation.reasoning,
                    "status": "succeeded",
                    "failure_scope": None,
                    "failure_code": None,
                    "duration_ms": 10.0,
                    "retry_after_seconds": None,
                    "usage": None,
                }
            ],
            "attempt_count": 1,
            "retry_used": False,
            "execution_status": "succeeded",
            "failure_scope": None,
            "failure_code": None,
        },
        "fallback_route": None,
        "active_route_role": "primary",
        "final_disposition": "awaiting_human",
        "verification_status": "passed",
        "human_approval_required": True,
        "fallback_assisted": False,
        "retry_assisted": False,
        "versions": {
            "runtime_version": "1.0.1.dev0",
            "repository_revision": "qualified-human-test",
            "routing_policy_revision": "qualified-human-policy-test",
            "registry_revision": "qualified-human-registry-test",
            "tool_versions": {},
        },
        "cost": {
            "status": "unknown",
            "amount": None,
            "currency": None,
            "source": None,
        },
        "provenance": {
            "source_dispatch_ids": [dispatch.dispatch_id],
            "verification_dispatch_id": dispatch.dispatch_id,
            "telemetry_event_count": 1,
        },
        "abandonment_reason": None,
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = canonical_hash(payload)
    return RouteOutcomeRecord.from_dict(payload, repo_root=REPO_ROOT)


def authority_grant(**overrides):
    values = {
        "subject_ref": "human-subject-operations-001",
        "authority_class": "critical-production-change-authority",
        "authority_requirement_ids": ["critical-runtime-finalization"],
        "risk_levels": ["critical"],
        "task_types": ["daily_coding"],
        "issuer": "enterprise-authority-registry",
        "evidence_ref": "authority-registry://critical-production-change-authority/001",
        "repo_root": REPO_ROOT,
        "issued_at": GRANT_ISSUED_AT,
        "valid_from": GRANT_ISSUED_AT,
        "valid_until": GRANT_VALID_UNTIL,
        "source_verified_at": GRANT_ISSUED_AT,
    }
    values.update(overrides)
    return build_qualified_human_authority_grant(**values)


def approval_request(dispatch=None, outcome=None, **overrides):
    dispatch = dispatch or critical_dispatch()
    outcome = outcome or awaiting_human_outcome(dispatch)
    values = {
        "authority_requirement_id": "critical-runtime-finalization",
        "required_authority_class": "critical-production-change-authority",
        "reason": "Critical effective risk requires qualified-human finalization authority.",
        "policy_source": "policy/routing/core/routing.yaml#verification_policy.critical",
        "repo_root": REPO_ROOT,
        "requested_at": REQUESTED_AT,
        "expires_at": REQUEST_EXPIRES_AT,
    }
    values.update(overrides)
    return build_qualified_human_approval_request(dispatch, outcome, **values)


def approved_disposition(request=None, grant=None, **overrides):
    request = request or approval_request()
    grant = grant or authority_grant()
    values = {
        "state": "approved",
        "reason": "Qualified authority accepts the exact verified outcome for finalization.",
        "evidence": ["authority scope and runtime evidence reviewed"],
        "repo_root": REPO_ROOT,
        "actor_subject_ref": grant.to_dict()["subject_ref"],
        "authority_grant": grant,
        "effective_at": APPROVED_AT,
        "approval_expires_at": APPROVAL_EXPIRES_AT,
    }
    values.update(overrides)
    return build_qualified_human_approval_disposition(request, **values)


def test_critical_dispatch_preserves_human_approval_gate() -> None:
    dispatch = critical_dispatch()
    assert dispatch.verification.human_approval_required is True
    assert "human_approval" in (
        BaseOrchestrationEngine.from_repo(str(REPO_ROOT))
        .config.routing["verification_policy"]["critical"]["minimum"]
    )


def test_request_requires_existing_human_authority_gate() -> None:
    dispatch = routine_dispatch()
    outcome = awaiting_human_outcome(critical_dispatch())
    with pytest.raises(ProviderAdapterContractError, match="already marked human_approval_required"):
        approval_request(dispatch=dispatch, outcome=outcome)


def test_request_binds_exact_dispatch_route_outcome_and_verification() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome).to_dict()

    assert request["dispatch_id"] == dispatch.dispatch_id
    assert request["dispatch_sha256"] == canonical_hash(dispatch.to_dict())
    assert request["route_outcome_ref"]["outcome_id"] == outcome.to_dict()["outcome_id"]
    assert request["route_outcome_ref"]["integrity_sha256"] == outcome.to_dict()["integrity_sha256"]
    assert request["verification"] == {
        "dispatch_id": dispatch.dispatch_id,
        "status": "passed",
    }
    assert request["qualified_human_approval_satisfied"] is False


def test_review_handoff_evidence_does_not_satisfy_human_approval() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(
        dispatch=dispatch,
        outcome=outcome,
        review_evidence_refs=[
            {
                "record_type": "shadow_recommendation_handoff",
                "record_id": "shadow-handoff-review-only",
                "integrity_sha256": "a" * 64,
            }
        ],
    )
    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [],
        authority_grants=[],
        repo_root=REPO_ROOT,
        finalized_at=FINALIZED_AT,
    ).to_dict()

    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == "requested"
    assert finalization["block_reason"] == "missing_approval"
    assert finalization["qualified_human_approval_satisfied"] is False


def test_scoped_authority_grant_can_approve_and_finalize_exact_outcome() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    disposition = approved_disposition(request=request, grant=grant)

    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [disposition],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at=FINALIZED_AT,
    ).to_dict()

    assert finalization["status"] == "completed"
    assert finalization["approval_state"] == "approved"
    assert finalization["block_reason"] == "none"
    assert finalization["qualified_human_approval_satisfied"] is True
    assert finalization["authority_class"] == "critical-production-change-authority"
    assert finalization["approver_subject_ref"] == "human-subject-operations-001"
    assert finalization["route_outcome_ref"]["integrity_sha256"] == outcome.to_dict()["integrity_sha256"]
    assert finalization["route_outcome_mutated"] is False
    assert outcome.to_dict()["final_disposition"] == "awaiting_human"


@pytest.mark.parametrize(
    ("grant_overrides", "match"),
    [
        ({"authority_class": "different-authority"}, "authority class"),
        ({"authority_requirement_ids": ["different-requirement"]}, "authority requirement"),
        ({"risk_levels": ["high"]}, "effective risk"),
        ({"task_types": ["documentation"]}, "task type"),
    ],
)
def test_out_of_scope_authority_grant_fails_closed(grant_overrides, match) -> None:
    request = approval_request()
    grant = authority_grant(**grant_overrides)
    with pytest.raises(ProviderAdapterContractError, match=match):
        approved_disposition(request=request, grant=grant)


def test_approval_cannot_outlive_request_or_authority_grant() -> None:
    request = approval_request()
    grant = authority_grant(valid_until="2026-08-10T20:40:00+00:00")
    with pytest.raises(ProviderAdapterContractError, match="outlive its authority grant"):
        approved_disposition(
            request=request,
            grant=grant,
            approval_expires_at="2026-08-10T20:50:00+00:00",
        )

    grant = authority_grant()
    with pytest.raises(ProviderAdapterContractError, match="outlive its approval request"):
        approved_disposition(
            request=request,
            grant=grant,
            approval_expires_at="2026-08-10T21:45:00+00:00",
        )


@pytest.mark.parametrize("state", ["rejected", "unable_to_determine"])
def test_nonapproval_human_dispositions_block_finalization(state: str) -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    disposition = build_qualified_human_approval_disposition(
        request,
        state=state,
        reason=f"Qualified authority returned {state}.",
        evidence=["authority review evidence"],
        actor_subject_ref=grant.to_dict()["subject_ref"],
        authority_grant=grant,
        repo_root=REPO_ROOT,
        effective_at=APPROVED_AT,
    )
    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [disposition],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at=FINALIZED_AT,
    ).to_dict()

    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == state
    assert finalization["block_reason"] == state
    assert finalization["qualified_human_approval_satisfied"] is False


def test_request_expiry_is_explicit_and_system_only() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    expired = build_qualified_human_approval_disposition(
        request,
        state="expired",
        reason="Approval request validity window elapsed.",
        evidence=["request expires_at elapsed"],
        repo_root=REPO_ROOT,
        effective_at="2026-08-10T21:31:00+00:00",
    )
    assert expired.to_dict()["actor"] == {"actor_type": "system", "subject_ref": None}

    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [expired],
        authority_grants=[],
        repo_root=REPO_ROOT,
        finalized_at="2026-08-10T21:32:00+00:00",
    ).to_dict()
    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == "expired"
    assert finalization["block_reason"] == "expired"


def test_approved_disposition_expires_fail_closed_without_rewriting_history() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)

    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [approved],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at="2026-08-10T21:01:00+00:00",
    ).to_dict()

    assert approved.to_dict()["state"] == "approved"
    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == "expired"
    assert finalization["block_reason"] == "expired"


def test_approved_disposition_can_be_revoked_before_expiry() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)
    revoked = build_qualified_human_approval_disposition(
        request,
        state="revoked",
        reason="Qualified authority revoked the prior approval.",
        evidence=["revocation evidence"],
        actor_subject_ref=grant.to_dict()["subject_ref"],
        authority_grant=grant,
        previous_disposition=approved,
        repo_root=REPO_ROOT,
        effective_at="2026-08-10T20:30:00+00:00",
    )

    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [approved, revoked],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at="2026-08-10T20:31:00+00:00",
    ).to_dict()
    assert finalization["status"] == "blocked"
    assert finalization["approval_state"] == "revoked"
    assert finalization["block_reason"] == "revoked"


def test_disposition_chain_must_be_contiguous() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)
    revoked = build_qualified_human_approval_disposition(
        request,
        state="revoked",
        reason="Revoked.",
        evidence=["revocation evidence"],
        actor_subject_ref=grant.to_dict()["subject_ref"],
        authority_grant=grant,
        previous_disposition=approved,
        repo_root=REPO_ROOT,
        effective_at="2026-08-10T20:30:00+00:00",
    )
    raw = revoked.to_dict()
    raw["previous_disposition_id"] = "approval-disposition-" + "0" * 20
    raw["integrity_sha256"] = canonical_hash(raw)
    forged = QualifiedHumanApprovalDispositionRecord.from_dict(raw, repo_root=REPO_ROOT)

    with pytest.raises(ProviderAdapterContractError, match="chain is not contiguous"):
        evaluate_qualified_human_finalization(
            dispatch,
            outcome,
            request,
            [approved, forged],
            authority_grants=[grant],
            repo_root=REPO_ROOT,
            finalized_at="2026-08-10T20:31:00+00:00",
        )


@pytest.mark.parametrize("actor_type", ["model", "specialist", "verifier", "mission_control", "maintainer"])
def test_nonhuman_control_plane_records_cannot_impersonate_approval(actor_type: str) -> None:
    request = approval_request()
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)
    raw = approved.to_dict()
    raw["actor"]["actor_type"] = actor_type
    raw["integrity_sha256"] = canonical_hash(raw)

    with pytest.raises(ProviderAdapterContractError, match="schema validation failed"):
        QualifiedHumanApprovalDispositionRecord.from_dict(raw, repo_root=REPO_ROOT)


def test_mutated_request_and_finalization_authority_fields_fail_closed() -> None:
    request = approval_request()
    raw_request = request.to_dict()
    raw_request["qualified_human_approval_satisfied"] = True
    raw_request["integrity_sha256"] = canonical_hash(raw_request)
    with pytest.raises(ProviderAdapterContractError, match="schema validation failed"):
        QualifiedHumanApprovalRequestRecord.from_dict(raw_request, repo_root=REPO_ROOT)

    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)
    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [approved],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at=FINALIZED_AT,
    )
    raw_finalization = finalization.to_dict()
    raw_finalization["live_routing_authority"] = True
    raw_finalization["integrity_sha256"] = canonical_hash(raw_finalization)
    with pytest.raises(ProviderAdapterContractError, match="schema validation failed"):
        QualifiedHumanFinalizationRecord.from_dict(raw_finalization, repo_root=REPO_ROOT)


def test_finalization_revalidates_exact_dispatch_and_route_outcome_binding() -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)

    dispatch.task = dispatch.task + " mutated"
    with pytest.raises(ProviderAdapterContractError, match="exact dispatch content"):
        evaluate_qualified_human_finalization(
            dispatch,
            outcome,
            request,
            [approved],
            authority_grants=[grant],
            repo_root=REPO_ROOT,
            finalized_at=FINALIZED_AT,
        )


def test_jsonl_ledger_preserves_all_authority_records(tmp_path: Path) -> None:
    dispatch = critical_dispatch()
    outcome = awaiting_human_outcome(dispatch)
    request = approval_request(dispatch=dispatch, outcome=outcome)
    grant = authority_grant()
    approved = approved_disposition(request=request, grant=grant)
    finalization = evaluate_qualified_human_finalization(
        dispatch,
        outcome,
        request,
        [approved],
        authority_grants=[grant],
        repo_root=REPO_ROOT,
        finalized_at=FINALIZED_AT,
    )
    ledger = JsonlQualifiedHumanApprovalLedger(
        tmp_path / "qualified-human-approval.jsonl",
        repo_root=REPO_ROOT,
    )
    for record in (grant, request, approved, finalization):
        ledger.append(record)

    records = ledger.read_all()
    assert [record.to_dict()["record_type"] for record in records] == [
        "qualified_human_authority_grant",
        "qualified_human_approval_request",
        "qualified_human_approval_disposition",
        "qualified_human_finalization",
    ]

    path = tmp_path / "qualified-human-approval.jsonl"
    raw = path.read_text(encoding="utf-8").splitlines()
    mutated = json.loads(raw[-1])
    mutated["policy_write_authority"] = True
    raw[-1] = json.dumps(mutated, sort_keys=True)
    path.write_text("\n".join(raw) + "\n", encoding="utf-8")
    with pytest.raises(ProviderAdapterContractError):
        ledger.read_all()
