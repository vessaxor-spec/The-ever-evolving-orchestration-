from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from teo_reference.config import ConfigBundle


REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET = REPO_ROOT / "reference/datasets/market-research-worker-conformance.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"Expected a mapping in {path}"
    return data


def test_market_research_worker_binding_and_boundaries() -> None:
    fixture = load_yaml(DATASET)["binding"]
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
        assert worker.get(field), f"market_research is missing required worker field {field}"
    for field in ("preferred_implementations", "fallbacks"):
        assert runtime_defaults.get(field), f"market_research is missing runtime compatibility field {field}"

    for field, expected_values in fixture["contains"].items():
        actual_values = worker[field]
        assert isinstance(actual_values, list), f"Expected a list at market_research.{field}"
        for expected_value in expected_values:
            assert expected_value in actual_values, (
                f"market_research no longer contains {expected_value!r} in {field}"
            )


def test_market_research_worker_is_distinct_from_broad_research() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)

    assert "market_research" in bundle.worker_registry
    assert "research" in bundle.worker_registry
    assert bundle.team_routes["market_research"]["primary_worker"] == "market_research"
    assert bundle.team_routes["deep_research"]["primary_worker"] == "research"
    assert bundle.worker_registry["market_research"] != bundle.worker_registry["research"]
    assert "no_investment_decision" in bundle.worker_registry["market_research"]["authority_boundaries"]
    assert "no_final_deliverable_ownership" in bundle.worker_registry["research"]["authority_boundaries"]
