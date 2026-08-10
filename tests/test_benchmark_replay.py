from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.benchmark_lab import load_benchmark_fixtures
from teo_reference.benchmark_replay import (
    BenchmarkReplayPlan,
    evaluate_controlled_replay,
    run_controlled_replay,
)
from teo_reference.config import ConfigBundle
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.specialist_routing import SpecialistRoutingEngine

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = (
    REPO_ROOT
    / "reference"
    / "datasets"
    / "benchmark-lab"
    / "benchmark-fixtures-v1.jsonl"
)


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def fixtures():
    return load_benchmark_fixtures(FIXTURE_PATH, repo_root=REPO_ROOT)


def verifier_decision() -> dict:
    return {
        "status": "passed",
        "output_present": "pass",
        "task_adherence": "pass",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "none",
    }


def _label_from_input(value: str) -> str:
    return "beta" if "Record: beta." in value else "alpha"


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
        model = payload["model"]
        if model == "gemini-3.5-flash-lite":
            response = {
                "id": "int_replay_execution",
                "model": model,
                "status": "completed",
                "output_text": _label_from_input(payload["input"]),
            }
        elif model == "gemini-3.6-flash":
            response = {
                "id": "int_replay_verifier",
                "model": model,
                "status": "completed",
                "output_text": json.dumps(verifier_decision()),
            }
        else:
            raise AssertionError(f"unexpected Google model {model}")
        return 200, {"x-request-id": "req_google_replay"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="google",
        authorization_headers={"authorization": "Bearer test-google-token"},
        transport=transport,
    )


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
        model = payload["model"]
        if model == "claude-haiku-4-5":
            task = payload["messages"][0]["content"]
            text = _label_from_input(task)
        elif model == "claude-sonnet-5":
            text = json.dumps(verifier_decision())
        else:
            raise AssertionError(f"unexpected Anthropic model {model}")
        response = {
            "id": "msg_replay",
            "model": model,
            "content": [{"type": "text", "text": text}],
        }
        return 200, {"request-id": "req_anthropic_replay"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="anthropic",
        authorization_headers={"x-api-key": "test-anthropic-token"},
        transport=transport,
    )


def plan_dict() -> dict:
    common_versions = {
        "runtime_version": "1.0.1.dev0",
        "repository_revision": "controlled-replay-test-revision",
        "routing_policy_revision": "controlled-replay-policy-v1",
        "registry_revision": "controlled-replay-registry-v1",
        "tool_versions": {"benchmark-replay-harness": "1"},
    }
    return {
        "benchmark_lab_version": "1",
        "record_type": "benchmark_replay_plan",
        "replay_id": "controlled-live-replay-v1",
        "claim_scope": "system_to_system",
        "suite_id": "high-volume-classification-v1",
        "suite_version": "1",
        "trials_per_fixture": 2,
        "primary_metric": "verified_completion_rate",
        "stopping_rule": "fixed_trials",
        "harness": {
            "harness_id": "teo-controlled-live-replay",
            "harness_version": "1",
            "tool_access_profile": "none",
            "max_attempts": 2,
            "max_wall_time_seconds": None,
            "selection_mode": "policy_with_additive_blocks",
            "circuit_state_profile": "isolated_per_trial",
            "verification_mode": "assigned_live_verifier",
        },
        "candidates": [
            {
                "candidate_id": "canonical-flash-lite-route",
                "provider_family": "google",
                "model": "gemini-3.5-flash-lite",
                "reasoning_effort": "low",
                "verifier_provider_family": "anthropic",
                "verifier_model": "claude-sonnet-5",
                **common_versions,
                "isolation": {
                    "blocked_implementations": [],
                    "blocked_providers": [],
                },
            },
            {
                "candidate_id": "canonical-haiku-route",
                "provider_family": "anthropic",
                "model": "claude-haiku-4-5",
                "reasoning_effort": "low",
                "verifier_provider_family": "google",
                "verifier_model": "gemini-3.6-flash",
                **common_versions,
                "isolation": {
                    "blocked_implementations": ["gemini-3.5-flash-lite"],
                    "blocked_providers": [],
                },
            },
        ],
    }


def replay_plan(raw: dict | None = None) -> BenchmarkReplayPlan:
    return BenchmarkReplayPlan.from_dict(raw or plan_dict(), repo_root=REPO_ROOT)


def test_controlled_live_replay_executes_normal_routes_and_generates_standard_evidence(
    tmp_path: Path,
) -> None:
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []
    plan = replay_plan()

    execution = run_controlled_replay(
        plan,
        fixtures(),
        engine(),
        {
            "google": google_connection(google_calls),
            "anthropic": anthropic_connection(anthropic_calls),
        },
        repo_root=REPO_ROOT,
        artifact_root=tmp_path / "replay-artifacts",
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
        attempt_clock=lambda: 0.0,
    )

    manifest = execution.manifest.to_dict()
    assert manifest["study_type"] == "replay"
    assert manifest["claim_scope"] == "system_to_system"
    assert manifest["experiment_id"] == f"replay-{plan.sha256}"
    assert len(manifest["bindings"]) == 8
    assert len(execution.outcomes) == 8

    outcome_payloads = [record.to_dict() for record in execution.outcomes]
    assert {item["primary_route"]["implementation"]["model"] for item in outcome_payloads} == {
        "gemini-3.5-flash-lite",
        "claude-haiku-4-5",
    }
    assert all(item["final_disposition"] == "completed" for item in outcome_payloads)
    assert all(
        item["versions"]["repository_revision"] == "controlled-replay-test-revision"
        for item in outcome_payloads
    )

    result = evaluate_controlled_replay(
        execution,
        fixtures(),
        repo_root=REPO_ROOT,
        generated_at="2026-08-10T18:00:00+00:00",
    ).to_dict()
    assert result["comparability_status"] == "passed"
    assert result["evidence_sufficiency"] == "descriptive_only"
    assert result["verifier_disagreement"]["status"] == "not_measured"
    assert all(item["completed"] == 4 for item in result["candidate_metrics"])
    assert all(item["primary_completed"] == 4 for item in result["candidate_metrics"])
    assert not any("live replay execution are not yet implemented" in item for item in result["limitations"])
    assert any("did not acquire route-selection authority" in item for item in result["limitations"])

    assert len(google_calls) == 8
    assert len(anthropic_calls) == 8
    assert {item["model"] for item in google_calls} == {
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
    }
    assert {item["model"] for item in anthropic_calls} == {
        "claude-haiku-4-5",
        "claude-sonnet-5",
    }


def test_candidate_mismatch_fails_preflight_before_any_provider_call(tmp_path: Path) -> None:
    raw = plan_dict()
    raw["candidates"] = [raw["candidates"][1], raw["candidates"][0]]
    raw["candidates"][0]["isolation"]["blocked_implementations"] = []
    plan = replay_plan(raw)
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []

    with pytest.raises(ProviderAdapterContractError, match="preflight did not resolve"):
        run_controlled_replay(
            plan,
            fixtures(),
            engine(),
            {
                "google": google_connection(google_calls),
                "anthropic": anthropic_connection(anthropic_calls),
            },
            repo_root=REPO_ROOT,
            artifact_root=tmp_path,
        )

    assert google_calls == []
    assert anthropic_calls == []


def test_replay_plan_cannot_block_its_declared_model_or_provider() -> None:
    raw = plan_dict()
    raw["candidates"][0]["isolation"]["blocked_implementations"] = [
        "gemini-3.5-flash-lite"
    ]
    with pytest.raises(ProviderAdapterContractError, match="cannot block its declared model"):
        replay_plan(raw)

    raw = plan_dict()
    raw["candidates"][0]["isolation"]["blocked_providers"] = ["google"]
    with pytest.raises(ProviderAdapterContractError, match="cannot block its declared provider"):
        replay_plan(raw)


def test_live_replay_schema_rejects_executor_only_claims() -> None:
    raw = plan_dict()
    raw["claim_scope"] = "executor_only"
    with pytest.raises(ProviderAdapterContractError, match="schema validation"):
        replay_plan(raw)


def test_replay_harness_attempt_budget_must_match_active_runtime_before_network(
    tmp_path: Path,
) -> None:
    raw = plan_dict()
    raw["harness"]["max_attempts"] = 1
    plan = replay_plan(raw)
    google_calls: list[dict] = []
    anthropic_calls: list[dict] = []

    with pytest.raises(ProviderAdapterContractError, match="max_attempts must match"):
        run_controlled_replay(
            plan,
            fixtures(),
            engine(),
            {
                "google": google_connection(google_calls),
                "anthropic": anthropic_connection(anthropic_calls),
            },
            repo_root=REPO_ROOT,
            artifact_root=tmp_path,
        )

    assert google_calls == []
    assert anthropic_calls == []


def test_replay_plan_requires_provider_diverse_verification() -> None:
    raw = plan_dict()
    raw["candidates"][0]["verifier_provider_family"] = "google"
    with pytest.raises(ProviderAdapterContractError, match="provider-diverse verification"):
        replay_plan(raw)
