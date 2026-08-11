from __future__ import annotations

import json
from pathlib import Path

import pytest

from teo_reference.live_scope_replay_cli import (
    connections_from_environment,
    main,
)
from teo_reference.provider_adapter import ProviderAdapterContractError

REPO_ROOT = Path(__file__).resolve().parents[1]


def plan_payload() -> dict:
    return {
        "replay_version": "1",
        "record_type": "live_scope_replay_plan",
        "replay_id": "documentation-cli-test-v1",
        "task_type": "documentation",
        "suite_id": "documentation-cli-test",
        "suite_version": "1",
        "trials_per_fixture": 1,
        "fixtures": [
            {
                "fixture_id": "a",
                "risk_level": "low",
                "task": "Rewrite: Alpha is blue.",
                "required_capabilities": ["transformation"],
            },
            {
                "fixture_id": "b",
                "risk_level": "medium",
                "task": "Summarize the supplied staged-state facts.",
                "required_capabilities": ["transformation"],
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
            "repository_revision": "documentation-cli-test-revision",
            "routing_policy_revision": "documentation-cli-policy-v1",
            "registry_revision": "documentation-cli-registry-v1",
            "tool_versions": {"live-scope-replay-harness": "1"},
        },
    }


def write_plan(tmp_path: Path) -> Path:
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan_payload()), encoding="utf-8")
    return path


def test_validate_command_never_requires_provider_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = main(
        [
            "--repo-root",
            str(REPO_ROOT),
            "validate",
            "--plan",
            str(write_plan(tmp_path)),
        ]
    )
    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "valid"
    assert payload["provider_calls"] == 0
    assert payload["activation_authorized"] is False


def test_live_command_requires_explicit_acknowledgement_before_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderAdapterContractError, match="--execute-live"):
        main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "run",
                "--plan",
                str(write_plan(tmp_path)),
            ]
        )


def test_environment_bridge_requires_both_staged_route_providers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-test")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderAdapterContractError, match="openai"):
        connections_from_environment()

    monkeypatch.setenv("OPENAI_API_KEY", "openai-test")
    connections = connections_from_environment()
    assert set(connections) == {"anthropic", "openai"}
