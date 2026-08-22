from __future__ import annotations

import json
from pathlib import Path

import pytest

from teo_reference.adapters.configured_runtime_selection import ConfiguredRuntimeSelectionAdapter
from teo_reference.config import ConfigBundle
from teo_reference.schemas import TaskRequest
from teo_reference.specialist_routing import SpecialistRoutingEngine

REPO_ROOT = Path(__file__).resolve().parents[1]


class RecordingSelector:
    def __init__(self, delegate) -> None:
        self.delegate = delegate
        self.requests = []
        self.decisions = []

    def select(self, request):
        self.requests.append(request)
        decision = self.delegate.select(request)
        self.decisions.append(decision)
        return decision


@pytest.mark.parametrize(
    "constraints",
    (
        {"blocked_implementations": ["claude-sonnet-5"]},
        {"blocked_providers": ["anthropic"]},
    ),
)
def test_documentation_failure_redispatch_selects_fresh_verifier_through_runtime_lifecycle(
    constraints: dict[str, list[str]],
) -> None:
    bundle = ConfigBundle.load(REPO_ROOT)
    selector = RecordingSelector(ConfiguredRuntimeSelectionAdapter(bundle.model_registry))
    engine = SpecialistRoutingEngine(bundle, runtime_selector=selector)

    dispatch = engine.dispatch(
        TaskRequest.from_dict(
            {
                "task_id": "documentation-recovery-runtime-binding",
                "task": "Draft a short technical note from bounded facts.",
                "task_type": "documentation",
                "risk_level": "low",
                "constraints": constraints,
            }
        )
    )

    assert dispatch.selected_implementation.provider_family == "openai"
    assert dispatch.selected_implementation.model == "gpt-5.6-sol"
    assert dispatch.verification.implementation.provider_family == "google"
    assert dispatch.verification.implementation.model == "gemini-3.7-flash"
    assert dispatch.verification.implementation.reasoning == "medium"

    verifier_request = selector.requests[-1]
    verifier_decision = selector.decisions[-1]
    assert verifier_request.scope.role == "verifier"
    assert verifier_decision.selected.implementation.configuration.model == "gemini-3.7-flash"
    encoded_effort = dict(
        verifier_decision.selected.implementation.configuration.reasoning_controls
    )["effort"]
    assert json.loads(encoded_effort) == "medium"
