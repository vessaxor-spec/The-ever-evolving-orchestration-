from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from teo_reference.verification_adapter import LiveVerificationError, VERIFICATION_CHECKS
from teo_reference.verification_policy import LiveVerificationPolicy


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_live_verification_policy_loads_guarded_independent_defaults() -> None:
    policy = LiveVerificationPolicy.load(REPO_ROOT)
    assert policy.task_types == {"high_volume_simple"}
    assert policy.risk_levels == {"low", "medium"}
    assert policy.assigned_verifier_only is True
    assert policy.require_independent_model is True
    assert policy.require_provider_diversity is True
    assert policy.verifier_attempts == 1
    assert policy.verifier_retry is False
    assert policy.verifier_fallback is False
    assert policy.structured_output_required is True
    assert policy.blinded_executor_identity is True
    assert policy.expose_retry_history is False
    assert policy.expose_fallback_history is False
    assert policy.expose_runtime_telemetry is False
    assert policy.semantic_ground_truth_must_not_be_invented is True
    assert policy.infrastructure_failure_is_not_a_verification_judgment is True
    assert policy.human_approval_satisfied_by_model_verifier is False
    assert policy.checks == VERIFICATION_CHECKS
    assert policy.statuses == {"passed", "failed", "needs_human"}


@pytest.mark.parametrize(
    "mutation",
    [
        {"require_provider_diversity": False},
        {"require_independent_model": False},
        {"assigned_verifier_only": False},
        {"verifier_attempts": 2},
        {"verifier_retry": True},
        {"verifier_fallback": True},
        {"blinded_executor_identity": False},
        {"structured_output_required": False},
        {"expose_retry_history": True},
        {"expose_fallback_history": True},
        {"expose_runtime_telemetry": True},
        {"semantic_ground_truth_must_not_be_invented": False},
        {"infrastructure_failure_is_not_a_verification_judgment": False},
        {"human_approval_satisfied_by_model_verifier": True},
    ],
)
def test_live_verification_policy_rejects_authority_or_bias_weakening(mutation: dict) -> None:
    policy = LiveVerificationPolicy.load(REPO_ROOT)
    weakened = replace(policy, **mutation)
    with pytest.raises(LiveVerificationError):
        weakened.validate()
