from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from teo_reference.host_integration_protocol import (
    PROTOCOL_VERSION,
    HostExecutionReceipt,
    HostIntegrationProtocolSession,
    HostVerificationReceipt,
)
from teo_reference.schemas import DispatchRecord, ImplementationChoice, VerificationPlan

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "reference/schemas/host-integration-protocol.schema.json").read_text(encoding="utf-8")
)
VALIDATOR = Draft202012Validator(SCHEMA)
SHA = "d" * 64


def _choice(provider: str, model: str) -> ImplementationChoice:
    return ImplementationChoice(
        agent="host",
        model=model,
        profile=None,
        provider_family=provider,
        availability="available",
        source="test",
        reasoning="high",
    )


def _dispatch() -> DispatchRecord:
    return DispatchRecord(
        task_id="task-schema",
        dispatch_id="dispatch-schema",
        created_at="2026-08-17T00:00:00+00:00",
        task="Implement schema canary",
        task_type="daily_coding",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="implementation-worker",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["coding"],
        selected_implementation=_choice("openai", "codex/test"),
        fallback_implementation=_choice("google", "gemini/test"),
        verification=VerificationPlan(
            team="verification",
            method=["independent_model_verification"],
            implementation=_choice("anthropic", "claude/verifier"),
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=[],
        warnings=[],
    )


def test_all_protocol_message_types_validate_against_wire_schema():
    session = HostIntegrationProtocolSession(_dispatch())
    execution_instruction = session.issue_execution()
    execution_receipt = HostExecutionReceipt(
        protocol_version=PROTOCOL_VERSION,
        instruction_id=execution_instruction.instruction_id,
        instruction_sha256=execution_instruction.instruction_sha256,
        dispatch_id=execution_instruction.dispatch_id,
        route_role=execution_instruction.route_role,
        provider_family=execution_instruction.provider_family,
        model=execution_instruction.model,
        attempt=execution_instruction.attempt,
        status="succeeded",
        output_ref="artifact://schema",
        output_sha256=SHA,
        evidence=("observed",),
    )
    session.accept_execution(execution_receipt)
    verification_instruction = session.issue_verification()
    verification_receipt = HostVerificationReceipt(
        protocol_version=PROTOCOL_VERSION,
        instruction_id=verification_instruction.instruction_id,
        instruction_sha256=verification_instruction.instruction_sha256,
        dispatch_id=verification_instruction.dispatch_id,
        verifier_provider_family=verification_instruction.verifier_provider_family,
        verifier_model=verification_instruction.verifier_model,
        output_ref=verification_instruction.output_ref,
        output_sha256=verification_instruction.output_sha256,
        status="passed",
        evidence=("verified",),
    )

    for message in (
        execution_instruction.to_dict(),
        execution_receipt.to_dict(),
        verification_instruction.to_dict(),
        verification_receipt.to_dict(),
    ):
        errors = list(VALIDATOR.iter_errors(message))
        assert errors == []
