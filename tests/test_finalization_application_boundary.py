from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path

import pytest

from teo_reference.application.finalization import FinalizationError, FinalizationService
from teo_reference.ports.artifact import ArtifactIntegrityPortError
from teo_reference.schemas import (
    DispatchRecord,
    ExecutionResult,
    ImplementationChoice,
    VerificationPlan,
    VerificationResult,
    VerifiedArtifact,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "reference" / "implementations" / "python" / "src" / "teo_reference"


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


def _dispatch(*, human: bool = False, fallback: bool = True) -> DispatchRecord:
    primary = _choice("executor-model", "openai")
    verifier = _choice("verifier-model", "anthropic")
    return DispatchRecord(
        task_id="task-finalization-boundary",
        dispatch_id="dispatch-finalization-boundary",
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
        fallback_implementation=_choice("fallback-model", "google") if fallback else None,
        verification=VerificationPlan(
            team="verification",
            method=["output_validation"],
            implementation=verifier,
            independent=True,
            human_approval_required=human,
        ),
        routing_explanation=[],
        warnings=[],
    )


def _verification(
    dispatch: DispatchRecord,
    *,
    status: str = "passed",
    binding: VerifiedArtifact | None = None,
) -> VerificationResult:
    return VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status=status,  # type: ignore[arg-type]
        verifier_model=dispatch.verification.implementation.model,
        evidence=["verification:test"],
        verified_artifact=binding,
    )


def test_non_artifact_finalization_is_pure_application_behavior() -> None:
    port = RecordingArtifactPort()
    service = FinalizationService(port)
    dispatch = _dispatch()

    outcome = service.finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            evidence=["execution:test", "verification:test"],
        ),
        _verification(dispatch),
    )

    assert outcome.status == "completed"
    assert outcome.evidence == ["execution:test", "verification:test"]
    assert port.calls == []


def test_artifact_finalization_uses_injected_integrity_port() -> None:
    port = RecordingArtifactPort()
    service = FinalizationService(port)
    dispatch = _dispatch()
    binding = VerifiedArtifact(
        output_ref="file:///authorized/output.txt",
        sha256="0" * 64,
        size_bytes=4,
    )

    outcome = service.finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            output_ref=binding.output_ref,
        ),
        _verification(dispatch, binding=binding),
        artifact_root="/authorized",
    )

    assert outcome.status == "completed"
    assert port.calls == [(binding.output_ref, binding, "/authorized")]


def test_artifact_port_failure_preserves_fail_closed_message() -> None:
    port = RecordingArtifactPort(error="artifact binding changed")
    service = FinalizationService(port)
    dispatch = _dispatch()
    binding = VerifiedArtifact(
        output_ref="file:///authorized/output.txt",
        sha256="0" * 64,
        size_bytes=4,
    )

    with pytest.raises(FinalizationError, match="artifact binding changed"):
        service.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                output_ref=binding.output_ref,
            ),
            _verification(dispatch, binding=binding),
            artifact_root="/authorized",
        )


def test_failed_execution_with_fallback_preserves_escalated_disposition() -> None:
    service = FinalizationService(RecordingArtifactPort())
    dispatch = _dispatch(fallback=True)

    outcome = service.finalize(
        dispatch,
        ExecutionResult(dispatch_id=dispatch.dispatch_id, status="failed", failed_attempts=2),
        _verification(dispatch, status="passed"),
    )

    assert outcome.status == "escalated"
    assert outcome.failed_attempts == 2
    assert outcome.escalation_used is False


def test_application_and_port_boundaries_do_not_import_outer_adapters() -> None:
    files = [
        *sorted((PACKAGE_ROOT / "application" / "finalization").glob("*.py")),
        PACKAGE_ROOT / "ports" / "artifact.py",
    ]
    forbidden_roots = {"adapters", "artifact_integrity", "config", "engine"}
    violations: list[str] = []

    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                if name.split(".")[0] in forbidden_roots:
                    violations.append(f"{path.relative_to(PACKAGE_ROOT)} -> {name}")

    assert violations == []
