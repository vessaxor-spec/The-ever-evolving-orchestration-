from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/mission-control-routing-conformance.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


def value_at_path(data: dict[str, Any], dotted_path: str) -> Any:
    value: Any = data
    for part in dotted_path.split("."):
        assert isinstance(value, dict), f"Cannot resolve {dotted_path}: {part} is not within a mapping"
        assert part in value, f"Missing expected path {dotted_path}"
        value = value[part]
    return value


SCENARIOS = load_yaml(DATASET)["scenarios"]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[scenario["id"] for scenario in SCENARIOS])
def test_mission_control_route(scenario: dict[str, Any]) -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    engine = OrchestrationEngine(bundle)
    dispatch = engine.dispatch(TaskRequest.from_dict(scenario["task"]))
    actual = dispatch.to_dict()

    assert scenario["expect"]["equals"]["task_type"] in bundle.implementation_routes

    for dotted_path, expected_value in scenario["expect"].get("equals", {}).items():
        assert value_at_path(actual, dotted_path) == expected_value, (
            f"{scenario['id']} changed {dotted_path}"
        )

    for dotted_path, expected_values in scenario["expect"].get("contains", {}).items():
        actual_values = value_at_path(actual, dotted_path)
        assert isinstance(actual_values, list), f"Expected a list at {dotted_path}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"{scenario['id']} no longer contains {expected_value!r} at {dotted_path}"
            )

    assert dispatch.selected_implementation.model != dispatch.verification.implementation.model


def test_mission_control_route_extension_is_additive() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    for route_name in ("orchestration", "operations", "project_delivery", "incident_response"):
        assert route_name in bundle.team_routes
        assert route_name in bundle.implementation_routes

    assert bundle.implementation_routes["daily_coding"]["primary"]["model"] == "gpt-5.6-terra"
