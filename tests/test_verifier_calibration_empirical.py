from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest
from jsonschema import Draft202012Validator

from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.verifier_calibration import (
    CalibrationError,
    load_calibration_policy,
    load_gold_cases,
)
from teo_reference.verifier_calibration_empirical import (
    COLLECTION_ROLE,
    assess_human_label_readiness,
    build_human_gold_cases,
    collect_live_observations,
    evaluate_empirical_calibration,
    load_empirical_policy,
    planned_collection,
    validate_empirical_policy_against_base,
    HumanCalibrationLabel,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EMPIRICAL_POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration-empirical.yaml"
OBSERVATION_SCHEMA_PATH = (
    REPO_ROOT / "reference/schemas/verifier-calibration-empirical-observation.schema.json"
)
HUMAN_LABEL_SCHEMA_PATH = (
    REPO_ROOT / "reference/schemas/verifier-calibration-human-label.schema.json"
)


def context():
    empirical = load_empirical_policy(EMPIRICAL_POLICY_PATH)
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    validate_empirical_policy_against_base(empirical, base)
    cases = load_gold_cases(REPO_ROOT / empirical.control_corpus_path, policy=base)
    return empirical, base, cases


def decision_dict(decision) -> dict:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def human_labels(cases, *, reviewers=("reviewer-a", "reviewer-b"), reviewed_at="2026-08-07T14:00:00Z"):
    labels = []
    for case in cases:
        for reviewer in reviewers:
            labels.append(
                HumanCalibrationLabel.from_dict(
                    {
                        "case_id": case.case_id,
                        "reviewer_id": reviewer,
                        "reviewer_role": "reviewer",
                        "reviewed_at": reviewed_at,
                        "rubric_version": case.rubric_version,
                        "observations_blinded": True,
                        "decision": decision_dict(case.gold),
                    }
                )
            )
    return labels


def request_prompt(provider: str, body: dict) -> str:
    if provider == "google":
        return body["input"]
    if provider == "anthropic":
        return body["messages"][0]["content"]
    return body["input"][1]["content"]


def provider_payload(provider: str, model: str, verdict: dict, *, include_usage=True) -> dict:
    if provider == "google":
        payload = {
            "id": "int_calibration",
            "model": model,
            "status": "completed",
            "steps": [
                {
                    "type": "model_output",
                    "content": [{"type": "text", "text": json.dumps(verdict)}],
                }
            ],
        }
        if include_usage:
            payload["usage"] = {
                "total_input_tokens": 11,
                "total_output_tokens": 5,
                "total_tokens": 16,
            }
        return payload
    if provider == "anthropic":
        payload = {
            "id": "msg_calibration",
            "model": model,
            "content": [{"type": "text", "text": json.dumps(verdict)}],
        }
        if include_usage:
            payload["usage"] = {
                "input_tokens": 12,
                "cache_creation_input_tokens": 2,
                "cache_read_input_tokens": 3,
                "output_tokens": 6,
            }
        return payload
    payload = {
        "id": "resp_calibration",
        "model": model,
        "status": "completed",
        "output": [
            {
                "type": "message",
                "content": [{"type": "output_text", "text": json.dumps(verdict)}],
            }
        ],
    }
    if include_usage:
        payload["usage"] = {
            "input_tokens": 13,
            "output_tokens": 7,
            "total_tokens": 20,
        }
    return payload


def mock_connection(provider: str, model: str, cases, calls: list[dict], *, include_usage=True):
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        decoded = json.loads(body.decode("utf-8"))
        prompt = request_prompt(provider, decoded)
        matched = None
        for case in cases:
            if (
                f"ORIGINAL TASK:\n{case.task}" in prompt
                and f"CANDIDATE OUTPUT:\n{case.candidate_output}" in prompt
            ):
                matched = case
                break
        assert matched is not None
        calls.append(
            {
                "provider": provider,
                "model": model,
                "body": decoded,
                "headers": dict(headers),
                "timeout": timeout,
                "case_id": matched.case_id,
            }
        )
        payload = provider_payload(
            provider,
            model,
            decision_dict(matched.gold),
            include_usage=include_usage,
        )
        return 200, {"x-request-id": f"req-{provider}"}, json.dumps(payload).encode("utf-8")

    return HeaderProviderConnection(
        provider_family=provider,
        authorization_headers={"authorization": "Bearer test-only"},
        transport=transport,
    )


def all_connections(empirical, cases, calls, *, include_usage=True):
    return {
        route.provider_family: mock_connection(
            route.provider_family,
            route.model,
            cases,
            calls,
            include_usage=include_usage,
        )
        for route in empirical.verifier_routes
    }


def test_empirical_policy_requires_three_provider_diverse_routes_and_no_authority() -> None:
    empirical, base, cases = context()
    assert len(empirical.verifier_routes) == 3
    assert {route.provider_family for route in empirical.verifier_routes} == {
        "google",
        "anthropic",
        "openai",
    }
    assert empirical.runs_per_case_per_route == 3
    plan = planned_collection(cases, empirical)
    assert plan["planned_live_calls"] == 72
    assert plan["collection_role"] == COLLECTION_ROLE
    assert plan["quality_claims_authorized"] is False
    assert plan["scope_expansion_authorized"] is False
    validate_empirical_policy_against_base(empirical, base)


def test_two_blinded_independent_reviewers_satisfy_human_label_floor() -> None:
    empirical, base, cases = context()
    labels = human_labels(cases)
    readiness = assess_human_label_readiness(cases, labels, empirical)
    assert readiness.human_label_requirements_met is True
    assert readiness.reviewer_ids == ["reviewer-a", "reviewer-b"]
    assert readiness.undercovered_cases == []
    assert readiness.disagreement_cases == []
    assert readiness.adjudication_missing_cases == []
    human_gold = build_human_gold_cases(cases, labels, empirical, base)
    assert [case.gold for case in human_gold] == [case.gold for case in cases]


def test_human_disagreement_requires_distinct_adjudicator() -> None:
    empirical, base, cases = context()
    labels = human_labels(cases)
    case = cases[0]
    altered = decision_dict(case.gold)
    altered["status"] = "failed"
    altered["task_adherence"] = "fail"
    labels = [
        label
        for label in labels
        if not (label.case_id == case.case_id and label.reviewer_id == "reviewer-b")
    ]
    labels.append(
        HumanCalibrationLabel.from_dict(
            {
                "case_id": case.case_id,
                "reviewer_id": "reviewer-b",
                "reviewer_role": "reviewer",
                "reviewed_at": "2026-08-07T14:00:00Z",
                "rubric_version": case.rubric_version,
                "observations_blinded": True,
                "decision": altered,
            }
        )
    )
    readiness = assess_human_label_readiness(cases, labels, empirical)
    assert readiness.human_label_requirements_met is False
    assert readiness.disagreement_cases == [case.case_id]
    assert readiness.adjudication_missing_cases == [case.case_id]

    labels.append(
        HumanCalibrationLabel.from_dict(
            {
                "case_id": case.case_id,
                "reviewer_id": "adjudicator-c",
                "reviewer_role": "adjudicator",
                "reviewed_at": "2026-08-07T14:05:00Z",
                "rubric_version": case.rubric_version,
                "observations_blinded": True,
                "decision": decision_dict(case.gold),
            }
        )
    )
    readiness = assess_human_label_readiness(cases, labels, empirical)
    assert readiness.human_label_requirements_met is True
    human_gold = build_human_gold_cases(cases, labels, empirical, base)
    assert human_gold[0].gold == case.gold


def test_empirical_collection_creates_72_content_free_observations_and_resumes(tmp_path: Path) -> None:
    empirical, base, cases = context()
    labels = human_labels(cases)
    calls: list[dict] = []
    connections = all_connections(empirical, cases, calls)
    output = tmp_path / "observations.jsonl"

    observations = collect_live_observations(
        cases,
        labels,
        empirical,
        base,
        connections,
        collector_revision="abcdef1234567890",
        output_path=output,
        now=lambda: "2026-08-07T15:00:00Z",
    )
    assert len(observations) == 72
    assert len(calls) == 72
    assert {observation.collection_role for observation in observations} == {
        COLLECTION_ROLE
    }
    assert {observation.verifier_provider_family for observation in observations} == {
        "google",
        "anthropic",
        "openai",
    }
    assert sum(observation.input_tokens for observation in observations) == 984
    assert sum(observation.output_tokens for observation in observations) == 432

    schema = json.loads(OBSERVATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    persisted = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    assert len(persisted) == 72
    for item in persisted:
        validator.validate(item)
        assert "task" not in item
        assert "candidate_output" not in item
        assert "execution_role" not in item
        assert "retry_count" not in item
        assert "fallback_used" not in item
        assert "evidence" not in item

    resumed = collect_live_observations(
        cases,
        labels,
        empirical,
        base,
        connections,
        collector_revision="abcdef1234567890",
        output_path=output,
        now=lambda: "2026-08-07T15:10:00Z",
    )
    assert len(resumed) == 72
    assert len(calls) == 72

    report = evaluate_empirical_calibration(
        cases,
        labels,
        resumed,
        empirical,
        base,
    )
    metrics = report["metrics_against_independent_human_labels"]
    assert metrics["exact_status_accuracy"] == 1.0
    assert metrics["false_pass_rate"] == 0.0
    assert metrics["false_fail_rate"] == 0.0
    assert metrics["missed_human_rate"] == 0.0
    assert metrics["unnecessary_human_rate"] == 0.0
    assert "by_execution_path" not in metrics
    assert metrics["by_collection_path"][COLLECTION_ROLE]["observations"] == 72
    assert report["evidence_readiness"]["data_requirements_met"] is True
    assert report["evidence_readiness"]["empirical_required_routes_present"] is True
    assert report["reference_control_vs_human_disagreement_cases"] == []
    assert report["authority"]["quality_claims_authorized"] is False
    assert report["authority"]["scope_expansion_authorized"] is False


def test_collection_refuses_before_independent_human_labels_are_ready(tmp_path: Path) -> None:
    empirical, base, cases = context()
    labels = human_labels(cases, reviewers=("reviewer-a",))
    calls: list[dict] = []
    with pytest.raises(CalibrationError, match="human labels are not ready"):
        collect_live_observations(
            cases,
            labels,
            empirical,
            base,
            all_connections(empirical, cases, calls),
            collector_revision="abcdef1234567890",
            output_path=tmp_path / "observations.jsonl",
            now=lambda: "2026-08-07T15:00:00Z",
        )
    assert calls == []


def test_collection_refuses_success_without_provider_reported_usage(tmp_path: Path) -> None:
    empirical, base, cases = context()
    labels = human_labels(cases)
    calls: list[dict] = []
    google_route = next(
        route for route in empirical.verifier_routes if route.provider_family == "google"
    )
    connection = mock_connection(
        "google",
        google_route.model,
        cases,
        calls,
        include_usage=False,
    )
    with pytest.raises(CalibrationError, match="required provider usage"):
        collect_live_observations(
            cases,
            labels,
            empirical,
            base,
            {"google": connection},
            collector_revision="abcdef1234567890",
            output_path=tmp_path / "observations.jsonl",
            providers={"google"},
            now=lambda: "2026-08-07T15:00:00Z",
        )
    assert len(calls) == 1
    assert not (tmp_path / "observations.jsonl").exists()


def test_human_label_schema_is_content_free_and_requires_blinding() -> None:
    empirical, base, cases = context()
    case = cases[0]
    schema = json.loads(HUMAN_LABEL_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    valid = {
        "case_id": case.case_id,
        "reviewer_id": "reviewer-a",
        "reviewer_role": "reviewer",
        "reviewed_at": "2026-08-07T14:00:00Z",
        "rubric_version": case.rubric_version,
        "observations_blinded": True,
        "decision": decision_dict(case.gold),
    }
    validator.validate(valid)

    unblinded = dict(valid)
    unblinded["observations_blinded"] = False
    assert list(validator.iter_errors(unblinded))

    content_bearing = dict(valid)
    content_bearing["reviewer_email"] = "person@example.test"
    assert list(validator.iter_errors(content_bearing))


def test_empirical_observations_cannot_predate_completed_human_labels(tmp_path: Path) -> None:
    empirical, base, cases = context()
    labels = human_labels(cases, reviewed_at="2026-08-07T16:00:00Z")
    calls: list[dict] = []
    with pytest.raises(CalibrationError, match="predates completion"):
        collect_live_observations(
            cases,
            labels,
            empirical,
            base,
            all_connections(empirical, cases, calls),
            collector_revision="abcdef1234567890",
            output_path=tmp_path / "observations.jsonl",
            providers={"google"},
            now=lambda: "2026-08-07T15:00:00Z",
        )
    # The first provider call completed, but the observation was rejected before it
    # could become valid empirical evidence.
    assert len(calls) == 1
