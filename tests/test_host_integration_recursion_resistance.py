from __future__ import annotations

import runpy
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

import pytest

from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_recursion_resistance.py"
RECURSION = runpy.run_path(str(HARNESS))
ProcessLocalRecursionAuthority = RECURSION["ProcessLocalRecursionAuthority"]
RecursionAdmissionError = RECURSION["RecursionAdmissionError"]
RecursionLimits = RECURSION["RecursionLimits"]


def choice(model: str, provider: str, *, agent: str) -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-recursion-resistance-research",
    )


def dispatch(*, dispatch_id: str = "dispatch-recursion") -> DispatchRecord:
    return DispatchRecord(
        task_id="task-recursion",
        dispatch_id=dispatch_id,
        created_at="2026-08-14T08:35:00+00:00",
        task="Exercise one bounded Host Integration orchestration lineage.",
        task_type="high_volume_simple",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=["tool_execution"],
        selected_implementation=choice("gpt-5.6-sol", "openai", agent="codex"),
        fallback_implementation=choice(
            "gemini-3.7-flash", "google", agent="agy"
        ),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice(
                "claude-sonnet-5", "anthropic", agent="claude"
            ),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["research fixture"],
        warnings=[],
        status="dispatched",
    )


def limits(**overrides: int) -> object:
    values = {
        "max_reentry_depth": 3,
        "max_descendants": 6,
        "max_specialist_spawns": 2,
        "max_active_branches": 3,
        "max_recovery_generations": 1,
    }
    values.update(overrides)
    return RecursionLimits(**values)


def claim(authority, parent, entry_kind: str, request_id: str):
    authorization = authority.authorize_descendant(
        parent,
        entry_kind=entry_kind,
        request_id=request_id,
    )
    return authority.claim_descendant(authorization, parent)


def test_bounded_lineage_tracks_depth_spawn_recovery_and_active_state() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits(max_active_branches=4))

    specialist = claim(authority, root, "specialist_spawn", "specialist-1")
    reentry = claim(authority, specialist, "teo_reentry", "reentry-1")
    recovery = claim(authority, reentry, "recovery_reentry", "recovery-1")

    assert specialist.depth == 1
    assert reentry.depth == 2
    assert recovery.depth == 3
    assert recovery.recovery_generation == 1
    snapshot = authority.snapshot(root)
    assert snapshot["descendants_claimed"] == 3
    assert snapshot["specialist_spawns_claimed"] == 1
    assert snapshot["active_descendants"] == 3


def test_same_dispatch_cannot_mint_a_second_root_budget() -> None:
    authority = ProcessLocalRecursionAuthority()
    current = dispatch()
    authority.begin_root(current, limits())

    with pytest.raises(RecursionAdmissionError, match="root already exists"):
        authority.begin_root(current, limits(max_descendants=20))


def test_depth_budget_rejects_nested_reentry_beyond_ceiling() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits(max_reentry_depth=1))
    child = claim(authority, root, "teo_reentry", "reentry-1")

    with pytest.raises(RecursionAdmissionError, match="re-entry depth"):
        authority.authorize_descendant(
            child, entry_kind="teo_reentry", request_id="reentry-2"
        )


def test_total_descendant_budget_is_not_refunded_after_release() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(
        dispatch(),
        limits(max_descendants=1, max_specialist_spawns=1),
    )
    child = claim(authority, root, "specialist_spawn", "specialist-1")
    authority.release(child)

    with pytest.raises(RecursionAdmissionError, match="descendant admission budget"):
        authority.authorize_descendant(
            root, entry_kind="teo_reentry", request_id="reentry-after-release"
        )


def test_specialist_spawn_budget_is_not_refunded_after_release() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(
        dispatch(), limits(max_descendants=3, max_specialist_spawns=1)
    )
    specialist = claim(authority, root, "specialist_spawn", "specialist-1")
    authority.release(specialist)

    with pytest.raises(RecursionAdmissionError, match="specialist spawn budget"):
        authority.authorize_descendant(
            root, entry_kind="specialist_spawn", request_id="specialist-2"
        )

    reentry = claim(authority, root, "teo_reentry", "reentry-1")
    assert reentry.entry_kind == "teo_reentry"


def test_parallel_branch_budget_releases_only_concurrency_slot() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(
        dispatch(), limits(max_active_branches=1, max_descendants=3)
    )
    first = claim(authority, root, "teo_reentry", "branch-1")

    with pytest.raises(RecursionAdmissionError, match="active branch budget"):
        authority.authorize_descendant(
            root, entry_kind="teo_reentry", request_id="branch-2"
        )

    authority.release(first)
    second = claim(authority, root, "teo_reentry", "branch-2")
    snapshot = authority.snapshot(root)
    assert second.request_id == "branch-2"
    assert snapshot["descendants_claimed"] == 2
    assert snapshot["active_descendants"] == 1


def test_recovery_generation_budget_rejects_recursive_recovery_loop() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(
        dispatch(), limits(max_reentry_depth=3, max_recovery_generations=1)
    )
    recovery = claim(authority, root, "recovery_reentry", "recovery-1")

    with pytest.raises(RecursionAdmissionError, match="recovery generation"):
        authority.authorize_descendant(
            recovery,
            entry_kind="recovery_reentry",
            request_id="recovery-2",
        )


def test_recovery_does_not_reset_root_descendant_or_spawn_consumption() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(
        dispatch(),
        limits(
            max_descendants=2,
            max_specialist_spawns=1,
            max_active_branches=1,
        ),
    )
    specialist = claim(authority, root, "specialist_spawn", "specialist-1")
    authority.release(specialist)
    recovery = claim(authority, root, "recovery_reentry", "recovery-1")
    authority.release(recovery)

    snapshot = authority.snapshot(root)
    assert snapshot["descendants_claimed"] == 2
    assert snapshot["specialist_spawns_claimed"] == 1
    with pytest.raises(RecursionAdmissionError, match="descendant admission budget"):
        authority.authorize_descendant(
            root, entry_kind="teo_reentry", request_id="post-recovery-reset"
        )


def test_forged_authorization_token_is_rejected() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    authorization = authority.authorize_descendant(
        root, entry_kind="teo_reentry", request_id="reentry-1"
    ).to_dict()
    authorization["authorization_token"] = "host-minted-token"

    with pytest.raises(RecursionAdmissionError, match="TEO-side recursion admission snapshot"):
        authority.claim_descendant(authorization, root)


def test_authorization_is_single_use() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    authorization = authority.authorize_descendant(
        root, entry_kind="teo_reentry", request_id="reentry-1"
    )
    authority.claim_descendant(authorization, root)

    with pytest.raises(RecursionAdmissionError, match="already been claimed"):
        authority.claim_descendant(authorization, root)


def test_parallel_preauthorization_goes_stale_after_first_claim() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits(max_active_branches=3))
    first = authority.authorize_descendant(
        root, entry_kind="teo_reentry", request_id="branch-1"
    )
    second = authority.authorize_descendant(
        root, entry_kind="teo_reentry", request_id="branch-2"
    )

    authority.claim_descendant(first, root)
    with pytest.raises(RecursionAdmissionError, match="stale"):
        authority.claim_descendant(second, root)


def test_cross_root_authorization_reuse_is_rejected() -> None:
    authority = ProcessLocalRecursionAuthority()
    root_one = authority.begin_root(dispatch(dispatch_id="dispatch-one"), limits())
    root_two = authority.begin_root(dispatch(dispatch_id="dispatch-two"), limits())
    authorization = authority.authorize_descendant(
        root_one, entry_kind="teo_reentry", request_id="reentry-one"
    )

    with pytest.raises(RecursionAdmissionError, match="parent lineage"):
        authority.claim_descendant(authorization, root_two)


def test_lease_budget_or_dispatch_binding_tampering_is_rejected() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())

    for field in ("limits_digest", "dispatch_digest"):
        tampered = deepcopy(root.to_dict())
        tampered[field] = "0" * 64
        with pytest.raises(RecursionAdmissionError, match="authority snapshot"):
            authority.authorize_descendant(
                tampered, entry_kind="teo_reentry", request_id=f"tamper-{field}"
            )


def test_authorization_lineage_counter_tampering_is_rejected() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    authorization = authority.authorize_descendant(
        root, entry_kind="recovery_reentry", request_id="recovery-1"
    ).to_dict()
    authorization["depth"] += 1

    with pytest.raises(RecursionAdmissionError, match="admission snapshot"):
        authority.claim_descendant(authorization, root)


def test_unknown_widening_fields_are_rejected_on_host_visible_records() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    root_payload = root.to_dict()
    root_payload["reset_budget"] = True

    with pytest.raises(RecursionAdmissionError, match="lease fields"):
        authority.authorize_descendant(
            root_payload, entry_kind="teo_reentry", request_id="unknown-lease-field"
        )

    authorization = authority.authorize_descendant(
        root, entry_kind="teo_reentry", request_id="unknown-auth-field"
    ).to_dict()
    authorization["extra_descendants"] = 1000
    with pytest.raises(RecursionAdmissionError, match="authorization fields"):
        authority.claim_descendant(authorization, root)


def test_request_identifier_cannot_be_reused_after_child_release() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    child = claim(authority, root, "teo_reentry", "reentry-1")
    authority.release(child)

    with pytest.raises(RecursionAdmissionError, match="already consumed"):
        authority.authorize_descendant(
            root, entry_kind="teo_reentry", request_id="reentry-1"
        )


def test_parent_cannot_be_released_while_child_is_active() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits(max_active_branches=3))
    parent = claim(authority, root, "teo_reentry", "parent")
    child = claim(authority, parent, "specialist_spawn", "child")

    with pytest.raises(RecursionAdmissionError, match="active child remains"):
        authority.release(parent)

    authority.release(child)
    authority.release(parent)


def test_released_parent_cannot_authorize_new_descendant() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())
    parent = claim(authority, root, "teo_reentry", "parent")
    authority.release(parent)

    with pytest.raises(RecursionAdmissionError, match="not active"):
        authority.authorize_descendant(
            parent, entry_kind="teo_reentry", request_id="child-after-release"
        )


def test_concurrent_claims_from_same_revision_cannot_multiply_branches() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits(max_active_branches=3))
    authorizations = [
        authority.authorize_descendant(
            root, entry_kind="teo_reentry", request_id=f"parallel-{index}"
        )
        for index in range(2)
    ]

    def attempt(authorization):
        try:
            authority.claim_descendant(authorization, root)
            return "accepted"
        except RecursionAdmissionError:
            return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(attempt, authorizations))

    assert sorted(results) == ["accepted", "rejected"]
    snapshot = authority.snapshot(root)
    assert snapshot["descendants_claimed"] == 1
    assert snapshot["active_descendants"] == 1


def test_root_lease_cannot_be_host_released_to_reset_session_state() -> None:
    authority = ProcessLocalRecursionAuthority()
    root = authority.begin_root(dispatch(), limits())

    with pytest.raises(RecursionAdmissionError, match="root lease lifetime"):
        authority.release(root)


def test_invalid_or_self_widening_limits_fail_before_root_creation() -> None:
    with pytest.raises(RecursionAdmissionError, match="at least 1"):
        RecursionLimits(
            max_reentry_depth=1,
            max_descendants=1,
            max_specialist_spawns=1,
            max_active_branches=0,
            max_recovery_generations=0,
        )
    with pytest.raises(RecursionAdmissionError, match="cannot exceed"):
        RecursionLimits(
            max_reentry_depth=1,
            max_descendants=1,
            max_specialist_spawns=2,
            max_active_branches=1,
            max_recovery_generations=0,
        )
