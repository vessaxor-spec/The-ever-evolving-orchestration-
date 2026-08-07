from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path
from typing import Mapping

import pytest
from jsonschema import Draft202012Validator

from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.verifier_calibration import CalibrationError, load_calibration_policy, load_gold_cases
from teo_reference.verifier_calibration_empirical import load_empirical_policy
from teo_reference.verifier_calibration_human_review import build_review_materials
from teo_reference.verifier_calibration_machine_panel import (
    EVIDENCE_TIER,
    MachinePanelLabel,
    assess_machine_panel_readiness,
    collect_machine_panel_labels,
    collect_provisional_observations,
    evaluate_provisional_calibration,
    load_machine_panel_policy,
    planned_machine_panel_study,
    validate_machine_panel_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration-machine-panel.yaml"
PANEL_SCHEMA_PATH = REPO_ROOT / "reference/schemas/verifier-calibration-machine-panel-label.schema.json"
OBS_SCHEMA_PATH = REPO_ROOT / "reference/schemas/verifier-calibration-provisional-observation.schema.json"


def context():
    panel = load_machine_panel_policy(POLICY_PATH)
    empirical = load_empirical_policy(REPO_ROOT / panel.empirical_policy_path)
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    validate_machine_panel_policy(panel, empirical, base)
    cases = load_gold_cases(REPO_ROOT / panel.control_corpus_path, policy=base)
    tokens = iter(["packet0000000001", *[f"item{i:014d}" for i in range(len(cases))]])
    packet, private_map = build_review_materials(
        cases,
        panel.rubric_version,
        token_factory=lambda: next(tokens),
    )
    return panel, empirical, base, cases, packet, private_map


def decision_dict(decision) -> dict:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def request_prompt(provider: str, body: dict) -> str:
    if provider == "google":
        return body["input"]
    if provider == "anthropic":
        return body["messages"][0]["content"]
    return body["input"][1]["content"]


def provider_payload(provider: str, model: str, verdict: dict, *, include_usage=True) -> dict:
    if provider == "google":
        payload = {
            "id": "int_machine_panel",
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
            "id": "msg_machine_panel",
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
        "id": "resp_machine_panel",
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
            expected = (
                f"ORIGINAL TASK:\n{case.task}\n\n"
                f"CANDIDATE OUTPUT:\n{case.candidate_output}\n\n"
                "Criteria:\n"
            )
            if expected in prompt:
                matched = case
                break
        assert matched is not None
        calls.append({"provider": provider, "model": model, "case_id": matched.case_id})
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


def connections_for_routes(routes, cases, calls, *, include_usage=True):
    return {
        route.provider_family: mock_connection(
            route.provider_family,
            route.model,
            cases,
            calls,
            include_usage=include_usage,
        )
        for route in routes
    }


def test_machine_panel_policy_is_provider_diverse_model_distinct_and_non_authoritative() -> None:
    panel, empirical, base, cases, packet, private_map = context()
    assert len(panel.panel_routes) == 3
    assert {route.provider_family for route in panel.panel_routes} == {
        "google",
        "anthropic",
        "openai",
    }
    assert not (
        {route.model for route in panel.panel_routes}
        & {route.model for route in empirical.verifier_routes}
    )
    plan = planned_machine_panel_study(cases, panel, empirical)
    assert plan["planned_machine_panel_calls"] == 24
    assert plan["planned_provisional_verifier_calls"] == 72
    assert plan["planned_total_live_calls"] == 96
    assert plan["human_ground_truth_claim_authorized"] is False
    assert plan["quality_claims_authorized"] is False
    assert plan["routing_authority"] is False
    validate_machine_panel_policy(panel, empirical, base)


def test_machine_panel_policy_refuses_exact_model_overlap_with_evaluated_routes() -> None:
    panel, empirical, base, cases, packet, private_map = context()
    overlapping_route = replace(
        panel.panel_routes[0],
        model=empirical.verifier_routes[0].model,
    )
    mutated = replace(panel, panel_routes=(overlapping_route, *panel.panel_routes[1:]))
    with pytest.raises(CalibrationError, match="must differ from evaluated verifier models"):
        validate_machine_panel_policy(mutated, empirical, base)


def test_machine_panel_collects_24_blinded_content_free_labels_and_resumes(tmp_path: Path) -> None:
    panel, empirical, base, cases, packet, private_map = context()
    calls: list[dict] = []
    labels_path = tmp_path / "panel-labels.jsonl"
    labels = collect_machine_panel_labels(
        packet,
        panel,
        empirical,
        connections_for_routes(panel.panel_routes, cases, calls),
        output_path=labels_path,
        now=lambda: "2026-08-07T15:00:00Z",
    )
    assert len(labels) == 24
    assert len(calls) == 24
    readiness = assess_machine_panel_readiness(packet, labels, panel)
    assert readiness.panel_coverage_requirements_met is True
    assert readiness.majority_items == 8
    assert readiness.unresolved_items == []
    assert readiness.human_ground_truth_claim_authorized is False
    assert readiness.quality_claims_authorized is False

    schema = json.loads(PANEL_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    persisted = [json.loads(line) for line in labels_path.read_text(encoding="utf-8").splitlines()]
    canonical_ids = {case.case_id for case in cases}
    for item in persisted:
        validator.validate(item)
        assert item["evidence_tier"] == EVIDENCE_TIER
        assert item["reference_control_labels_blinded"] is True
        assert item["model_observations_blinded"] is True
        assert "case_id" not in item
        assert "task" not in item
        assert "candidate_output" not in item
        assert not (canonical_ids & set(item.values()))

    resumed = collect_machine_panel_labels(
        packet,
        panel,
        empirical,
        connections_for_routes(panel.panel_routes, cases, calls),
        output_path=labels_path,
        now=lambda: "2026-08-07T15:05:00Z",
    )
    assert len(resumed) == 24
    assert len(calls) == 24


def test_machine_panel_preserves_no_majority_as_unresolved_without_blocking_coverage() -> None:
    panel, empirical, base, cases, packet, private_map = context()
    item_id = packet["items"][0]["review_item_id"]
    decisions = [case.gold for case in cases[:3]]
    labels = []
    for route, decision in zip(panel.panel_routes, decisions, strict=True):
        labels.append(
            MachinePanelLabel(
                review_item_id=item_id,
                judge_provider_family=route.provider_family,
                judge_model=route.model,
                judge_reasoning=route.reasoning,
                observed_at="2026-08-07T15:00:00Z",
                rubric_version=panel.rubric_version,
                duration_ms=1.0,
                input_tokens=1,
                output_tokens=1,
                decision=decision,
            )
        )
    for item in packet["items"][1:]:
        case = next(
            case
            for case in cases
            if case.task == item["task"] and case.candidate_output == item["candidate_output"]
        )
        for route in panel.panel_routes:
            labels.append(
                MachinePanelLabel(
                    review_item_id=item["review_item_id"],
                    judge_provider_family=route.provider_family,
                    judge_model=route.model,
                    judge_reasoning=route.reasoning,
                    observed_at="2026-08-07T15:00:00Z",
                    rubric_version=panel.rubric_version,
                    duration_ms=1.0,
                    input_tokens=1,
                    output_tokens=1,
                    decision=case.gold,
                )
            )
    readiness = assess_machine_panel_readiness(packet, labels, panel)
    assert readiness.panel_coverage_requirements_met is True
    assert readiness.unresolved_items == [item_id]
    assert readiness.majority_items == 7


def test_provisional_collection_creates_separate_72_observations_and_reference_control_report(tmp_path: Path) -> None:
    panel, empirical, base, cases, packet, private_map = context()
    calls: list[dict] = []
    panel_labels = collect_machine_panel_labels(
        packet,
        panel,
        empirical,
        connections_for_routes(panel.panel_routes, cases, calls),
        output_path=tmp_path / "panel-labels.jsonl",
        now=lambda: "2026-08-07T15:00:00Z",
    )
    assert len(calls) == 24
    observations = collect_provisional_observations(
        cases,
        packet,
        panel_labels,
        panel,
        empirical,
        connections_for_routes(empirical.verifier_routes, cases, calls),
        collector_revision="abcdef1234567890",
        output_path=tmp_path / "provisional-observations.jsonl",
        now=lambda: "2026-08-07T16:00:00Z",
    )
    assert len(observations) == 72
    assert len(calls) == 96
    assert {observation.evidence_tier for observation in observations} == {EVIDENCE_TIER}

    schema = json.loads(OBS_SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    persisted = [
        json.loads(line)
        for line in (tmp_path / "provisional-observations.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    for item in persisted:
        validator.validate(item)
        assert item["evidence_tier"] == EVIDENCE_TIER
        assert "human_label" not in item
        assert "task" not in item
        assert "candidate_output" not in item

    report = evaluate_provisional_calibration(
        cases,
        packet,
        private_map,
        panel_labels,
        observations,
        panel,
        empirical,
        base,
    )
    assert report["evidence_tier"] == EVIDENCE_TIER
    assert report["provisional_evidence_complete"] is True
    assert report["metrics_against_reference_control"]["exact_status_accuracy"] == 1.0
    assert len(report["metrics_by_verifier_route_against_reference_control"]) == 3
    assert report["machine_panel"]["majority_coverage_rate"] == 1.0
    assert report["machine_panel"]["reference_control_exact_agreement_rate"] == 1.0
    assert report["machine_panel"]["human_ground_truth"] is False
    assert report["authority"]["quality_claims_authorized"] is False
    assert report["authority"]["routing_authority"] is False
    assert report["authority"]["human_review_tier_replaced"] is False


def test_provisional_collection_refuses_incomplete_machine_panel_before_provider_spend(tmp_path: Path) -> None:
    panel, empirical, base, cases, packet, private_map = context()
    route = panel.panel_routes[0]
    item = packet["items"][0]
    label = MachinePanelLabel(
        review_item_id=item["review_item_id"],
        judge_provider_family=route.provider_family,
        judge_model=route.model,
        judge_reasoning=route.reasoning,
        observed_at="2026-08-07T15:00:00Z",
        rubric_version=panel.rubric_version,
        duration_ms=1.0,
        input_tokens=1,
        output_tokens=1,
        decision=cases[0].gold,
    )
    calls: list[dict] = []
    with pytest.raises(CalibrationError, match="coverage must be complete"):
        collect_provisional_observations(
            cases,
            packet,
            [label],
            panel,
            empirical,
            connections_for_routes(empirical.verifier_routes, cases, calls),
            collector_revision="abcdef1234567890",
            output_path=tmp_path / "observations.jsonl",
            now=lambda: "2026-08-07T16:00:00Z",
        )
    assert calls == []


def test_machine_panel_collection_refuses_missing_provider_usage(tmp_path: Path) -> None:
    panel, empirical, base, cases, packet, private_map = context()
    calls: list[dict] = []
    google_route = next(route for route in panel.panel_routes if route.provider_family == "google")
    with pytest.raises(CalibrationError, match="required provider usage"):
        collect_machine_panel_labels(
            packet,
            replace(panel, panel_routes=(google_route,)),
            empirical,
            connections_for_routes((google_route,), cases, calls, include_usage=False),
            output_path=tmp_path / "labels.jsonl",
            now=lambda: "2026-08-07T15:00:00Z",
        )
    assert len(calls) == 1
    assert not (tmp_path / "labels.jsonl").exists()
