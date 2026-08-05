#!/usr/bin/env python3
"""Run one complete provider-neutral TEO dispatch lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from teo_reference import OrchestrationEngine, TaskRequest, VerificationResult
from teo_reference.schemas import ExecutionResult


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    task_data = yaml.safe_load((repo_root / "reference/examples/phase5-task.yaml").read_text())
    engine = OrchestrationEngine.from_repo(str(repo_root))
    dispatch = engine.dispatch(TaskRequest.from_dict(task_data))

    execution = ExecutionResult(
        dispatch_id=dispatch.dispatch_id,
        status="succeeded",
        output_ref="reference/implementations/python/",
        evidence=["pytest: all reference-router tests passed"],
    )
    verification = VerificationResult(
        dispatch_id=dispatch.dispatch_id,
        status="passed",
        verifier_model=dispatch.verification.implementation.model,
        checks=dispatch.verification.method,
        evidence=["independent review confirmed route, fallback, and audit behavior"],
    )
    outcome = engine.finalize(dispatch, execution, verification)
    print(json.dumps({"dispatch": dispatch.to_dict(), "outcome": outcome.to_dict()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
