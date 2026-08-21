from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

import pytest

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.ports.artifact import ArtifactIntegrityPortError
from teo_reference.schemas import (
    DispatchRecord,
    ExecutionResult,
    ImplementationChoice,
    VerificationPlan,
    VerificationResult,
    VerifiedArtifact,
)


@dataclass
class RecordingArtifactPort:
    error: str | None = None
    calls: list[tuple[str, VerifiedArtifact, str | Path]] = field(default_factory=list)

    def revalidate(
        self,
        output_ref: str,
        verified_artifact: VerifiedArtifact,
        *,
        allowed_root: str | Path,
    ) -> None:
        self.calls.append((output_ref, verified_artifact, allowed_root))
        if self.error is not None:
            raise ArtifactIntegrityPortError(self.error)


def _choice(model: str, provider: str) -> ImplementationChoice:
    return ImplementationChoice(
        agent="test",
        model=model,
        profile="sol",
        provider_family=provider,
        availability="current",
        source="test",
    )


def _dispatch() -> DispatchRecord:
    primary = _choice("executor-model", "openai")
    verifier = _choice("verifier-model", "anthropic")
    return DispatchRecord(
        task_id="task-finalization-facade",
        dispatch_id="dispatch-finalization-facade",
        created_at="2026-08-21T00:00:00+00:00",
        task="Finalize the verified execution result.",
        task_type="daily_coding",
        risk_level="medium",
        selected_team="engineering",
        selected_worker="backend",
        selected_specialist=None,
        specialist_source=None,
        specialist_risk_profile=None,
        required_capabilities=["coding"],
        selected_implementation=primary,
        fallback_implementation=_choice("fallback-model", "google"),
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=verifier,
            independent=True,
            human_approval_required=False,
        ),
        routing_explanation=[],
        warnings=[],
    )


def _verification(dispatch: DispatchRecord, binding: VerifiedArtifact) -> VerificationResult:
    return VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model=dispatch.verification.implementation.model,
        verified_artifact=binding,
    )


def test_engine_finalize_uses_injected_artifact_integrity_port() -> None:
    port = RecordingArtifactPort()
    engine = OrchestrationEngine(cast(ConfigBundle, object()), artifact_integrity=port)
    dispatch = _dispatch()
    binding = VerifiedArtifact(
        output_ref="file:///authorized/output.txt",
        sha256="0" * 64,
        size_bytes=4,
    )

    outcome = engine.finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            output_ref=binding.output_ref,
        ),
        _verification(dispatch, binding),
        artifact_root="/authorized",
    )

    assert outcome.status == "completed"
    assert port.calls == [(binding.output_ref, binding, "/authorized")]


def test_engine_finalize_preserves_public_routing_error_surface() -> None:
    port = RecordingArtifactPort(error="artifact binding changed")
    engine = OrchestrationEngine(cast(ConfigBundle, object()), artifact_integrity=port)
    dispatch = _dispatch()
    binding = VerifiedArtifact(
        output_ref="file:///authorized/output.txt",
        sha256="0" * 64,
        size_bytes=4,
    )

    with pytest.raises(RoutingError, match="artifact binding changed"):
        engine.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                output_ref=binding.output_ref,
            ),
            _verification(dispatch, binding),
            artifact_root="/authorized",
        )
