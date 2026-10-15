"""T6D-1 cost attribution evaluation namespace, shim, and dependency contract."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import teo_reference


def test_cost_attribution_preserves_all_legacy_exports_by_identity() -> None:
    legacy = importlib.import_module("teo_reference.cost_attribution")
    implementation = importlib.import_module("teo_reference.adapters.evaluation.cost_attribution")
    for name, value in vars(implementation).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(legacy, name) is value, f"Legacy cost attribution lost {name}"
    for name in (
        "PricingCatalog", "PricingEvidenceRecord", "RouteCostAttributionRecord",
        "JsonlRouteCostAttributionSink", "attribute_route_cost", "load_pricing_evidence",
    ):
        assert getattr(teo_reference, name) is getattr(implementation, name)


def test_cost_attribution_behaviour_owned_by_outer_layer_only() -> None:
    old = importlib.import_module("teo_reference.cost_attribution")
    outer = importlib.import_module("teo_reference.adapters.evaluation.cost_attribution")
    legacy_tree = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    outer_tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in legacy_tree.body)
    assert any(isinstance(node, ast.ClassDef) and node.name == "PricingCatalog" for node in outer_tree.body)
    assert outer.PricingCatalog.__module__ == outer.__name__
    assert outer.attribute_route_cost.__module__ == outer.__name__


def test_cost_attribution_dependency_direction_is_stable() -> None:
    outer = importlib.import_module("teo_reference.adapters.evaluation.cost_attribution")
    tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))
    internal = [
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level
    ]
    assert sorted(internal) == [(3, "provider_adapter"), (3, "route_outcome")]
