from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from teo_reference.verifier_calibration import (
    CalibrationError,
    load_calibration_policy,
    load_gold_cases,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration.yaml"
GOLD_PATH = REPO_ROOT / "reference/datasets/verifier-calibration-gold.yaml"


def write_yaml(path: Path, payload: dict) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


@pytest.mark.parametrize(
    ("section", "field", "message"),
    [
        ("scope", "live_scope_expansion_authorized", "must not authorize live scope expansion"),
        ("scope", "routing_authority", "must not have routing authority"),
        ("scope", "quality_claims_authorized", "must not authorize quality claims"),
        ("expansion_gate", "automatic_expansion", "must not authorize automatic expansion"),
    ],
)
def test_authority_expansion_mutations_fail_closed(
    tmp_path: Path,
    section: str,
    field: str,
    message: str,
) -> None:
    payload = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    payload[section][field] = True
    mutated = tmp_path / "verifier-calibration.yaml"
    write_yaml(mutated, payload)

    with pytest.raises(CalibrationError, match=message):
        load_calibration_policy(mutated)


def test_provider_diversity_floor_cannot_be_disabled_with_zero(tmp_path: Path) -> None:
    payload = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    payload["observation_requirements"]["minimum_distinct_verifier_provider_families"] = 0
    mutated = tmp_path / "verifier-calibration.yaml"
    write_yaml(mutated, payload)

    with pytest.raises(CalibrationError, match="must be a positive integer"):
        load_calibration_policy(mutated)


def test_gold_candidate_mutation_is_detected_against_preserved_label(tmp_path: Path) -> None:
    policy = load_calibration_policy(POLICY_PATH)
    payload = yaml.safe_load(GOLD_PATH.read_text(encoding="utf-8"))
    mutated_payload = deepcopy(payload)
    target = next(case for case in mutated_payload["cases"] if case["id"] == "correct-two-labels")
    target["candidate_output"] = "alpha\nalpha"
    mutated = tmp_path / "verifier-calibration-gold.yaml"
    write_yaml(mutated, mutated_payload)

    with pytest.raises(CalibrationError, match="conflicts with gold"):
        load_gold_cases(mutated, policy=policy)


def test_rubric_precedence_mutation_is_rejected(tmp_path: Path) -> None:
    policy = load_calibration_policy(POLICY_PATH)
    payload = yaml.safe_load(GOLD_PATH.read_text(encoding="utf-8"))
    payload["rubric"]["status_precedence"] = [
        "any_uncertain_means_needs_human",
        "otherwise_any_fail_means_failed",
        "otherwise_passed",
    ]
    mutated = tmp_path / "verifier-calibration-gold.yaml"
    write_yaml(mutated, payload)

    with pytest.raises(CalibrationError, match="preserve verifier status precedence"):
        load_gold_cases(mutated, policy=policy)
