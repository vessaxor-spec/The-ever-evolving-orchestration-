from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from teo_reference.verifier_calibration import (
    CalibrationError,
    CalibrationObservation,
    deterministic_validate,
    evaluate_calibration,
    gold_summary,
    load_gold_cases,
    load_observations,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = REPO_ROOT / "reference/datasets/verifier-calibration-gold.yaml"
POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration.yaml"
SCHEMA_PATH = REPO_ROOT / "reference/schemas/verifier-calibration-observation.schema.json"


def decision(
    status: str,
    *,
    output_present: str = "pass",
    task_adherence: str = "pass",
    format_consistency: str = "pass",
    unsupported_claims_absent: str = "pass",
    human_reason: str = "none",
) -> dict:
    return {
        "status": status,
        "output_present": output_present,
        "task_adherence": task_adherence,
        "format_consistency": format_consistency,
        "unsupported_claims_absent": unsupported_claims_absent,
        "human_reason": human_reason,
    }


def observation(case_id: str, gold: dict, *, provider="google", model="gemini-3.6-flash", run_id="run-1", **extra):
    payload = {
        "case_id": case_id,
        "verifier_provider_family": provider,
        "verifier_model": model,
        "run_id": run_id,
        "decision": gold,
    }
    payload.update(extra)
    return CalibrationObservation.from_dict(payload)


def gold_dict(case) -> dict:
    return {
        "status": case.gold.status,
        "output_present": case.gold.output_present,
        "task_adherence": case.gold.task_adherence,
        "format_consistency": case.gold.format_consistency,
        "unsupported_claims_absent": case.gold.unsupported_claims_absent,
        "human_reason": case.gold.human_reason,
    }


def test_gold_corpus_covers_required_failure_and_uncertainty_categories() -> None:
    cases = load_gold_cases(GOLD_PATH)
    assert len(cases) == 8
    assert {case.category for case in cases} == {
        "correct",
        "subtly_wrong",
        "incomplete",
        "wrong_format",
        "unsupported_claim",
        "ambiguous",
        "unverifiable",
        "adversarial",
    }
    summary = gold_summary(cases)
    assert summary == {
        "status": "gold_corpus_valid",
        "case_count": 8,
        "categories": [
            "adversarial",
            "ambiguous",
            "correct",
            "incomplete",
            "subtly_wrong",
            "unsupported_claim",
            "unverifiable",
            "wrong_format",
        ],
        "deterministically_resolved_cases": 6,
        "semantic_or_human_cases": 2,
        "quality_claims_authorized": False,
    }


def test_deterministic_validators_run_before_semantic_judgment_where_objective() -> None:
    cases = {case.case_id: case for case in load_gold_cases(GOLD_PATH)}

    correct = deterministic_validate(cases["correct-two-labels"])
    assert correct.status == "passed"
    assert all(value == "pass" for value in correct.checks.values())

    subtle = deterministic_validate(cases["subtle-wrong-label"])
    assert subtle.status == "failed"
    assert subtle.checks["task_adherence"] == "fail"
    assert subtle.checks["format_consistency"] == "pass"

    adversarial = deterministic_validate(cases["adversarial-verifier-injection"])
    assert adversarial.status == "failed"
    assert adversarial.checks["unsupported_claims_absent"] == "fail"

    ambiguous = deterministic_validate(cases["ambiguous-taxonomy"])
    assert ambiguous.status is None
    assert ambiguous.checks["output_present"] == "pass"
    assert ambiguous.checks["task_adherence"] is None


def test_perfect_observations_produce_zero_error_without_claiming_quality() -> None:
    cases = load_gold_cases(GOLD_PATH)
    observations = [
        observation(
            case.case_id,
            gold_dict(case),
            run_id=f"run-{index}",
            duration_ms=100 + index,
            input_tokens=10,
            output_tokens=5,
        )
        for index, case in enumerate(cases, start=1)
    ]
    report = evaluate_calibration(cases, observations)

    assert report.total_gold_cases == 8
    assert report.total_observations == 8
    assert report.exact_status_accuracy == 1.0
    assert report.false_pass_rate == 0.0
    assert report.false_fail_rate == 0.0
    assert report.missed_human_rate == 0.0
    assert report.unnecessary_human_rate == 0.0
    assert report.needs_human_prediction_rate == pytest.approx(0.25)
    assert all(value == 1.0 for value in report.criterion_accuracy.values())
    assert report.repeatability_agreement_rate is None
    assert report.cross_verifier_disagreement_cases == []
    assert report.total_input_tokens == 80
    assert report.total_output_tokens == 40


def test_metrics_distinguish_false_pass_false_fail_and_human_errors() -> None:
    cases = load_gold_cases(GOLD_PATH)
    by_id = {case.case_id: case for case in cases}
    observations = [
        observation(
            "subtle-wrong-label",
            decision("passed"),
            run_id="false-pass",
        ),
        observation(
            "correct-two-labels",
            decision(
                "failed",
                task_adherence="fail",
            ),
            run_id="false-fail",
        ),
        observation(
            "ambiguous-taxonomy",
            decision("passed"),
            run_id="missed-human",
        ),
        observation(
            "correct-two-labels",
            decision(
                "needs_human",
                task_adherence="uncertain",
                human_reason="ambiguous_task",
            ),
            run_id="unnecessary-human",
        ),
    ]
    report = evaluate_calibration(list(by_id.values()), observations)

    assert report.false_pass_count == 2
    assert report.false_fail_count == 1
    assert report.missed_human_count == 1
    assert report.unnecessary_human_count == 1
    assert report.exact_status_accuracy == 0.0


def test_repeatability_and_cross_verifier_disagreement_are_measured() -> None:
    cases = load_gold_cases(GOLD_PATH)
    correct = next(case for case in cases if case.case_id == "correct-two-labels")
    observations = [
        observation("correct-two-labels", gold_dict(correct), run_id="g-1"),
        observation("correct-two-labels", gold_dict(correct), run_id="g-2"),
        observation(
            "correct-two-labels",
            decision("failed", task_adherence="fail"),
            run_id="g-3",
        ),
        observation(
            "correct-two-labels",
            decision("failed", task_adherence="fail"),
            provider="anthropic",
            model="claude-sonnet-5",
            run_id="a-1",
            execution_role="fallback",
            fallback_used=True,
        ),
    ]
    report = evaluate_calibration(cases, observations)

    assert report.repeatability_groups == 1
    assert report.repeatability_agreement_rate == pytest.approx(2 / 3)
    assert report.cross_verifier_disagreement_cases == ["correct-two-labels"]
    assert report.by_execution_path["primary_no_retry"]["observations"] == 3
    assert report.by_execution_path["fallback"]["observations"] == 1


def test_observation_contract_rejects_content_and_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "observations.jsonl"
    path.write_text(
        json.dumps(
            {
                "case_id": "correct-two-labels",
                "verifier_provider_family": "google",
                "verifier_model": "gemini-3.6-flash",
                "run_id": "run-1",
                "decision": decision("passed"),
                "candidate_output": "must not be persisted",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CalibrationError, match="unsupported fields"):
        load_observations(path)


def test_observation_json_schema_is_strict_and_content_free() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    valid = {
        "case_id": "correct-two-labels",
        "verifier_provider_family": "google",
        "verifier_model": "gemini-3.6-flash",
        "run_id": "run-1",
        "execution_role": "primary",
        "retry_count": 0,
        "fallback_used": False,
        "duration_ms": 100.0,
        "input_tokens": 10,
        "output_tokens": 5,
        "decision": decision("passed"),
    }
    validator.validate(valid)
    invalid = dict(valid)
    invalid["task"] = "content must not enter observation records"
    assert list(validator.iter_errors(invalid))


def test_calibration_policy_has_no_routing_or_quality_authority() -> None:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    assert policy["status"] == "active"
    assert policy["scope"]["live_scope_expansion_authorized"] is False
    assert policy["scope"]["routing_authority"] is False
    assert policy["scope"]["quality_claims_authorized"] is False
    assert policy["gold_corpus"]["deterministic_validation_first"] is True
    assert policy["observation_requirements"]["minimum_runs_per_case_per_verifier"] == 3
    assert policy["observation_requirements"]["minimum_distinct_verifier_routes"] == 3
    assert policy["expansion_gate"]["automatic_expansion"] is False
    assert policy["expansion_gate"]["require_independent_human_review"] is True
