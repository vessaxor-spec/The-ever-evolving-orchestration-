from __future__ import annotations

from pathlib import Path

from teo_reference.verifier_calibration import load_calibration_policy, load_gold_cases
from teo_reference.verifier_calibration_empirical import (
    EmpiricalCalibrationObservation,
    HumanCalibrationLabel,
    load_empirical_policy,
    validate_empirical_policy_against_base,
)
from teo_reference.verifier_calibration_empirical_report import build_empirical_report


REPO_ROOT = Path(__file__).resolve().parents[1]


def decision_dict(decision) -> dict:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def context():
    empirical = load_empirical_policy(
        REPO_ROOT / "policy/verification/verifier-calibration-empirical.yaml"
    )
    base = load_calibration_policy(REPO_ROOT / empirical.base_policy_path)
    validate_empirical_policy_against_base(empirical, base)
    cases = load_gold_cases(REPO_ROOT / empirical.control_corpus_path, policy=base)
    return empirical, base, cases


def labels_for(cases):
    labels = []
    for case in cases:
        for reviewer in ("reviewer-a", "reviewer-b"):
            labels.append(
                HumanCalibrationLabel.from_dict(
                    {
                        "case_id": case.case_id,
                        "reviewer_id": reviewer,
                        "reviewer_role": "reviewer",
                        "reviewed_at": "2026-08-07T14:00:00Z",
                        "rubric_version": case.rubric_version,
                        "observations_blinded": True,
                        "reference_control_labels_blinded": True,
                        "source_packet_id": "packet-test-report",
                        "decision": decision_dict(case.gold),
                    }
                )
            )
    return labels


def observations_for(cases, empirical, *, providers=None):
    observations = []
    for route in empirical.verifier_routes:
        if providers is not None and route.provider_family not in providers:
            continue
        for case in cases:
            for run_number in range(1, 4):
                observations.append(
                    EmpiricalCalibrationObservation(
                        case_id=case.case_id,
                        verifier_provider_family=route.provider_family,
                        verifier_model=route.model,
                        verifier_reasoning=route.reasoning,
                        run_id=f"r{run_number:02d}",
                        observed_at="2026-08-07T15:00:00Z",
                        rubric_version=empirical.rubric_version,
                        verification_policy_version=empirical.verification_policy_version,
                        empirical_policy_version=empirical.version,
                        collector_revision="abcdef1234567890",
                        duration_ms=100.0 + run_number,
                        input_tokens=10,
                        output_tokens=5,
                        decision=case.gold,
                    )
                )
    return observations


def test_final_empirical_report_exposes_each_verifier_route_separately() -> None:
    empirical, base, cases = context()
    report = build_empirical_report(
        cases,
        labels_for(cases),
        observations_for(cases, empirical),
        empirical,
        base,
    )

    expected_routes = {route.route_id for route in empirical.verifier_routes}
    assert set(report["metrics_by_verifier_route"]) == expected_routes
    assert report["route_specific_evidence_complete"] is True
    assert report["evidence_readiness"]["data_requirements_met"] is True

    for metrics in report["metrics_by_verifier_route"].values():
        assert metrics["total_observations"] == 24
        assert metrics["exact_status_accuracy"] == 1.0
        assert metrics["false_pass_opportunities"] == 21
        assert metrics["false_fail_opportunities"] == 3
        assert metrics["human_required_opportunities"] == 6
        assert metrics["non_human_opportunities"] == 18
        assert metrics["by_collection_path"]["calibration_direct"]["observations"] == 24
        assert "by_execution_path" not in metrics

    assert report["authority"]["quality_claims_authorized"] is False
    assert report["authority"]["scope_expansion_authorized"] is False
    assert report["authority"]["routing_authority"] is False
    assert report["authority"]["automatic_route_update"] is False


def test_missing_verifier_route_cannot_be_hidden_by_aggregate_metrics() -> None:
    empirical, base, cases = context()
    report = build_empirical_report(
        cases,
        labels_for(cases),
        observations_for(cases, empirical, providers={"google", "anthropic"}),
        empirical,
        base,
    )

    assert len(report["metrics_by_verifier_route"]) == 2
    assert report["route_specific_evidence_complete"] is False
    assert report["evidence_readiness"]["data_requirements_met"] is False
    assert report["authority"]["quality_claims_authorized"] is False
