from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from teo_reference.verifier_calibration import CalibrationError, load_calibration_policy, load_gold_cases
from teo_reference.verifier_calibration_empirical import load_empirical_policy
from teo_reference.verifier_calibration_human_review import (
    BlindedReviewLabel,
    build_review_materials,
    normalize_blinded_labels,
    validate_review_packet_is_blinded,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKET_SCHEMA = REPO_ROOT / "reference/schemas/verifier-calibration-human-review-packet.schema.json"
MAP_SCHEMA = REPO_ROOT / "reference/schemas/verifier-calibration-human-review-map.schema.json"
RAW_LABEL_SCHEMA = REPO_ROOT / "reference/schemas/verifier-calibration-human-review-label.schema.json"


def cases_and_policy():
    empirical = load_empirical_policy(
        REPO_ROOT / "policy/verification/verifier-calibration-empirical.yaml"
    )
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    cases = load_gold_cases(REPO_ROOT / empirical.control_corpus_path, policy=base)
    return cases, empirical


def decision_dict(decision):
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def tokens():
    values = iter(["packet0001"] + [f"blind{i:04d}" for i in range(1, 9)])
    return lambda: next(values)


def test_review_packet_hides_control_labels_categories_rules_and_case_ids() -> None:
    cases, empirical = cases_and_policy()
    packet, private_map = build_review_materials(
        cases,
        empirical.rubric_version,
        token_factory=tokens(),
    )
    validate_review_packet_is_blinded(packet)

    packet_schema = json.loads(PACKET_SCHEMA.read_text(encoding="utf-8"))
    map_schema = json.loads(MAP_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(packet_schema)
    Draft202012Validator.check_schema(map_schema)
    Draft202012Validator(packet_schema).validate(packet)
    Draft202012Validator(map_schema).validate(private_map)

    serialized = json.dumps(packet)
    for case in cases:
        assert case.case_id not in serialized
        assert case.category not in serialized
    assert '"gold"' not in serialized
    assert '"deterministic"' not in serialized
    assert len(packet["items"]) == len(cases) == 8
    assert {item["review_item_id"] for item in packet["items"]} == {
        item["review_item_id"] for item in private_map["items"]
    }
    assert {item["case_id"] for item in private_map["items"]} == {
        case.case_id for case in cases
    }


def test_blinded_raw_label_requires_both_blinding_attestations() -> None:
    cases, empirical = cases_and_policy()
    packet, private_map = build_review_materials(
        cases,
        empirical.rubric_version,
        token_factory=tokens(),
    )
    review_id = packet["items"][0]["review_item_id"]
    mapped_case_id = next(
        item["case_id"]
        for item in private_map["items"]
        if item["review_item_id"] == review_id
    )
    case = next(case for case in cases if case.case_id == mapped_case_id)
    raw = {
        "review_item_id": review_id,
        "reviewer_id": "reviewer-a",
        "reviewer_role": "reviewer",
        "reviewed_at": "2026-08-07T14:00:00Z",
        "rubric_version": empirical.rubric_version,
        "observations_blinded": True,
        "reference_control_labels_blinded": True,
        "decision": decision_dict(case.gold),
    }

    schema = json.loads(RAW_LABEL_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(raw)
    label = BlindedReviewLabel.from_dict(raw)
    normalized = normalize_blinded_labels(private_map, [label])
    assert normalized[0]["case_id"] == mapped_case_id
    assert "review_item_id" not in normalized[0]
    assert normalized[0]["observations_blinded"] is True

    for field in ("observations_blinded", "reference_control_labels_blinded"):
        mutated = dict(raw)
        mutated[field] = False
        assert list(Draft202012Validator(schema).iter_errors(mutated))
        with pytest.raises(CalibrationError, match="blinded"):
            BlindedReviewLabel.from_dict(mutated)


def test_packet_validation_rejects_reference_control_leak() -> None:
    cases, empirical = cases_and_policy()
    packet, _ = build_review_materials(
        cases,
        empirical.rubric_version,
        token_factory=tokens(),
    )
    packet["items"][0]["case_id"] = cases[0].case_id
    with pytest.raises(CalibrationError, match="leaks reference-control"):
        validate_review_packet_is_blinded(packet)


def test_unknown_blind_alias_cannot_be_normalized() -> None:
    cases, empirical = cases_and_policy()
    _, private_map = build_review_materials(
        cases,
        empirical.rubric_version,
        token_factory=tokens(),
    )
    label = BlindedReviewLabel.from_dict(
        {
            "review_item_id": "item-unknown0001",
            "reviewer_id": "reviewer-a",
            "reviewer_role": "reviewer",
            "reviewed_at": "2026-08-07T14:00:00Z",
            "rubric_version": empirical.rubric_version,
            "observations_blinded": True,
            "reference_control_labels_blinded": True,
            "decision": decision_dict(cases[0].gold),
        }
    )
    with pytest.raises(CalibrationError, match="unknown review item"):
        normalize_blinded_labels(private_map, [label])
