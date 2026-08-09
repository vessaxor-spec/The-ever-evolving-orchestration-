from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/governance/v1-readiness.yaml"
STEWARDSHIP_PATH = REPO_ROOT / "docs/stewardship/community-human-verification.md"


def load_policy() -> dict:
    payload = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_functional_v1_does_not_require_human_calibration() -> None:
    policy = load_policy()
    definition = policy["v1_definition"]
    assert definition["functional_reference_release_may_precede_human_calibration"] is True
    assert policy["human_stewardship"]["blocking_for_functional_v1_release"] is False


def test_deferred_human_tier_cannot_be_replaced_by_machine_panel() -> None:
    policy = load_policy()
    provisional = policy["provisional_operational_evidence"]
    authority = policy["authority_boundary"]

    assert provisional["human_ground_truth_equivalent"] is False
    assert provisional["may_authorize_quality_claims"] is False
    assert provisional["may_expand_live_scope"] is False
    assert provisional["may_change_routes_automatically"] is False
    assert provisional["may_remove_human_review_tier"] is False
    assert authority["machine_panel_must_never_be_labeled_human_review"] is True
    assert authority["provisional_evidence_must_remain_provisional"] is True


def test_runtime_human_authority_is_not_weakened() -> None:
    policy = load_policy()
    assert policy["authority_boundary"]["critical_effective_risk_still_requires_qualified_human_approval"] is True
    stewardship = policy["human_stewardship"]
    assert stewardship["blocking_for_human_ground_truth_claims"] is True
    assert stewardship["blocking_for_evidence_based_scope_expansion"] is True


def test_community_stewardship_is_documented() -> None:
    text = STEWARDSHIP_PATH.read_text(encoding="utf-8")
    assert "Issue #75" in text
    assert "Machine-panel evidence is not a substitute" in text
    assert "private alias map" in text
