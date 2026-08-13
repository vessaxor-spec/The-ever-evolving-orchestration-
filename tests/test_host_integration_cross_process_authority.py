from __future__ import annotations

import json
import runpy
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan


ROOT = Path(__file__).resolve().parents[1]
BASE_HARNESS = (
    ROOT
    / "research"
    / "runtime"
    / "host_integration_execution_envelope_integrity.py"
)
CROSS_PROCESS_HARNESS = (
    ROOT / "research" / "runtime" / "host_integration_cross_process_authority.py"
)
BASE = runpy.run_path(str(BASE_HARNESS))
CROSS = runpy.run_path(str(CROSS_PROCESS_HARNESS))
ExecutionEnvelopeAuthority = BASE["ExecutionEnvelopeAuthority"]
HostExecutionEnvelopeScope = BASE["HostExecutionEnvelopeScope"]
ResourceTarget = BASE["ResourceTarget"]
TEOActionAuthorization = BASE["TEOActionAuthorization"]
TEOExecutionScope = BASE["TEOExecutionScope"]
TEORetryScope = BASE["TEORetryScope"]
HostAuthorityGateway = CROSS["HostAuthorityGateway"]
CrossProcessAuthorityEndpoint = CROSS["CrossProcessAuthorityEndpoint"]
PROTOCOL_VERSION = CROSS["PROTOCOL_VERSION"]

LIVE_POLICY = ROOT / "policy" / "runtime" / "live-execution-expansion.yaml"
RETRY_POLICY = ROOT / "policy" / "runtime" / "canary-retry.yaml"
PREREQUISITES = ["workspace_scoped", "sandbox_ready"]

CLIENT_CODE = r'''
import json
import runpy
import sys

module = runpy.run_path(sys.argv[1])
request = json.loads(sys.stdin.read())
response = module["send_request"](sys.argv[2], int(sys.argv[3]), request)
sys.stdout.write(json.dumps(response, sort_keys=True))
'''


def choice(model: str, provider: str, *, agent: str) -> ImplementationChoice:
    return ImplementationChoice(
        agent=agent,
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="host-integration-cross-process-authority-research",
    )


def dispatch(*, dispatch_id: str = "dispatch-cross-process") -> DispatchRecord:
    return DispatchRecord(
        task_id="task-cross-process",
        dispatch_id=dispatch_id,
        created_at="2026-08-13T07:45:00+00:00",
        task="Execute one exact host action through a cross-process authority broker.",
        task_type="high_volume_simple",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist="backend-engineer",
        specialist_source="community/specialists/backend-engineer.md",
        specialist_risk_profile="medium",
        required_capabilities=["tool_execution"],
        selected_implementation=choice("gpt-5.6-sol", "openai", agent="codex"),
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
        routing_explanation=["cross-process authority research fixture"],
        warnings=[],
    )


def build_gateway():
    authority = ExecutionEnvelopeAuthority(
        teo_scope=TEOExecutionScope.from_live_execution_policy(LIVE_POLICY),
        retry_scope=TEORetryScope.from_retry_policy(RETRY_POLICY),
        host_scope=HostExecutionEnvelopeScope(
            scope_id="host-cross-process-v1",
            allowed_resource_kinds=("workspace_path",),
            allowed_target_prefixes=("workspace://repo/",),
            allowed_side_effect_classes=("workspace_mutation",),
            required_prerequisites=("sandbox_ready",),
            max_attempts_per_dispatch=4,
            active=True,
        ),
    )
    routed = dispatch()
    candidate = TEOActionAuthorization.from_parameters(
        authorization_id="cross-process-action-v1",
        capability="tool_execution",
        operation="host_tool_execute",
        effective_risk="medium",
        target=ResourceTarget("workspace_path", "workspace://repo/src/app.py"),
        parameters={"mode": "safe", "path": "src/app.py"},
        side_effect_class="workspace_mutation",
        required_prerequisites=("workspace_scoped",),
        max_attempts_per_dispatch=2,
    )
    action_token, issued = authority.issue_teo_action(
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
    gateway = HostAuthorityGateway(
        authority,
        action_token=action_token,
        dispatch=routed,
        action=issued,
    )
    return authority, gateway


def child_request(endpoint, request):
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            CLIENT_CODE,
            str(CROSS_PROCESS_HARNESS),
            endpoint.host,
            str(endpoint.port),
        ],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(completed.stdout)


def request_from(endpoint, *, operation="authorize", attempt_number=1):
    descriptor = endpoint.descriptor()
    return {
        "version": PROTOCOL_VERSION,
        "session_id": descriptor["session_id"],
        "operation": operation,
        "action_token": descriptor["action_token"],
        "dispatch": descriptor["dispatch"],
        "action": descriptor["action"],
        "satisfied_prerequisites": list(PREREQUISITES),
        "attempt_number": attempt_number,
    }


def authorize(endpoint, *, attempt_number=1):
    return child_request(
        endpoint,
        request_from(endpoint, operation="authorize", attempt_number=attempt_number),
    )


def claim(endpoint, execution_token, *, attempt_number=1):
    request = request_from(endpoint, operation="claim", attempt_number=attempt_number)
    request["execution_token"] = execution_token
    return child_request(endpoint, request)


def test_exact_action_can_be_authorized_and_claimed_by_separate_host_processes() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        authorization = authorize(endpoint)
        assert authorization["ok"] is True
        claimed = claim(endpoint, authorization["execution_token"])
        assert claimed == {
            "attempt_number": 1,
            "ok": True,
            "operation": "claim",
            "session_id": endpoint.descriptor()["session_id"],
            "version": PROTOCOL_VERSION,
        }


def test_host_surface_cannot_request_teo_action_issuance() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        request = request_from(endpoint)
        request["operation"] = "issue"
        response = child_request(endpoint, request)
    assert response["ok"] is False
    assert "not exposed" in response["message"]


def test_forged_action_token_is_rejected_across_process_boundary() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        request = request_from(endpoint)
        request["action_token"] = "host-minted-token"
        response = child_request(endpoint, request)
    assert response["ok"] is False
    assert "authority-issued action token" in response["message"]


def test_dispatch_mutation_is_rejected_before_execution_authorization() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        request = request_from(endpoint)
        request["dispatch"] = deepcopy(request["dispatch"])
        request["dispatch"]["selected_worker"] = "frontend"
        response = child_request(endpoint, request)
    assert response["ok"] is False
    assert "dispatch does not match" in response["message"]


def test_action_mutation_is_rejected_before_execution_authorization() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        request = request_from(endpoint)
        request["action"] = deepcopy(request["action"])
        request["action"]["parameters"]["mode"] = "unsafe"
        response = child_request(endpoint, request)
    assert response["ok"] is False
    assert "action does not match" in response["message"]


def test_session_binding_rejects_token_reuse_against_other_gateway() -> None:
    _, first_gateway = build_gateway()
    _, second_gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(first_gateway) as first, CrossProcessAuthorityEndpoint(
        second_gateway
    ) as second:
        request = request_from(first)
        response = child_request(second, request)
    assert response["ok"] is False
    assert "authority session" in response["message"]


def test_old_action_token_remains_invalid_even_if_new_session_id_is_substituted() -> None:
    _, first_gateway = build_gateway()
    _, second_gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(first_gateway) as first, CrossProcessAuthorityEndpoint(
        second_gateway
    ) as second:
        request = request_from(first)
        second_descriptor = second.descriptor()
        request["session_id"] = second_descriptor["session_id"]
        request["dispatch"] = second_descriptor["dispatch"]
        request["action"] = second_descriptor["action"]
        response = child_request(second, request)
    assert response["ok"] is False
    assert "authority-issued action token" in response["message"]


def test_unknown_protocol_fields_are_rejected_instead_of_best_effort_parsed() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        request = request_from(endpoint)
        request["fallback_override"] = "host-choice"
        response = child_request(endpoint, request)
    assert response["ok"] is False
    assert "unexpected=fallback_override" in response["message"]


def test_claim_without_prior_authorization_is_rejected() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        response = claim(endpoint, "host-minted-execution-token")
    assert response["ok"] is False
    assert "host execution token was not issued" in response["message"]


def test_execution_claim_is_single_use_across_host_processes() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        authorization = authorize(endpoint)
        token = authorization["execution_token"]
        assert claim(endpoint, token)["ok"] is True
        replay = claim(endpoint, token)
    assert replay["ok"] is False
    assert "host execution token was not issued" in replay["message"]


def test_parallel_duplicate_claim_allows_exactly_one_process_to_win() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        token = authorize(endpoint)["execution_token"]
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: claim(endpoint, token), range(2)))
    assert sum(response["ok"] is True for response in responses) == 1
    assert sum(response["ok"] is False for response in responses) == 1


def test_only_one_pending_execution_authorization_exists_for_an_attempt() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        first = authorize(endpoint)
        second = authorize(endpoint)
    assert first["ok"] is True
    assert second["ok"] is False
    assert "already pending" in second["message"]


def test_consumed_attempt_cannot_be_reauthorized_as_attempt_one() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        first = authorize(endpoint)
        assert claim(endpoint, first["execution_token"])["ok"] is True
        replayed_attempt = authorize(endpoint, attempt_number=1)
        next_attempt = authorize(endpoint, attempt_number=2)
    assert replayed_attempt["ok"] is False
    assert "continue at 2" in replayed_attempt["message"]
    assert next_attempt["ok"] is True


def test_cross_process_retry_cannot_multiply_teo_attempt_budget() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        first = authorize(endpoint, attempt_number=1)
        assert claim(endpoint, first["execution_token"], attempt_number=1)["ok"] is True
        second = authorize(endpoint, attempt_number=2)
        assert claim(endpoint, second["execution_token"], attempt_number=2)["ok"] is True
        third = authorize(endpoint, attempt_number=3)
    assert third["ok"] is False
    assert "exceeds effective attempt budget 2" in third["message"]


def test_boolean_or_string_attempt_numbers_are_not_accepted_as_integers() -> None:
    _, gateway = build_gateway()
    with CrossProcessAuthorityEndpoint(gateway) as endpoint:
        for invalid in (True, "1"):
            request = request_from(endpoint)
            request["attempt_number"] = invalid
            response = child_request(endpoint, request)
            assert response["ok"] is False
            assert "positive integer" in response["message"]
