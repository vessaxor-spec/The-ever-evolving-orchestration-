from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker

from teo_reference.verifier_calibration import (
    CalibrationError,
    CalibrationObservation,
    assess_evidence_readiness,
    deterministic_validate,
    evaluate_calibration,
    gold_summary,
    load_calibration_policy,
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


def observation(
    case_id: str,
    gold: dict,
    *,
    provider: str = "google",
    model: str = "gemini-3.6-flash",
    reasoning: str | None = "medium",
    run_id: str = "run-1",
    observed_at: str = "2026-08-07T13:00:00Z",
    rubric_version: str = "1.0",
    verification_policy_version: str = "1.1",
    **extra,
) -> CalibrationObservation:
    payload = {
        "case_id": case_id,
        "verifier_provider_family": provider,
        "verifier_model": model,
        "verifier_reasoning": reasoning,
        "run_id": run_id,
        "observed_at": observed_at,
        "rubric_version": rubric_version,
        "verification_policy_version": verification_policy_version,
        "decision": gold,
        "execution_role": "primary",
        "retry_count": 0,
        "fallback_used": False,
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
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
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
    summary = gold_summary(cases, policy=policy)
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
        "rubric_version": "1.0",
        "deterministically_resolved_cases": 6,
        "semantic_or_human_cases": 2,
        "quality_claims_authorized": False,
        "scope_expansion_authorized": False,
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


def test_perfect_observations_produce_zero_conditional_error_without_claiming_quality() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    observations = [
        observation(
            case.case_id,
            gold_dict(case),
            run_id=f"run-{index}",
            observed_at=f"2026-08-07T13:{index:02d}:00Z",
            duration_ms=100 + index,
            input_tokens=10,
            output_tokens=5,
        )
        for index, case in enumerate(cases, start=1)
    ]
    report = evaluate_calibration(cases, observations, policy=policy)

    assert report.total_gold_cases == 8
    assert report.total_observations == 8
    assert report.exact_status_accuracy == 1.0
    assert report.false_pass_count == 0
    assert report.false_pass_opportunities == 7
    assert report.false_pass_rate == 0.0
    assert report.false_fail_count == 0
    assert report.false_fail_opportunities == 1
    assert report.false_fail_rate == 0.0
    assert report.human_required_opportunities == 2
    assert report.missed_human_rate == 0.0
    assert report.non_human_opportunities == 6
    assert report.unnecessary_human_rate == 0.0
    assert report.needs_human_prediction_rate == pytest.approx(0.25)
    assert all(value == 1.0 for value in report.criterion_accuracy.values())
    assert report.repeatability_agreement_rate is None
    assert report.cross_verifier_disagreement_cases == []
    assert report.verifier_routes == ["google/gemini-3.6-flash/medium"]
    assert report.verifier_provider_families == ["google"]
    assert report.observation_window_start == "2026-08-07T13:01:00Z"
    assert report.observation_window_end == "2026-08-07T13:08:00Z"
    assert report.total_input_tokens == 80
    assert report.total_output_tokens == 40


def test_metrics_use_relevant_gold_opportunities_as_denominators() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    observations = [
        observation(
            "subtle-wrong-label",
            decision("passed"),
            run_id="false-pass",
        ),
        observation(
            "correct-two-labels",
            decision("failed", task_adherence="fail"),
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
    report = evaluate_calibration(cases, observations, policy=policy)

    assert report.false_pass_count == 2
    assert report.false_pass_opportunities == 2
    assert report.false_pass_rate == 1.0
    assert report.false_fail_count == 1
    assert report.false_fail_opportunities == 2
    assert report.false_fail_rate == pytest.approx(0.5)
    assert report.missed_human_count == 1
    assert report.human_required_opportunities == 1
    assert report.missed_human_rate == 1.0
    assert report.unnecessary_human_count == 1
    assert report.non_human_opportunities == 3
    assert report.unnecessary_human_rate == pytest.approx(1 / 3)
    assert report.exact_status_accuracy == 0.0


def test_repeatability_cross_verifier_disagreement_and_execution_paths_are_measured() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
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
            reasoning="medium",
            run_id="a-1",
            execution_role="fallback",
            fallback_used=True,
        ),
    ]
    report = evaluate_calibration(cases, observations, policy=policy)

    assert report.repeatability_groups == 1
    assert report.repeatability_agreement_rate == pytest.approx(1 / 3)
    assert report.cross_verifier_disagreement_cases == ["correct-two-labels"]
    assert report.by_execution_path["primary_no_retry"]["observations"] == 3
    assert report.by_execution_path["fallback"]["observations"] == 1
    assert report.verifier_routes == [
        "anthropic/claude-sonnet-5/medium",
        "google/gemini-3.6-flash/medium",
    ]


def test_observation_contract_rejects_content_and_unknown_fields(tmp_path: Path) -> None:
    path = tmp_path / "observations.jsonl"
    path.write_text(
        json.dumps(
            {
                "case_id": "correct-two-labels",
                "verifier_provider_family": "google",
                "verifier_model": "gemini-3.6-flash",
                "verifier_reasoning": "medium",
                "run_id": "run-1",
                "observed_at": "2026-08-07T13:00:00Z",
                "rubric_version": "1.0",
                "verification_policy_version": "1.1",
                "execution_role": "primary",
                "retry_count": 0,
                "fallback_used": False,
                "decision": decision("passed"),
                "candidate_output": "must not be persisted",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(CalibrationError, match="unsupported fields"):
        load_observations(path)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("retry_count", "1", "retry_count must be a non-negative integer"),
        ("retry_count", True, "retry_count must be a non-negative integer"),
        ("fallback_used", "false", "fallback_used must be a boolean"),
        ("case_id", 42, "case_id must be a non-empty string"),
        ("observed_at", "2026-08-07 13:00:00", "observed_at must include a UTC offset"),
    ],
)
def test_parser_rejects_schema_incompatible_type_or_time_coercion(field, value, message) -> None:
    payload = {
        "case_id": "correct-two-labels",
        "verifier_provider_family": "google",
        "verifier_model": "gemini-3.6-flash",
        "verifier_reasoning": "medium",
        "run_id": "run-1",
        "observed_at": "2026-08-07T13:00:00Z",
        "rubric_version": "1.0",
        "verification_policy_version": "1.1",
        "execution_role": "primary",
        "retry_count": 0,
        "fallback_used": False,
        "decision": decision("passed"),
    }
    payload[field] = value
    with pytest.raises(CalibrationError, match=message):
        CalibrationObservation.from_dict(payload)


def test_parser_rejects_missing_required_observation_fields() -> None:
    payload = {
        "case_id": "correct-two-labels",
        "verifier_provider_family": "google",
        "verifier_model": "gemini-3.6-flash",
        "verifier_reasoning": "medium",
        "run_id": "run-1",
        "rubric_version": "1.0",
        "verification_policy_version": "1.1",
        "execution_role": "primary",
        "retry_count": 0,
        "fallback_used": False,
        "decision": decision("passed"),
    }
    with pytest.raises(CalibrationError, match="missing required fields: observed_at"):
        CalibrationObservation.from_dict(payload)


def test_parser_rejects_execution_role_fallback_disagreement() -> None:
    with pytest.raises(CalibrationError, match="execution_role and fallback_used must agree"):
        observation(
            "correct-two-labels",
            decision("passed"),
            execution_role="fallback",
            fallback_used=False,
        )


def test_observation_json_schema_is_strict_content_free_and_route_consistent() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    valid = {
        "case_id": "correct-two-labels",
        "verifier_provider_family": "google",
        "verifier_model": "gemini-3.6-flash",
        "verifier_reasoning": "medium",
        "run_id": "run-1",
        "observed_at": "2026-08-07T13:00:00Z",
        "rubric_version": "1.0",
        "verification_policy_version": "1.1",
        "execution_role": "primary",
        "retry_count": 0,
        "fallback_used": False,
        "duration_ms": 100.0,
        "input_tokens": 10,
        "output_tokens": 5,
        "decision": decision("passed"),
    }
    validator.validate(valid)

    content_bearing = dict(valid)
    content_bearing["task"] = "content must not enter observation records"
    assert list(validator.iter_errors(content_bearing))

    string_retry = dict(valid)
    string_retry["retry_count"] = "1"
    assert list(validator.iter_errors(string_retry))

    missing_timestamp = dict(valid)
    del missing_timestamp["observed_at"]
    assert list(validator.iter_errors(missing_timestamp))

    invalid_timestamp = dict(valid)
    invalid_timestamp["observed_at"] = "not-a-time"
    assert list(validator.iter_errors(invalid_timestamp))

    inconsistent_fallback = dict(valid)
    inconsistent_fallback["execution_role"] = "fallback"
    inconsistent_fallback["fallback_used"] = False
    assert list(validator.iter_errors(inconsistent_fallback))


def test_duplicate_observation_identity_is_rejected() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    correct = next(case for case in cases if case.case_id == "correct-two-labels")
    duplicate = observation("correct-two-labels", gold_dict(correct), run_id="same")
    with pytest.raises(CalibrationError, match="Duplicate calibration observation identity"):
        evaluate_calibration(cases, [duplicate, duplicate], policy=policy)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("rubric_version", "0.9", "rubric version"),
        ("verification_policy_version", "1.0", "unsupported verification policy version"),
    ],
)
def test_observation_version_drift_is_rejected(field, value, message) -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    correct = next(case for case in cases if case.case_id == "correct-two-labels")
    kwargs = {field: value}
    drifted = observation("correct-two-labels", gold_dict(correct), **kwargs)
    with pytest.raises(CalibrationError, match=message):
        evaluate_calibration(cases, [drifted], policy=policy)


def test_empty_observations_do_not_produce_zero_error_report() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    with pytest.raises(CalibrationError, match="observations are empty"):
        evaluate_calibration(cases, [], policy=policy)


def test_evidence_readiness_stays_closed_when_routes_or_repeats_are_missing() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    correct = next(case for case in cases if case.case_id == "correct-two-labels")
    readiness = assess_evidence_readiness(
        cases,
        [observation("correct-two-labels", gold_dict(correct), run_id="one")],
        policy,
    )

    assert readiness.data_requirements_met is False
    assert readiness.distinct_verifier_routes == 1
    assert readiness.required_distinct_verifier_routes == 3
    assert readiness.distinct_verifier_provider_families == 1
    assert readiness.required_distinct_verifier_provider_families == 3
    assert readiness.undercovered_case_routes
    assert readiness.independent_human_review_required is True
    assert readiness.quality_claims_authorized is False
    assert readiness.scope_expansion_authorized is False


def test_three_routes_from_one_provider_do_not_satisfy_provider_diversity() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    routes = [
        ("google", "gemini-3.6-flash", "low"),
        ("google", "gemini-3.6-flash", "medium"),
        ("google", "gemini-3.1-pro-preview", "high"),
    ]
    observations = []
    for case in cases:
        for route_index, (provider, model, reasoning) in enumerate(routes, start=1):
            for run in range(1, 4):
                observations.append(
                    observation(
                        case.case_id,
                        gold_dict(case),
                        provider=provider,
                        model=model,
                        reasoning=reasoning,
                        run_id=f"{case.case_id}-{route_index}-{run}",
                    )
                )

    readiness = assess_evidence_readiness(cases, observations, policy)

    assert readiness.distinct_verifier_routes == 3
    assert readiness.distinct_verifier_provider_families == 1
    assert readiness.data_requirements_met is False


def test_evidence_readiness_can_confirm_data_coverage_but_never_self_authorize() -> None:
    policy = load_calibration_policy(POLICY_PATH)
    cases = load_gold_cases(GOLD_PATH, policy=policy)
    routes = [
        ("google", "gemini-3.6-flash", "medium"),
        ("anthropic", "claude-sonnet-5", "medium"),
        ("openai", "gpt-5.6-sol", "high"),
    ]
    observations = []
    for case in cases:
        for provider, model, reasoning in routes:
            for run in range(1, 4):
                observations.append(
                    observation(
                        case.case_id,
                        gold_dict(case),
                        provider=provider,
                        model=model,
                        reasoning=reasoning,
                        run_id=f"{case.case_id}-{provider}-{run}",
                    )
                )

    readiness = assess_evidence_readiness(cases, observations, policy)

    assert len(observations) == 72
    assert readiness.data_requirements_met is True
    assert readiness.distinct_verifier_routes == 3
    assert readiness.distinct_verifier_provider_families == 3
    assert readiness.undercovered_case_routes == []
    assert readiness.independent_human_review_required is True
    assert readiness.quality_claims_authorized is False
    assert readiness.scope_expansion_authorized is False


def test_calibration_policy_has_no_routing_quality_or_scope_authority() -> None:
    policy_raw = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    policy = load_calibration_policy(POLICY_PATH)

    assert policy_raw["status"] == "active"
    assert policy_raw["scope"]["live_scope_expansion_authorized"] is False
    assert policy_raw["scope"]["routing_authority"] is False
    assert policy_raw["scope"]["quality_claims_authorized"] is False
    assert policy_raw["gold_corpus"]["deterministic_validation_first"] is True
    assert policy.minimum_runs_per_case_per_verifier == 3
    assert policy.minimum_distinct_verifier_routes == 3
    assert policy.minimum_distinct_verifier_provider_families == 3
    assert policy.expected_rubric_version == "1.0"
    assert policy.expected_verification_policy_version == "1.1"
    assert policy_raw["expansion_gate"]["automatic_expansion"] is False
    assert policy.require_independent_human_review is True
