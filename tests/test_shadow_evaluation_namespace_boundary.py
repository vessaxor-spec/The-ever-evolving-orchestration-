"""T6D shadow recommendation evidence namespace, public alias and dependency tests."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path


def test_shadow_evaluation_imports_keep_object_identities() -> None:
    old = importlib.import_module("teo_reference.shadow_evaluation")
    new = importlib.import_module("teo_reference.adapters.evaluation.shadow_evaluation")
    package = importlib.import_module("teo_reference")
    for name, value in vars(new).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(old, name) is value, f"shadow_evaluation lost {name}"
    assert package.ShadowRecommendationRecord is new.ShadowRecommendationRecord
    assert package.evaluate_shadow_routes is new.evaluate_shadow_routes
    tree = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body)


def test_shadow_evaluation_imports_benchmark_and_cost_from_concrete_namespace() -> None:
    new = importlib.import_module("teo_reference.adapters.evaluation.shadow_evaluation")
    tree = ast.parse(Path(new.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.level == 1:
                assert node.module in {"benchmark_conclusion", "benchmark_lab", "cost_attribution"}
            else:
                assert node.level == 3 and node.module in {"provider_adapter", "route_outcome"}
