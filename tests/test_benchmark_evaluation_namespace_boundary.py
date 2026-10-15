"""T6D1 benchmark evaluation namespace and accepted legacy import regressions."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

CASES = (
    ("benchmark_lab", "BenchmarkExperimentManifest"),
    ("benchmark_replay", "BenchmarkReplayPlan"),
    ("benchmark_verification", "BenchmarkVerifierObservation"),
    ("benchmark_conclusion", "BenchmarkConclusionRecord"),
)


@pytest.mark.parametrize("module, name", CASES)
def test_benchmark_legacy_import_identity_and_ownership(module: str, name: str) -> None:
    old = importlib.import_module(f"teo_reference.{module}")
    new = importlib.import_module(f"teo_reference.adapters.evaluation.{module}")
    package = importlib.import_module("teo_reference")
    assert getattr(old, name) is getattr(new, name)
    assert getattr(package, name) is getattr(new, name)
    for attr, value in vars(new).items():
        if not (attr.startswith("__") and attr.endswith("__")):
            assert getattr(old, attr) is value, f"{module} lost compatibility export {attr}"
    old_ast = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    new_ast = ast.parse(Path(new.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in old_ast.body)
    assert any(isinstance(node, (ast.FunctionDef, ast.ClassDef)) for node in new_ast.body)


@pytest.mark.parametrize("module, name", CASES)
def test_benchmark_evaluation_dependency_direction(module: str, name: str) -> None:
    new = importlib.import_module(f"teo_reference.adapters.evaluation.{module}")
    tree = ast.parse(Path(new.__file__).read_text(encoding="utf-8"))
    allowed_outer = {"runtime.canary", "runtime.circuit_breaker", "runtime.retry", "runtime.telemetry", "runtime.verification", "verifiers.anthropic", "verifiers.google", "verifiers.openai"}
    allowed_core = {"provider_adapter", "provider_connection", "route_outcome", "schemas", "specialist_routing", "verification_adapter", "verification_policy"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.level == 1:
                assert node.module in {"benchmark_lab", "benchmark_replay", "benchmark_verification", "benchmark_conclusion"}
            elif node.level == 2:
                assert node.module in allowed_outer
            else:
                assert node.level == 3 and node.module in allowed_core
