"""T6B namespace and behavioral import invariants for concrete live verifiers."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
import teo_reference
from teo_reference import runtime_verification


CASES = (
    ("openai", "OpenAILiveVerifier"),
    ("google", "GoogleLiveVerifier"),
    ("anthropic", "AnthropicLiveVerifier"),
)


@pytest.mark.parametrize("provider, class_name", CASES)
def test_legacy_verifier_imports_are_identity_equivalent(provider: str, class_name: str) -> None:
    legacy = importlib.import_module(f"teo_reference.{provider}_verifier")
    outer = importlib.import_module(f"teo_reference.adapters.verifiers.{provider}")

    for name, value in vars(outer).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(legacy, name) is value, f"Legacy verifier export changed: {provider}.{name}"
    verifier = getattr(outer, class_name)
    assert getattr(teo_reference, class_name) is verifier
    assert getattr(runtime_verification, class_name) is verifier
    assert verifier.__module__ == outer.__name__


@pytest.mark.parametrize("provider, class_name", CASES)
def test_verifier_implementation_owns_behavior_and_legacy_module_is_pure_shim(
    provider: str, class_name: str
) -> None:
    legacy = importlib.import_module(f"teo_reference.{provider}_verifier")
    outer = importlib.import_module(f"teo_reference.adapters.verifiers.{provider}")
    legacy_tree = ast.parse(Path(legacy.__file__).read_text(encoding="utf-8"))
    outer_tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))

    assert not any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        for node in legacy_tree.body
    )
    assert any(
        isinstance(node, ast.ClassDef) and node.name == class_name
        for node in outer_tree.body
    )


@pytest.mark.parametrize("provider, class_name", CASES)
def test_verifier_outer_layer_does_not_import_compatibility_facades_or_runtime(
    provider: str, class_name: str
) -> None:
    outer = importlib.import_module(f"teo_reference.adapters.verifiers.{provider}")
    tree = ast.parse(Path(outer.__file__).read_text(encoding="utf-8"))
    concrete_deps = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            if node.level == 2:
                assert node.module == f"providers.{provider}"
                concrete_deps.append(node.module)
            else:
                assert node.level == 3
                assert node.module in {"provider_connection", "verification_adapter"}
    assert concrete_deps == [f"providers.{provider}"]
