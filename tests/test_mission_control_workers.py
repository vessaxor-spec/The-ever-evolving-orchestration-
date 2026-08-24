from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/mission-control-worker-conformance.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


BINDINGS = load_yaml(DATASET)["bindings"]


@pytest.mark.parametrize("fixture", BINDINGS, ids=[entry["worker"] for entry in BINDINGS])
def test_mission_control_worker_binding(fixture: dict[str, Any]) -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    specialist = bundle.specialist_registry[fixture["specialist"]]
    worker = bundle.worker_registry[fixture["worker"]]
    runtime_defaults = bundle.worker_runtime_defaults[fixture["worker"]]

    assert specialist["worker_binding"] == fixture["worker"]
    assert specialist["primary_team"] == fixture["primary_team"]
    assert specialist["risk_profile"] == fixture["risk_profile"]
    assert specialist["role_card"] == fixture["role_card"]
    assert worker["owning_team"] == fixture["primary_team"]

    for field in (
        "mission",
        "responsibilities",
        "required_capabilities",
        "verification",
        "escalation",
        "authority_boundaries",
    ):
        assert worker.get(field), f"{fixture['worker']} is missing required worker field {field}"
    for field in ("preferred_implementations", "fallbacks"):
        assert runtime_defaults.get(field), (
            f"{fixture['worker']} is missing runtime compatibility field {field}"
        )

    for field, expected_values in fixture["contains"].items():
        actual_values = worker[field]
        assert isinstance(actual_values, list), f"Expected a list at {fixture['worker']}.{field}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"{fixture['worker']} no longer contains {expected_value!r} in {field}"
            )


def test_incident_response_worker_extension_is_additive() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    assert bundle.worker_registry["incident_response"]["owning_team"] == "mission_control"
    assert bundle.worker_registry["architecture"]["owning_team"] == "planning"
    assert bundle.worker_registry["backend"]["owning_team"] == "engineering"
