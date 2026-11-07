"""T6D deterministic verifier-calibration namespace, compatibility and CLI gates."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
CONCRETE = "teo_reference.adapters.evaluation.verifier_calibration"
LEGACY = "teo_reference.verifier_calibration"


def _concrete():
    return pytest.importorskip(CONCRETE)


def test_verifier_calibration_concrete_namespace_exists() -> None:
    # RED: a concrete implementation must exist before legacy imports can delegate.
    assert importlib.util.find_spec(CONCRETE) is not None


def test_verifier_calibration_legacy_imports_preserve_all_symbol_identities() -> None:
    concrete = _concrete()
    legacy = importlib.import_module(LEGACY)

    for name, value in vars(concrete).items():
        if not (name.startswith("__") and name.endswith("__")):
            assert getattr(legacy, name) is value, f"Legacy calibration lost {name}"

    assert legacy.CalibrationError is concrete.CalibrationError
    assert legacy.CalibrationPolicy is concrete.CalibrationPolicy
    assert legacy.assess_evidence_readiness is concrete.assess_evidence_readiness
    assert legacy.main is concrete.main

    legacy_tree = ast.parse(Path(legacy.__file__).read_text(encoding="utf-8"))
    assert not any(
        isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        for node in legacy_tree.body
    )


def test_verifier_calibration_concrete_depends_only_on_existing_verifier_contracts() -> None:
    concrete = _concrete()
    tree = ast.parse(Path(concrete.__file__).read_text(encoding="utf-8"))
    package_imports = [
        (node.level, node.module)
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.level
    ]
    assert package_imports == [(3, "verification_adapter")]


def _run_cli(module: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", module, *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=30,
    )


def test_verifier_calibration_cli_preserves_help_and_deterministic_report() -> None:
    _concrete()
    for args in (
        ("--help",),
        (
            "--policy", "policy/verification/verifier-calibration.yaml",
            "--gold", "reference/datasets/verifier-calibration-gold.yaml",
        ),
    ):
        legacy = _run_cli(LEGACY, *args)
        concrete = _run_cli(CONCRETE, *args)
        assert legacy.returncode == concrete.returncode == 0, (legacy.stderr, concrete.stderr)
        assert legacy.stdout == concrete.stdout
        if "--help" not in args:
            data = json.loads(legacy.stdout)
            assert data["quality_claims_authorized"] is False
            assert data["scope_expansion_authorized"] is False
