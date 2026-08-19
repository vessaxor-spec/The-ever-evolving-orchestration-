from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
import yaml

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine, RoutingError
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = REPO_ROOT / "reference/datasets"
PREVIEW_MODELS = ["gemini-3.1-pro"]


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


def conformance_task(data: dict[str, Any]) -> TaskRequest:
    payload = deepcopy(data)
    constraints = payload.setdefault("constraints", {})
    constraints.setdefault("accepted_preview_models", PREVIEW_MODELS)
    return TaskRequest.from_dict(payload)


CONFORMANCE = load_yaml(DATASET_ROOT / "routing-conformance.yaml")
SCENARIOS = CONFORMANCE["scenarios"]


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[scenario["id"] for scenario in SCENARIOS])
def test_routing_conformance_scenario(scenario: dict[str, Any]) -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(conformance_task(scenario["task"]))
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
    assert (
        dispatch.selected_implementation.provider_family
        != dispatch.verification.implementation.provider_family
    ), f"{scenario['id']} lost provider-diverse implementation verification"


def test_preview_model_requires_explicit_task_authorization() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    without_acceptance = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare current primary sources.",
                "task_type": "deep_research",
                "risk_level": "medium",
            }
        )
    )
    assert without_acceptance.selected_implementation.model == "gemini-3.1-pro"
    assert without_acceptance.selected_implementation.availability == "stable"

    with_acceptance = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare current primary sources.",
                "task_type": "deep_research",
                "risk_level": "medium",
                "constraints": {"accepted_preview_models": PREVIEW_MODELS},
            }
        )
    )
    assert with_acceptance.selected_implementation.model == "gemini-3.1-pro"
    assert with_acceptance.selected_implementation.availability == "stable"


def test_declared_low_risk_cannot_lower_content_derived_risk_floor() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task": "Classify the production credentials into the approved inventory labels.",
                "task_type": "high_volume_simple",
                "risk_level": "low",
            }
        )
    )
    assert dispatch.risk_level == "critical"
    assert any("could not lower" in item for item in dispatch.routing_explanation)


def test_unknown_requested_capability_fails_closed() -> None:
    engine = OrchestrationEngine(ConfigBundle.load(REPO_ROOT))
    with pytest.raises(RoutingError, match="not registered"):
        engine.dispatch(
            TaskRequest.from_dict(
                {
                    "task": "Implement a bounded backend endpoint.",
                    "task_type": "daily_coding",
                    "constraints": {"required_capabilities": ["imaginary_capability"]},
                }
            )
        )


def test_canonical_verification_policy_keys_are_resolved() -> None:
    policy = ConfigBundle.load(REPO_ROOT).routing["verification_policy"]

    for risk in ("low", "medium", "high"):
        assert policy[risk] == policy[f"{risk}_risk"]


def test_configuration_warning_baseline_is_exact() -> None:
    baseline = load_yaml(DATASET_ROOT / "configuration-warning-baseline.yaml")
    issues = ConfigBundle.load(REPO_ROOT).validate()

    assert not any(issue.startswith("ERROR:") for issue in issues)
    assert issues == baseline["expected_issues"], (
        "Configuration issues changed. Resolve the underlying inconsistency or update the "
        "versioned baseline explicitly in the same reviewed change."
    )
