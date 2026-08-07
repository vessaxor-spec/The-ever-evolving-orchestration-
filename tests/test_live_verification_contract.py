from __future__ import annotations

from pathlib import Path

import pytest

from teo_reference.verification_adapter import (
    LiveVerificationDecision,
    LiveVerificationError,
    read_execution_output,
)
from teo_reference.verification_policy import LiveVerificationPolicy


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_policy_requires_one_blinded_provider_diverse_attempt() -> None:
    policy = LiveVerificationPolicy.load(REPO_ROOT)
    assert policy.task_types == {"high_volume_simple"}
    assert policy.risk_levels == {"low", "medium"}
    assert policy.assigned_verifier_only is True
    assert policy.require_independent_model is True
    assert policy.require_provider_diversity is True
    assert policy.verifier_attempts == 1
    assert policy.verifier_retry is False
    assert policy.verifier_fallback is False
    assert policy.blinded_executor_identity is True
    assert policy.expose_retry_history is False
    assert policy.expose_fallback_history is False
    assert policy.expose_runtime_telemetry is False
    assert policy.human_approval_satisfied_by_model_verifier is False


def test_pass_requires_every_criterion_to_pass() -> None:
    with pytest.raises(LiveVerificationError, match="every criterion to pass"):
        LiveVerificationDecision(
            status="passed",
            output_present="pass",
            task_adherence="fail",
            format_consistency="pass",
            unsupported_claims_absent="pass",
            human_reason="none",
        )


def test_failed_cannot_hide_uncertainty() -> None:
    with pytest.raises(LiveVerificationError, match="no uncertain criteria"):
        LiveVerificationDecision(
            status="failed",
            output_present="pass",
            task_adherence="fail",
            format_consistency="uncertain",
            unsupported_claims_absent="pass",
            human_reason="none",
        )


def test_needs_human_requires_uncertainty_and_reason() -> None:
    with pytest.raises(LiveVerificationError, match="needs_human requires uncertainty"):
        LiveVerificationDecision(
            status="needs_human",
            output_present="pass",
            task_adherence="pass",
            format_consistency="pass",
            unsupported_claims_absent="pass",
            human_reason="insufficient_evidence",
        )


def test_output_reader_rejects_oversized_artifact(tmp_path: Path) -> None:
    path = tmp_path / "too-large.txt"
    path.write_text("x" * 65537, encoding="utf-8")
    with pytest.raises(LiveVerificationError, match="exceeds guarded verification limit"):
        read_execution_output(path.resolve().as_uri())


def test_output_reader_rejects_non_file_reference() -> None:
    with pytest.raises(LiveVerificationError, match="only local file"):
        read_execution_output("https://example.test/output.txt")
