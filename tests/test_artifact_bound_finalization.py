from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from teo_reference.artifact_integrity import read_verified_text_artifact
from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.schemas import ExecutionResult, TaskRequest, VerificationResult, VerifiedArtifact

REPO_ROOT = Path(__file__).resolve().parents[1]


def _engine_and_dispatch():
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "task-artifact-binding",
                "task": "Classify the bounded records into the supported labels.",
                "task_type": "high_volume_simple",
                "risk_level": "low",
            }
        )
    )
    return engine, dispatch


def _artifact(tmp_path: Path, name: str = "output.txt", text: str = "label_a\n"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    output_ref = path.resolve().as_uri()
    _, binding = read_verified_text_artifact(output_ref, allowed_root=tmp_path)
    return path, output_ref, binding


def _verification(dispatch, binding: VerifiedArtifact | None) -> VerificationResult:
    return VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model=dispatch.verification.implementation.model,
        checks=["output_validation:pass"],
        evidence=["verification:test"],
        verified_artifact=binding,
    )


def test_exact_unchanged_artifact_can_finalize(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    _, output_ref, binding = _artifact(tmp_path)
    outcome = engine.finalize(
        dispatch,
        ExecutionResult(
            dispatch_id=dispatch.dispatch_id,
            status="succeeded",
            output_ref=output_ref,
            evidence=["execution:test"],
        ),
        _verification(dispatch, binding),
        artifact_root=tmp_path,
    )
    assert outcome.status == "completed"


def test_pass_without_verified_artifact_cannot_finalize_artifact(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    _, output_ref, _ = _artifact(tmp_path)
    with pytest.raises(RoutingError, match="requires exact verified artifact identity"):
        engine.finalize(
            dispatch,
            ExecutionResult(dispatch_id=dispatch.dispatch_id, status="succeeded", output_ref=output_ref),
            _verification(dispatch, None),
            artifact_root=tmp_path,
        )


def test_pass_without_authorized_root_cannot_finalize_artifact(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    _, output_ref, binding = _artifact(tmp_path)
    with pytest.raises(RoutingError, match="requires an authorized artifact_root"):
        engine.finalize(
            dispatch,
            ExecutionResult(dispatch_id=dispatch.dispatch_id, status="succeeded", output_ref=output_ref),
            _verification(dispatch, binding),
        )


def test_post_verification_mutation_invalidates_pass(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    path, output_ref, binding = _artifact(tmp_path)
    path.write_text("different-label\n", encoding="utf-8")
    with pytest.raises(RoutingError, match="does not match the exact artifact"):
        engine.finalize(
            dispatch,
            ExecutionResult(dispatch_id=dispatch.dispatch_id, status="succeeded", output_ref=output_ref),
            _verification(dispatch, binding),
            artifact_root=tmp_path,
        )


def test_sibling_artifact_substitution_invalidates_pass(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    _, _, binding = _artifact(tmp_path, "verified.txt", "label_a\n")
    _, substituted_ref, _ = _artifact(tmp_path, "substituted.txt", "label_a\n")
    with pytest.raises(RoutingError, match="does not match the exact artifact"):
        engine.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                output_ref=substituted_ref,
            ),
            _verification(dispatch, binding),
            artifact_root=tmp_path,
        )


def test_non_revalidatable_artifact_scheme_fails_closed(tmp_path: Path) -> None:
    engine, dispatch = _engine_and_dispatch()
    binding = VerifiedArtifact(
        output_ref=(tmp_path / "synthetic.txt").resolve().as_uri(),
        sha256="0" * 64,
        size_bytes=1,
    )
    with pytest.raises(RoutingError, match="only local file output artifacts"):
        engine.finalize(
            dispatch,
            ExecutionResult(
                dispatch_id=dispatch.dispatch_id,
                status="succeeded",
                output_ref="artifact://synthetic",
            ),
            _verification(dispatch, binding),
            artifact_root=tmp_path,
        )


def test_non_artifact_result_preserves_legacy_finalization() -> None:
    engine, dispatch = _engine_and_dispatch()
    outcome = engine.finalize(
        dispatch,
        ExecutionResult(dispatch_id=dispatch.dispatch_id, status="succeeded", output_ref=None),
        _verification(dispatch, None),
    )
    assert outcome.status == "completed"


def test_verified_artifact_passes_strict_verification_result_schema(tmp_path: Path) -> None:
    _, dispatch = _engine_and_dispatch()
    _, _, binding = _artifact(tmp_path)
    payload = asdict(_verification(dispatch, binding))
    schema = __import__("json").loads(
        (REPO_ROOT / "reference/schemas/verification-result.schema.json").read_text(encoding="utf-8")
    )
    assert list(Draft202012Validator(schema).iter_errors(payload)) == []
