from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from teo_reference.cost_attribution import (
    BillingSurfaceContext,
    JsonlRouteCostAttributionSink,
    PricingCatalog,
    PricingEvidenceRecord,
    RouteCostAttributionRecord,
    VerificationUsageEvidence,
    attribute_route_cost,
    load_pricing_evidence,
)
from teo_reference.provider_adapter import ProviderAdapterContractError, ProviderUsage
from teo_reference.route_outcome import RouteOutcomeRecord

REPO_ROOT = Path(__file__).resolve().parents[1]
PRICING_PATH = REPO_ROOT / "reference" / "datasets" / "cost-attribution" / "pricing-evidence-v1.jsonl"
OUTCOME_PATH = REPO_ROOT / "reference" / "datasets" / "benchmark-lab" / "route-outcomes-v1.jsonl"


def _hash(payload: dict) -> str:
    data = dict(payload)
    data.pop("integrity_sha256", None)
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def pricing():
    return load_pricing_evidence(PRICING_PATH, repo_root=REPO_ROOT)


def _raw_outcomes() -> list[dict]:
    return [json.loads(line) for line in OUTCOME_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def _openai_primary_outcome() -> RouteOutcomeRecord:
    raw = next(
        deepcopy(item)
        for item in _raw_outcomes()
        if item["primary_route"]["implementation"]["model"] == "gpt-5.6-luna"
        and item["active_route_role"] == "primary"
        and item["verification_status"] == "passed"
    )
    attempt = raw["primary_route"]["attempts"][0]
    attempt["recorded_at"] = "2026-08-10T19:50:00+00:00"
    attempt["usage"] = {
        "input_tokens": 1000,
        "output_tokens": 100,
        "cached_input_tokens": 200,
        "cache_creation_input_tokens": 100,
        "reasoning_output_tokens": 20,
        "tool_tokens": 0,
        "total_tokens": 1100,
    }
    raw["recorded_at"] = "2026-08-10T19:51:00+00:00"
    raw["integrity_sha256"] = _hash(raw)
    return RouteOutcomeRecord.from_dict(raw, repo_root=REPO_ROOT)


def _fallback_outcome() -> RouteOutcomeRecord:
    raw = next(deepcopy(item) for item in _raw_outcomes() if item["active_route_role"] == "fallback")
    primary_attempt = raw["primary_route"]["attempts"][0]
    primary_attempt["recorded_at"] = "2026-08-10T19:50:00+00:00"
    primary_attempt["usage"] = {
        "input_tokens": 1000,
        "output_tokens": 100,
        "cached_input_tokens": 0,
        "cache_creation_input_tokens": 0,
        "reasoning_output_tokens": 0,
        "tool_tokens": 0,
        "total_tokens": 1100,
    }
    fallback_attempt = raw["fallback_route"]["attempts"][0]
    fallback_attempt["recorded_at"] = "2026-08-10T19:50:05+00:00"
    fallback_attempt["usage"] = {
        "input_tokens": 500,
        "output_tokens": 50,
        "cached_input_tokens": 0,
        "cache_creation_input_tokens": 0,
        "reasoning_output_tokens": 0,
        "tool_tokens": 0,
        "total_tokens": 550,
    }
    raw["recorded_at"] = "2026-08-10T19:51:00+00:00"
    raw["integrity_sha256"] = _hash(raw)
    return RouteOutcomeRecord.from_dict(raw, repo_root=REPO_ROOT)


def _verification_usage(outcome: RouteOutcomeRecord, *, when: str = "2026-08-10T19:50:10+00:00") -> VerificationUsageEvidence:
    data = outcome.to_dict()
    active = data["primary_route"] if data["active_route_role"] == "primary" else data["fallback_route"]
    return VerificationUsageEvidence(
        dispatch_id=data["provenance"]["verification_dispatch_id"],
        provider_family=active["verifier"]["provider_family"],
        model=active["verifier"]["model"],
        recorded_at=when,
        usage=ProviderUsage(
            input_tokens=500,
            output_tokens=50,
            cached_input_tokens=0,
            cache_creation_input_tokens=0,
            reasoning_output_tokens=0,
            tool_tokens=0,
            total_tokens=550,
        ),
    )


def test_first_party_pricing_dataset_is_integrity_valid_and_effective_dated() -> None:
    records = pricing()
    assert len(records) == 8
    payloads = [item.to_dict() for item in records]
    assert {item["source"]["authority_type"] for item in payloads} == {"first_party"}
    assert {item["source"]["publisher"] for item in payloads} == {"OpenAI", "Anthropic", "Google"}
    assert all(item["source"]["url"].startswith("https://") for item in payloads)
    assert any(item["effective_basis"] == "verified_from" for item in payloads)
    assert any(item["effective_until"] is not None for item in payloads)


def test_known_route_cost_preserves_execution_and_verifier_cost_separately() -> None:
    outcome = _openai_primary_outcome()
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={outcome.to_dict()["primary_route"]["dispatch_id"]: "openai_api_standard"},
            execution_additional_billable_events={outcome.to_dict()["primary_route"]["dispatch_id"]: "none"},
            verifier_surface="anthropic_api_standard",
            verifier_additional_billable_events="none",
        ),
        verification_usage=_verification_usage(outcome),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["status"] == "known"
    assert result["primary_route"]["amount"] == "0.001445"
    assert result["fallback_route"] is None
    assert result["verifier"]["amount"] == "0.0015"
    assert result["total_amount"] == "0.002945"
    assert result["primary_route"]["attempts"][0]["components"]["uncached_input"]["quantity_tokens"] == 700
    assert result["primary_route"]["attempts"][0]["components"]["cached_input"]["quantity_tokens"] == 200
    assert result["primary_route"]["attempts"][0]["components"]["cache_write_input"]["quantity_tokens"] == 100


def test_fallback_cost_is_not_hidden_inside_primary_cost() -> None:
    outcome = _fallback_outcome()
    data = outcome.to_dict()
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={
                data["primary_route"]["dispatch_id"]: "gemini_api_paid_standard",
                data["fallback_route"]["dispatch_id"]: "openai_api_standard",
            },
            execution_additional_billable_events={
                data["primary_route"]["dispatch_id"]: "none",
                data["fallback_route"]["dispatch_id"]: "none",
            },
            verifier_surface="anthropic_api_standard",
            verifier_additional_billable_events="none",
        ),
        verification_usage=_verification_usage(outcome),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["status"] == "known"
    assert result["primary_route"]["role"] == "primary"
    assert result["fallback_route"]["role"] == "fallback"
    assert result["primary_route"]["amount"] == "0.00055"
    assert result["fallback_route"]["amount"] == "0.0008"
    assert result["verifier"]["amount"] == "0.0015"
    assert result["total_amount"] == "0.00285"


def test_subscription_or_unknown_surface_is_not_assumed_to_be_api_list_price() -> None:
    outcome = _openai_primary_outcome()
    dispatch_id = outcome.to_dict()["primary_route"]["dispatch_id"]
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "codex_subscription_oauth"},
            execution_additional_billable_events={dispatch_id: "none"},
        ),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["status"] == "unknown"
    assert result["total_amount"] is None
    assert "pricing_evidence_missing_or_inapplicable" in result["primary_route"]["issues"]
    assert result["verifier"]["status"] == "unknown"


def test_unknown_additional_billable_events_refuse_monetary_total() -> None:
    outcome = _openai_primary_outcome()
    dispatch_id = outcome.to_dict()["primary_route"]["dispatch_id"]
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "openai_api_standard"},
            execution_additional_billable_events={},
        ),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["primary_route"]["status"] == "unknown"
    assert "additional_billable_events_unknown" in result["primary_route"]["issues"]
    assert result["total_amount"] is None


def test_missing_cache_split_remains_unknown_instead_of_becoming_zero() -> None:
    raw = _openai_primary_outcome().to_dict()
    raw["primary_route"]["attempts"][0]["usage"]["cached_input_tokens"] = None
    raw["integrity_sha256"] = _hash(raw)
    outcome = RouteOutcomeRecord.from_dict(raw, repo_root=REPO_ROOT)
    dispatch_id = raw["primary_route"]["dispatch_id"]
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "openai_api_standard"},
            execution_additional_billable_events={dispatch_id: "none"},
        ),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["primary_route"]["status"] == "unknown"
    assert "cached_input_tokens_unknown" in result["primary_route"]["issues"]


def test_openai_long_context_does_not_apply_base_rate_outside_evidenced_condition() -> None:
    raw = _openai_primary_outcome().to_dict()
    usage = raw["primary_route"]["attempts"][0]["usage"]
    usage.update(
        input_tokens=272001,
        cached_input_tokens=0,
        cache_creation_input_tokens=0,
        output_tokens=100,
        total_tokens=272101,
    )
    raw["integrity_sha256"] = _hash(raw)
    outcome = RouteOutcomeRecord.from_dict(raw, repo_root=REPO_ROOT)
    dispatch_id = raw["primary_route"]["dispatch_id"]
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "openai_api_standard"},
            execution_additional_billable_events={dispatch_id: "none"},
        ),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()

    assert result["primary_route"]["status"] == "unknown"
    assert "pricing_evidence_missing_or_inapplicable" in result["primary_route"]["issues"]


def test_effective_date_selects_sonnet_intro_and_post_intro_rates() -> None:
    catalog = PricingCatalog(pricing())
    intro = catalog.select(
        provider_family="anthropic",
        model="claude-sonnet-5",
        billable_surface="anthropic_api_standard",
        recorded_at="2026-08-31T23:59:59+00:00",
        input_tokens=100,
    )
    standard = catalog.select(
        provider_family="anthropic",
        model="claude-sonnet-5",
        billable_surface="anthropic_api_standard",
        recorded_at="2026-09-01T00:00:00+00:00",
        input_tokens=100,
    )
    assert intro["rates"]["uncached_input_per_1m"] == "2"
    assert intro["rates"]["output_per_1m"] == "10"
    assert standard["rates"]["uncached_input_per_1m"] == "3"
    assert standard["rates"]["output_per_1m"] == "15"


def test_overlapping_pricing_windows_fail_closed() -> None:
    first = pricing()[0].to_dict()
    second = deepcopy(first)
    second["pricing_id"] = "pricing-overlap-test"
    second["effective_from"] = "2026-08-01T00:00:00+00:00"
    second["integrity_sha256"] = _hash(second)
    overlapping = PricingEvidenceRecord.from_dict(second, repo_root=REPO_ROOT)
    with pytest.raises(ProviderAdapterContractError, match="overlapping effective windows"):
        PricingCatalog([pricing()[0], overlapping])


def test_pricing_and_cost_integrity_fail_closed_on_mutation() -> None:
    price = pricing()[0].to_dict()
    price["rates"]["output_per_1m"] = "999"
    with pytest.raises(ProviderAdapterContractError, match="Pricing evidence integrity hash"):
        PricingEvidenceRecord.from_dict(price, repo_root=REPO_ROOT)

    outcome = _openai_primary_outcome()
    dispatch_id = outcome.to_dict()["primary_route"]["dispatch_id"]
    result = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "openai_api_standard"},
            execution_additional_billable_events={dispatch_id: "none"},
            verifier_surface="anthropic_api_standard",
            verifier_additional_billable_events="none",
        ),
        verification_usage=_verification_usage(outcome),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    ).to_dict()
    result["total_amount"] = "999"
    with pytest.raises(ProviderAdapterContractError, match="Route cost attribution integrity hash"):
        RouteCostAttributionRecord.from_dict(result, repo_root=REPO_ROOT)


def test_cost_attribution_jsonl_sink_round_trip(tmp_path: Path) -> None:
    outcome = _openai_primary_outcome()
    dispatch_id = outcome.to_dict()["primary_route"]["dispatch_id"]
    record = attribute_route_cost(
        outcome,
        pricing(),
        BillingSurfaceContext(
            execution_surfaces={dispatch_id: "openai_api_standard"},
            execution_additional_billable_events={dispatch_id: "none"},
            verifier_surface="anthropic_api_standard",
            verifier_additional_billable_events="none",
        ),
        verification_usage=_verification_usage(outcome),
        repo_root=REPO_ROOT,
        attributed_at="2026-08-10T19:52:00+00:00",
    )
    sink = JsonlRouteCostAttributionSink(tmp_path / "cost.jsonl", repo_root=REPO_ROOT)
    sink.append(record)
    assert [item.to_dict() for item in sink.read_all()] == [record.to_dict()]
