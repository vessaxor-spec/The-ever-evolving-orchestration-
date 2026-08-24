from __future__ import annotations

import inspect
from pathlib import Path

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
    )
    for path in DISPATCH_PACKAGE.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for marker in forbidden:
            assert marker not in text, f"{path.name} depends on outer boundary {marker}"


def test_specialist_routing_hooks_remain_bound_through_tranche_3_bridge() -> None:
    router = SpecialistRoutingEngine(ConfigBundle.load(REPO_ROOT))

    assert router._dispatch_service._refine_risk.__self__ is router
    assert (
        router._dispatch_service._refine_risk.__func__
        is SpecialistRoutingEngine._refine_effective_risk
    )
    assert router._implementation_selector._select_runtime.__self__ is router

    # Tranche 3 intentionally preserves the inheritance bridge. Tranche 4 owns
    # removal of this coupling after the application boundary is qualified.
    assert issubclass(SpecialistRoutingEngine, OrchestrationEngine)
