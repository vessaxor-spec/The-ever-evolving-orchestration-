from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.live_scope_candidate import (
    LiveScopeExpansionPolicy,
    evaluate_live_scope_candidate,
)
from teo_reference.provider_adapter import ProviderAdapterContractError
from teo_reference.runtime_canary import _copy_task_for_redispatch, execute_guarded_canary
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> SpecialistRoutingEngine:
    return SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))


def documentation_task(*, risk_level: str = "low") -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "task-documentation-live-candidate",
            "task": "Draft a bounded technical note from the supplied facts only.",
            "task_type": "documentation",
            "risk_level": risk_level,
        }
    )


def throughput_task() -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "task-throughput-regression-guard",
            "task": "Classify this bounded item.",
            "task_type": "high_volume_simple",
            "risk_level": "low",
        }
    )


def test_documentation_is_staged_without_widening_active_live_scope() -> None:
    policy = LiveScopeExpansionPolicy.load(REPO_ROOT)
    candidate = policy.candidate("documentation")

    assert policy.active_task_types == {"high_volume_simple"}
    assert policy.active_risk_levels == {"low", "medium"}
    assert candidate["state"] == "staged"
    assert candidate["activation_authorized"] is False
    assert set(candidate["risk_levels"]) == {"low", "medium"}


def test_runtime_override_no_longer_mutates_shared_documentation_worker() -> None:
    worker = engine().config.worker_registry["documentation"]

    assert worker["preferred_implementations"] == [
        "claude-sonnet-5",
        "gpt-5.6-sol",
        "gemini-3.7-flash",
        "claude-haiku-4-5",
    ]
    assert worker["fallbacks"] == ["gemini-3.1-pro-preview", "gpt-5.6-sol"]


def test_throughput_primary_and_fresh_verifier_rotation_survive_override_removal() -> None:
    routing_engine = engine()
    task = throughput_task()
    primary = routing_engine.dispatch(task)

    assert primary.selected_implementation.model == "gemini-3.7-flash"
    assert primary.selected_implementation.provider_family == "google"
    assert primary.fallback_implementation is not None
    assert primary.fallback_implementation.model == "claude-haiku-4-5"
    assert primary.fallback_implementation.provider_family == "anthropic"
    assert primary.verification.implementation.model == "claude-sonnet-5"
    assert primary.verification.implementation.provider_family == "anthropic"

    model_redispatch = routing_engine.dispatch(
        _copy_task_for_redispatch(task, primary, "model")
    )
    assert model_redispatch.selected_implementation.model == "claude-haiku-4-5"
    assert model_redispatch.selected_implementation.provider_family == "anthropic"
    assert model_redispatch.verification.implementation.model == "gpt-5.6-sol"
    assert model_redispatch.verification.implementation.provider_family == "openai"

    provider_redispatch = routing_engine.dispatch(
        _copy_task_for_redispatch(task, primary, "provider")
    )
    assert provider_redispatch.selected_implementation.model == "claude-haiku-4-5"
    assert provider_redispatch.selected_implementation.provider_family == "anthropic"
    assert provider_redispatch.verification.implementation.model == "gpt-5.6-sol"
    assert provider_redispatch.verification.implementation.provider_family == "openai"


def test_documentation_preflight_reports_repaired_topology_and_remaining_evidence_gates() -> None:
    evaluation = evaluate_live_scope_candidate(engine())
    gates = {gate.name: gate.passed for gate in evaluation.gates}

    assert evaluation.task_type == "documentation"
    assert evaluation.state == "staged"
    assert evaluation.activation_authorized is False
    assert evaluation.ready_for_activation is False

    assert evaluation.primary_dispatch["primary_provider_family"] == "anthropic"
    assert evaluation.primary_dispatch["primary_model"] == "claude-sonnet-5"
    assert evaluation.primary_dispatch["primary_reasoning_effort"] == "medium"
    assert evaluation.primary_dispatch["fallback_provider_family"] == "openai"
    assert evaluation.primary_dispatch["fallback_model"] == "gpt-5.6-sol"
    assert evaluation.primary_dispatch["verifier_provider_family"] == "openai"
    assert evaluation.primary_dispatch["verifier_model"] == "gpt-5.6-terra"
    assert evaluation.primary_dispatch["verifier_reasoning_effort"] == "medium"
    assert evaluation.primary_dispatch["human_approval_required"] is False

    for redispatch in (
        evaluation.model_failure_redispatch,
        evaluation.provider_failure_redispatch,
    ):
        assert redispatch is not None
        assert redispatch["primary_provider_family"] == "openai"
        assert redispatch["primary_model"] == "gpt-5.6-sol"
        assert redispatch["verifier_provider_family"] == "google"
        assert redispatch["verifier_model"] == "gemini-3.7-flash"
        assert redispatch["verifier_reasoning_effort"] == "medium"

    assert gates["active_scope_unchanged"] is True
    assert gates["exact_primary_route_matches"] is True
    assert gates["exact_initial_fallback_matches"] is True
    assert gates["initial_fallback_provider_diverse"] is True
    assert gates["primary_verifier_matches"] is True
    assert gates["failure_redispatch_route_matches"] is True
    assert gates["primary_executor_adapter_supported"] is True
    assert gates["failure_redispatch_executor_adapter_supported"] is True
    assert gates["primary_verifier_adapter_supported"] is True
    assert gates["failure_redispatch_verifier_adapter_supported"] is True
    assert gates["fallback_redispatch_verifier_is_fresh"] is True
    assert gates["controlled_replay_evidence_present"] is False
    assert gates["shadow_evaluation_evidence_present"] is False
    assert gates["high_and_critical_risk_refusal_proven"] is True


def test_documentation_model_failure_redispatch_preserves_preview_refusal() -> None:
    routing_engine = engine()
    task = documentation_task()
    primary = routing_engine.dispatch(task)
    assert primary.fallback_implementation is not None
    assert primary.fallback_implementation.model == "gpt-5.6-sol"
    assert "gemini-3.1-pro-preview" not in task.constraints.accepted_preview_models


def test_staged_documentation_candidate_cannot_invoke_guarded_runtime(tmp_path: Path) -> None:
    with pytest.raises(
        ProviderAdapterContractError,
        match="authorized only for explicit high_volume_simple tasks",
    ):
        execute_guarded_canary(
            engine(),
            documentation_task(),
            {},
            artifact_root=tmp_path,
        )


def test_high_risk_documentation_is_not_smuggled_through_candidate_policy(tmp_path: Path) -> None:
    with pytest.raises(
        ProviderAdapterContractError,
        match="authorized only for explicit high_volume_simple tasks",
    ):
        execute_guarded_canary(
            engine(),
            documentation_task(risk_level="high"),
            {},
            artifact_root=tmp_path,
        )


def test_candidate_policy_rejects_active_scope_widening_without_activation_change() -> None:
    payload = deepcopy(LiveScopeExpansionPolicy.load(REPO_ROOT).payload)
    payload["active_scope"]["task_types"].append("documentation")

    with pytest.raises(
        ProviderAdapterContractError,
        match="must not widen the currently authorized live task scope",
    ):
        LiveScopeExpansionPolicy(payload)


def test_candidate_policy_rejects_premature_activation() -> None:
    payload = deepcopy(LiveScopeExpansionPolicy.load(REPO_ROOT).payload)
    payload["candidates"]["documentation"]["activation_authorized"] = True

    with pytest.raises(
        ProviderAdapterContractError,
        match="must remain staged and unauthorized",
    ):
        LiveScopeExpansionPolicy(payload)


def test_candidate_policy_rejects_high_or_critical_risk_expansion() -> None:
    payload = deepcopy(LiveScopeExpansionPolicy.load(REPO_ROOT).payload)
    payload["candidates"]["documentation"]["risk_levels"].append("high")

    with pytest.raises(
        ProviderAdapterContractError,
        match="restricted to low and medium risk",
    ):
        LiveScopeExpansionPolicy(payload)


def test_staged_candidate_cannot_claim_replay_or_shadow_evidence() -> None:
    payload = deepcopy(LiveScopeExpansionPolicy.load(REPO_ROOT).payload)
    payload["candidates"]["documentation"]["evidence"]["controlled_replay"] = "invented.json"

    with pytest.raises(
        ProviderAdapterContractError,
        match="cannot claim replay or shadow evidence",
    ):
        LiveScopeExpansionPolicy(payload)
