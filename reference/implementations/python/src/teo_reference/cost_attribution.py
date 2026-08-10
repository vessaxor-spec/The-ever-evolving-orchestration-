from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from jsonschema import Draft202012Validator

from .provider_adapter import ProviderAdapterContractError, ProviderUsage
from .route_outcome import RouteOutcomeRecord

COST_ATTRIBUTION_VERSION = "1"
PRICING_EVIDENCE_SCHEMA_PATH = "reference/schemas/pricing-evidence.schema.json"
ROUTE_COST_ATTRIBUTION_SCHEMA_PATH = "reference/schemas/route-cost-attribution.schema.json"
AdditionalBillableEventsStatus = Literal["none", "unknown"]


def _canonical_sha256(data: Mapping[str, Any], *, omit: str | None = None) -> str:
    canonical = dict(data)
    if omit is not None:
        canonical.pop(omit, None)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _load_schema(repo_root: str | Path, relative_path: str) -> dict[str, Any]:
    path = Path(repo_root) / relative_path
    if not path.is_file():
        raise ProviderAdapterContractError(f"Cost attribution schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(f"Cost attribution schema could not be loaded: {path}") from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Cost attribution schema must be an object")
    return raw


def _validate_schema(
    data: dict[str, Any],
    *,
    repo_root: str | Path,
    relative_path: str,
    label: str,
) -> None:
    validator = Draft202012Validator(_load_schema(repo_root, relative_path))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(item) for item in first.path) or "<root>"
        raise ProviderAdapterContractError(
            f"{label} schema validation failed at {path}: {first.message}"
        )


def _parse_datetime(value: str, name: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(f"Cost attribution {name} is required")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProviderAdapterContractError(f"Cost attribution {name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ProviderAdapterContractError(f"Cost attribution {name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _decimal(value: str | None, name: str) -> Decimal | None:
    if value is None:
        return None
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ProviderAdapterContractError(f"Cost attribution {name} must be decimal text") from exc
    if result < 0:
        raise ProviderAdapterContractError(f"Cost attribution {name} cannot be negative")
    return result


def _decimal_text(value: Decimal) -> str:
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


@dataclass(frozen=True, slots=True)
class PricingEvidenceRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "PricingEvidenceRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=PRICING_EVIDENCE_SCHEMA_PATH,
            label="Pricing evidence",
        )
        effective_from = _parse_datetime(data["effective_from"], "pricing effective_from")
        effective_until = (
            _parse_datetime(data["effective_until"], "pricing effective_until")
            if data["effective_until"] is not None
            else None
        )
        if effective_until is not None and effective_until <= effective_from:
            raise ProviderAdapterContractError(
                "Pricing evidence effective_until must be later than effective_from"
            )
        verified_at = _parse_datetime(data["source"]["verified_at"], "pricing source verified_at")
        if data["effective_basis"] == "verified_from" and effective_from > verified_at:
            raise ProviderAdapterContractError(
                "verified_from pricing cannot begin after its verification timestamp"
            )
        for name, value in data["rates"].items():
            _decimal(value, f"pricing rate {name}")
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError("Pricing evidence integrity hash does not match content")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class VerificationUsageEvidence:
    dispatch_id: str
    provider_family: str
    model: str
    recorded_at: str
    usage: ProviderUsage

    def __post_init__(self) -> None:
        if not self.dispatch_id.strip() or not self.provider_family.strip() or not self.model.strip():
            raise ProviderAdapterContractError(
                "Verification cost evidence requires dispatch, provider, and model identity"
            )
        _parse_datetime(self.recorded_at, "verification usage recorded_at")


@dataclass(frozen=True, slots=True)
class BillingSurfaceContext:
    execution_surfaces: Mapping[str, str]
    execution_additional_billable_events: Mapping[str, AdditionalBillableEventsStatus] | None = None
    verifier_surface: str | None = None
    verifier_additional_billable_events: AdditionalBillableEventsStatus = "unknown"

    def __post_init__(self) -> None:
        for dispatch_id, surface in self.execution_surfaces.items():
            if not str(dispatch_id).strip() or not str(surface).strip():
                raise ProviderAdapterContractError(
                    "Billing surface context requires non-empty dispatch and surface identity"
                )
        for dispatch_id, status in (self.execution_additional_billable_events or {}).items():
            if dispatch_id not in self.execution_surfaces:
                raise ProviderAdapterContractError(
                    "Additional-billable-event status references an unknown execution dispatch"
                )
            if status not in {"none", "unknown"}:
                raise ProviderAdapterContractError(
                    "Additional-billable-event status must be none or unknown"
                )
        if self.verifier_surface is not None and not self.verifier_surface.strip():
            raise ProviderAdapterContractError("Verifier billable surface cannot be blank")
        if self.verifier_additional_billable_events not in {"none", "unknown"}:
            raise ProviderAdapterContractError(
                "Verifier additional-billable-event status must be none or unknown"
            )


@dataclass(frozen=True, slots=True)
class RouteCostAttributionRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "RouteCostAttributionRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=ROUTE_COST_ATTRIBUTION_SCHEMA_PATH,
            label="Route cost attribution",
        )
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError(
                "Route cost attribution integrity hash does not match content"
            )
        _validate_attribution_semantics(data)
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def _validate_attribution_semantics(data: dict[str, Any]) -> None:
    components: list[dict[str, Any]] = [data["primary_route"]]
    if data["fallback_route"] is not None:
        components.append(data["fallback_route"])
    verifier = data["verifier"]
    statuses = [item["status"] for item in components]
    if verifier["status"] != "not_performed":
        statuses.append(verifier["status"])
    if data["status"] == "known":
        if any(status != "known" for status in statuses) or data["total_amount"] is None:
            raise ProviderAdapterContractError(
                "Known route cost attribution requires every performed component to be known"
            )
    elif data["total_amount"] is not None:
        raise ProviderAdapterContractError(
            "Partial or unknown route cost attribution cannot publish a total amount"
        )
    if verifier["status"] == "not_performed" and verifier["amount"] != "0":
        raise ProviderAdapterContractError("Unperformed verification must have zero cost")


class PricingCatalog:
    def __init__(self, records: Sequence[PricingEvidenceRecord]) -> None:
        payloads = [record.to_dict() for record in records]
        ids = [str(item["pricing_id"]) for item in payloads]
        if len(ids) != len(set(ids)):
            raise ProviderAdapterContractError("Pricing evidence IDs must be unique")
        self._records = tuple(payloads)
        self._validate_ambiguity()

    def _validate_ambiguity(self) -> None:
        groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
        for item in self._records:
            key = (
                str(item["provider_family"]),
                str(item["model"]),
                str(item["billable_surface"]),
                str(item["processing_mode"]),
            )
            groups.setdefault(key, []).append(item)
        for key, records in groups.items():
            ordered = sorted(records, key=lambda item: _parse_datetime(item["effective_from"], "effective_from"))
            for left, right in zip(ordered, ordered[1:]):
                left_until = (
                    _parse_datetime(left["effective_until"], "effective_until")
                    if left["effective_until"] is not None
                    else None
                )
                right_from = _parse_datetime(right["effective_from"], "effective_from")
                if left_until is None or left_until > right_from:
                    raise ProviderAdapterContractError(
                        "Pricing evidence contains overlapping effective windows for "
                        + "/".join(key)
                    )

    def select(
        self,
        *,
        provider_family: str,
        model: str,
        billable_surface: str,
        recorded_at: str,
        input_tokens: int | None,
    ) -> dict[str, Any] | None:
        timestamp = _parse_datetime(recorded_at, "attempt recorded_at")
        matches: list[dict[str, Any]] = []
        for item in self._records:
            if (
                item["provider_family"] != provider_family
                or item["model"] != model
                or item["billable_surface"] != billable_surface
                or item["processing_mode"] != "standard"
            ):
                continue
            start = _parse_datetime(item["effective_from"], "effective_from")
            end = (
                _parse_datetime(item["effective_until"], "effective_until")
                if item["effective_until"] is not None
                else None
            )
            if timestamp < start or (end is not None and timestamp >= end):
                continue
            max_input = item["conditions"]["max_input_tokens_inclusive"]
            if max_input is not None and input_tokens is not None and input_tokens > max_input:
                continue
            matches.append(item)
        if len(matches) > 1:
            raise ProviderAdapterContractError(
                f"Ambiguous pricing evidence for {provider_family}/{model}/{billable_surface}"
            )
        return matches[0] if matches else None


def load_pricing_evidence(
    path: str | Path,
    *,
    repo_root: str | Path,
) -> list[PricingEvidenceRecord]:
    file_path = Path(path)
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProviderAdapterContractError(f"Could not read pricing evidence JSONL: {file_path}") from exc
    records: list[PricingEvidenceRecord] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProviderAdapterContractError(
                f"Invalid pricing evidence JSONL at line {index}"
            ) from exc
        if not isinstance(raw, dict):
            raise ProviderAdapterContractError(
                f"Pricing evidence JSONL line {index} must be an object"
            )
        records.append(PricingEvidenceRecord.from_dict(raw, repo_root=repo_root))
    PricingCatalog(records)
    return records


def _component(quantity: int, rate: Decimal) -> dict[str, Any]:
    amount = Decimal(quantity) * rate / Decimal(1_000_000)
    return {
        "quantity_tokens": quantity,
        "rate_per_1m": _decimal_text(rate),
        "amount": _decimal_text(amount),
    }


def _unknown_attempt(
    *,
    attempt_number: int,
    recorded_at: str,
    provider_family: str,
    model: str,
    billable_surface: str | None,
    additional_status: AdditionalBillableEventsStatus,
    usage: dict[str, Any] | None,
    pricing_id: str | None,
    issues: Sequence[str],
) -> dict[str, Any]:
    return {
        "attempt_number": attempt_number,
        "recorded_at": recorded_at,
        "provider_family": provider_family,
        "model": model,
        "billable_surface": billable_surface,
        "additional_billable_events_status": additional_status,
        "status": "unknown",
        "usage": usage,
        "pricing_evidence_id": pricing_id,
        "components": {
            "uncached_input": None,
            "cached_input": None,
            "cache_write_input": None,
            "output": None,
        },
        "amount": None,
        "issues": sorted(set(issues)),
    }


def _cost_usage(
    *,
    attempt_number: int,
    recorded_at: str,
    provider_family: str,
    model: str,
    billable_surface: str | None,
    additional_status: AdditionalBillableEventsStatus,
    usage: ProviderUsage | None,
    catalog: PricingCatalog,
) -> dict[str, Any]:
    usage_data = usage.to_dict() if usage is not None else None
    issues: list[str] = []
    if billable_surface is None:
        issues.append("billable_surface_unknown")
    if additional_status != "none":
        issues.append("additional_billable_events_unknown")
    if usage is None:
        issues.append("usage_unknown")
    if issues:
        return _unknown_attempt(
            attempt_number=attempt_number,
            recorded_at=recorded_at,
            provider_family=provider_family,
            model=model,
            billable_surface=billable_surface,
            additional_status=additional_status,
            usage=usage_data,
            pricing_id=None,
            issues=issues,
        )

    assert usage is not None and billable_surface is not None
    pricing = catalog.select(
        provider_family=provider_family,
        model=model,
        billable_surface=billable_surface,
        recorded_at=recorded_at,
        input_tokens=usage.input_tokens,
    )
    if pricing is None:
        return _unknown_attempt(
            attempt_number=attempt_number,
            recorded_at=recorded_at,
            provider_family=provider_family,
            model=model,
            billable_surface=billable_surface,
            additional_status=additional_status,
            usage=usage_data,
            pricing_id=None,
            issues=["pricing_evidence_missing_or_inapplicable"],
        )

    pricing_id = str(pricing["pricing_id"])
    rates = pricing["rates"]
    conditions = pricing["conditions"]
    if usage.input_tokens is None:
        issues.append("input_tokens_unknown")
    if usage.output_tokens is None:
        issues.append("output_tokens_unknown")
    if usage.cached_input_tokens is None:
        issues.append("cached_input_tokens_unknown")
    if usage.cache_creation_input_tokens is None:
        if rates["cache_write_input_per_1m"] is not None:
            issues.append("cache_creation_input_tokens_unknown")
    if usage.tool_tokens not in {None, 0} and conditions["tool_tokens_billing"] == "unmodeled":
        issues.append("tool_token_billing_unmodeled")
    if usage.reasoning_output_tokens not in {None, 0} and conditions["reasoning_tokens_billing"] == "unmodeled":
        issues.append("reasoning_token_billing_unmodeled")
    if usage.cached_input_tokens not in {None, 0} and rates["cached_input_per_1m"] is None:
        issues.append("cached_input_rate_unknown")
    if usage.cache_creation_input_tokens not in {None, 0} and rates["cache_write_input_per_1m"] is None:
        issues.append("cache_write_input_rate_unknown")
    if rates["uncached_input_per_1m"] is None:
        issues.append("uncached_input_rate_unknown")
    if rates["output_per_1m"] is None:
        issues.append("output_rate_unknown")

    if issues:
        return _unknown_attempt(
            attempt_number=attempt_number,
            recorded_at=recorded_at,
            provider_family=provider_family,
            model=model,
            billable_surface=billable_surface,
            additional_status=additional_status,
            usage=usage_data,
            pricing_id=pricing_id,
            issues=issues,
        )

    assert usage.input_tokens is not None
    assert usage.output_tokens is not None
    assert usage.cached_input_tokens is not None
    cached = usage.cached_input_tokens
    cache_write = usage.cache_creation_input_tokens or 0
    uncached = usage.input_tokens - cached - cache_write
    if uncached < 0:
        return _unknown_attempt(
            attempt_number=attempt_number,
            recorded_at=recorded_at,
            provider_family=provider_family,
            model=model,
            billable_surface=billable_surface,
            additional_status=additional_status,
            usage=usage_data,
            pricing_id=pricing_id,
            issues=["normalized_input_components_exceed_input_tokens"],
        )

    uncached_rate = _decimal(rates["uncached_input_per_1m"], "uncached input rate")
    output_rate = _decimal(rates["output_per_1m"], "output rate")
    assert uncached_rate is not None and output_rate is not None
    cached_rate = _decimal(rates["cached_input_per_1m"], "cached input rate")
    cache_write_rate = _decimal(rates["cache_write_input_per_1m"], "cache write rate")

    components: dict[str, Any] = {
        "uncached_input": _component(uncached, uncached_rate),
        "cached_input": _component(cached, cached_rate) if cached_rate is not None else None,
        "cache_write_input": (
            _component(cache_write, cache_write_rate) if cache_write_rate is not None else None
        ),
        "output": _component(usage.output_tokens, output_rate),
    }
    amount = sum(
        (
            Decimal(component["amount"])
            for component in components.values()
            if component is not None
        ),
        Decimal(0),
    )
    return {
        "attempt_number": attempt_number,
        "recorded_at": recorded_at,
        "provider_family": provider_family,
        "model": model,
        "billable_surface": billable_surface,
        "additional_billable_events_status": additional_status,
        "status": "known",
        "usage": usage_data,
        "pricing_evidence_id": pricing_id,
        "components": components,
        "amount": _decimal_text(amount),
        "issues": [],
    }


def _route_cost(
    route: dict[str, Any],
    *,
    billing: BillingSurfaceContext,
    catalog: PricingCatalog,
) -> dict[str, Any]:
    dispatch_id = str(route["dispatch_id"])
    surface = billing.execution_surfaces.get(dispatch_id)
    additional_status = (billing.execution_additional_billable_events or {}).get(
        dispatch_id, "unknown"
    )
    attempts = [
        _cost_usage(
            attempt_number=int(attempt["attempt_number"]),
            recorded_at=str(attempt["recorded_at"]),
            provider_family=str(attempt["provider_family"]),
            model=str(attempt["model"]),
            billable_surface=surface,
            additional_status=additional_status,
            usage=ProviderUsage.from_dict(attempt["usage"]) if attempt["usage"] is not None else None,
            catalog=catalog,
        )
        for attempt in route["attempts"]
    ]
    known = [item for item in attempts if item["status"] == "known"]
    unknown = [item for item in attempts if item["status"] == "unknown"]
    if not attempts or not unknown:
        status = "known"
        amount = _decimal_text(
            sum((Decimal(item["amount"]) for item in known), Decimal(0))
        )
    elif known:
        status = "partial"
        amount = None
    else:
        status = "unknown"
        amount = None
    issues = sorted(
        {
            issue
            for attempt in attempts
            for issue in attempt["issues"]
        }
    )
    return {
        "dispatch_id": dispatch_id,
        "role": route["role"],
        "status": status,
        "attempts": attempts,
        "amount": amount,
        "issues": issues,
    }


def _verifier_cost(
    outcome: dict[str, Any],
    *,
    billing: BillingSurfaceContext,
    verification_usage: VerificationUsageEvidence | None,
    catalog: PricingCatalog,
) -> dict[str, Any]:
    verification_dispatch_id = outcome["provenance"]["verification_dispatch_id"]
    empty_components = {
        "uncached_input": None,
        "cached_input": None,
        "cache_write_input": None,
        "output": None,
    }
    if verification_dispatch_id is None:
        return {
            "dispatch_id": None,
            "provider_family": None,
            "model": None,
            "recorded_at": None,
            "billable_surface": None,
            "additional_billable_events_status": "none",
            "status": "not_performed",
            "usage": None,
            "pricing_evidence_id": None,
            "components": empty_components,
            "amount": "0",
            "issues": [],
        }
    active_role = outcome["active_route_role"]
    active = (
        outcome["primary_route"]
        if active_role == "primary"
        else outcome["fallback_route"]
    )
    if active is None:
        raise ProviderAdapterContractError(
            "Verification cost requires an active route when verification provenance exists"
        )
    verifier = active["verifier"]
    if verification_usage is None:
        return {
            "dispatch_id": verification_dispatch_id,
            "provider_family": verifier["provider_family"],
            "model": verifier["model"],
            "recorded_at": None,
            "billable_surface": billing.verifier_surface,
            "additional_billable_events_status": billing.verifier_additional_billable_events,
            "status": "unknown",
            "usage": None,
            "pricing_evidence_id": None,
            "components": empty_components,
            "amount": None,
            "issues": ["verifier_usage_unknown"],
        }
    if verification_usage.dispatch_id != verification_dispatch_id:
        raise ProviderAdapterContractError(
            "Verification cost usage belongs to a different dispatch"
        )
    if verification_usage.provider_family != verifier["provider_family"]:
        raise ProviderAdapterContractError(
            "Verification cost usage changed the assigned verifier provider"
        )
    if verification_usage.model != verifier["model"]:
        raise ProviderAdapterContractError(
            "Verification cost usage changed the assigned verifier model"
        )
    attempt = _cost_usage(
        attempt_number=1,
        recorded_at=verification_usage.recorded_at,
        provider_family=verification_usage.provider_family,
        model=verification_usage.model,
        billable_surface=billing.verifier_surface,
        additional_status=billing.verifier_additional_billable_events,
        usage=verification_usage.usage,
        catalog=catalog,
    )
    return {
        "dispatch_id": verification_dispatch_id,
        "provider_family": verification_usage.provider_family,
        "model": verification_usage.model,
        "recorded_at": verification_usage.recorded_at,
        "billable_surface": attempt["billable_surface"],
        "additional_billable_events_status": attempt["additional_billable_events_status"],
        "status": attempt["status"],
        "usage": attempt["usage"],
        "pricing_evidence_id": attempt["pricing_evidence_id"],
        "components": attempt["components"],
        "amount": attempt["amount"],
        "issues": attempt["issues"],
    }


def attribute_route_cost(
    outcome: RouteOutcomeRecord,
    pricing_records: Sequence[PricingEvidenceRecord],
    billing: BillingSurfaceContext,
    *,
    repo_root: str | Path,
    verification_usage: VerificationUsageEvidence | None = None,
    attributed_at: str | None = None,
) -> RouteCostAttributionRecord:
    """Create reproducible cost evidence without modifying canonical route outcomes."""
    outcome_data = outcome.to_dict()
    catalog = PricingCatalog(pricing_records)
    primary = _route_cost(outcome_data["primary_route"], billing=billing, catalog=catalog)
    fallback = (
        _route_cost(outcome_data["fallback_route"], billing=billing, catalog=catalog)
        if outcome_data["fallback_route"] is not None
        else None
    )
    verifier = _verifier_cost(
        outcome_data,
        billing=billing,
        verification_usage=verification_usage,
        catalog=catalog,
    )

    performed = [primary] + ([fallback] if fallback is not None else [])
    component_statuses = [item["status"] for item in performed]
    if verifier["status"] != "not_performed":
        component_statuses.append(verifier["status"])
    known_amounts = [
        Decimal(item["amount"])
        for item in performed
        if item["status"] == "known" and item["amount"] is not None
    ]
    if verifier["status"] == "known" and verifier["amount"] is not None:
        known_amounts.append(Decimal(verifier["amount"]))

    if component_statuses and all(status == "known" for status in component_statuses):
        status = "known"
        total_amount = _decimal_text(sum(known_amounts, Decimal(0)))
    elif any(status == "known" for status in component_statuses):
        status = "partial"
        total_amount = None
    else:
        status = "unknown"
        total_amount = None

    pricing_ids = sorted(
        {
            attempt["pricing_evidence_id"]
            for route in performed
            for attempt in route["attempts"]
            if attempt["pricing_evidence_id"] is not None
        }
        | (
            {verifier["pricing_evidence_id"]}
            if verifier["pricing_evidence_id"] is not None
            else set()
        )
    )
    issues = sorted(
        {
            issue
            for route in performed
            for issue in route["issues"]
        }
        | set(verifier["issues"])
    )
    timestamp = attributed_at or datetime.now(timezone.utc).isoformat()
    _parse_datetime(timestamp, "attributed_at")
    seed = json.dumps(
        {
            "outcome_integrity_sha256": outcome_data["integrity_sha256"],
            "billing_surfaces": dict(sorted(billing.execution_surfaces.items())),
            "verifier_surface": billing.verifier_surface,
            "pricing_evidence_ids": pricing_ids,
            "attributed_at": timestamp,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    payload: dict[str, Any] = {
        "cost_attribution_version": COST_ATTRIBUTION_VERSION,
        "record_type": "route_cost_attribution",
        "attribution_id": f"cost-{hashlib.sha256(seed).hexdigest()[:20]}",
        "attributed_at": timestamp,
        "outcome_id": outcome_data["outcome_id"],
        "outcome_integrity_sha256": outcome_data["integrity_sha256"],
        "currency": "USD",
        "status": status,
        "primary_route": primary,
        "fallback_route": fallback,
        "verifier": verifier,
        "total_amount": total_amount,
        "pricing_evidence_ids": pricing_ids,
        "issues": issues,
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return RouteCostAttributionRecord.from_dict(payload, repo_root=repo_root)


class JsonlRouteCostAttributionSink:
    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, record: RouteCostAttributionRecord) -> None:
        payload = record.to_dict()
        RouteCostAttributionRecord.from_dict(payload, repo_root=self.repo_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Route cost attribution could not be persisted"
            ) from exc

    def read_all(self) -> list[RouteCostAttributionRecord]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Route cost attribution JSONL could not be read"
            ) from exc
        records: list[RouteCostAttributionRecord] = []
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError(
                    f"Invalid route cost attribution JSONL at line {index}"
                ) from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError(
                    f"Route cost attribution JSONL line {index} must be an object"
                )
            records.append(RouteCostAttributionRecord.from_dict(raw, repo_root=self.repo_root))
        return records
