from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from teo_reference.benchmark_conclusion import (
    BenchmarkConclusionHandoffRecord,
    BenchmarkConclusionRecord,
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
from teo_reference.provider_adapter import ProviderAdapterContractError

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


def base_report() -> BenchmarkExperimentReport:
    return evaluate_benchmark(
        manifest(),
        load_benchmark_fixtures(FIXTURE_PATH, repo_root=REPO_ROOT),
        load_route_outcomes(OUTCOME_PATH, repo_root=REPO_ROOT),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T19:20:00+00:00",
    )


def measured_report() -> BenchmarkExperimentReport:
    payload = base_report().to_dict()
    payload["verifier_disagreement"] = {
        "status": "measured",
        "panel_plan_id": "conclusion-test-panel",
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


def originator() -> dict:
    return {
        "actor_type": "specialist",
        "actor_id": "orchestration-evaluation-analyst",
        "provider_family": "openai",
        "model": "gpt-5.6-sol",
    }


def independent_verifier() -> dict:
    return {
        "actor_type": "specialist",
        "actor_id": "independent-benchmark-reviewer",
        "provider_family": "anthropic",
        "model": "claude-sonnet-5",
    }


def passing_checks() -> dict:
    return {
        "evidence_support": "pass",
        "uncertainty_preserved": "pass",
        "authority_boundary_preserved": "pass",
        "unsupported_causality_absent": "pass",
    }


def consequential_conclusion() -> BenchmarkConclusionRecord:
    return build_benchmark_conclusion(
        measured_report(),
        conclusion_kind="comparative_claim",
        consequence_level="consequential",
        statement=(
            "The controlled evidence supports a comparative finding, subject to the report's stated uncertainty and disagreement evidence."
        ),
        evidence_refs=[
            "candidate_metrics",
            "verifier_disagreement",
            "provenance.source_outcome_ids",
        ],
        originator=originator(),
        repo_root=REPO_ROOT,
        created_at="2026-08-10T19:25:00+00:00",
    )


def test_consequential_comparative_claim_requires_measured_disagreement() -> None:
    with pytest.raises(ProviderAdapterContractError, match="measured multi-verifier disagreement"):
        build_benchmark_conclusion(
            base_report(),
            conclusion_kind="comparative_claim",
            consequence_level="consequential",
            statement="Candidate evidence appears materially different.",
            evidence_refs=["candidate_metrics"],
            originator=originator(),
            repo_root=REPO_ROOT,
        )


def test_consequential_conclusion_cannot_advance_without_independent_verification() -> None:
    conclusion = consequential_conclusion()
    with pytest.raises(ProviderAdapterContractError, match="requires independent verification"):
        advance_benchmark_conclusion(conclusion, repo_root=REPO_ROOT)


def test_model_originated_conclusion_requires_provider_diverse_verification() -> None:
    conclusion = consequential_conclusion()
    same_provider = {
        "actor_type": "specialist",
        "actor_id": "different-openai-reviewer",
        "provider_family": "openai",
        "model": "gpt-5.6-luna",
    }
    with pytest.raises(ProviderAdapterContractError, match="provider-diverse verification"):
        build_benchmark_conclusion_verification(
            conclusion,
            verifier=same_provider,
            decision="verified",
            checks=passing_checks(),
            human_reason="none",
            evidence=["independent review of benchmark report"],
            repo_root=REPO_ROOT,
        )


def test_verified_consequential_conclusion_advances_only_to_review_without_policy_authority() -> None:
    conclusion = consequential_conclusion()
    verification = build_benchmark_conclusion_verification(
        conclusion,
        verifier=independent_verifier(),
        decision="verified",
        checks=passing_checks(),
        human_reason="none",
        evidence=[
            "report integrity verified",
            "comparability and disagreement evidence independently challenged",
        ],
        repo_root=REPO_ROOT,
        verified_at="2026-08-10T19:30:00+00:00",
    )
    handoff = advance_benchmark_conclusion(
        conclusion,
        verification=verification,
        repo_root=REPO_ROOT,
        created_at="2026-08-10T19:31:00+00:00",
    ).to_dict()

    assert handoff["status"] == "ready_for_review"
    assert handoff["destination"] == "mission_control_or_maintainer_review"
    assert handoff["independent_verification_performed"] is True
    assert handoff["policy_write_authority"] is False
    assert handoff["qualified_human_approval_satisfied"] is False
    assert handoff["verification_id"] == verification.to_dict()["verification_id"]


def test_rejected_independent_verification_blocks_review_advancement() -> None:
    conclusion = consequential_conclusion()
    checks = passing_checks()
    checks["evidence_support"] = "fail"
    verification = build_benchmark_conclusion_verification(
        conclusion,
        verifier=independent_verifier(),
        decision="rejected",
        checks=checks,
        human_reason="none",
        evidence=["claimed comparison exceeded evidence support"],
        repo_root=REPO_ROOT,
    )
    handoff = advance_benchmark_conclusion(
        conclusion,
        verification=verification,
        repo_root=REPO_ROOT,
    ).to_dict()
    assert handoff["status"] == "rejected"
    assert handoff["policy_write_authority"] is False


def test_routine_descriptive_conclusion_can_handoff_without_creating_approval_authority() -> None:
    conclusion = build_benchmark_conclusion(
        base_report(),
        conclusion_kind="descriptive_summary",
        consequence_level="routine",
        statement="The benchmark report contains controlled descriptive metrics.",
        evidence_refs=["candidate_metrics"],
        originator={
            "actor_type": "system",
            "actor_id": "benchmark-report-summarizer",
            "provider_family": None,
            "model": None,
        },
        repo_root=REPO_ROOT,
    )
    handoff = advance_benchmark_conclusion(
        conclusion,
        repo_root=REPO_ROOT,
    ).to_dict()
    assert handoff["status"] == "ready_for_review"
    assert handoff["independent_verification_performed"] is False
    assert handoff["qualified_human_approval_satisfied"] is False


def test_conclusion_and_handoff_integrity_fail_closed_on_mutation() -> None:
    conclusion = consequential_conclusion()
    raw = conclusion.to_dict()
    raw["statement"] = "mutated statement"
    with pytest.raises(ProviderAdapterContractError, match="integrity hash"):
        BenchmarkConclusionRecord.from_dict(raw, repo_root=REPO_ROOT)

    verification = build_benchmark_conclusion_verification(
        conclusion,
        verifier=independent_verifier(),
        decision="verified",
        checks=passing_checks(),
        human_reason="none",
        evidence=["verified"],
        repo_root=REPO_ROOT,
    )
    handoff = advance_benchmark_conclusion(
        conclusion,
        verification=verification,
        repo_root=REPO_ROOT,
    ).to_dict()
    handoff["policy_write_authority"] = True
    with pytest.raises(ProviderAdapterContractError):
        BenchmarkConclusionHandoffRecord.from_dict(handoff, repo_root=REPO_ROOT)
