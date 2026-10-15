"""T6C legacy runtime identity, implementation ownership and dependency fitness."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


CASES = (
    ("runtime_canary", "canary", "execute_guarded_canary", "CanaryRuntimeOutcome"),
    ("runtime_circuit_breaker", "circuit_breaker", "ProviderCircuitBreaker", "ProviderCircuitPolicy"),
    ("runtime_retry", "retry", "execute_with_transient_retry", "RetryPolicy"),
    ("runtime_telemetry", "telemetry", "RuntimeTelemetryEvent", "RuntimeTelemetryPolicy"),
    ("runtime_verification", "verification", "verify_guarded_canary_outcome", "LiveVerificationExecution"),
)


@pytest.mark.parametrize("legacy, module, public, support", CASES)
def test_runtime_legacy_imports_retain_identity(legacy: str, module: str, public: str, support: str) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    new = importlib.import_module(f"teo_reference.adapters.runtime.{module}")
    package = importlib.import_module("teo_reference")
    for name, value in vars(new).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(old, name) is value, f"{legacy} lost {name}"
    for name in (public, support):
        assert getattr(package, name) is getattr(new, name)


@pytest.mark.parametrize("legacy, module, public, support", CASES)
def test_runtime_implementation_ownership_and_inward_imports(legacy: str, module: str, public: str, support: str) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    new = importlib.import_module(f"teo_reference.adapters.runtime.{module}")
    old_ast = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    new_ast = ast.parse(Path(new.__file__).read_text(encoding="utf-8"))
    assert not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for n in old_ast.body)
    assert any(isinstance(n, (ast.FunctionDef, ast.ClassDef)) for n in new_ast.body)
    for node in ast.walk(new_ast):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.level == 1:
                assert node.module in {"canary", "circuit_breaker", "retry", "telemetry", "verification"}
            elif node.level == 2:
                assert node.module in {"providers.anthropic", "providers.google", "providers.openai", "verifiers.anthropic", "verifiers.google", "verifiers.openai"}
            else:
                assert node.level == 3
                assert node.module in {"provider_adapter", "provider_connection", "schemas", "specialist_routing", "runtime_identity", "verification_adapter", "verification_policy"}


def test_runtime_identity_keeps_separate_ownership() -> None:
    identity = importlib.import_module("teo_reference.runtime_identity")
    from teo_reference.provider_adapter import RuntimeIdentityObservation
    assert identity.RuntimeIdentityObservation is RuntimeIdentityObservation
    assert identity.compare_runtime_identity.__module__ == identity.__name__
