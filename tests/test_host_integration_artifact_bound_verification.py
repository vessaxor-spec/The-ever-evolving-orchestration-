from __future__ import annotations

import runpy
from dataclasses import replace
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = (
    ROOT
    / "research"
    / "runtime"
    / "host_integration_artifact_bound_verification.py"
)
RESEARCH = runpy.run_path(str(HARNESS))
ArtifactBindingError = RESEARCH["ArtifactBindingError"]
ArtifactIdentity = RESEARCH["ArtifactIdentity"]
ArtifactVerificationEvidence = RESEARCH["ArtifactVerificationEvidence"]
FinalizationRequest = RESEARCH["FinalizationRequest"]
artifact_digest = RESEARCH["artifact_digest"]
build_independent_verifier_request = RESEARCH["build_independent_verifier_request"]
finalize_artifact_bound = RESEARCH["finalize_artifact_bound"]


ARTIFACT_TEXT = "verified artifact content"


def identity(**overrides):
    values = {
        "task_id": "task-artifact-bound",
        "dispatch_id": "dispatch-artifact-bound",
        "change_id": "change-144-next",
        "artifact_id": "workspace://repo/docs/guide.md",
        "revision": "rev-7",
        "digest": artifact_digest(ARTIFACT_TEXT),
        "target_ref": "refs/heads/codex/artifact-bound-verification",
    }
    values.update(overrides)
    return ArtifactIdentity(**values)


def evidence(binding=None, *, verdict="passed", provider="openai", model="gpt-5.6-terra"):
    return ArtifactVerificationEvidence(
        binding=binding or identity(),
        verdict=verdict,
        verifier_id=f"verifier-{provider}",
        verifier_provider_family=provider,
        verifier_model=model,
        verified_at="2026-08-12T16:45:00+00:00",
        evidence_refs=("evidence://artifact-bound/verification-1",),
    )


def test_independent_verifier_request_contains_only_declared_artifact_context() -> None:
    binding = identity()

    request = build_independent_verifier_request(
        binding=binding,
        task="Verify the exact documentation artifact.",
        artifact_text=ARTIFACT_TEXT,
        verification_methods=("output_validation", "claim_check"),
        verifier_provider_family="anthropic",
        verifier_model="claude-sonnet-5",
        evidence_refs=("evidence://source/authoritative-1",),
    )

    assert request.binding == binding
    assert request.artifact_text == ARTIFACT_TEXT
    assert request.verification_methods == ("output_validation", "claim_check")
    assert not hasattr(request, "executor_reasoning")
    assert not hasattr(request, "conversation_history")
    assert not hasattr(request, "prior_verdict")


@pytest.mark.parametrize(
    "context_key",
    (
        "executor_reasoning",
        "executor_messages",
        "conversation_history",
        "prior_verdict",
        "self_assessment",
    ),
)
def test_executor_derived_context_cannot_prime_independent_verifier(context_key) -> None:
    with pytest.raises(ArtifactBindingError, match="verdict-priming host context"):
        build_independent_verifier_request(
            binding=identity(),
            task="Verify the exact documentation artifact.",
            artifact_text=ARTIFACT_TEXT,
            verification_methods=("output_validation",),
            verifier_provider_family="anthropic",
            verifier_model="claude-sonnet-5",
            evidence_refs=("evidence://source/authoritative-1",),
            host_context={context_key: "executor-controlled value"},
        )


@pytest.mark.parametrize(
    ("provider", "model"),
    (
        ("openai", "gpt-5.6-terra"),
        ("anthropic", "claude-sonnet-5"),
        ("google", "gemini-3.6-flash"),
    ),
)
def test_exact_artifact_pass_is_provider_neutral(provider, model) -> None:
    binding = identity()

    outcome = finalize_artifact_bound(
        FinalizationRequest(binding=binding),
        evidence(binding, provider=provider, model=model),
    )

    assert outcome.status == "completed"
    assert outcome.binding == binding
    assert outcome.verifier_provider_family == provider
    assert outcome.verifier_model == model


@pytest.mark.parametrize(
    ("field_name", "mutated_value"),
    (
        ("task_id", "task-other"),
        ("dispatch_id", "dispatch-other"),
        ("change_id", "change-other"),
        ("artifact_id", "workspace://repo/docs/other.md"),
        ("revision", "rev-6"),
        ("digest", artifact_digest("content changed after verification")),
        ("target_ref", "refs/heads/other-branch"),
    ),
)
def test_artifact_binding_mutation_is_rejected(field_name, mutated_value) -> None:
    verified = identity()
    final_target = replace(verified, **{field_name: mutated_value})

    with pytest.raises(ArtifactBindingError, match=field_name):
        finalize_artifact_bound(
            FinalizationRequest(binding=final_target),
            evidence(verified),
        )


@pytest.mark.parametrize("verdict", ("failed", "needs_human"))
def test_non_pass_verdict_cannot_finalize_exact_artifact(verdict) -> None:
    binding = identity()

    with pytest.raises(ArtifactBindingError, match="does not authorize completion"):
        finalize_artifact_bound(
            FinalizationRequest(binding=binding),
            evidence(binding, verdict=verdict),
        )


def test_failed_execution_cannot_reuse_exact_artifact_pass() -> None:
    binding = identity()

    with pytest.raises(ArtifactBindingError, match="failed execution"):
        finalize_artifact_bound(
            FinalizationRequest(binding=binding, execution_status="failed"),
            evidence(binding),
        )


@pytest.mark.parametrize(
    ("field_name", "mutated_value", "message"),
    (
        ("artifact_id", "   ", "artifact_id must be a non-empty string"),
        ("digest", "sha256:not-a-real-digest", "digest must be canonical sha256"),
    ),
)
def test_malformed_artifact_identity_is_rejected(field_name, mutated_value, message) -> None:
    values = {
        "task_id": "task-artifact-bound",
        "dispatch_id": "dispatch-artifact-bound",
        "change_id": "change-144-next",
        "artifact_id": "workspace://repo/docs/guide.md",
        "revision": "rev-7",
        "digest": artifact_digest(ARTIFACT_TEXT),
        "target_ref": "refs/heads/codex/artifact-bound-verification",
    }
    values[field_name] = mutated_value

    with pytest.raises(ArtifactBindingError, match=message):
        ArtifactIdentity(**values)
