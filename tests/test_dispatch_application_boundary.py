from __future__ import annotations

import inspect
from pathlib import Path

from teo_reference.application.dispatch.specialist_policy import SpecialistRoutingPolicy
from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.specialist_routing import SpecialistRoutingEngine


REPO_ROOT = Path(__file__).resolve().parents[1]
DISPATCH_PACKAGE = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "application"
    / "dispatch"
)
SPECIALIST_ROUTING_MODULE = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "specialist_routing.py"
)
SPECIALIST_POLICY_ADAPTER = (
    REPO_ROOT
    / "reference"
    / "implementations"
    / "python"
    / "src"
    / "teo_reference"
    / "adapters"
    / "specialist_selection_policy.py"
)


def test_engine_dispatch_is_a_thin_application_service_facade() -> None:
    source = inspect.getsource(OrchestrationEngine.dispatch)
    assert "self._dispatch_service.dispatch(task)" in source
    assert "selected_implementation=" not in source
    assert "uuid4" not in source


def test_dispatch_application_boundary_does_not_import_outer_engine_or_adapters() -> None:
    forbidden = (
        "teo_reference.engine",
        "from ...engine",
        "from ...adapters",
        "from ...provider_",
        "from ...cli",
        "import yaml",
    )
    for path in DISPATCH_PACKAGE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path.name} depends on outer boundary {marker}"


def test_specialist_routing_uses_composition_instead_of_engine_inheritance() -> None:
    router = SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))

    assert not issubclass(SpecialistRoutingEngine, OrchestrationEngine)
    assert isinstance(router._engine, OrchestrationEngine)
    assert router._dispatch_service is router._engine._dispatch_service
    assert router._engine._risk_refiner.__self__ is router._specialist_policy
    assert (
        router._engine._risk_refiner.__func__
        is SpecialistRoutingPolicy.refine_effective_risk
    )
    assert (
        router._engine._selection_preference_refiner.__self__
        is router._specialist_policy
    )
    assert (
        router._engine._selection_preference_refiner.__func__
        is SpecialistRoutingPolicy.refine_selection_preferences
    )


def test_specialist_policy_loading_is_outside_application_boundary() -> None:
    application_policy = (
        DISPATCH_PACKAGE / "specialist_policy.py"
    ).read_text(encoding="utf-8")
    adapter = SPECIALIST_POLICY_ADAPTER.read_text(encoding="utf-8")
    facade = SPECIALIST_ROUTING_MODULE.read_text(encoding="utf-8")

    assert "import yaml" not in application_policy
    assert "Path(" not in application_policy
    assert "import yaml" in adapter
    assert "YamlSpecialistSelectionPolicyAdapter" in facade
