from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from teo_reference.cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def plan_dispatch(tmp_path: Path) -> tuple[Path, dict]:
    task = tmp_path / "task.yaml"
    dispatch = tmp_path / "dispatch.json"
    write_yaml(
        task,
        {
            "task": "Implement a bounded backend endpoint.",
            "task_type": "daily_coding",
            "risk_level": "low",
        },
    )
    assert main(
        ["--repo-root", str(REPO_ROOT), "plan", str(task), "--output", str(dispatch)]
    ) == 0
    return dispatch, json.loads(dispatch.read_text(encoding="utf-8"))


def runtime_identity(implementation: dict, *, source: str, model: str | None = None) -> dict:
    return {
        "provider_family": implementation["provider_family"],
        "model": model or implementation["model"],
        "source": source,
        "model_observed": True,
        "configuration_fingerprint": None,
        "configuration_observed": False,
    }


def write_finalize_inputs(
    tmp_path: Path,
    dispatch: dict,
    *,
    executor_model: str | None = None,
    include_executor_identity: bool = True,
    unexpected_execution_field: bool = False,
) -> tuple[Path, Path]:
    execution = tmp_path / "execution.json"
    verification = tmp_path / "verification.json"
    execution_data = {
        "dispatch_id": dispatch["dispatch_id"],
        "status": "succeeded",
        "evidence": ["execution:test"],
    }
    if include_executor_identity:
        execution_data["observed_identity"] = runtime_identity(
            dispatch["selected_implementation"],
            source="provider_response",
            model=executor_model,
        )
    if unexpected_execution_field:
        execution_data["unexpected_authority"] = "bypass"

    verifier = dispatch["verification"]["implementation"]
    verification_data = {
        "dispatch_id": dispatch["dispatch_id"],
        "status": "passed",
        "verifier_model": verifier["model"],
        "evidence": ["verification:test"],
        "observed_identity": runtime_identity(verifier, source="verifier_response"),
    }
    write_json(execution, execution_data)
    write_json(verification, verification_data)
    return execution, verification


def test_plan_rejects_unknown_task_fields_at_schema_boundary(tmp_path: Path) -> None:
    task = tmp_path / "task.yaml"
    write_yaml(
        task,
        {
            "task": "Implement a bounded backend endpoint.",
            "task_type": "daily_coding",
            "unexpected_authority": "bypass",
        },
    )
    with pytest.raises(SystemExit) as exc:
        main(["--repo-root", str(REPO_ROOT), "plan", str(task)])
    assert exc.value.code == 2


def test_plan_rejects_unknown_constraint_fields_at_schema_boundary(tmp_path: Path) -> None:
    task = tmp_path / "task.yaml"
    write_yaml(
        task,
        {
            "task": "Implement a bounded backend endpoint.",
            "task_type": "daily_coding",
            "constraints": {"silent_preview_acceptance": True},
        },
    )
    with pytest.raises(SystemExit) as exc:
        main(["--repo-root", str(REPO_ROOT), "plan", str(task)])
    assert exc.value.code == 2


def test_plan_emits_dispatch_that_passes_strict_schema(tmp_path: Path, capsys) -> None:
    task = tmp_path / "task.yaml"
    output = tmp_path / "dispatch.json"
    write_yaml(
        task,
        {
            "task": "Implement a bounded backend endpoint.",
            "task_type": "daily_coding",
            "risk_level": "low",
        },
    )
    assert main(
        ["--repo-root", str(REPO_ROOT), "plan", str(task), "--output", str(output)]
    ) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "dispatched"
    assert payload["selected_implementation"]["model"] == "gpt-5.6-terra"
    assert json.loads(capsys.readouterr().out)["dispatch_id"] == payload["dispatch_id"]


def test_finalize_accepts_matching_executor_observed_identity(tmp_path: Path, capsys) -> None:
    dispatch_path, dispatch = plan_dispatch(tmp_path)
    capsys.readouterr()
    execution, verification = write_finalize_inputs(tmp_path, dispatch)
    output = tmp_path / "final.json"

    assert main(
        [
            "--repo-root",
            str(REPO_ROOT),
            "finalize",
            str(dispatch_path),
            str(execution),
            str(verification),
            "--output",
            str(output),
        ]
    ) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert json.loads(capsys.readouterr().out)["dispatch_id"] == dispatch["dispatch_id"]


def test_finalize_rejects_executor_observed_identity_mismatch(tmp_path: Path, capsys) -> None:
    dispatch_path, dispatch = plan_dispatch(tmp_path)
    capsys.readouterr()
    execution, verification = write_finalize_inputs(
        tmp_path,
        dispatch,
        executor_model="unexpected-executor-model",
    )

    with pytest.raises(SystemExit) as exc:
        main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "finalize",
                str(dispatch_path),
                str(execution),
                str(verification),
            ]
        )
    assert exc.value.code == 2
    assert "executor runtime identity is mismatch" in capsys.readouterr().err


def test_finalize_execution_schema_remains_strict_for_unknown_fields(
    tmp_path: Path,
    capsys,
) -> None:
    dispatch_path, dispatch = plan_dispatch(tmp_path)
    capsys.readouterr()
    execution, verification = write_finalize_inputs(
        tmp_path,
        dispatch,
        unexpected_execution_field=True,
    )

    with pytest.raises(SystemExit) as exc:
        main(
            [
                "--repo-root",
                str(REPO_ROOT),
                "finalize",
                str(dispatch_path),
                str(execution),
                str(verification),
            ]
        )
    assert exc.value.code == 2
    assert "execution input failed schema validation" in capsys.readouterr().err


def test_finalize_preserves_legacy_execution_without_observed_identity(
    tmp_path: Path,
    capsys,
) -> None:
    dispatch_path, dispatch = plan_dispatch(tmp_path)
    capsys.readouterr()
    execution, verification = write_finalize_inputs(
        tmp_path,
        dispatch,
        include_executor_identity=False,
    )

    assert main(
        [
            "--repo-root",
            str(REPO_ROOT),
            "finalize",
            str(dispatch_path),
            str(execution),
            str(verification),
        ]
    ) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "completed"
