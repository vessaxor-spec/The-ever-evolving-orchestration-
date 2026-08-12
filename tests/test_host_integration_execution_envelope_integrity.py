from __future__ import annotations

import runpy
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT
    / "research"
    / "runtime"
    / "host_integration_execution_envelope_integrity.py"
)
RESEARCH = runpy.run_path(str(HARNESS))
ExecutionEnvelopeAuthority = RESEARCH["ExecutionEnvelopeAuthority"]
ExecutionEnvelopeError = RESEARCH["ExecutionEnvelopeError"]
HostExecutionEnvelopeScope = RESEARCH["HostExecutionEnvelopeScope"]
ResourceTarget = RESEARCH["ResourceTarget"]
TEOActionAuthorization = RESEARCH["TEOActionAuthorization"]
TEOExecutionScope = RESEARCH["TEOExecutionScope"]
TEORetryScope = RESEARCH["TEORetryScope"]
execute_authorized_action = RESEARCH["execute_authorized_action"]


LIVE_POLICY = ROOT / "policy" / "runtime" / "live-execution-expansion.yaml"
RETRY_POLICY = ROOT / "policy" / "runtime" / "canary-retry.yaml"
DEFAULT_PREREQUISITES = ("workspace_scoped", "sandbox_ready")


def choice(
    model: str,
    provider: str,
    *,
    agent: str = "host-integration-envelope",
) -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-execution-envelope-research",
    )


def dispatch(
    *,
    risk: str = "medium",
    capabilities: list[str] | None = None,
    dispatch_id: str = "dispatch-execution-envelope",
) -> DispatchRecord:
    return DispatchRecord(
        task_id="task-execution-envelope",
        dispatch_id=dispatch_id,
        created_at="2026-08-12T07:00:00+00:00",
        task="Execute one exact host action inside the authority-bound envelope.",
        task_type="high_volume_simple",
        risk_level=risk,
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=capabilities or ["tool_execution"],
        selected_implementation=choice("gpt-5.6-sol", "openai"),
        fallback_implementation=choice(
            "gemini-3.6-flash", "google", agent="agy"
        ),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=choice(
                "claude-sonnet-5", "anthropic", agent="claude"
            ),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=["execution-envelope integrity research fixture"],
        warnings=[],
    )


def host_scope(**overrides):
    base = HostExecutionEnvelopeScope(
        scope_id="host-envelope-v1",
        allowed_resource_kinds=("workspace_path", "service_endpoint"),
        allowed_target_prefixes=("workspace://repo/", "service://sandbox/"),
        allowed_side_effect_classes=("read_only", "workspace_mutation"),
        required_prerequisites=("sandbox_ready",),
        max_attempts_per_dispatch=5,
        active=True,
    )
    return replace(base, **overrides)


def authority(**host_overrides):
    return ExecutionEnvelopeAuthority(
        teo_scope=TEOExecutionScope.from_live_execution_policy(LIVE_POLICY),
        retry_scope=TEORetryScope.from_retry_policy(RETRY_POLICY),
        host_scope=host_scope(**host_overrides),
    )


def action(
    *,
    effective_risk: str = "medium",
    capability: str = "tool_execution",
    target: ResourceTarget | None = None,
    parameters=None,
    side_effect_class: str = "workspace_mutation",
    prerequisites: tuple[str, ...] = ("workspace_scoped",),
    max_attempts: int = 2,
    authorization_id: str = "action-envelope-v1",
):
    return TEOActionAuthorization.from_parameters(
        authorization_id=authorization_id,
        capability=capability,
        operation="host_tool_execute",
        effective_risk=effective_risk,
        target=target
        or ResourceTarget("workspace_path", "workspace://repo/src/app.py"),
        parameters=parameters or {"mode": "safe", "path": "src/app.py"},
        side_effect_class=side_effect_class,
        required_prerequisites=prerequisites,
        max_attempts_per_dispatch=max_attempts,
    )


def issue(current_authority, routed=None, **overrides):
    routed = routed or dispatch()
    candidate = action(**overrides)
    token, issued = current_authority.issue_teo_action(
        routed,
        authorization_id=candidate.authorization_id,
        capability=candidate.capability,
        operation=candidate.operation,
        effective_risk=candidate.effective_risk,
        target=candidate.target,
        parameters=candidate.parameters,
        side_effect_class=candidate.side_effect_class,
        required_prerequisites=candidate.required_prerequisites,
        max_attempts_per_dispatch=candidate.max_attempts_per_dispatch,
    )
    return routed, token, issued


class RecordingAction:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self) -> str:
        self.calls += 1
        return "executed"


def authorize_attempt(
    current_authority,
    action_token,
    routed,
    issued,
    *,
    prerequisites=DEFAULT_PREREQUISITES,
    attempt_number=1,
):
    return current_authority.authorize_host_execution(
        action_token,
        routed,
        issued,
        satisfied_prerequisites=prerequisites,
        attempt_number=attempt_number,
    )


def execute_attempt(
    current_authority,
    execution_token,
    action_token,
    routed,
    issued,
    recorder,
    *,
    prerequisites=DEFAULT_PREREQUISITES,
    attempt_number=1,
):
    return execute_authorized_action(
        current_authority,
        execution_token,
        action_token,
        routed,
        issued,
        satisfied_prerequisites=prerequisites,
        attempt_number=attempt_number,
        action=recorder,
    )


def test_current_execution_and_retry_scopes_are_loaded_from_active_policy() -> None:
    current = authority()

    assert current.teo_scope.task_types == ("high_volume_simple",)
    assert current.teo_scope.risk_levels == ("low", "medium")
    assert current.retry_scope.max_attempts_per_dispatch == 2
    assert current.retry_scope.retry_same_dispatch is True
    assert current.retry_scope.redispatch_during_retry is False
    assert current.retry_scope.fallback_after_transient_exhaustion is False


def test_exact_action_executes_when_teo_and_host_envelopes_both_allow_it() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    recorder = RecordingAction()

    result = execute_attempt(
        current,
        execution_token,
        action_token,
        routed,
        issued,
        recorder,
    )

    assert result == "executed"
    assert recorder.calls == 1


def test_host_cannot_self_issue_a_teo_action_token() -> None:
    current = authority()
    routed = dispatch()
    forged = action()

    with pytest.raises(ExecutionEnvelopeError, match="TEO action token was not issued"):
        authorize_attempt(current, "host-self-issued", routed, forged)


def test_action_risk_cannot_be_lowered_below_dispatch_effective_risk() -> None:
    current = authority()

    with pytest.raises(ExecutionEnvelopeError, match="must exactly match"):
        issue(current, effective_risk="low")


def test_action_cannot_add_a_capability_absent_from_dispatch() -> None:
    current = authority()

    with pytest.raises(ExecutionEnvelopeError, match="does not authorize capability"):
        issue(current, capability="web_research")


def test_action_retry_budget_cannot_exceed_current_teo_retry_policy() -> None:
    current = authority()

    with pytest.raises(ExecutionEnvelopeError, match="exceeds current retry-policy"):
        issue(current, max_attempts=3)


def test_host_resource_kind_restriction_blocks_action() -> None:
    current = authority(allowed_resource_kinds=("service_endpoint",))
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="did not authorize resource kind"):
        authorize_attempt(current, action_token, routed, issued)


def test_host_resource_prefix_restriction_blocks_action() -> None:
    current = authority(allowed_target_prefixes=("workspace://repo/tests/",))
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="did not authorize target"):
        authorize_attempt(current, action_token, routed, issued)


def test_host_side_effect_restriction_blocks_mutating_action() -> None:
    current = authority(allowed_side_effect_classes=("read_only",))
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="did not authorize side effect class"):
        authorize_attempt(current, action_token, routed, issued)


def test_missing_teo_action_prerequisite_blocks_execution_authorization() -> None:
    current = authority()
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="workspace_scoped"):
        authorize_attempt(
            current,
            action_token,
            routed,
            issued,
            prerequisites=("sandbox_ready",),
        )


def test_missing_host_prerequisite_blocks_execution_authorization() -> None:
    current = authority(required_prerequisites=("sandbox_ready", "credential_ready"))
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="credential_ready"):
        authorize_attempt(current, action_token, routed, issued)


def test_broader_host_retry_budget_cannot_widen_teo_budget() -> None:
    current = authority(max_attempts_per_dispatch=9)
    routed, action_token, issued = issue(current)

    with pytest.raises(ExecutionEnvelopeError, match="exceeds effective attempt budget 2"):
        authorize_attempt(
            current,
            action_token,
            routed,
            issued,
            attempt_number=3,
        )


def test_narrower_host_retry_budget_wins_over_teo_budget() -> None:
    current = authority(max_attempts_per_dispatch=1)
    routed, action_token, issued = issue(current)
    first_token = authorize_attempt(current, action_token, routed, issued)
    recorder = RecordingAction()
    execute_attempt(
        current,
        first_token,
        action_token,
        routed,
        issued,
        recorder,
    )

    with pytest.raises(ExecutionEnvelopeError, match="exceeds effective attempt budget 1"):
        authorize_attempt(
            current,
            action_token,
            routed,
            issued,
            attempt_number=2,
        )

    assert recorder.calls == 1


def test_target_cannot_change_after_teo_action_issuance() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    changed = replace(
        issued,
        target=ResourceTarget("workspace_path", "workspace://repo/src/other.py"),
    )

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, routed, changed)


def test_parameters_cannot_change_after_teo_action_issuance() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    changed = action(parameters={"mode": "unsafe", "path": "src/app.py"})

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, routed, changed)


def test_side_effect_class_cannot_change_after_teo_action_issuance() -> None:
    current = authority(
        allowed_side_effect_classes=("read_only", "workspace_mutation", "external_mutation")
    )
    routed, action_token, issued = issue(current)
    changed = replace(issued, side_effect_class="external_mutation")

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, routed, changed)


def test_dispatch_snapshot_cannot_change_after_teo_action_issuance() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    changed = deepcopy(routed)
    changed.selected_worker = "frontend"

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, changed, issued)


def test_target_cannot_change_after_host_execution_authorization() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    changed = replace(
        issued,
        target=ResourceTarget("workspace_path", "workspace://repo/src/other.py"),
    )
    recorder = RecordingAction()

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        execute_attempt(
            current,
            execution_token,
            action_token,
            routed,
            changed,
            recorder,
        )

    assert recorder.calls == 0


def test_prerequisite_evidence_cannot_change_after_execution_authorization() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    recorder = RecordingAction()

    with pytest.raises(ExecutionEnvelopeError, match="authorized envelope"):
        execute_attempt(
            current,
            execution_token,
            action_token,
            routed,
            issued,
            recorder,
            prerequisites=("workspace_scoped", "sandbox_ready", "extra_claim"),
        )

    assert recorder.calls == 0


def test_attempt_number_cannot_change_after_execution_authorization() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    recorder = RecordingAction()

    with pytest.raises(ExecutionEnvelopeError, match="authorized envelope"):
        execute_attempt(
            current,
            execution_token,
            action_token,
            routed,
            issued,
            recorder,
            attempt_number=2,
        )

    assert recorder.calls == 0


def test_host_scope_change_invalidates_pending_execution_token() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    current.replace_host_scope(host_scope(scope_id="host-envelope-v2"))
    recorder = RecordingAction()

    with pytest.raises(ExecutionEnvelopeError, match="authorized envelope"):
        execute_attempt(
            current,
            execution_token,
            action_token,
            routed,
            issued,
            recorder,
        )

    assert recorder.calls == 0


def test_retry_policy_change_invalidates_existing_teo_action_token() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    current.replace_retry_scope(
        replace(current.retry_scope, source=current.retry_scope.source + "#changed")
    )

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, routed, issued)


def test_teo_scope_change_invalidates_existing_teo_action_token() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    current.replace_teo_scope(
        replace(current.teo_scope, source=current.teo_scope.source + "#changed")
    )

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, routed, issued)


def test_execution_token_is_single_use_and_retry_requires_new_attempt_authorization() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    execution_token = authorize_attempt(current, action_token, routed, issued)
    recorder = RecordingAction()
    execute_attempt(
        current,
        execution_token,
        action_token,
        routed,
        issued,
        recorder,
    )

    with pytest.raises(ExecutionEnvelopeError, match="host execution token was not issued"):
        execute_attempt(
            current,
            execution_token,
            action_token,
            routed,
            issued,
            recorder,
        )

    second_token = authorize_attempt(
        current,
        action_token,
        routed,
        issued,
        attempt_number=2,
    )
    execute_attempt(
        current,
        second_token,
        action_token,
        routed,
        issued,
        recorder,
        attempt_number=2,
    )

    assert recorder.calls == 2


def test_cross_dispatch_action_token_reuse_is_rejected() -> None:
    current = authority()
    routed, action_token, issued = issue(current)
    other = dispatch(dispatch_id="dispatch-other")

    with pytest.raises(ExecutionEnvelopeError, match="authority-issued snapshot"):
        authorize_attempt(current, action_token, other, issued)
