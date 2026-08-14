from __future__ import annotations

import runpy
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT
    / "research"
    / "runtime"
    / "host_integration_portfolio_authority_separation.py"
)
PORTFOLIO = runpy.run_path(str(HARNESS))
HostPortfolioAuthority = PORTFOLIO["HostPortfolioAuthority"]
PortfolioAuthorityError = PORTFOLIO["PortfolioAuthorityError"]
TaskAdmissionGrant = PORTFOLIO["TaskAdmissionGrant"]
TEOAdmissionRequest = PORTFOLIO["TEOAdmissionRequest"]


def task(task_id: str = "task-alpha", *, body: str = "Perform admitted work") -> dict:
    return {
        "task_id": task_id,
        "task": body,
        "task_type": "high_volume_simple",
        "risk_level": "medium",
        "required_capabilities": ["tool_execution"],
    }


def request(grant) -> dict[str, str]:
    return {
        "operation": "orchestrate_admitted_task",
        "admission_id": grant.admission_id,
        "task_id": grant.task_id,
    }


def admit(authority, payload, *, priority: int = 10):
    authority.enqueue_task(payload, priority=priority)
    grant = authority.admit_task(payload["task_id"])
    return grant, authority.teo_gateway()


def test_exact_host_admission_can_be_claimed_and_revalidated() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)

    session = gateway.claim(request(grant), grant, payload)

    assert session.task_id == payload["task_id"]
    assert session.admission_id == grant.admission_id
    assert gateway.revalidate(session, payload) == session


def test_queued_task_is_not_admitted_merely_because_it_is_routable() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    authority.enqueue_task(payload, priority=5)
    gateway = authority.teo_gateway()
    fake = TaskAdmissionGrant(
        authorization_token="0" * 64,
        portfolio_id=authority.portfolio_id,
        admission_id="admission-host-did-not-issue",
        task_id=payload["task_id"],
        task_digest="1" * 64,
        admission_revision=1,
    )

    with pytest.raises(PortfolioAuthorityError, match="signature"):
        gateway.claim(request(fake), fake, payload)


def test_teo_request_cannot_inject_priority_or_queue_position() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    widened = request(grant)
    widened["priority"] = 0
    widened["queue_position"] = 1

    with pytest.raises(PortfolioAuthorityError, match="fields do not match"):
        gateway.claim(widened, grant, payload)


def test_teo_request_cannot_inject_cancel_or_admit_operations() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    widened = request(grant)
    widened["cancel_task"] = True
    widened["admit_task_id"] = "task-beta"

    with pytest.raises(PortfolioAuthorityError, match="fields do not match"):
        gateway.claim(widened, grant, payload)


def test_unsupported_teo_portfolio_operation_is_rejected() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    widened = request(grant)
    widened["operation"] = "dequeue_next_task"

    with pytest.raises(PortfolioAuthorityError, match="unsupported TEO admission operation"):
        gateway.claim(widened, grant, payload)


def test_forged_host_admission_token_is_rejected() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    forged = grant.to_dict()
    forged["authorization_token"] = "f" * 64

    with pytest.raises(PortfolioAuthorityError, match="signature"):
        gateway.claim(request(grant), forged, payload)


def test_admission_identity_mutation_is_rejected() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    forged = grant.to_dict()
    forged["admission_id"] = "admission-substituted"

    with pytest.raises(PortfolioAuthorityError, match="signature"):
        gateway.claim(request(grant), forged, payload)


def test_task_identity_mutation_is_rejected() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    forged = grant.to_dict()
    forged["task_id"] = "task-beta"

    with pytest.raises(PortfolioAuthorityError, match="signature"):
        gateway.claim(request(grant), forged, payload)


def test_post_admission_task_payload_mutation_is_rejected() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    mutated = deepcopy(payload)
    mutated["task"] = "Perform broader work than host admitted"

    with pytest.raises(PortfolioAuthorityError, match="digest"):
        gateway.claim(request(grant), grant, mutated)


def test_sibling_admission_cannot_authorize_another_task() -> None:
    authority = HostPortfolioAuthority()
    alpha = task("task-alpha")
    beta = task("task-beta")
    authority.enqueue_task(alpha, priority=10)
    authority.enqueue_task(beta, priority=20)
    alpha_grant = authority.admit_task("task-alpha")
    beta_grant = authority.admit_task("task-beta")
    gateway = authority.teo_gateway()

    with pytest.raises(PortfolioAuthorityError, match="request task_id"):
        gateway.claim(request(beta_grant), alpha_grant, alpha)

    beta_session = gateway.claim(request(beta_grant), beta_grant, beta)
    assert beta_session.task_id == "task-beta"


def test_admission_grant_is_single_claim_and_cannot_duplicate_work() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    gateway.claim(request(grant), grant, payload)

    with pytest.raises(PortfolioAuthorityError, match="already been claimed"):
        gateway.claim(request(grant), grant, payload)


def test_concurrent_claims_produce_only_one_session() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)

    def claim_once():
        try:
            return gateway.claim(request(grant), grant, payload)
        except PortfolioAuthorityError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: claim_once(), range(2)))

    sessions = [outcome for outcome in outcomes if not isinstance(outcome, Exception)]
    failures = [outcome for outcome in outcomes if isinstance(outcome, Exception)]
    assert len(sessions) == 1
    assert len(failures) == 1
    assert "already been claimed" in str(failures[0])


def test_host_cancellation_revokes_active_teo_session() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    session = gateway.claim(request(grant), grant, payload)

    authority.cancel_task(payload["task_id"])

    with pytest.raises(PortfolioAuthorityError, match="revoked or cancelled"):
        gateway.revalidate(session, payload)


def test_host_admission_revocation_revokes_active_teo_session() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    session = gateway.claim(request(grant), grant, payload)

    authority.revoke_admission(grant.admission_id)

    with pytest.raises(PortfolioAuthorityError, match="revoked or cancelled"):
        gateway.revalidate(session, payload)


def test_host_reprioritization_does_not_become_teo_execution_authority() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload, priority=50)
    session = gateway.claim(request(grant), grant, payload)

    before = authority.task_record(payload["task_id"])
    after = authority.reprioritize_task(payload["task_id"], priority=1)

    assert before.priority == 50
    assert after.priority == 1
    assert gateway.revalidate(session, payload) == session
    assert "priority" not in session.to_dict()


def test_teo_gateway_exposes_no_portfolio_mutation_api() -> None:
    authority = HostPortfolioAuthority()
    gateway = authority.teo_gateway()

    for forbidden in (
        "enqueue_task",
        "reprioritize_task",
        "cancel_task",
        "admit_task",
        "revoke_admission",
        "task_record",
        "dequeue_next_task",
        "list_tasks",
    ):
        assert not hasattr(gateway, forbidden)


def test_host_cancellation_of_sibling_does_not_widen_or_revoke_current_task() -> None:
    authority = HostPortfolioAuthority()
    alpha = task("task-alpha")
    beta = task("task-beta")
    alpha_grant, gateway = admit(authority, alpha, priority=10)
    authority.enqueue_task(beta, priority=20)
    session = gateway.claim(request(alpha_grant), alpha_grant, alpha)

    authority.cancel_task("task-beta")

    assert gateway.revalidate(session, alpha) == session
    assert authority.task_record("task-beta").state == "cancelled"


def test_grant_from_another_portfolio_is_rejected() -> None:
    first = HostPortfolioAuthority(portfolio_id="portfolio-one")
    second = HostPortfolioAuthority(portfolio_id="portfolio-two")
    payload = task()
    grant, _ = admit(first, payload)
    second.enqueue_task(payload, priority=10)
    gateway = second.teo_gateway()

    with pytest.raises(PortfolioAuthorityError, match="another portfolio"):
        gateway.claim(request(grant), grant, payload)


def test_unknown_grant_fields_fail_closed() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    widened = grant.to_dict()
    widened["host_claimed_freshness"] = "trusted"

    with pytest.raises(PortfolioAuthorityError, match="fields do not match"):
        gateway.claim(request(grant), widened, payload)


def test_session_task_substitution_is_rejected_on_revalidation() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    session = gateway.claim(request(grant), grant, payload)
    substituted = task("task-beta")

    with pytest.raises(PortfolioAuthorityError, match="identity"):
        gateway.revalidate(session, substituted)


def test_session_binding_tamper_is_rejected_on_revalidation() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    grant, gateway = admit(authority, payload)
    session = gateway.claim(request(grant), grant, payload).to_dict()
    session["task_digest"] = "a" * 64

    with pytest.raises(PortfolioAuthorityError, match="digest"):
        gateway.revalidate(session, payload)


def test_duplicate_host_admission_is_not_created_for_same_task() -> None:
    authority = HostPortfolioAuthority()
    payload = task()
    authority.enqueue_task(payload, priority=10)
    authority.admit_task(payload["task_id"])

    with pytest.raises(PortfolioAuthorityError, match="not eligible for admission"):
        authority.admit_task(payload["task_id"])


def test_request_type_validation_rejects_boolean_or_mapping_widening() -> None:
    with pytest.raises(PortfolioAuthorityError, match="fields do not match"):
        TEOAdmissionRequest.from_dict(
            {
                "operation": "orchestrate_admitted_task",
                "admission_id": "admission-one",
                "task_id": "task-one",
                "portfolio_action": False,
            }
        )
