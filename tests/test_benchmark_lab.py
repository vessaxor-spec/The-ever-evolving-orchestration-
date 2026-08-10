from __future__ import annotations

import json
from pathlib import Path

import pytest

from teo_reference.benchmark_lab import (
    BenchmarkExperimentManifest,
    BenchmarkExperimentReport,
    BenchmarkFixtureRecord,
    JsonlBenchmarkReportSink,
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


def manifest() -> BenchmarkExperimentManifest:
    return BenchmarkExperimentManifest.from_dict(
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8")),
        repo_root=REPO_ROOT,
    )


def fixtures():
    return load_benchmark_fixtures(FIXTURE_PATH, repo_root=REPO_ROOT)


def outcomes():
    return load_route_outcomes(OUTCOME_PATH, repo_root=REPO_ROOT)


def report():
    return evaluate_benchmark(
        manifest(),
        fixtures(),
        outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T16:30:00+00:00",
    )


def metrics_by_candidate(payload: dict):
    return {
        item["candidate_id"]: item
        for item in payload["candidate_metrics"]
    }


def test_foundation_dataset_is_reproducible_balanced_and_comparable() -> None:
    result = report().to_dict()

    assert result["comparability_status"] == "passed"
    assert result["comparability_issues"] == []
    assert result["evidence_sufficiency"] == "descriptive_only"
    assert result["fixture_count"] == 2
    assert result["trials_per_fixture"] == 2
    assert len(result["provenance"]["source_outcome_ids"]) == 8
    assert result["verifier_disagreement"]["status"] == "not_measured"

    metrics = metrics_by_candidate(result)
    google = metrics["candidate-google-flash-lite"]
    openai = metrics["candidate-openai-luna"]

    assert google["trials"] == 4
    assert google["completed"] == 4
    assert google["primary_completed"] == 3
    assert google["fallback_assisted_completed"] == 1
    assert google["fallback_assistance_rate"] == 0.25
    assert google["retry_assistance_rate"] == 0.0
    assert google["verified_completion_rate"] == 1.0
    assert google["primary_verified_completion_rate"] == 0.75
    assert google["pass_all_trials_fixture_rate"] == 1.0
    assert google["mean_total_duration_ms"] == 125.0
    assert google["token_observation_status"] == "complete"
    assert google["total_tokens_observed"] == 47

    assert openai["trials"] == 4
    assert openai["completed"] == 3
    assert openai["primary_completed"] == 3
    assert openai["verification_failed"] == 1
    assert openai["retry_assisted_completed"] == 1
    assert openai["retry_assistance_rate"] == 0.25
    assert openai["verified_completion_rate"] == 0.75
    assert openai["primary_verified_completion_rate"] == 0.75
    assert openai["pass_any_trial_fixture_rate"] == 1.0
    assert openai["pass_all_trials_fixture_rate"] == 0.5
    assert openai["mean_total_duration_ms"] == 101.25
    assert openai["total_tokens_observed"] == 39

    assert result["regression_signals"] == []


def test_fixed_repeated_trials_preserve_primary_retry_and_fallback_distinctions() -> None:
    result = report().to_dict()
    metrics = metrics_by_candidate(result)

    assert metrics["candidate-google-flash-lite"]["fallback_assisted_completed"] == 1
    assert metrics["candidate-google-flash-lite"]["primary_completed"] == 3
    assert metrics["candidate-openai-luna"]["retry_assisted_completed"] == 1

    assert (
        metrics["candidate-google-flash-lite"]["verified_completion_rate"]
        > metrics["candidate-google-flash-lite"]["primary_verified_completion_rate"]
    )


def test_executor_only_manifest_rejects_non_executor_configuration_drift() -> None:
    raw = manifest().to_dict()
    raw["candidates"][1]["verifier_model"] = "gpt-5.6-sol"

    with pytest.raises(ProviderAdapterContractError, match="non-executor field verifier_model"):
        BenchmarkExperimentManifest.from_dict(raw, repo_root=REPO_ROOT)


def test_missing_trial_is_not_silently_dropped() -> None:
    raw = manifest().to_dict()
    raw["bindings"] = raw["bindings"][:-1]
    broken = BenchmarkExperimentManifest.from_dict(raw, repo_root=REPO_ROOT)

    result = evaluate_benchmark(
        broken,
        fixtures(),
        outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T16:31:00+00:00",
    ).to_dict()

    assert result["comparability_status"] == "failed"
    assert result["evidence_sufficiency"] == "insufficient"
    assert result["candidate_metrics"] == []
    assert any(item.startswith("missing_trials:candidate-openai-luna") for item in result["comparability_issues"])


def test_route_outcome_candidate_drift_fails_comparability_gate() -> None:
    raw_manifest = manifest().to_dict()
    raw_manifest["candidates"][1]["model"] = "gpt-5.6-terra"
    changed = BenchmarkExperimentManifest.from_dict(raw_manifest, repo_root=REPO_ROOT)

    result = evaluate_benchmark(
        changed,
        fixtures(),
        outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T16:32:00+00:00",
    ).to_dict()

    assert result["comparability_status"] == "failed"
    assert any(item.startswith("model_mismatch:candidate-openai-luna") for item in result["comparability_issues"])


def test_regression_mode_reports_descriptive_drop_without_policy_authority() -> None:
    raw = manifest().to_dict()
    raw["study_type"] = "regression"
    raw["regression_baseline_candidate_id"] = "candidate-google-flash-lite"
    regression = BenchmarkExperimentManifest.from_dict(raw, repo_root=REPO_ROOT)

    result = evaluate_benchmark(
        regression,
        fixtures(),
        outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T16:33:00+00:00",
    ).to_dict()

    assert result["comparability_status"] == "passed"
    assert result["regression_signals"] == [
        {
            "candidate_id": "candidate-openai-luna",
            "metric": "verified_completion_rate",
            "baseline_candidate_id": "candidate-google-flash-lite",
            "delta": -0.25,
            "classification": "descriptive_drop",
        }
    ]
    assert any("not automatic routing authority" in item for item in result["limitations"])


def test_fixture_and_report_integrity_fail_closed_on_mutation() -> None:
    fixture = fixtures()[0].to_dict()
    fixture["controlled_input"] = "changed after fixture publication"
    with pytest.raises(ProviderAdapterContractError, match="fixture integrity hash"):
        BenchmarkFixtureRecord.from_dict(fixture, repo_root=REPO_ROOT)

    result = report().to_dict()
    result["candidate_metrics"][0]["completed"] = 0
    with pytest.raises(ProviderAdapterContractError, match="report integrity hash"):
        BenchmarkExperimentReport.from_dict(result, repo_root=REPO_ROOT)


def test_report_schema_rejects_unknown_fields() -> None:
    result = report().to_dict()
    result["winner"] = "candidate-google-flash-lite"
    with pytest.raises(ProviderAdapterContractError, match="schema validation"):
        BenchmarkExperimentReport.from_dict(result, repo_root=REPO_ROOT)


def test_jsonl_report_sink_revalidates_persisted_records(tmp_path: Path) -> None:
    sink = JsonlBenchmarkReportSink(
        tmp_path / "benchmark-reports.jsonl",
        repo_root=REPO_ROOT,
    )
    expected = report()
    sink.append(expected)
    loaded = sink.read_all()

    assert len(loaded) == 1
    assert loaded[0].to_dict() == expected.to_dict()


def test_manifest_bindings_cannot_reuse_one_outcome_across_trials() -> None:
    raw = manifest().to_dict()
    raw["bindings"][1]["outcome_id"] = raw["bindings"][0]["outcome_id"]

    with pytest.raises(ProviderAdapterContractError, match="cannot satisfy multiple benchmark trials"):
        BenchmarkExperimentManifest.from_dict(raw, repo_root=REPO_ROOT)
