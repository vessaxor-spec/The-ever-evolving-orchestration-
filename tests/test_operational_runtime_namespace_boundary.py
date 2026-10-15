"""T6C: runtime implementation ownership and compatibility / dependency direction."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
import teo_reference


CASES = (
    ("runtime_canary", "canary", "CanaryRuntimeOutcome"),
    ("runtime_retry", "retry", "RetryPolicy"),
    ("runtime_circuit_breaker", "circuit_breaker", "ProviderCircuitBreaker"),
    ("runtime_telemetry", "telemetry", "RuntimeTelemetryEvent"),
    ("runtime_verification", "verification", "LiveVerificationExecution"),
)


@pytest.mark.parametrize("legacy, outer_name, representative", CASES)
def test_legacy_runtime_surfaces_remain_identical(
    legacy: str, outer_name: str, representative: str
) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    outer = importlib.import_module(f"teo_reference.adapters.runtime.{outer_name}")
    for name, value in vars(outer).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(old, name) is value, f"Runtime compatibility lost: {legacy}.{name}"
    assert getattr(old, representative) is getattr(outer, representative)
    assert getattr(teo_reference, representative) is getattr(outer, representative)
    assert getattr(outer, representative).__module__ == outer.__name__


@pytest.mark.parametrize("legacy, outer_name, representative", CASES)
def test_runtime_legacy_is_shim_and_implementation_owns_behavior(
    legacy: str, outer_name: str, representative: str
) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    outer = importlib.import_module(f"teo_reference.adapters.runtime.{outer_name}")
    legacy_tree = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    outer_tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))
    assert not any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        for node in legacy_tree.body
    )
    assert any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef))
        for node in outer_tree.body
    )


@pytest.mark.parametrize("legacy, outer_name, representative", CASES)
def test_runtime_outer_namespace_imports_do_not_depend_on_legacy_runtime_facades(
    legacy: str, outer_name: str, representative: str
) -> None:
    outer = importlib.import_module(f"teo_reference.adapters.runtime.{outer_name}")
    tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.level == 1:
                assert node.module in {
                    "canary", "retry", "circuit_breaker", "telemetry", "verification"
                }
            elif node.level == 2:
                assert node.module in {
                    "providers.anthropic", "providers.google", "providers.openai",
                    "verifiers.anthropic", "verifiers.google", "verifiers.openai",
                }
            else:
                assert node.level == 3
                assert not (node.module or "").startswith("runtime_")


def test_runtime_identity_is_not_implicitly_rehomed_with_operational_cluster() -> None:
    runtime_identity = importlib.import_module("teo_reference.runtime_identity")
    assert runtime_identity.RuntimeIdentityObservation.__module__ == "teo_reference.runtime_identity"
