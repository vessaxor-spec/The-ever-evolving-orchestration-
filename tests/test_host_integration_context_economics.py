from __future__ import annotations

import runpy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_context_economics.py"


def test_candidate_one_card_projection_materially_reduces_static_specialist_payload() -> None:
    # Non-normative research guard only. This does not authorize host integration or
    # establish a runtime context budget.
    measure = runpy.run_path(str(HARNESS))["measure_context_economics"]
    result = measure(ROOT)

    assert result["authority"] == "non_normative_research"
    assert result["measurement_scope"] == "active_specialist_role_cards_only"
    assert result["active_specialist_count"] > 1
    assert result["worst_case_payload_reduction_percent"] >= 95.0
    assert result["unmeasured"] == [
        "provider_token_usage",
        "provider_inference_latency",
        "task_adherence",
        "non_specialist_prompt_components",
    ]
