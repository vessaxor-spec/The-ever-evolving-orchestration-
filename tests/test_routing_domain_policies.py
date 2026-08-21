from __future__ import annotations

import ast
from pathlib import Path
from types import SimpleNamespace

import pytest

from teo_reference.domain.routing import RoutingPolicyError, assess_risk, classify_task
from teo_reference.engine import RISK_PATTERNS, TASK_PATTERNS, OrchestrationEngine, RoutingError
from teo_reference.schemas import RISK_ORDER, TaskRequest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "domain"
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

    engine = OrchestrationEngine(SimpleNamespace(team_routes={"daily_coding": {}}))  # type: ignore[arg-type]
    with pytest.raises(RoutingError, match="Task type is ambiguous"):
        engine._classify_task(TaskRequest(task="Consider this request"))


def _resolve_import(path: Path, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return node.module

    relative_parent = path.relative_to(DOMAIN_ROOT).parent
    package_parts = ["teo_reference", "domain", *relative_parent.parts]
    keep = len(package_parts) - (node.level - 1)
    if keep < 0:
        return node.module
    target = package_parts[:keep]
    if node.module:
        target.extend(node.module.split("."))
    return ".".join(target)


def test_domain_package_cannot_depend_on_outer_teo_layers() -> None:
    leaks: list[str] = []
    for path in sorted(DOMAIN_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                resolved = _resolve_import(path, node)
                if resolved:
                    imports.append(resolved)

        for module in imports:
            if module.startswith("teo_reference.") and not module.startswith("teo_reference.domain"):
                leaks.append(f"{path.relative_to(REPO_ROOT)} -> {module}")

    assert leaks == []
