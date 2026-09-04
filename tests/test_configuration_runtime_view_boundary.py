from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from teo_reference.adapters.configured_runtime_selection import ConfiguredRuntimeSelectionAdapter
from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_VIEW_MODULE = (
    REPO_ROOT
    / "reference/implementations/python/src/teo_reference/application/configuration/runtime_view.py"
)


def _daily_coding_task() -> TaskRequest:
    return TaskRequest.from_dict(
        {
            "task_id": "t5d-runtime-view",
            "task": "Implement a minimal backend endpoint with tests.",
            "task_type": "daily_coding",
            "risk_level": "medium",
        }
    )


def test_runtime_view_is_detached_deeply_immutable_and_container_compatible() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    view = bundle.runtime_view()

    assert isinstance(view.team_routes, dict)
    assert isinstance(view.runtime_task_routes["daily_coding"], dict)
    assert isinstance(view.worker_runtime_defaults["backend"]["fallbacks"], list)

    original_worker = view.team_routes["daily_coding"]["primary_worker"]
    original_fallbacks = list(view.worker_runtime_defaults["backend"]["fallbacks"])

    with pytest.raises(TypeError, match="runtime configuration view is immutable"):
        view.team_routes["daily_coding"]["primary_worker"] = "frontend"
    with pytest.raises(TypeError, match="runtime configuration view is immutable"):
        view.worker_runtime_defaults["backend"]["fallbacks"].append("mutation")

    bundle.team_routes["daily_coding"]["primary_worker"] = "frontend"
    bundle.worker_runtime_defaults["backend"]["fallbacks"].append("mutation")

    assert view.team_routes["daily_coding"]["primary_worker"] == original_worker
    assert list(view.worker_runtime_defaults["backend"]["fallbacks"]) == original_fallbacks
    assert bundle.runtime_view().team_routes["daily_coding"]["primary_worker"] == "frontend"


def test_engine_config_remains_mutable_compatibility_surface_outside_dispatch() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    router = OrchestrationEngine(bundle)

    assert router.config is bundle
    bundle.team_routes["daily_coding"]["verification_team"] = "verification-before-dispatch"

    dispatch = router.dispatch(_daily_coding_task())

    assert dispatch.verification.team == "verification-before-dispatch"
    assert router.config is bundle


class _MutatingRuntimeSelector:
    def __init__(self, bundle: ConfigBundle) -> None:
        self._bundle = bundle
        self._delegate = ConfiguredRuntimeSelectionAdapter(bundle.model_registry)
        self._mutated = False

    def select(self, request: Any) -> Any:
        if not self._mutated:
            self._bundle.team_routes["daily_coding"]["verification_team"] = "mutated-during-dispatch"
            self._mutated = True
        return self._delegate.select(request)


def test_dispatch_uses_one_snapshot_even_if_mutable_bundle_changes_mid_dispatch() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    expected_team = str(bundle.team_routes["daily_coding"].get("verification_team", "verification"))
    selector = _MutatingRuntimeSelector(bundle)
    router = OrchestrationEngine(bundle, runtime_selector=selector)

    dispatch = router.dispatch(_daily_coding_task())

    assert bundle.team_routes["daily_coding"]["verification_team"] == "mutated-during-dispatch"
    assert dispatch.verification.team == expected_team


def test_runtime_view_boundary_has_no_outer_layer_dependencies() -> None:
    tree = ast.parse(RUNTIME_VIEW_MODULE.read_text(encoding="utf-8"))
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert imported_modules <= {
        "__future__",
        "contextlib",
        "contextvars",
        "dataclasses",
        "pathlib",
        "typing",
    }
