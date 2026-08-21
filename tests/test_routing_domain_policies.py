from __future__ import annotations

import ast
from pathlib import Path

import pytest

from teo_reference.domain.routing import RoutingPolicyError, assess_risk, classify_task
from teo_reference.engine import RISK_PATTERNS, TASK_PATTERNS, RoutingError
from teo_reference.schemas import RISK_ORDER, TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROUTING = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "domain"
    / "routing.py"
)


def test_explicit_task_type_is_accepted_when_supported() -> None:
    task = TaskRequest(task="Anything", task_type="daily_coding")

    task_type, reason = classify_task(task, supported_task_types={"daily_coding"})

    assert task_type == "daily_coding"
    assert reason == "Explicit task type daily_coding was accepted."


def test_unsupported_explicit_task_type_fails_closed() -> None:
    task = TaskRequest(task="Anything", task_type="invented_route")

    with pytest.raises(RoutingPolicyError, match="Unsupported explicit task type: invented_route"):
        classify_task(task, supported_task_types={"daily_coding"})


def test_keyword_classification_preserves_canonical_precedence() -> None:
    task = TaskRequest(task="Refactor the repository-wide architecture without changing behavior")

    task_type, reason = classify_task(
        task,
        supported_task_types={"repo_wide_refactor", "architecture_design"},
    )

    assert task_type == "repo_wide_refactor"
    assert reason == "Task classified as repo_wide_refactor by deterministic keyword rules."


def test_ambiguous_task_fails_closed() -> None:
    task = TaskRequest(task="Consider this request")

    with pytest.raises(RoutingPolicyError, match="Task type is ambiguous"):
        classify_task(task, supported_task_types={"daily_coding"})


def test_declared_risk_cannot_lower_content_derived_floor() -> None:
    task = TaskRequest(task="Change production authentication behavior", risk_level="low")

    risk, reason = assess_risk(task, risk_order=RISK_ORDER)

    assert risk == "high"
    assert reason == (
        "Declared risk low could not lower the content-derived high risk floor "
        "triggered by 'production'."
    )


def test_declared_risk_can_raise_content_derived_floor() -> None:
    task = TaskRequest(task="Update internal documentation", risk_level="high")

    risk, reason = assess_risk(task, risk_order=RISK_ORDER)

    assert risk == "high"
    assert reason == "Declared risk high elevated the content-derived low risk floor."


def test_engine_compatibility_surface_is_preserved() -> None:
    assert RoutingError.__module__ == "teo_reference.engine"
    assert isinstance(TASK_PATTERNS, list)
    assert isinstance(RISK_PATTERNS, dict)


def test_domain_routing_has_no_outer_layer_imports() -> None:
    tree = ast.parse(DOMAIN_ROUTING.read_text(encoding="utf-8"))
    forbidden = (
        "teo_reference.config",
        "teo_reference.provider",
        "teo_reference.runtime",
        "teo_reference.artifact",
        "teo_reference.verification",
    )
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)

    assert not [name for name in imported if name.startswith(forbidden)]
