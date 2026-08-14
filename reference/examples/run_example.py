#!/usr/bin/env python3
"""Run one complete provider-neutral TEO dispatch lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from teo_reference import OrchestrationEngine, TaskRequest, VerificationResult
from teo_reference.artifact_integrity import read_verified_text_artifact
from teo_reference.schemas import ExecutionResult


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    task_data = yaml.safe_load((repo_root / "reference/examples/phase5-task.yaml").read_text())
    engine = OrchestrationEngine.from_repo(str(repo_root))
    dispatch = engine.dispatch(TaskRequest.from_dict(task_data))

    artifact_root = repo_root / ".teo" / "reference-example"
    artifact_root.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_root / "execution-output.txt"
    artifact_path.write_text("provider-neutral reference lifecycle output\n", encoding="utf-8")
    output_ref = artifact_path.resolve().as_uri()
    _, verified_artifact = read_verified_text_artifact(
        output_ref,
        allowed_root=artifact_root,
    )

    execution = ExecutionResult(
        dispatch_id=dispatch.dispatch_id,
        status="succeeded",
        output_ref=output_ref,
        evidence=["reference example execution artifact created"],
    )
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model=dispatch.verification.implementation.model,
        checks=dispatch.verification.method,
        evidence=["reference example verification fixture accepted the bound artifact"],
        verified_artifact=verified_artifact,
    )
    outcome = engine.finalize(
        dispatch,
        execution,
        verification,
        artifact_root=artifact_root,
    )
    print(json.dumps({"dispatch": dispatch.to_dict(), "outcome": outcome.to_dict()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
