from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from teo_reference.cli import main


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


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
