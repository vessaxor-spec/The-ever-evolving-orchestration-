from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from teo_reference.verifier_calibration import CalibrationError, load_calibration_policy
from teo_reference.verifier_calibration_empirical import (
    load_empirical_policy,
    validate_empirical_policy_against_base,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration-empirical.yaml"


def payload() -> dict:
    value = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def write_policy(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "empirical.yaml"
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("acceptance", "empirical_quality_claims_authorized", True),
        ("acceptance", "live_scope_expansion_authorized", True),
        ("acceptance", "routing_authority", True),
        ("acceptance", "automatic_route_update", True),
        ("acceptance", "require_human_label_readiness_before_live_collection", False),
        ("acceptance", "require_independent_residual_risk_review_after_collection", False),
        ("acceptance", "require_explicit_human_acceptance_after_metrics", False),
        ("collection", "require_all_routes", False),
        ("collection", "stop_on_verifier_infrastructure_error", False),
        ("collection", "resume_without_duplicate_calls", False),
        ("collection", "require_provider_reported_usage", False),
        ("collection", "require_duration_measurement", False),
        ("collection", "require_offset_aware_timestamp", False),
        ("collection", "require_single_collector_revision_per_evidence_set", False),
        ("collection", "persist_prompt_or_candidate_content", True),
        ("collection", "persist_provider_native_payload", True),
        ("collection", "persist_credentials_or_authorization", True),
        ("collection", "persist_connection_mechanism", True),
        ("collection", "persist_provider_request_identifiers", True),
        ("human_labeling", "reviewers_blinded_from_model_observations", False),
        ("human_labeling", "adjudication_required_on_disagreement", False),
        ("human_labeling", "adjudicator_must_be_distinct_from_case_reviewers", False),
        ("human_labeling", "require_offset_aware_timestamp", False),
    ],
)
def test_empirical_policy_control_mutations_fail_closed(
    tmp_path: Path,
    section: str,
    field: str,
    value: object,
) -> None:
    mutated = payload()
    mutated[section][field] = value
    with pytest.raises(CalibrationError):
        load_empirical_policy(write_policy(tmp_path, mutated))


def test_empirical_policy_cannot_relabel_direct_collection_as_runtime_execution(
    tmp_path: Path,
) -> None:
    mutated = payload()
    mutated["collection"]["role"] = "primary"
    with pytest.raises(CalibrationError, match="calibration_direct"):
        load_empirical_policy(write_policy(tmp_path, mutated))


def test_empirical_policy_cannot_increase_collection_risk(tmp_path: Path) -> None:
    mutated = payload()
    mutated["collection"]["risk_level"] = "medium"
    with pytest.raises(CalibrationError, match="remain low risk"):
        load_empirical_policy(write_policy(tmp_path, mutated))


def test_empirical_policy_cannot_collapse_provider_diversity(tmp_path: Path) -> None:
    mutated = payload()
    mutated["verifier_routes"][1]["provider_family"] = "google"
    mutated["verifier_routes"][1]["model"] = "gemini-3.1-pro"
    with pytest.raises(CalibrationError, match="distinct provider families"):
        load_empirical_policy(write_policy(tmp_path, mutated))


def test_empirical_policy_cannot_drop_below_base_route_floor(tmp_path: Path) -> None:
    mutated = payload()
    mutated["verifier_routes"] = mutated["verifier_routes"][:2]
    empirical = load_empirical_policy(write_policy(tmp_path, mutated))
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    with pytest.raises(CalibrationError, match="route count"):
        validate_empirical_policy_against_base(empirical, base)


def test_empirical_policy_cannot_drop_below_base_repeat_floor(tmp_path: Path) -> None:
    mutated = payload()
    mutated["collection"]["runs_per_case_per_route"] = 2
    empirical = load_empirical_policy(write_policy(tmp_path, mutated))
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    with pytest.raises(CalibrationError, match="below base calibration minimum"):
        validate_empirical_policy_against_base(empirical, base)


def test_active_empirical_policy_requires_two_independent_reviewers() -> None:
    policy = load_empirical_policy(POLICY_PATH)
    assert policy.minimum_independent_reviewers_per_case >= 2


def test_empirical_policy_versions_remain_bound_to_base_calibration(tmp_path: Path) -> None:
    base_policy = load_calibration_policy(
        REPO_ROOT / "policy/verification/verifier-calibration.yaml"
    )
    for field, value in (
        ("rubric_version", "0.9"),
        ("live_verification_policy_version", "1.0"),
    ):
        mutated = payload()
        mutated["base_calibration"][field] = value
        empirical = load_empirical_policy(write_policy(tmp_path, mutated))
        with pytest.raises(CalibrationError):
            validate_empirical_policy_against_base(empirical, base_policy)


def test_active_policy_contains_no_hidden_authority_or_content_persistence() -> None:
    active = payload()
    for field in (
        "empirical_quality_claims_authorized",
        "live_scope_expansion_authorized",
        "routing_authority",
        "automatic_route_update",
    ):
        assert active["acceptance"][field] is False
    for field in (
        "persist_prompt_or_candidate_content",
        "persist_provider_native_payload",
        "persist_credentials_or_authorization",
        "persist_connection_mechanism",
        "persist_provider_request_identifiers",
    ):
        assert active["collection"][field] is False
