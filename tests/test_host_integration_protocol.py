from __future__ import annotations

from dataclasses import replace

import pytest

from teo_reference.host_integration_protocol import (
    PROTOCOL_VERSION,
    HostExecutionReceipt,
    HostIntegrationProtocolError,
    HostIntegrationProtocolSession,
    HostVerificationReceipt,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan

OUTPUT_SHA = "a" * 64
FALLBACK_SHA = "b" * 64


def _choice(provider: str, model: str, reasoning: str | None = None) -> ImplementationChoice:
    return ImplementationChoice(
        agent="host",
        model=model,
        profile=None,
        provider_family=provider,
        availability="available",
        source="test",
        reasoning=reasoning,
    )


def _dispatch() -> DispatchRecord:
    return DispatchRecord(
        task_id="task-host-001",
        dispatch_id="dispatch-host-001",
        created_at="2026-08-17T00:00:00+00:00",
        task="Implement the bounded host integration canary",
        task_type="daily_coding",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="implementation-worker",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["coding", "tool_execution"],
        selected_implementation=_choice("openai", "codex/test", "high"),
        fallback_implementation=_choice("google", "gemini/test", "medium"),
        verification=VerificationPlan(
            team="verification",
            method=["independent_model_verification", "artifact_binding"],
            implementation=_choice("anthropic", "claude/verifier", "high"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=[],
        warnings=[],
    )


def _receipt(instruction, *, status="succeeded", provider=None, model=None, output_ref="artifact://primary", output_sha256=OUTPUT_SHA):
    return HostExecutionReceipt(
        protocol_version=PROTOCOL_VERSION,
        instruction_id=instruction.instruction_id,
        instruction_sha256=instruction.instruction_sha256,
        dispatch_id=instruction.dispatch_id,
        route_role=instruction.route_role,
        provider_family=provider or instruction.provider_family,
        model=model or instruction.model,
        attempt=instruction.attempt,
        status=status,
        output_ref=output_ref if status == "succeeded" else None,
        output_sha256=output_sha256 if status == "succeeded" else None,
        evidence=("host-observation",),
    )


def _verification_receipt(instruction, *, status="passed", provider=None, model=None, output_ref=None, output_sha256=None):
    return HostVerificationReceipt(
        protocol_version=PROTOCOL_VERSION,
        instruction_id=instruction.instruction_id,
        instruction_sha256=instruction.instruction_sha256,
        dispatch_id=instruction.dispatch_id,
        verifier_provider_family=provider or instruction.verifier_provider_family,
        verifier_model=model or instruction.verifier_model,
        output_ref=output_ref or instruction.output_ref,
        output_sha256=output_sha256 or instruction.output_sha256,
        status=status,
        evidence=("verifier-observation",),
    )


def test_primary_instruction_binds_selected_route_and_minimum_context():
    instruction = HostIntegrationProtocolSession(_dispatch()).issue_execution()
    assert instruction.provider_family == "openai"
    assert instruction.model == "codex/test"
    assert instruction.reasoning_effort == "high"
    assert instruction.task == _dispatch().task
    assert instruction.required_capabilities == ("coding", "tool_execution")
    instruction.validate_integrity()


def test_execution_receipt_provider_drift_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    with pytest.raises(HostIntegrationProtocolError, match="does not match"):
        session.accept_execution(_receipt(instruction, provider="google"))


def test_execution_receipt_model_drift_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    with pytest.raises(HostIntegrationProtocolError, match="does not match"):
        session.accept_execution(_receipt(instruction, model="codex/other"))


def test_execution_instruction_mutation_breaks_integrity():
    instruction = HostIntegrationProtocolSession(_dispatch()).issue_execution()
    tampered = replace(instruction, model="codex/other")
    with pytest.raises(HostIntegrationProtocolError, match="integrity mismatch"):
        tampered.validate_integrity()


def test_dispatch_mutation_after_session_creation_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    session.dispatch.selected_implementation.model = "codex/other"
    with pytest.raises(HostIntegrationProtocolError, match="dispatch snapshot changed"):
        session.issue_execution()


def test_success_requires_output_identity():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    receipt = _receipt(instruction, output_ref=None, output_sha256=None)
    with pytest.raises(HostIntegrationProtocolError, match="requires output_ref"):
        session.accept_execution(receipt)


def test_failed_execution_cannot_claim_successful_output_identity():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    receipt = HostExecutionReceipt(
        protocol_version=PROTOCOL_VERSION,
        instruction_id=instruction.instruction_id,
        instruction_sha256=instruction.instruction_sha256,
        dispatch_id=instruction.dispatch_id,
        route_role=instruction.route_role,
        provider_family=instruction.provider_family,
        model=instruction.model,
        attempt=instruction.attempt,
        status="failed",
        output_ref="artifact://contradictory",
        output_sha256=OUTPUT_SHA,
        evidence=("host-observation",),
    )
    with pytest.raises(HostIntegrationProtocolError, match="must not claim"):
        session.accept_execution(receipt)


def test_execution_receipt_replay_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    receipt = _receipt(instruction)
    session.accept_execution(receipt)
    with pytest.raises(HostIntegrationProtocolError, match="replay"):
        session.accept_execution(receipt)


def test_fallback_cannot_be_host_invented_before_primary_failure():
    session = HostIntegrationProtocolSession(_dispatch())
    with pytest.raises(HostIntegrationProtocolError, match="fallback may be issued"):
        session.issue_execution(route_role="fallback")


def test_teo_issues_declared_fallback_only_after_primary_failure():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary, status="failed"))
    fallback = session.issue_execution(route_role="fallback")
    assert fallback.provider_family == "google"
    assert fallback.model == "gemini/test"
    session.accept_execution(
        _receipt(
            fallback,
            output_ref="artifact://fallback",
            output_sha256=FALLBACK_SHA,
        )
    )
    assert session.active_execution().route_role == "fallback"


def test_retry_requires_immediately_preceding_failed_attempt():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    with pytest.raises(HostIntegrationProtocolError, match="immediately preceding"):
        session.issue_execution(attempt=2)
    first = session.issue_execution(attempt=1)
    session.accept_execution(_receipt(first, status="failed"))
    second = session.issue_execution(attempt=2)
    assert second.attempt == 2


def test_retry_budget_cannot_be_multiplied_by_host():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    first = session.issue_execution(attempt=1)
    session.accept_execution(_receipt(first, status="failed"))
    second = session.issue_execution(attempt=2)
    session.accept_execution(_receipt(second, status="failed"))
    with pytest.raises(HostIntegrationProtocolError, match="exceeds"):
        session.issue_execution(attempt=3)


def test_verifier_instruction_is_provider_diverse_and_artifact_bound():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary))
    verification = session.issue_verification()
    assert verification.verifier_provider_family == "anthropic"
    assert verification.verifier_model == "claude/verifier"
    assert verification.executor_provider_family == "openai"
    assert verification.output_sha256 == OUTPUT_SHA
    verification.validate_integrity()


def test_verifier_provider_drift_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary))
    verification = session.issue_verification()
    with pytest.raises(HostIntegrationProtocolError, match="does not match"):
        session.accept_verification(_verification_receipt(verification, provider="openai"))


def test_stale_verifier_artifact_binding_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary))
    verification = session.issue_verification()
    with pytest.raises(HostIntegrationProtocolError, match="does not match"):
        session.accept_verification(
            _verification_receipt(verification, output_sha256="c" * 64)
        )


def test_verification_receipt_replay_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary))
    verification = session.issue_verification()
    receipt = _verification_receipt(verification)
    session.accept_verification(receipt)
    with pytest.raises(HostIntegrationProtocolError, match="replay"):
        session.accept_verification(receipt)


def test_fallback_evidence_projection_reports_actual_execution_lane():
    session = HostIntegrationProtocolSession(_dispatch())
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary, status="failed"))
    fallback = session.issue_execution(route_role="fallback")
    session.accept_execution(
        _receipt(
            fallback,
            output_ref="artifact://fallback",
            output_sha256=FALLBACK_SHA,
        )
    )
    verification = session.issue_verification()
    session.accept_verification(_verification_receipt(verification))
    evidence = session.evidence_projection()
    assert evidence["active_route_role"] == "fallback"
    assert evidence["executor_provider_family"] == "google"
    assert evidence["executor_model"] == "gemini/test"
    assert evidence["verifier_provider_family"] == "anthropic"
    assert evidence["verification_status"] == "passed"
