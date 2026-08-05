from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "reference/datasets"


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


CONFORMANCE = load_yaml(DATASET_ROOT / "routing-conformance.yaml")
SCENARIOS = CONFORMANCE["scenarios"]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[scenario["id"] for scenario in SCENARIOS])
def test_routing_conformance_scenario(scenario: dict[str, Any]) -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(TaskRequest.from_dict(scenario["task"]))
    actual = dispatch.to_dict()
    expected = scenario["expect"]

    for dotted_path, expected_value in expected.get("equals", {}).items():
        assert value_at_path(actual, dotted_path) == expected_value, (
            f"{scenario['id']} changed {dotted_path}"
        )

    for dotted_path, expected_values in expected.get("contains", {}).items():
        actual_values = value_at_path(actual, dotted_path)
        assert isinstance(actual_values, list), f"Expected a list at {dotted_path}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"{scenario['id']} no longer contains {expected_value!r} at {dotted_path}"
            )

    assert dispatch.selected_implementation.model != dispatch.verification.implementation.model, (
        f"{scenario['id']} lost independent implementation verification"
    )


def test_configuration_warning_baseline_is_exact() -> None:
    baseline = load_yaml(DATASET_ROOT / "configuration-warning-baseline.yaml")
    issues = ConfigBundle.load(REPO_ROOT).validate()

    assert not any(issue.startswith("ERROR:") for issue in issues)
    assert issues == baseline["expected_issues"], (
        "Configuration warnings changed. Resolve the underlying inconsistency or update the "
        "versioned baseline explicitly in the same reviewed change."
    )
