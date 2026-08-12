from __future__ import annotations

import runpy
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_authority_intersection.py"
RESEARCH = runpy.run_path(str(HARNESS))
AuthorityIntersectionError = RESEARCH["AuthorityIntersectionError"]
HostExecutionScope = RESEARCH["HostExecutionScope"]
RestrictiveAuthorityGate = RESEARCH["RestrictiveAuthorityGate"]
TEOExecutionScope = RESEARCH["TEOExecutionScope"]
execute_authorized_host_action = RESEARCH["execute_authorized_host_action"]


LIVE_POLICY = ROOT / "policy" / "runtime" / "live-execution-expansion.yaml"


def choice(model: str, provider: str, *, agent: str = "host-integration") -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-authority-intersection-research",
    )


def dispatch(
    *,
    task_type: str = "high_volume_simple",
    risk: str = "medium",
    capabilities: list[str] | None = None,
    provider: str = "openai",
    model: str = "gpt-5.6-sol",
    dispatch_id: str = "dispatch-authority-intersection",
) -> DispatchRecord:
    return DispatchRecord(
        task_id="task-authority-intersection",
        dispatch_id=dispatch_id,
        created_at="2026-08-12T00:20:00+00:00",
        task="Execute one bounded host-native capability under intersected authority.",
        task_type=task_type,
        risk_level=risk,
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=capabilities or ["tool_execution"],
        selected_implementation=choice(model, provider),
        fallback_implementation=choice("gemini-3.6-flash", "google", agent="agy"),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice("claude-sonnet-5", "anthropic", agent="claude"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["authority intersection research fixture"],
        warnings=[],
    )


def host_scope(**overrides):
    base = HostExecutionScope(
        scope_id="host-scope-v1",
        allowed_task_types=("high_volume_simple", "documentation", "daily_coding"),
        allowed_risk_levels=("low", "medium", "high", "critical"),
        allowed_capabilities=("tool_execution", "testing", "web_research"),
        allowed_provider_families=("openai", "anthropic", "google"),
        allowed_operations=("host_tool_execute", "host_test_execute"),
    )
    return replace(base, **overrides)


def gate(**host_overrides):
    return RestrictiveAuthorityGate(
        TEOExecutionScope.from_live_execution_policy(LIVE_POLICY),
        host_scope(**host_overrides),
    )


class RecordingAction:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        return "executed"


def authorize_and_execute(current_gate, routed, *, capability="tool_execution", operation="host_tool_execute"):
    action = RecordingAction()
    token = current_gate.authorize(routed, capability=capability, operation=operation)
    result = execute_authorized_host_action(
        current_gate,
        token,
        routed,
        capability=capability,
        operation=operation,
        action=action,
    )
    return result, action


def test_current_teo_scope_is_derived_only_from_active_live_policy() -> None:
    scope = TEOExecutionScope.from_live_execution_policy(LIVE_POLICY)

    assert scope.task_types == ("high_volume_simple",)
    assert scope.risk_levels == ("low", "medium")
    assert "documentation" not in scope.task_types


def test_action_executes_when_both_teo_and_host_authorize_exact_scope() -> None:
    result, action = authorize_and_execute(gate(), dispatch())

    assert result == "executed"
    assert action.calls == 1


def test_host_denial_blocks_a_teo_authorized_task_type() -> None:
    current_gate = gate(denied_task_types=("high_volume_simple",))
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="explicitly denied task_type"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")

    assert action.calls == 0


def test_teo_denial_blocks_a_host_authorized_staged_task_type() -> None:
    current_gate = gate()

    with pytest.raises(AuthorityIntersectionError, match="TEO active scope does not authorize task_type"):
        current_gate.authorize(
            dispatch(task_type="documentation"),
            capability="tool_execution",
            operation="host_tool_execute",
        )


def test_host_risk_restriction_blocks_medium_when_teo_allows_it() -> None:
    current_gate = gate(allowed_risk_levels=("low",))

    with pytest.raises(AuthorityIntersectionError, match="did not authorize risk_level: medium"):
        current_gate.authorize(dispatch(risk="medium"), capability="tool_execution", operation="host_tool_execute")


def test_teo_risk_restriction_blocks_high_even_when_host_allows_it() -> None:
    current_gate = gate()

    with pytest.raises(AuthorityIntersectionError, match="TEO active scope does not authorize risk_level: high"):
        current_gate.authorize(dispatch(risk="high"), capability="tool_execution", operation="host_tool_execute")


def test_host_explicit_capability_deny_wins_over_host_allow_and_teo_dispatch() -> None:
    current_gate = gate(denied_capabilities=("tool_execution",))

    with pytest.raises(AuthorityIntersectionError, match="explicitly denied capability"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")


def test_host_missing_capability_blocks_teo_authorized_capability() -> None:
    current_gate = gate(allowed_capabilities=("testing",))

    with pytest.raises(AuthorityIntersectionError, match="did not authorize capability: tool_execution"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")


def test_host_extra_capability_cannot_widen_teo_dispatch_authority() -> None:
    current_gate = gate()
    routed = dispatch(capabilities=["tool_execution"])

    with pytest.raises(AuthorityIntersectionError, match="TEO dispatch does not authorize capability: web_research"):
        current_gate.authorize(routed, capability="web_research", operation="host_tool_execute")


def test_host_provider_restriction_blocks_teo_selected_provider() -> None:
    current_gate = gate(allowed_provider_families=("anthropic", "google"))

    with pytest.raises(AuthorityIntersectionError, match="did not authorize provider_family: openai"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")


def test_host_operation_restriction_blocks_unapproved_action_surface() -> None:
    current_gate = gate(allowed_operations=("host_test_execute",))

    with pytest.raises(AuthorityIntersectionError, match="did not authorize operation: host_tool_execute"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")


def test_inactive_host_scope_blocks_execution() -> None:
    current_gate = gate(active=False)

    with pytest.raises(AuthorityIntersectionError, match="host execution scope is inactive"):
        current_gate.authorize(dispatch(), capability="tool_execution", operation="host_tool_execute")


def test_unissued_host_action_token_fails_before_action() -> None:
    current_gate = gate()
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="token was not issued"):
        execute_authorized_host_action(
            current_gate,
            "host-self-issued-token",
            dispatch(),
            capability="tool_execution",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0


def test_authorization_token_cannot_be_reused_for_another_dispatch() -> None:
    current_gate = gate()
    original = dispatch()
    token = current_gate.authorize(original, capability="tool_execution", operation="host_tool_execute")
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            dispatch(dispatch_id="dispatch-other"),
            capability="tool_execution",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0


def test_authorization_token_cannot_switch_to_another_capability() -> None:
    current_gate = gate()
    routed = dispatch(capabilities=["tool_execution", "testing"])
    token = current_gate.authorize(routed, capability="tool_execution", operation="host_tool_execute")
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            routed,
            capability="testing",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0


def test_authorization_token_cannot_switch_operation() -> None:
    current_gate = gate()
    routed = dispatch(capabilities=["tool_execution", "testing"])
    token = current_gate.authorize(routed, capability="tool_execution", operation="host_tool_execute")
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            routed,
            capability="tool_execution",
            operation="host_test_execute",
            action=action,
        )

    assert action.calls == 0


@pytest.mark.parametrize(
    "mutation",
    [
        lambda routed: setattr(routed, "task_id", "task-mutated"),
        lambda routed: setattr(routed, "selected_worker", "frontend"),
        lambda routed: setattr(routed.selected_implementation, "model", "gpt-5.6-terra"),
        lambda routed: setattr(routed.verification.implementation, "model", "claude-opus-5"),
        lambda routed: routed.routing_explanation.append("host-added-routing-claim"),
    ],
)
def test_exact_dispatch_snapshot_cannot_change_after_authorization(mutation) -> None:
    current_gate = gate()
    routed = dispatch()
    token = current_gate.authorize(routed, capability="tool_execution", operation="host_tool_execute")
    changed = deepcopy(routed)
    mutation(changed)
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            changed,
            capability="tool_execution",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0


def test_host_scope_change_invalidates_preexisting_authorization() -> None:
    current_gate = gate()
    routed = dispatch()
    token = current_gate.authorize(routed, capability="tool_execution", operation="host_tool_execute")
    current_gate.replace_host_scope(host_scope(scope_id="host-scope-v2"))
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            routed,
            capability="tool_execution",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0


def test_teo_scope_change_invalidates_preexisting_authorization() -> None:
    current_gate = gate()
    routed = dispatch()
    token = current_gate.authorize(routed, capability="tool_execution", operation="host_tool_execute")
    current_gate.replace_teo_scope(
        TEOExecutionScope(
            source="policy/runtime/live-execution-expansion.yaml#research-mutated",
            task_types=("high_volume_simple",),
            risk_levels=("low", "medium"),
        )
    )
    action = RecordingAction()

    with pytest.raises(AuthorityIntersectionError, match="authority-bound execution scope"):
        execute_authorized_host_action(
            current_gate,
            token,
            routed,
            capability="tool_execution",
            operation="host_tool_execute",
            action=action,
        )

    assert action.calls == 0
