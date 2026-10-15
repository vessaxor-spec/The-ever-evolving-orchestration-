"""T6A boundary and legacy-import equivalence checks for provider execution adapters."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest
import teo_reference


CASES = (
    ("openai_adapter", "openai", "OpenAIResponsesAdapter", "execute_openai_canary_once", "OPENAI_RESPONSES_URL"),
    ("google_adapter", "google", "GeminiInteractionsAdapter", "execute_gemini_canary_once", "GEMINI_INTERACTIONS_URL"),
    ("anthropic_adapter", "anthropic", "AnthropicMessagesAdapter", "execute_anthropic_canary_once", "ANTHROPIC_MESSAGES_URL"),
)


@pytest.mark.parametrize("legacy, provider, adapter_name, execute_name, url_name", CASES)
def test_legacy_provider_surface_is_identity_equivalent(
    legacy: str, provider: str, adapter_name: str, execute_name: str, url_name: str
) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    implementation = importlib.import_module(f"teo_reference.adapters.providers.{provider}")

    for name, value in vars(implementation).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(old, name) is value, f"{legacy}.{name} lost its legacy surface"
    for name in (adapter_name, execute_name):
        assert getattr(teo_reference, name) is getattr(implementation, name)
    assert getattr(old, url_name) == getattr(implementation, url_name)
    assert getattr(old, "_extract_usage") is getattr(implementation, "_extract_usage")
    assert getattr(implementation, adapter_name).__module__ == implementation.__name__


@pytest.mark.parametrize("legacy, provider, adapter_name, execute_name, url_name", CASES)
def test_provider_implementation_owns_behavior_and_compatibility_file_is_a_shim(
    legacy: str, provider: str, adapter_name: str, execute_name: str, url_name: str
) -> None:
    old = importlib.import_module(f"teo_reference.{legacy}")
    implementation = importlib.import_module(f"teo_reference.adapters.providers.{provider}")
    old_tree = ast.parse(Path(old.__file__).read_text(encoding="utf-8"))
    implementation_tree = ast.parse(Path(implementation.__file__).read_text(encoding="utf-8"))

    assert not any(isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) for node in old_tree.body)
    assert any(isinstance(node, ast.ClassDef) and node.name == adapter_name for node in implementation_tree.body)
    assert any(isinstance(node, ast.FunctionDef) and node.name == execute_name for node in implementation_tree.body)
    for node in ast.walk(implementation_tree):
        if isinstance(node, ast.ImportFrom) and node.level:
            assert node.level == 3
            assert node.module in {"provider_adapter", "provider_connection", "schemas"}
