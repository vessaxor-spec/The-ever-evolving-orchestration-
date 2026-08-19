from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.benchmark_lab import (
    BenchmarkExperimentManifest,
    evaluate_benchmark,
    load_benchmark_fixtures,
    load_route_outcomes,
)
from teo_reference.benchmark_verification import (
    BenchmarkVerifierObservation,
    BenchmarkVerifierPanelPlan,
    JsonlBenchmarkVerifierObservationSink,
    attach_verifier_disagreement,
    execute_benchmark_verifier_panel,
)
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.provider_connection import HeaderProviderConnection

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


def base_report():
    return evaluate_benchmark(
        manifest(),
        fixtures(),
        outcomes(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T19:00:00+00:00",
    )


def passed_decision() -> dict:
    return {
        "status": "passed",
        "output_present": "pass",
        "task_adherence": "pass",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "none",
    }


def uncertain_decision() -> dict:
    return {
        "status": "needs_human",
        "output_present": "pass",
        "task_adherence": "uncertain",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "insufficient_evidence",
    }


def anthropic_connection(calls: list[dict]) -> HeaderProviderConnection:
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        payload = json.loads(body.decode("utf-8"))
        calls.append(payload)
        assert payload["model"] == "claude-sonnet-5"
        response = {
            "id": "msg_benchmark_panel",
            "model": payload["model"],
            "content": [{"type": "text", "text": json.dumps(passed_decision())}],
        }
        return 200, {"request-id": "req_anthropic_panel"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="anthropic",
        authorization_headers={"x-api-key": "test-anthropic-token"},
        transport=transport,
    )


def openai_connection(calls: list[dict]) -> HeaderProviderConnection:
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        payload = json.loads(body.decode("utf-8"))
        calls.append(payload)
        assert payload["model"] == "gpt-5.6-sol"
        response = {
            "id": "resp_benchmark_panel",
            "model": payload["model"],
            "status": "completed",
            "output_text": json.dumps(passed_decision()),
        }
        return 200, {"x-request-id": "req_openai_panel"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="openai",
        authorization_headers={"authorization": "Bearer test-openai-token"},
        transport=transport,
    )


def google_connection(calls: list[dict]) -> HeaderProviderConnection:
    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        payload = json.loads(body.decode("utf-8"))
        calls.append(payload)
        assert payload["model"] == "gemini-3.7-flash"
        prompt = payload["input"]
        decision = uncertain_decision() if "CANDIDATE OUTPUT:\nbeta" in prompt else passed_decision()
        response = {
            "id": "int_benchmark_panel",
            "model": payload["model"],
            "status": "completed",
            "output_text": json.dumps(decision),
        }
        return 200, {"x-request-id": "req_google_panel"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="google",
        authorization_headers={"authorization": "Bearer test-google-token"},
        transport=transport,
    )


def panel_plan_dict() -> dict:
    return {
        "benchmark_lab_version": "1",
        "record_type": "benchmark_verifier_panel_plan",
        "panel_plan_id": "cross-provider-diagnostic-panel",
        "panel_plan_version": "1",
        "experiment_id": "benchmark-lab-foundation-v1",
        "policy": {
            "minimum_observers_per_trial": 2,
            "minimum_provider_families": 2,
            "decision_use": "diagnostic_only",
            "canonical_runtime_verifier_override": False,
        },
        "panels": [
            {
                "candidate_id": "candidate-google-flash-lite",
                "observers": [
                    {
                        "observer_id": "anthropic-sonnet-observer",
                        "provider_family": "anthropic",
                        "model": "claude-sonnet-5",
                        "reasoning_effort": "medium",
                    },
                    {
                        "observer_id": "openai-sol-observer",
                        "provider_family": "openai",
                        "model": "gpt-5.6-sol",
                        "reasoning_effort": "medium",
                    },
                ],
            },
            {
                "candidate_id": "candidate-openai-luna",
                "observers": [
                    {
                        "observer_id": "anthropic-sonnet-observer",
                        "provider_family": "anthropic",
                        "model": "claude-sonnet-5",
                        "reasoning_effort": "medium",
                    },
                    {
                        "observer_id": "google-flash-observer",
                        "provider_family": "google",
                        "model": "gemini-3.7-flash",
                        "reasoning_effort": "medium",
                    },
                ],
            },
        ],
    }


def panel_plan(raw: dict | None = None) -> BenchmarkVerifierPanelPlan:
    return BenchmarkVerifierPanelPlan.from_dict(raw or panel_plan_dict(), repo_root=REPO_ROOT)


def generate_observations():
    plan = panel_plan()
    experiment = manifest().to_dict()
    outcome_map = {item.to_dict()["outcome_id"]: item for item in outcomes()}
    fixture_map = {item.to_dict()["fixture_id"]: item.to_dict() for item in fixtures()}
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []
    google_calls: list[dict] = []
    connections = {
        "anthropic": anthropic_connection(anthropic_calls),
        "openai": openai_connection(openai_calls),
        "google": google_connection(google_calls),
    }
    observations = []
    for binding in experiment["bindings"]:
        fixture = fixture_map[binding["fixture_id"]]
        output_text = "beta" if "Record: beta." in fixture["controlled_input"] else "alpha"
        observations.extend(
            execute_benchmark_verifier_panel(
                plan,
                candidate_id=binding["candidate_id"],
                fixture_id=binding["fixture_id"],
                trial_index=binding["trial_index"],
                outcome=outcome_map[binding["outcome_id"]],
                task=fixture["controlled_input"],
                output_text=output_text,
                connections=connections,
                repo_root=REPO_ROOT,
                observed_at="2026-08-10T19:05:00+00:00",
            )
        )
    return plan, observations, anthropic_calls, openai_calls, google_calls


def test_multi_verifier_disagreement_is_measured_without_overriding_runtime_result() -> None:
    base = base_report().to_dict()
    plan, observations, anthropic_calls, openai_calls, google_calls = generate_observations()
    enriched = attach_verifier_disagreement(
        base_report(),
        manifest(),
        outcomes(),
        plan,
        observations,
        repo_root=REPO_ROOT,
    ).to_dict()

    disagreement = enriched["verifier_disagreement"]
    assert disagreement["status"] == "measured"
    assert disagreement["observation_count"] == 16
    assert disagreement["verifiable_trials"] == 8
    assert disagreement["disagreement_trials"] == 2
    assert disagreement["disagreement_rate"] == 0.25
    assert disagreement["decision_use"] == "diagnostic_only"
    assert disagreement["canonical_runtime_verifier_override"] is False

    summaries = {item["candidate_id"]: item for item in disagreement["candidate_summaries"]}
    assert summaries["candidate-google-flash-lite"]["disagreement_rate"] == 0.0
    assert summaries["candidate-openai-luna"]["disagreement_rate"] == 0.5
    assert summaries["candidate-openai-luna"]["status_disagreement_trials"] == 2
    assert summaries["candidate-openai-luna"]["criterion_disagreement_trials"] == 2

    assert enriched["candidate_metrics"] == base["candidate_metrics"]
    assert enriched["comparability_status"] == base["comparability_status"]
    assert len(enriched["provenance"]["source_verifier_observation_ids"]) == 16
    assert enriched["provenance"]["panel_plan_sha256"] == plan.sha256
    assert any("No majority vote" in item for item in enriched["limitations"])

    assert len(anthropic_calls) == 8
    assert len(openai_calls) == 4
    assert len(google_calls) == 4


def test_missing_panel_observation_is_explicitly_insufficient() -> None:
    plan, observations, *_ = generate_observations()
    enriched = attach_verifier_disagreement(
        base_report(),
        manifest(),
        outcomes(),
        plan,
        observations[:-1],
        repo_root=REPO_ROOT,
    ).to_dict()

    assert enriched["verifier_disagreement"]["status"] == "insufficient"
    assert any(
        item.startswith("missing_observation:")
        for item in enriched["verifier_disagreement"]["issues"]
    )
    assert enriched["candidate_metrics"] == base_report().to_dict()["candidate_metrics"]


def test_panel_plan_requires_cross_provider_observers() -> None:
    raw = panel_plan_dict()
    raw["panels"][0]["observers"][1]["provider_family"] = "anthropic"
    raw["panels"][0]["observers"][1]["model"] = "claude-haiku-4-5"

    with pytest.raises(ProviderAdapterContractError, match="at least two provider families"):
        panel_plan(raw)


def test_panel_cannot_reuse_active_executor_model() -> None:
    raw = panel_plan_dict()
    raw["panels"][0]["observers"][0] = {
        "observer_id": "executor-reuse",
        "provider_family": "google",
        "model": "gemini-3.5-flash-lite",
        "reasoning_effort": "low",
    }
    plan = panel_plan(raw)
    experiment = manifest().to_dict()
    binding = experiment["bindings"][0]
    outcome_map = {item.to_dict()["outcome_id"]: item for item in outcomes()}

    with pytest.raises(ProviderAdapterContractError, match="active executor model"):
        execute_benchmark_verifier_panel(
            plan,
            candidate_id=binding["candidate_id"],
            fixture_id=binding["fixture_id"],
            trial_index=binding["trial_index"],
            outcome=outcome_map[binding["outcome_id"]],
            task="Classify the record.",
            output_text="alpha",
            connections={},
            repo_root=REPO_ROOT,
        )


def test_verifier_observation_integrity_and_jsonl_round_trip(tmp_path: Path) -> None:
    _, observations, *_ = generate_observations()
    raw = observations[0].to_dict()
    raw["decision"]["status"] = "failed"
    with pytest.raises(ProviderAdapterContractError):
        BenchmarkVerifierObservation.from_dict(raw, repo_root=REPO_ROOT)

    sink = JsonlBenchmarkVerifierObservationSink(
        tmp_path / "benchmark-verifier-observations.jsonl",
        repo_root=REPO_ROOT,
    )
    sink.append(observations[0])
    loaded = sink.read_all()
    assert [item.to_dict() for item in loaded] == [observations[0].to_dict()]
