from pathlib import Path

from teo_reference.config import ConfigBundle
from teo_reference.engine import OrchestrationEngine
from teo_reference.schemas import TaskRequest


REPO_ROOT = Path(__file__).resolve().parents[1]


def engine() -> OrchestrationEngine:
    return OrchestrationEngine(ConfigBundle.load(REPO_ROOT))


def test_preview_primary_skip_is_visible_in_dispatch_warnings() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare the current evidence.",
                "task_type": "deep_research",
                "risk_level": "low",
            }
        )
    )
    assert dispatch.selected_implementation.model == "claude-sonnet-5"
    assert any(
        "gemini-3.1-pro-preview" in warning
        and "accepted_preview_models" in warning
        for warning in dispatch.warnings
    )


def test_explicit_preview_acceptance_selects_declared_primary_without_skip_warning() -> None:
    dispatch = engine().dispatch(
        TaskRequest.from_dict(
            {
                "task": "Research and compare the current evidence.",
                "task_type": "deep_research",
                "risk_level": "low",
                "constraints": {
                    "accepted_preview_models": ["gemini-3.1-pro-preview"],
                },
            }
        )
    )
    assert dispatch.selected_implementation.model == "gemini-3.1-pro-preview"
    assert not any("was skipped" in warning for warning in dispatch.warnings)


def test_task_routing_metadata_is_not_a_selectable_implementation_route() -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    assert "task_routing" not in bundle.implementation_routes
    assert isinstance(bundle.routing.get("task_routing"), dict)
    expected = set(bundle.team_routes) - {"release"}
    assert set(bundle.implementation_routes) == expected
