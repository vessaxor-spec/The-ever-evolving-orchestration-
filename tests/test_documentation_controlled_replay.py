from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.live_scope_replay import (
    LiveScopeReplayPlan,
    run_staged_documentation_replay,
)
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.provider_connection import HeaderProviderConnection
from teo_reference.runtime_canary import execute_guarded_canary
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine

REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def verifier_decision() -> dict:
    return {
        "status": "passed",
        "output_present": "pass",
        "task_adherence": "pass",
        "format_consistency": "pass",
        "unsupported_claims_absent": "pass",
        "human_reason": "none",
    }


def plan_dict() -> dict:
    return {
        "replay_version": "1",
        "record_type": "live_scope_replay_plan",
        "replay_id": "documentation-controlled-replay-v1",
        "task_type": "documentation",
        "suite_id": "documentation-bounded-v1",
        "suite_version": "1",
        "trials_per_fixture": 2,
        "fixtures": [
            {
                "fixture_id": "bounded-note",
                "risk_level": "low",
                "task": (
                    "Using only these facts, write two concise sentences: service A calls service B; "
                    "the retry budget is two attempts; no external tools are allowed."
                ),
                "required_capabilities": ["synthesis", "technical_accuracy", "clear_writing"],
            },
            {
                "fixture_id": "bounded-summary",
                "risk_level": "medium",
                "task": (
                    "Summarize these supplied facts in three bullets without adding claims: the route is staged; "
                    "live activation is false; the current active task class is high_volume_simple."
                ),
                "required_capabilities": ["synthesis", "technical_accuracy", "clear_writing"],
            },
        ],
        "harness": {
            "harness_id": "teo-staged-live-scope-replay",
            "harness_version": "1",
            "tool_access_profile": "none",
            "max_attempts": 2,
            "selection_mode": "canonical_candidate_route",
            "circuit_state_profile": "isolated_per_trial",
            "verification_mode": "assigned_candidate_verifier",
            "authority_mode": "staged_evidence_only",
            "fallback_mode": "disabled_until_recovery_gate",
        },
        "versions": {
            "runtime_version": "1.0.1.dev0",
            "repository_revision": "documentation-replay-test-revision",
            "routing_policy_revision": "documentation-replay-policy-v1",
            "registry_revision": "documentation-replay-registry-v1",
            "tool_versions": {"live-scope-replay-harness": "1"},
        },
    }


def replay_plan(raw: dict | None = None) -> LiveScopeReplayPlan:
    return LiveScopeReplayPlan.from_dict(raw or plan_dict(), repo_root=REPO_ROOT)


def anthropic_connection(calls: list[dict], *, fail_mode: str | None = None) -> HeaderProviderConnection:
    state = {"count": 0}

    def transport(
        url: str,
        method: str,
        body: bytes,
        headers: Mapping[str, str],
        timeout: float,
    ):
        payload = json.loads(body.decode("utf-8"))
        calls.append(payload)
        state["count"] += 1
        assert payload["model"] == "claude-sonnet-5"
        assert payload["output_config"] == {"effort": "medium"}

        if fail_mode == "model":
            return (
                404,
                {"request-id": "req-sonnet-model-failure"},
                json.dumps(
                    {
                        "type": "error",
                        "error": {
                            "type": "not_found_error",
                            "message": "controlled model failure",
                        },
                    }
                ).encode("utf-8"),
            )
        if fail_mode == "transient_once" and state["count"] == 1:
            return (
                529,
                {"request-id": "req-sonnet-transient"},
                json.dumps(
                    {
                        "type": "error",
                        "error": {
                            "type": "overloaded_error",
                            "message": "controlled transient failure",
                        },
                    }
                ).encode("utf-8"),
            )

        task = payload["messages"][0]["content"]
        response = {
            "id": f"msg-replay-{state['count']}",
            "model": "claude-sonnet-5",
            "content": [
                {
                    "type": "text",
                    "text": "Bounded documentation output derived only from the supplied task: " + task[:80],
                }
            ],
            "usage": {"input_tokens": 20, "output_tokens": 15},
        }
        return 200, {"request-id": f"req-sonnet-{state['count']}"}, json.dumps(response).encode("utf-8")

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
        assert payload["model"] == "gpt-5.6-terra"
        assert payload["reasoning"] == {"effort": "medium"}
        assert payload["text"]["format"]["type"] == "json_schema"
        response = {
            "id": "resp-terra-replay-verifier",
            "model": "gpt-5.6-terra",
            "status": "completed",
            "output_text": json.dumps(verifier_decision()),
            "usage": {"input_tokens": 30, "output_tokens": 12, "total_tokens": 42},
        }
        return 200, {"x-request-id": "req-terra-replay"}, json.dumps(response).encode("utf-8")

    return HeaderProviderConnection(
        provider_family="openai",
        authorization_headers={"authorization": "Bearer test-openai-token"},
        transport=transport,
    )


def test_staged_documentation_replay_generates_canonical_route_outcomes_without_activation(
    tmp_path: Path,
) -> None:
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []

    execution = run_staged_documentation_replay(
        replay_plan(),
        engine(),
        {
            "anthropic": anthropic_connection(anthropic_calls),
            "openai": openai_connection(openai_calls),
        },
        repo_root=REPO_ROOT,
        artifact_root=tmp_path / "staged-replay",
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
        attempt_clock=lambda: 0.0,
    )

    assert len(execution.outcomes) == 4
    assert len(anthropic_calls) == 4
    assert len(openai_calls) == 4

    outcomes = [item.to_dict() for item in execution.outcomes]
    assert all(item["task_type"] == "documentation" for item in outcomes)
    assert all(item["primary_route"]["implementation"]["provider_family"] == "anthropic" for item in outcomes)
    assert all(item["primary_route"]["implementation"]["model"] == "claude-sonnet-5" for item in outcomes)
    assert all(item["primary_route"]["verifier"]["provider_family"] == "openai" for item in outcomes)
    assert all(item["primary_route"]["verifier"]["model"] == "gpt-5.6-terra" for item in outcomes)
    assert all(item["fallback_route"] is None for item in outcomes)
    assert all(item["final_disposition"] == "completed" for item in outcomes)
    assert all(item["versions"]["repository_revision"] == "documentation-replay-test-revision" for item in outcomes)

    record = execution.record.to_dict()
    assert record["candidate_state"] == "staged"
    assert record["activation_authorized"] is False
    assert record["evidence_only"] is True
    assert record["live_scope_widened"] is False
    assert record["telemetry_persisted"] is False
    assert record["active_scope"] == {
        "task_types": ["high_volume_simple"],
        "risk_levels": ["low", "medium"],
    }
    assert record["summary"]["total_trials"] == 4
    assert record["summary"]["completed"] == 4
    assert record["candidate_route"]["primary"]["model"] == "claude-sonnet-5"
    assert record["candidate_route"]["initial_fallback"]["model"] == "gpt-5.6-sol"
    assert record["candidate_route"]["primary_verifier"]["model"] == "gpt-5.6-terra"
    assert record["candidate_route"]["failure_redispatch_verifier"]["model"] == "gemini-3.6-flash"
    assert any("does not authorize documentation live execution" in item for item in record["limitations"])
    assert any("Automatic fallback is disabled" in item for item in record["limitations"])


def test_replay_preflights_entire_plan_before_provider_calls(tmp_path: Path) -> None:
    raw = plan_dict()
    raw["fixtures"][1]["required_capabilities"] = ["multimodal"]
    plan = replay_plan(raw)
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []

    with pytest.raises(ProviderAdapterContractError):
        run_staged_documentation_replay(
            plan,
            engine(),
            {
                "anthropic": anthropic_connection(anthropic_calls),
                "openai": openai_connection(openai_calls),
            },
            repo_root=REPO_ROOT,
            artifact_root=tmp_path,
        )

    assert anthropic_calls == []
    assert openai_calls == []


def test_replay_harness_retry_budget_must_match_active_policy_before_network(
    tmp_path: Path,
) -> None:
    raw = plan_dict()
    raw["harness"]["max_attempts"] = 1
    plan = replay_plan(raw)
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []

    with pytest.raises(ProviderAdapterContractError, match="max_attempts must match"):
        run_staged_documentation_replay(
            plan,
            engine(),
            {
                "anthropic": anthropic_connection(anthropic_calls),
                "openai": openai_connection(openai_calls),
            },
            repo_root=REPO_ROOT,
            artifact_root=tmp_path,
        )

    assert anthropic_calls == []
    assert openai_calls == []


def test_model_failure_is_recorded_without_automatic_fallback(tmp_path: Path) -> None:
    raw = plan_dict()
    raw["fixtures"] = raw["fixtures"][:2]
    raw["trials_per_fixture"] = 1
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []

    execution = run_staged_documentation_replay(
        replay_plan(raw),
        engine(),
        {
            "anthropic": anthropic_connection(anthropic_calls, fail_mode="model"),
            "openai": openai_connection(openai_calls),
        },
        repo_root=REPO_ROOT,
        artifact_root=tmp_path,
        sleeper=lambda _: None,
    )

    assert len(anthropic_calls) == 2
    assert openai_calls == []
    outcomes = [item.to_dict() for item in execution.outcomes]
    assert all(item["final_disposition"] == "execution_failed" for item in outcomes)
    assert all(item["primary_route"]["failure_scope"] == "model" for item in outcomes)
    assert all(item["fallback_route"] is None for item in outcomes)
    assert execution.record.to_dict()["summary"]["execution_failed"] == 2


def test_transient_retry_preserves_same_staged_dispatch(tmp_path: Path) -> None:
    raw = plan_dict()
    raw["fixtures"] = raw["fixtures"][:2]
    raw["trials_per_fixture"] = 1
    anthropic_calls: list[dict] = []
    openai_calls: list[dict] = []

    execution = run_staged_documentation_replay(
        replay_plan(raw),
        engine(),
        {
            "anthropic": anthropic_connection(anthropic_calls, fail_mode="transient_once"),
            "openai": openai_connection(openai_calls),
        },
        repo_root=REPO_ROOT,
        artifact_root=tmp_path,
        sleeper=lambda _: None,
        random_source=lambda: 0.5,
        attempt_clock=lambda: 0.0,
    )

    outcomes = [item.to_dict() for item in execution.outcomes]
    assert len(anthropic_calls) == 3
    assert len(openai_calls) == 2
    assert outcomes[0]["primary_route"]["attempt_count"] == 2
    assert outcomes[0]["primary_route"]["retry_used"] is True
    assert outcomes[0]["retry_assisted"] is True
    assert outcomes[0]["fallback_route"] is None
    assert outcomes[0]["final_disposition"] == "completed"


def test_plan_rejects_duplicate_fixture_ids_and_high_risk() -> None:
    raw = plan_dict()
    raw["fixtures"][1]["fixture_id"] = raw["fixtures"][0]["fixture_id"]
    with pytest.raises(ProviderAdapterContractError, match="fixture IDs must be unique"):
        replay_plan(raw)

    raw = plan_dict()
    raw["fixtures"][0]["risk_level"] = "high"
    with pytest.raises(ProviderAdapterContractError, match="schema validation"):
        replay_plan(raw)


def test_active_guarded_runtime_still_refuses_documentation_after_replay_support(
    tmp_path: Path,
) -> None:
    task = TaskRequest.from_dict(
        {
            "task_id": "documentation-still-staged",
            "task": "Draft a bounded technical note.",
            "task_type": "documentation",
            "risk_level": "low",
        }
    )
    with pytest.raises(
        ProviderAdapterContractError,
        match="authorized only for explicit high_volume_simple tasks",
    ):
        execute_guarded_canary(
            engine(),
            task,
            {},
            artifact_root=tmp_path,
        )
