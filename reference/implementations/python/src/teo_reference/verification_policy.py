from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from .verification_adapter import LiveVerificationError, VERIFICATION_CHECKS

LIVE_VERIFICATION_POLICY_PATH = "policy/runtime/live-verification.yaml"


@dataclass(frozen=True, slots=True)
class LiveVerificationPolicy:
    task_types: frozenset[str]
    risk_levels: frozenset[str]
    max_output_bytes: int
    assigned_verifier_only: bool
    require_independent_model: bool
    require_provider_diversity: bool
    verifier_attempts: int
    verifier_retry: bool
    verifier_fallback: bool
    structured_output_required: bool
    blinded_executor_identity: bool
    artifact_root_confinement: bool
    candidate_output_is_untrusted_data: bool
    expose_retry_history: bool
    expose_fallback_history: bool
    expose_runtime_telemetry: bool
    semantic_ground_truth_must_not_be_invented: bool
    infrastructure_failure_is_not_a_verification_judgment: bool
    human_approval_satisfied_by_model_verifier: bool
    status_precedence: tuple[str, ...]
    checks: tuple[str, ...]
    statuses: frozenset[str]

    @classmethod
    def load(cls, repo_root: str | Path) -> "LiveVerificationPolicy":
        path = Path(repo_root) / LIVE_VERIFICATION_POLICY_PATH
        if not path.is_file():
            raise LiveVerificationError(f"Live verification policy not found: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("status") != "active":
            raise LiveVerificationError("Live verification policy must be an active mapping")
        scope = data.get("scope")
        verification = data.get("verification")
        if not isinstance(scope, dict) or not isinstance(verification, dict):
            raise LiveVerificationError("Live verification policy requires scope and verification mappings")
        policy = cls(
            task_types=frozenset(str(item) for item in scope.get("task_types", [])),
            risk_levels=frozenset(str(item) for item in scope.get("risk_levels", [])),
            max_output_bytes=int(scope.get("max_output_bytes", 0)),
            assigned_verifier_only=bool(verification.get("assigned_verifier_only", False)),
            require_independent_model=bool(verification.get("require_independent_model", False)),
            require_provider_diversity=bool(verification.get("require_provider_diversity", False)),
            verifier_attempts=int(verification.get("verifier_attempts", 0)),
            verifier_retry=bool(verification.get("verifier_retry", False)),
            verifier_fallback=bool(verification.get("verifier_fallback", False)),
            structured_output_required=bool(verification.get("structured_output_required", False)),
            blinded_executor_identity=bool(verification.get("blinded_executor_identity", False)),
            artifact_root_confinement=bool(verification.get("artifact_root_confinement", False)),
            candidate_output_is_untrusted_data=bool(
                verification.get("candidate_output_is_untrusted_data", False)
            ),
            expose_retry_history=bool(verification.get("expose_retry_history", False)),
            expose_fallback_history=bool(verification.get("expose_fallback_history", False)),
            expose_runtime_telemetry=bool(verification.get("expose_runtime_telemetry", False)),
            semantic_ground_truth_must_not_be_invented=bool(
                verification.get("semantic_ground_truth_must_not_be_invented", False)
            ),
            infrastructure_failure_is_not_a_verification_judgment=bool(
                verification.get("infrastructure_failure_is_not_a_verification_judgment", False)
            ),
            human_approval_satisfied_by_model_verifier=bool(
                verification.get("human_approval_satisfied_by_model_verifier", False)
            ),
            status_precedence=tuple(str(item) for item in verification.get("status_precedence", [])),
            checks=tuple(str(item) for item in verification.get("checks", [])),
            statuses=frozenset(str(item) for item in verification.get("statuses", [])),
        )
        policy.validate()
        return policy

    def validate(self) -> None:
        if self.task_types != {"high_volume_simple"}:
            raise LiveVerificationError("Guarded live verification must remain scoped to high_volume_simple")
        if self.risk_levels != {"low", "medium"}:
            raise LiveVerificationError("Guarded live verification must remain low/medium risk only")
        if self.max_output_bytes != 65536:
            raise LiveVerificationError("Guarded live verification output bound must remain 65536 bytes")
        if not self.assigned_verifier_only:
            raise LiveVerificationError("Live verification must use only the dispatch-assigned verifier")
        if not self.require_independent_model or not self.require_provider_diversity:
            raise LiveVerificationError("Live verification must require model and provider independence")
        if self.verifier_attempts != 1 or self.verifier_retry or self.verifier_fallback:
            raise LiveVerificationError("Guarded live verifier must perform exactly one attempt with no retry or fallback")
        if not self.structured_output_required or not self.blinded_executor_identity:
            raise LiveVerificationError("Live verification requires structured output and blinded executor identity")
        if not self.artifact_root_confinement:
            raise LiveVerificationError("Live verification must confine execution artifacts to the authorized root")
        if not self.candidate_output_is_untrusted_data:
            raise LiveVerificationError("Live verification must treat candidate output as untrusted data")
        if self.expose_retry_history or self.expose_fallback_history or self.expose_runtime_telemetry:
            raise LiveVerificationError("Live verifier must not receive retry, fallback, or telemetry history")
        if not self.semantic_ground_truth_must_not_be_invented:
            raise LiveVerificationError("Live verifier must not invent absent semantic ground truth")
        if not self.infrastructure_failure_is_not_a_verification_judgment:
            raise LiveVerificationError("Verification infrastructure failure must fail closed outside model judgment")
        if self.human_approval_satisfied_by_model_verifier:
            raise LiveVerificationError("Model verification cannot satisfy qualified-human approval")
        if self.status_precedence != (
            "any_fail_means_failed",
            "otherwise_any_uncertain_means_needs_human",
            "otherwise_passed",
        ):
            raise LiveVerificationError("Live verification status precedence must remain fail, uncertain, pass")
        if self.checks != VERIFICATION_CHECKS:
            raise LiveVerificationError("Live verification checks must match the fixed guarded rubric")
        if self.statuses != {"passed", "failed", "needs_human"}:
            raise LiveVerificationError("Live verification statuses must remain passed/failed/needs_human")
