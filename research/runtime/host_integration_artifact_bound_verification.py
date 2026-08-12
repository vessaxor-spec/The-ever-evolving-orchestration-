from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Literal, Mapping, Any


class ArtifactBindingError(ValueError):
    """Raised when verification cannot remain independent or bind to the exact artifact."""


_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_HOST_CONTEXT = frozenset(
    {
        "executor_reasoning",
        "executor_messages",
        "conversation_history",
        "prior_verdict",
        "self_assessment",
    }
)


def _text(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ArtifactBindingError(f"{field_name} must be a non-empty string")
    return value.strip()


def _string_tuple(values, field_name: str) -> tuple[str, ...]:
    normalized = tuple(_text(value, field_name) for value in values)
    if not normalized:
        raise ArtifactBindingError(f"at least one {field_name} is required")
    if len(set(normalized)) != len(normalized):
        raise ArtifactBindingError(f"{field_name} values cannot contain duplicates")
    return normalized


def artifact_digest(payload: bytes | str) -> str:
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    if not isinstance(payload, bytes):
        raise ArtifactBindingError("artifact payload must be bytes or text")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


@dataclass(frozen=True, slots=True)
class ArtifactIdentity:
    task_id: str
    dispatch_id: str
    change_id: str
    artifact_id: str
    revision: str
    digest: str
    target_ref: str

    def __post_init__(self) -> None:
        for field_name in (
            "task_id",
            "dispatch_id",
            "change_id",
            "artifact_id",
            "revision",
            "target_ref",
        ):
            object.__setattr__(
                self, field_name, _text(getattr(self, field_name), field_name)
            )
        digest = _text(self.digest, "digest")
        algorithm, separator, value = digest.partition(":")
        if separator != ":" or algorithm != "sha256" or not _HEX_64.fullmatch(value):
            raise ArtifactBindingError("digest must be canonical sha256:<64 lowercase hex>")
        object.__setattr__(self, "digest", digest)


@dataclass(frozen=True, slots=True)
class IndependentVerifierRequest:
    binding: ArtifactIdentity
    task: str
    artifact_text: str
    verification_methods: tuple[str, ...]
    verifier_provider_family: str
    verifier_model: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "task", _text(self.task, "task"))
        object.__setattr__(self, "artifact_text", _text(self.artifact_text, "artifact_text"))
        object.__setattr__(
            self,
            "verification_methods",
            _string_tuple(self.verification_methods, "verification_method"),
        )
        object.__setattr__(
            self,
            "verifier_provider_family",
            _text(self.verifier_provider_family, "verifier_provider_family"),
        )
        object.__setattr__(
            self, "verifier_model", _text(self.verifier_model, "verifier_model")
        )
        object.__setattr__(
            self, "evidence_refs", _string_tuple(self.evidence_refs, "evidence_ref")
        )


def build_independent_verifier_request(
    *,
    binding: ArtifactIdentity,
    task: str,
    artifact_text: str,
    verification_methods: tuple[str, ...],
    verifier_provider_family: str,
    verifier_model: str,
    evidence_refs: tuple[str, ...],
    host_context: Mapping[str, Any] | None = None,
) -> IndependentVerifierRequest:
    """Build a verifier request from declared artifact inputs, never executor-private context."""

    host_context = host_context or {}
    forbidden = sorted(_FORBIDDEN_HOST_CONTEXT.intersection(host_context))
    if forbidden:
        raise ArtifactBindingError(
            "verifier request contains executor-derived or verdict-priming host context: "
            + ", ".join(forbidden)
        )
    if host_context:
        raise ArtifactBindingError(
            "opaque host context is not admitted to the independent verifier request: "
            + ", ".join(sorted(str(key) for key in host_context))
        )

    if artifact_digest(artifact_text) != binding.digest:
        raise ArtifactBindingError(
            "artifact_text digest does not match the artifact identity being verified"
        )

    return IndependentVerifierRequest(
        binding=binding,
        task=task,
        artifact_text=artifact_text,
        verification_methods=verification_methods,
        verifier_provider_family=verifier_provider_family,
        verifier_model=verifier_model,
        evidence_refs=evidence_refs,
    )


@dataclass(frozen=True, slots=True)
class ArtifactVerificationEvidence:
    binding: ArtifactIdentity
    verdict: Literal["passed", "failed", "needs_human"]
    verifier_id: str
    verifier_provider_family: str
    verifier_model: str
    verified_at: str
    evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.verdict not in {"passed", "failed", "needs_human"}:
            raise ArtifactBindingError(f"unsupported verdict: {self.verdict}")
        for field_name in (
            "verifier_id",
            "verifier_provider_family",
            "verifier_model",
            "verified_at",
        ):
            object.__setattr__(
                self, field_name, _text(getattr(self, field_name), field_name)
            )
        object.__setattr__(
            self, "evidence_refs", _string_tuple(self.evidence_refs, "evidence_ref")
        )


@dataclass(frozen=True, slots=True)
class FinalizationRequest:
    binding: ArtifactIdentity
    execution_status: Literal["succeeded", "failed"] = "succeeded"

    def __post_init__(self) -> None:
        if self.execution_status not in {"succeeded", "failed"}:
            raise ArtifactBindingError(
                f"unsupported execution_status: {self.execution_status}"
            )


@dataclass(frozen=True, slots=True)
class ArtifactBoundFinalization:
    status: Literal["completed"]
    binding: ArtifactIdentity
    verifier_id: str
    verifier_provider_family: str
    verifier_model: str
    evidence_refs: tuple[str, ...]


_BINDING_FIELDS = (
    "task_id",
    "dispatch_id",
    "change_id",
    "artifact_id",
    "revision",
    "digest",
    "target_ref",
)


def finalize_artifact_bound(
    request: FinalizationRequest,
    verification: ArtifactVerificationEvidence,
) -> ArtifactBoundFinalization:
    """Research-only fail-closed finalization for one exact verified artifact identity."""

    if request.execution_status != "succeeded":
        raise ArtifactBindingError("failed execution cannot be finalized as completed")
    if verification.verdict != "passed":
        raise ArtifactBindingError(
            f"verification verdict does not authorize completion: {verification.verdict}"
        )

    mismatches = tuple(
        field_name
        for field_name in _BINDING_FIELDS
        if getattr(request.binding, field_name) != getattr(verification.binding, field_name)
    )
    if mismatches:
        raise ArtifactBindingError(
            "verification evidence is not bound to the exact finalization target: "
            + ", ".join(mismatches)
        )

    return ArtifactBoundFinalization(
        status="completed",
        binding=request.binding,
        verifier_id=verification.verifier_id,
        verifier_provider_family=verification.verifier_provider_family,
        verifier_model=verification.verifier_model,
        evidence_refs=verification.evidence_refs,
    )
