from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from teo_reference.benchmark_conclusion import (
    advance_benchmark_conclusion,
    build_benchmark_conclusion,
    build_benchmark_conclusion_verification,
)
from teo_reference.benchmark_lab import (
    BenchmarkExperimentManifest,
    BenchmarkExperimentReport,
    evaluate_benchmark,
    load_benchmark_fixtures,
    load_route_outcomes,
)
from teo_reference.cost_attribution import RouteCostAttributionRecord
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.route_outcome import RouteOutcomeRecord
from teo_reference.shadow_evaluation import (
    JsonlShadowRecommendationSink,
    ShadowEvaluationInputRecord,
    ShadowRecommendationHandoffRecord,
    ShadowRecommendationRecord,
    advance_shadow_recommendation,
    build_shadow_evaluation_input,
    build_shadow_recommendation_verification,
    evaluate_shadow_routes,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "reference" / "datasets" / "benchmark-lab"
FIXTURE_PATH = DATASET_ROOT / "benchmark-fixtures-v1.jsonl"
OUTCOME_PATH = DATASET_ROOT / "route-outcomes-v1.jsonl"
MANIFEST_PATH = DATASET_ROOT / "benchmark-experiment-v1.json"


def canonical_hash(payload: dict) -> str:
    data = dict(payload)
    data.pop("integrity_sha256", None)
    encoded = json.dumps(
        data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def manifest() -> BenchmarkExperimentManifest:
    return BenchmarkExperimentManifest.from_dict(
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8")),
        repo_root=REPO_ROOT,
    )


def fixtures():
    return load_benchmark_fixtures(FIXTURE_PATH, repo_root=REPO_ROOT)


def outcomes():
    return load_route_outcomes(OUTCOME_PATH, repo_root=REPO_ROOT)


def base_report(route_outcomes=None) -> BenchmarkExperimentReport:
    return evaluate_benchmark(
        manifest(),
        fixtures(),
        route_outcomes or outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T20:20:00+00:00",
    )


def with_measured_disagreement(report: BenchmarkExperimentReport) -> BenchmarkExperimentReport:
    payload = report.to_dict()
    payload["verifier_disagreement"] = {
        "status": "measured",
        "panel_plan_id": "shadow-test-panel",
        "panel_plan_version": "1",
        "observation_count": 16,
        "verifiable_trials": 8,
        "unanimous_trials": 6,
        "disagreement_trials": 2,
        "disagreement_rate": 0.25,
        "status_disagreement_trials": 2,
        "criterion_disagreement_trials": 2,
        "human_reason_disagreement_trials": 2,
        "candidate_summaries": [
            {
                "candidate_id": "candidate-google-flash-lite",
                "panel_size": 2,
                "verifiable_trials": 4,
                "observation_count": 8,
                "unanimous_trials": 4,
                "disagreement_trials": 0,
                "disagreement_rate": 0.0,
                "status_disagreement_trials": 0,
                "criterion_disagreement_trials": 0,
                "human_reason_disagreement_trials": 0,
            },
            {
                "candidate_id": "candidate-openai-luna",
                "panel_size": 2,
                "verifiable_trials": 4,
                "observation_count": 8,
                "unanimous_trials": 2,
                "disagreement_trials": 2,
                "disagreement_rate": 0.5,
                "status_disagreement_trials": 2,
                "criterion_disagreement_trials": 2,
                "human_reason_disagreement_trials": 2,
            },
        ],
        "decision_use": "diagnostic_only",
        "canonical_runtime_verifier_override": False,
    }
    payload["integrity_sha256"] = canonical_hash(payload)
    return BenchmarkExperimentReport.from_dict(payload, repo_root=REPO_ROOT)


def shadow_candidate_report() -> BenchmarkExperimentReport:
    payload = with_measured_disagreement(base_report()).to_dict()
    candidate = next(
        item
        for item in payload["candidate_metrics"]
        if item["candidate_id"] == "candidate-google-flash-lite"
    )
    candidate["primary_completed"] = candidate["completed"]
    candidate["fallback_assisted_completed"] = 0
    candidate["verified_completion_rate"] = 1.0
    candidate["primary_verified_completion_rate"] = 1.0
    candidate["fallback_assistance_rate"] = 0.0
    candidate["retry_assistance_rate"] = 0.0
    payload["integrity_sha256"] = canonical_hash(payload)
    return BenchmarkExperimentReport.from_dict(payload, repo_root=REPO_ROOT)


def analyst_actor() -> dict:
    return {
        "actor_type": "specialist",
        "actor_id": "orchestration-evaluation-analyst",
        "provider_family": "openai",
        "model": "gpt-5.6-sol",
    }


def independent_shadow_verifier() -> dict:
    return {
        "actor_type": "specialist",
        "actor_id": "independent-shadow-reviewer",
        "provider_family": "google",
        "model": "gemini-3.6-flash",
    }


def passing_shadow_checks() -> dict:
    return {
        "source_binding": "pass",
        "evidence_sufficiency": "pass",
        "uncertainty_preserved": "pass",
        "authority_boundary_preserved": "pass",
        "cost_not_primary_authority": "pass",
        "unsupported_causality_absent": "pass",
    }


def consequential_chain(report: BenchmarkExperimentReport):
    conclusion = build_benchmark_conclusion(
        report,
        conclusion_kind="comparative_claim",
        consequence_level="consequential",
        statement="Controlled comparative evidence supports review under preserved uncertainty.",
        evidence_refs=["candidate_metrics", "verifier_disagreement", "provenance.source_outcome_ids"],
        originator=analyst_actor(),
        repo_root=REPO_ROOT,
        created_at="2026-08-10T20:21:00+00:00",
    )
    verification = build_benchmark_conclusion_verification(
        conclusion,
        verifier={
            "actor_type": "specialist",
            "actor_id": "independent-benchmark-reviewer",
            "provider_family": "anthropic",
            "model": "claude-sonnet-5",
        },
        decision="verified",
        checks={
            "evidence_support": "pass",
            "uncertainty_preserved": "pass",
            "authority_boundary_preserved": "pass",
            "unsupported_causality_absent": "pass",
        },
        human_reason="none",
        evidence=["benchmark report and disagreement evidence independently challenged"],
        repo_root=REPO_ROOT,
        verified_at="2026-08-10T20:22:00+00:00",
    )
    handoff = advance_benchmark_conclusion(
        conclusion,
        verification=verification,
        repo_root=REPO_ROOT,
        created_at="2026-08-10T20:23:00+00:00",
    )
    return conclusion, verification, handoff


def build_input(report=None, route_outcomes=None, *, consequence_level="routine", dimensions=None, costs=()):
    report = report or with_measured_disagreement(base_report())
    route_outcomes = route_outcomes or outcomes()
    kwargs = {}
    if consequence_level == "consequential":
        conclusion, verification, handoff = consequential_chain(report)
        kwargs = {
            "conclusion": conclusion,
            "conclusion_verification": verification,
            "conclusion_handoff": handoff,
        }
    record = build_shadow_evaluation_input(
        manifest(),
        report,
        route_outcomes,
        candidate_id="candidate-google-flash-lite",
        baseline_candidate_id="candidate-openai-luna",
        analyst_actor=analyst_actor(),
        question="Should the Google candidate advance as a shadow route candidate?",
        consequence_level=consequence_level,
        decision_dimensions=dimensions or [
            "verified_quality",
            "primary_reliability",
            "retry_dependence",
            "fallback_dependence",
            "verifier_disagreement",
        ],
        cost_attributions=costs,
        repo_root=REPO_ROOT,
        created_at="2026-08-10T20:24:00+00:00",
        **kwargs,
    )
    return record, kwargs


def known_cost_record(outcome: RouteOutcomeRecord, amount: str) -> RouteCostAttributionRecord:
    source = outcome.to_dict()
    primary = source["primary_route"]
    verifier = primary["verifier"]
    payload = {
        "cost_attribution_version": "1",
        "record_type": "route_cost_attribution",
        "attribution_id": f"cost-{hashlib.sha256((source['outcome_id'] + amount).encode()).hexdigest()[:20]}",
        "attributed_at": "2026-08-10T20:25:00+00:00",
        "outcome_id": source["outcome_id"],
        "outcome_integrity_sha256": source["integrity_sha256"],
        "currency": "USD",
        "status": "known",
        "primary_route": {
            "dispatch_id": primary["dispatch_id"],
            "role": "primary",
            "status": "known",
            "attempts": [],
            "amount": amount,
            "issues": [],
        },
        "fallback_route": None,
        "verifier": {
            "dispatch_id": source["provenance"]["verification_dispatch_id"],
            "provider_family": verifier["provider_family"],
            "model": verifier["model"],
            "recorded_at": source["recorded_at"],
            "billable_surface": "test_api_surface",
            "additional_billable_events_status": "none",
            "status": "known",
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cached_input_tokens": 0,
                "cache_creation_input_tokens": 0,
                "reasoning_output_tokens": 0,
                "tool_tokens": 0,
                "total_tokens": 0,
            },
            "pricing_evidence_id": "pricing-test-api",
            "components": {
                "uncached_input": None,
                "cached_input": None,
                "cache_write_input": None,
                "output": None,
            },
            "amount": "0",
            "issues": [],
        },
        "total_amount": amount,
        "pricing_evidence_ids": ["pricing-test-api"],
        "issues": [],
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = canonical_hash(payload)
    return RouteCostAttributionRecord.from_dict(payload, repo_root=REPO_ROOT)


def all_known_costs(candidate_amount="1", baseline_amount="2"):
    records = []
    bindings = manifest().to_dict()["bindings"]
    candidate_by_outcome = {item["outcome_id"]: item["candidate_id"] for item in bindings}
    for outcome in outcomes():
        amount = (
            candidate_amount
            if candidate_by_outcome[outcome.to_dict()["outcome_id"]] == "candidate-google-flash-lite"
            else baseline_amount
        )
        records.append(known_cost_record(outcome, amount))
    return records


def test_shadow_input_binds_exact_evidence_and_denies_authority() -> None:
    evaluation, _ = build_input()
    data = evaluation.to_dict()
    assert data["specialist_id"] == "orchestration-evaluation-analyst"
    assert data["analyst_actor"]["provider_family"] == "openai"
    assert data["decision_owner"] == "mission_control_or_maintainer_review"
    assert data["policy_write_authority"] is False
    assert data["live_routing_authority"] is False
    assert data["qualified_human_approval_satisfied"] is False
    assert {item["record_type"] for item in data["evidence_refs"]} >= {
        "benchmark_experiment",
        "benchmark_report",
        "route_outcome",
    }


def test_shadow_input_refuses_same_candidate_and_baseline() -> None:
    with pytest.raises(ProviderAdapterContractError, match="must be different"):
        build_shadow_evaluation_input(
            manifest(),
            with_measured_disagreement(base_report()),
            outcomes(),
            candidate_id="candidate-google-flash-lite",
            baseline_candidate_id="candidate-google-flash-lite",
            analyst_actor=analyst_actor(),
            question="invalid",
            consequence_level="routine",
            decision_dimensions=["verified_quality"],
            repo_root=REPO_ROOT,
        )


def test_cost_dimension_requires_every_candidate_and_baseline_cost_record() -> None:
    with pytest.raises(ProviderAdapterContractError, match="requires attribution records"):
        build_input(dimensions=["verified_quality", "source_backed_cost"], costs=())


def test_consequential_shadow_input_requires_complete_challenged_conclusion_chain() -> None:
    report = shadow_candidate_report()
    with pytest.raises(ProviderAdapterContractError, match="complete benchmark conclusion challenge chain"):
        build_shadow_evaluation_input(
            manifest(),
            report,
            outcomes(),
            candidate_id="candidate-google-flash-lite",
            baseline_candidate_id="candidate-openai-luna",
            analyst_actor=analyst_actor(),
            question="consequential comparison",
            consequence_level="consequential",
            decision_dimensions=["verified_quality", "verifier_disagreement"],
            repo_root=REPO_ROOT,
        )


def test_quality_gain_with_worse_fallback_dependence_does_not_become_change_candidate() -> None:
    report = with_measured_disagreement(base_report())
    evaluation, kwargs = build_input(report)
    recommendation = evaluate_shadow_routes(
        evaluation,
        manifest(),
        report,
        outcomes(),
        repo_root=REPO_ROOT,
        **kwargs,
    ).to_dict()
    assert recommendation["comparison"]["verified_completion_rate_delta"] > 0
    assert recommendation["comparison"]["fallback_assistance_rate_delta"] > 0
    assert recommendation["disposition"] == "NO_CHANGE_JUSTIFIED"
    assert recommendation["proposed_change"] is None


def test_controlled_quality_improvement_can_only_be_shadow_change_candidate() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation,
        manifest(),
        report,
        outcomes(),
        repo_root=REPO_ROOT,
        **kwargs,
    ).to_dict()
    assert recommendation["disposition"] == "SHADOW_CHANGE_CANDIDATE"
    assert recommendation["proposed_change"]["status"] == "shadow_only_not_authorized"
    assert recommendation["authority"] == {
        "policy_write_authority": False,
        "live_routing_authority": False,
        "live_scope_change_authority": False,
        "effective_risk_lowering_authority": False,
        "capability_bypass_authority": False,
        "verifier_bypass_authority": False,
        "preview_acceptance_authority": False,
        "provider_access_change_authority": False,
        "qualified_human_approval_satisfied": False,
    }


def test_lower_cost_alone_never_creates_shadow_change_candidate() -> None:
    report_payload = with_measured_disagreement(base_report()).to_dict()
    google = next(item for item in report_payload["candidate_metrics"] if item["candidate_id"] == "candidate-google-flash-lite")
    openai = next(item for item in report_payload["candidate_metrics"] if item["candidate_id"] == "candidate-openai-luna")
    for field in (
        "verified_completion_rate",
        "primary_verified_completion_rate",
        "fallback_assistance_rate",
        "retry_assistance_rate",
        "mean_total_duration_ms",
    ):
        google[field] = openai[field]
    report_payload["integrity_sha256"] = canonical_hash(report_payload)
    report = BenchmarkExperimentReport.from_dict(report_payload, repo_root=REPO_ROOT)
    costs = all_known_costs(candidate_amount="1", baseline_amount="2")
    evaluation, kwargs = build_input(
        report,
        dimensions=["verified_quality", "source_backed_cost"],
        costs=costs,
    )
    recommendation = evaluate_shadow_routes(
        evaluation,
        manifest(),
        report,
        outcomes(),
        cost_attributions=costs,
        repo_root=REPO_ROOT,
        **kwargs,
    ).to_dict()
    assert recommendation["cost_evidence"]["status"] == "known"
    assert float(recommendation["cost_evidence"]["delta_amount"]) < 0
    assert recommendation["disposition"] == "NO_CHANGE_JUSTIFIED"


def test_candidate_regression_signal_preempts_change_candidate() -> None:
    payload = shadow_candidate_report().to_dict()
    payload["regression_signals"] = [
        {
            "candidate_id": "candidate-google-flash-lite",
            "metric": "verified_completion_rate",
            "baseline_candidate_id": "candidate-openai-luna",
            "delta": -0.1,
            "classification": "descriptive_drop",
        }
    ]
    payload["integrity_sha256"] = canonical_hash(payload)
    report = BenchmarkExperimentReport.from_dict(payload, repo_root=REPO_ROOT)
    evaluation, kwargs = build_input(report)
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    ).to_dict()
    assert recommendation["disposition"] == "REGRESSION_INVESTIGATION"
    assert recommendation["proposed_change"] is None


def test_incomparable_benchmark_returns_insufficient_evidence() -> None:
    payload = with_measured_disagreement(base_report()).to_dict()
    payload["comparability_status"] = "failed"
    payload["comparability_issues"] = ["intentional_test_incomparability"]
    payload["evidence_sufficiency"] = "insufficient"
    payload["integrity_sha256"] = canonical_hash(payload)
    report = BenchmarkExperimentReport.from_dict(payload, repo_root=REPO_ROOT)
    evaluation, kwargs = build_input(report)
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    ).to_dict()
    assert recommendation["disposition"] == "INSUFFICIENT_EVIDENCE"
    assert recommendation["evidence_sufficiency"] == "insufficient"


def test_pending_human_or_missing_verification_surfaces_policy_control_concern() -> None:
    modified = outcomes()
    first = modified[0].to_dict()
    first["final_disposition"] = "awaiting_human"
    first["verification_status"] = "needs_human"
    first["human_approval_required"] = True
    first["integrity_sha256"] = canonical_hash(first)
    modified[0] = RouteOutcomeRecord.from_dict(first, repo_root=REPO_ROOT)
    report = with_measured_disagreement(base_report(modified))
    evaluation, kwargs = build_input(report, modified)
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, modified, repo_root=REPO_ROOT, **kwargs
    ).to_dict()
    assert recommendation["disposition"] == "POLICY_OR_CONTROL_CONCERN"
    assert "control_disposition:awaiting_human" in recommendation["contradictory_evidence"]


def test_shadow_evaluation_refuses_evidence_set_mutation() -> None:
    report = with_measured_disagreement(base_report())
    evaluation, kwargs = build_input(report)
    raw = evaluation.to_dict()
    raw["evidence_refs"] = raw["evidence_refs"][:-1]
    raw["integrity_sha256"] = canonical_hash(raw)
    mutated = ShadowEvaluationInputRecord.from_dict(raw, repo_root=REPO_ROOT)
    with pytest.raises(ProviderAdapterContractError, match="exact supplied evidence set"):
        evaluate_shadow_routes(
            mutated, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
        )


def test_shadow_recommendation_integrity_and_authority_mutations_fail_closed() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    raw = recommendation.to_dict()
    raw["authority"]["policy_write_authority"] = True
    raw["integrity_sha256"] = canonical_hash(raw)
    with pytest.raises(ProviderAdapterContractError):
        ShadowRecommendationRecord.from_dict(raw, repo_root=REPO_ROOT)


def test_shadow_recommendation_requires_provider_diverse_independent_challenge() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    with pytest.raises(ProviderAdapterContractError, match="provider-diverse"):
        build_shadow_recommendation_verification(
            evaluation,
            recommendation,
            verifier={
                "actor_type": "specialist",
                "actor_id": "different-openai-reviewer",
                "provider_family": "openai",
                "model": "gpt-5.6-luna",
            },
            decision="verified",
            checks=passing_shadow_checks(),
            human_reason="none",
            evidence=["independent challenge"],
            repo_root=REPO_ROOT,
        )


def test_verified_shadow_recommendation_advances_only_to_mission_control_review() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    verification = build_shadow_recommendation_verification(
        evaluation,
        recommendation,
        verifier=independent_shadow_verifier(),
        decision="verified",
        checks=passing_shadow_checks(),
        human_reason="none",
        evidence=["source bindings, uncertainty, and authority boundaries independently challenged"],
        repo_root=REPO_ROOT,
        verified_at="2026-08-10T20:26:00+00:00",
    )
    handoff = advance_shadow_recommendation(
        recommendation,
        verification,
        repo_root=REPO_ROOT,
        created_at="2026-08-10T20:27:00+00:00",
    ).to_dict()
    assert handoff["status"] == "ready_for_review"
    assert handoff["destination"] == "mission_control_or_maintainer_review"
    assert handoff["independent_verification_performed"] is True
    assert handoff["policy_write_authority"] is False
    assert handoff["live_routing_authority"] is False
    assert handoff["qualified_human_approval_satisfied"] is False


def test_rejected_shadow_challenge_cannot_be_ready_for_review() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    checks = passing_shadow_checks()
    checks["evidence_sufficiency"] = "fail"
    verification = build_shadow_recommendation_verification(
        evaluation,
        recommendation,
        verifier=independent_shadow_verifier(),
        decision="rejected",
        checks=checks,
        human_reason="none",
        evidence=["evidence challenge rejected recommendation"],
        repo_root=REPO_ROOT,
    )
    handoff = advance_shadow_recommendation(
        recommendation, verification, repo_root=REPO_ROOT
    ).to_dict()
    assert handoff["status"] == "rejected"
    assert handoff["policy_write_authority"] is False


def test_shadow_handoff_integrity_fails_closed_on_authority_mutation() -> None:
    report = shadow_candidate_report()
    evaluation, kwargs = build_input(report, consequence_level="consequential")
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    verification = build_shadow_recommendation_verification(
        evaluation,
        recommendation,
        verifier=independent_shadow_verifier(),
        decision="verified",
        checks=passing_shadow_checks(),
        human_reason="none",
        evidence=["verified"],
        repo_root=REPO_ROOT,
    )
    raw = advance_shadow_recommendation(
        recommendation, verification, repo_root=REPO_ROOT
    ).to_dict()
    raw["live_routing_authority"] = True
    raw["integrity_sha256"] = canonical_hash(raw)
    with pytest.raises(ProviderAdapterContractError):
        ShadowRecommendationHandoffRecord.from_dict(raw, repo_root=REPO_ROOT)


def test_shadow_recommendation_jsonl_sink_revalidates_persistence(tmp_path: Path) -> None:
    report = with_measured_disagreement(base_report())
    evaluation, kwargs = build_input(report)
    recommendation = evaluate_shadow_routes(
        evaluation, manifest(), report, outcomes(), repo_root=REPO_ROOT, **kwargs
    )
    sink = JsonlShadowRecommendationSink(
        tmp_path / "shadow-recommendations.jsonl", repo_root=REPO_ROOT
    )
    sink.append(recommendation)
    loaded = sink.read_all()
    assert len(loaded) == 1
    assert loaded[0].to_dict() == recommendation.to_dict()
