from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from jsonschema import Draft202012Validator

from .provider_adapter import ProviderAdapterContractError, ProviderExecutionResponse
from .runtime_canary import CanaryRuntimeOutcome
from .runtime_telemetry import RuntimeTelemetryEvent
from .schemas import DispatchRecord, VerificationResult

ROUTE_OUTCOME_VERSION = "1"
ROUTE_OUTCOME_SCHEMA_PATH = "reference/schemas/route-outcome-record.schema.json"
RouteRole = Literal["primary", "fallback"]


def _require_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(f"Route outcome {name} is required")
    return text


@dataclass(frozen=True, slots=True)
class RouteOutcomeVersionContext:
    runtime_version: str
    repository_revision: str
    routing_policy_revision: str | None = None
    registry_revision: str | None = None
    tool_versions: Mapping[str, str | None] | None = None

    def __post_init__(self) -> None:
        _require_text(self.runtime_version, "runtime_version")
        _require_text(self.repository_revision, "repository_revision")
        for key, value in (self.tool_versions or {}).items():
            _require_text(key, "tool version key")
            if value is not None:
                _require_text(value, f"tool version {key}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "runtime_version": self.runtime_version,
            "repository_revision": self.repository_revision,
            "routing_policy_revision": self.routing_policy_revision,
            "registry_revision": self.registry_revision,
            "tool_versions": dict(sorted((self.tool_versions or {}).items())),
        }


@dataclass(frozen=True, slots=True)
class RouteOutcomeRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "RouteOutcomeRecord":
        _validate_schema(data, repo_root)
        _validate_route_semantics(data)
        expected = str(data["integrity_sha256"])
        actual = _integrity_sha256(data)
        if expected != actual:
            raise ProviderAdapterContractError("Route outcome integrity hash does not match content")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def _schema(repo_root: str | Path) -> dict[str, Any]:
    path = Path(repo_root) / ROUTE_OUTCOME_SCHEMA_PATH
    if not path.is_file():
        raise ProviderAdapterContractError(f"Route outcome schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError("Route outcome schema could not be loaded") from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Route outcome schema must be an object")
    return raw


def _validate_schema(data: dict[str, Any], repo_root: str | Path) -> None:
    validator = Draft202012Validator(_schema(repo_root))
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if errors:
        first = errors[0]
        path = ".".join(str(item) for item in first.path) or "<root>"
        raise ProviderAdapterContractError(
            f"Route outcome schema validation failed at {path}: {first.message}"
        )


def _validate_route_semantics(data: dict[str, Any]) -> None:
    primary = data["primary_route"]
    fallback = data["fallback_route"]
    routes = [primary] + ([fallback] if fallback is not None else [])
    if primary["role"] != "primary":
        raise ProviderAdapterContractError("Route outcome primary_route must have primary role")
    if fallback is not None and fallback["role"] != "fallback":
        raise ProviderAdapterContractError("Route outcome fallback_route must have fallback role")

    for route in routes:
        attempts = route["attempts"]
        if route["attempt_count"] != len(attempts):
            raise ProviderAdapterContractError("Route outcome attempt_count does not match attempts")
        if route["retry_used"] != (len(attempts) > 1):
            raise ProviderAdapterContractError("Route outcome retry_used does not match attempts")
        if [attempt["attempt_number"] for attempt in attempts] != list(range(1, len(attempts) + 1)):
            raise ProviderAdapterContractError(
                "Route outcome attempts must be contiguous and start at one"
            )
        for attempt in attempts:
            if attempt["model"] != route["implementation"]["model"]:
                raise ProviderAdapterContractError(
                    "Route outcome attempt model does not match route implementation"
                )
            if attempt["provider_family"] != route["implementation"]["provider_family"]:
                raise ProviderAdapterContractError(
                    "Route outcome attempt provider does not match route implementation"
                )

    active = data["active_route_role"]
    if data["fallback_assisted"] != (active == "fallback"):
        raise ProviderAdapterContractError(
            "Route outcome fallback_assisted does not match active route"
        )
    if active == "fallback" and fallback is None:
        raise ProviderAdapterContractError(
            "Fallback-assisted route outcome requires fallback_route"
        )
    retry_assisted = primary["retry_used"] or bool(fallback and fallback["retry_used"])
    if data["retry_assisted"] != retry_assisted:
        raise ProviderAdapterContractError(
            "Route outcome retry_assisted does not match route evidence"
        )

    source_ids = [primary["dispatch_id"]]
    if fallback is not None:
        source_ids.append(fallback["dispatch_id"])
    if data["provenance"]["source_dispatch_ids"] != source_ids:
        raise ProviderAdapterContractError(
            "Route outcome provenance does not match dispatch lineage"
        )
    expected_events = sum(route["attempt_count"] for route in routes)
    if data["provenance"]["telemetry_event_count"] != expected_events:
        raise ProviderAdapterContractError(
            "Route outcome telemetry_event_count does not match route evidence"
        )

    active_route = primary if active == "primary" else fallback if active == "fallback" else None
    verification_dispatch = data["provenance"]["verification_dispatch_id"]
    disposition = data["final_disposition"]
    verification_status = data["verification_status"]

    if active_route is not None and active_route["execution_status"] != "succeeded":
        raise ProviderAdapterContractError(
            "Route outcome active route must have succeeded execution"
        )
    if verification_dispatch is not None:
        if active_route is None or verification_dispatch != active_route["dispatch_id"]:
            raise ProviderAdapterContractError(
                "Route outcome verification provenance does not match active route"
            )

    if disposition in {"completed", "verification_failed", "awaiting_human"}:
        if active_route is None or verification_status is None or verification_dispatch is None:
            raise ProviderAdapterContractError(
                "Verified route outcome requires active route and verification provenance"
            )
    elif disposition == "verification_missing":
        if active_route is None or verification_status is not None or verification_dispatch is not None:
            raise ProviderAdapterContractError(
                "verification_missing requires an unverified successful active route"
            )
    elif disposition == "execution_failed":
        if active_route is not None or verification_status is not None or verification_dispatch is not None:
            raise ProviderAdapterContractError(
                "execution_failed cannot have active or verification evidence"
            )
    elif disposition == "abandoned":
        if active_route is not None or verification_status is not None or verification_dispatch is not None:
            raise ProviderAdapterContractError(
                "abandoned route outcome cannot have active or verification evidence"
            )

    if disposition == "completed" and verification_status != "passed":
        raise ProviderAdapterContractError("Completed route outcome requires passed verification")
    if disposition == "verification_failed" and verification_status != "failed":
        raise ProviderAdapterContractError(
            "verification_failed route outcome requires failed verification"
        )
    if data["human_approval_required"] and disposition == "completed":
        raise ProviderAdapterContractError(
            "Human-approval-required route outcome cannot be completed by model verification"
        )


def _integrity_sha256(data: dict[str, Any]) -> str:
    canonical = dict(data)
    canonical.pop("integrity_sha256", None)
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _attempt_payload(event: RuntimeTelemetryEvent) -> dict[str, Any]:
    return {
        "recorded_at": event.recorded_at,
        "attempt_number": event.attempt_number,
        "provider_family": event.provider_family,
        "model": event.model,
        "reasoning_effort": event.reasoning_effort,
        "status": event.status,
        "failure_scope": event.failure_scope,
        "failure_code": event.failure_code,
        "duration_ms": event.duration_ms,
        "retry_after_seconds": event.retry_after_seconds,
        "usage": event.usage.to_dict() if event.usage else None,
    }


def _events_for_dispatch(
    telemetry_events: Sequence[RuntimeTelemetryEvent],
    dispatch: DispatchRecord,
    *,
    role: RouteRole,
) -> list[RuntimeTelemetryEvent]:
    events = sorted(
        (event for event in telemetry_events if event.dispatch_id == dispatch.dispatch_id),
        key=lambda event: event.attempt_number,
    )
    if [event.attempt_number for event in events] != list(range(1, len(events) + 1)):
        raise ProviderAdapterContractError(
            "Route outcome telemetry attempts must be contiguous and start at one"
        )
    for event in events:
        if event.role != role:
            raise ProviderAdapterContractError("Route outcome telemetry role does not match lineage")
        if event.task_type != dispatch.task_type or event.risk_level != dispatch.risk_level:
            raise ProviderAdapterContractError("Route outcome telemetry changed task or risk identity")
        if event.provider_family != dispatch.selected_implementation.provider_family:
            raise ProviderAdapterContractError(
                "Route outcome telemetry changed the dispatch-selected provider"
            )
        if event.model != dispatch.selected_implementation.model:
            raise ProviderAdapterContractError(
                "Route outcome telemetry changed the dispatch-selected model"
            )
        if event.verifier_model != dispatch.verification.implementation.model:
            raise ProviderAdapterContractError(
                "Route outcome telemetry changed the assigned verifier"
            )
    return events


def _route_payload(
    dispatch: DispatchRecord,
    response: ProviderExecutionResponse | None,
    telemetry_events: Sequence[RuntimeTelemetryEvent],
    *,
    role: RouteRole,
    execution_status: str | None = None,
) -> dict[str, Any]:
    events = _events_for_dispatch(telemetry_events, dispatch, role=role)
    failure = response.failure if response is not None else None
    status = execution_status or (response.status if response is not None else "abandoned")
    return {
        "dispatch_id": dispatch.dispatch_id,
        "role": role,
        "selected_team": dispatch.selected_team,
        "selected_worker": dispatch.selected_worker,
        "selected_specialist": dispatch.selected_specialist,
        "required_capabilities": list(dispatch.required_capabilities),
        "implementation": {
            "provider_family": dispatch.selected_implementation.provider_family,
            "model": dispatch.selected_implementation.model,
            "reasoning_effort": dispatch.selected_implementation.reasoning,
        },
        "verifier": {
            "provider_family": dispatch.verification.implementation.provider_family,
            "model": dispatch.verification.implementation.model,
        },
        "attempts": [_attempt_payload(event) for event in events],
        "attempt_count": len(events),
        "retry_used": len(events) > 1,
        "execution_status": status,
        "failure_scope": failure.scope if failure else None,
        "failure_code": failure.code if failure else None,
    }


def _outcome_id(primary_dispatch_id: str, fallback_dispatch_id: str | None) -> str:
    seed = f"{primary_dispatch_id}|{fallback_dispatch_id or ''}".encode("utf-8")
    return f"outcome-{hashlib.sha256(seed).hexdigest()[:20]}"


def _finalize_payload(
    payload: dict[str, Any],
    *,
    repo_root: str | Path,
) -> RouteOutcomeRecord:
    payload["integrity_sha256"] = _integrity_sha256(payload)
    return RouteOutcomeRecord.from_dict(payload, repo_root=repo_root)


def build_guarded_canary_route_outcome(
    outcome: CanaryRuntimeOutcome,
    telemetry_events: Sequence[RuntimeTelemetryEvent],
    *,
    repo_root: str | Path,
    versions: RouteOutcomeVersionContext,
    verification: VerificationResult | None = None,
    recorded_at: str | None = None,
) -> RouteOutcomeRecord:
    dispatch_ids = {outcome.primary_dispatch.dispatch_id}
    if outcome.fallback_dispatch is not None:
        dispatch_ids.add(outcome.fallback_dispatch.dispatch_id)
    unrelated = sorted(
        {event.dispatch_id for event in telemetry_events if event.dispatch_id not in dispatch_ids}
    )
    if unrelated:
        raise ProviderAdapterContractError(
            f"Route outcome includes unrelated telemetry: {', '.join(unrelated)}"
        )

    primary_route = _route_payload(
        outcome.primary_dispatch,
        outcome.primary_response,
        telemetry_events,
        role="primary",
    )
    if primary_route["attempt_count"] != outcome.primary_attempts:
        raise ProviderAdapterContractError(
            "Route outcome primary telemetry count does not match runtime attempts"
        )

    fallback_route = None
    if outcome.fallback_dispatch is not None:
        if outcome.fallback_response is None:
            raise ProviderAdapterContractError("Fallback dispatch requires a fallback response")
        fallback_route = _route_payload(
            outcome.fallback_dispatch,
            outcome.fallback_response,
            telemetry_events,
            role="fallback",
        )
        if fallback_route["attempt_count"] != outcome.fallback_attempts:
            raise ProviderAdapterContractError(
                "Route outcome fallback telemetry count does not match runtime attempts"
            )

    active_dispatch: DispatchRecord | None = None
    active_role: RouteRole | None = None
    if outcome.status == "primary_executed" and outcome.primary_response.status == "succeeded":
        active_dispatch = outcome.primary_dispatch
        active_role = "primary"
    elif (
        outcome.status == "fallback_executed"
        and outcome.fallback_dispatch is not None
        and outcome.fallback_response is not None
        and outcome.fallback_response.status == "succeeded"
    ):
        active_dispatch = outcome.fallback_dispatch
        active_role = "fallback"

    verification_status: str | None = None
    verification_dispatch_id: str | None = None
    human_approval_required = bool(
        active_dispatch and active_dispatch.verification.human_approval_required
    )
    if active_dispatch is None:
        if verification is not None:
            raise ProviderAdapterContractError(
                "Failed execution route outcome cannot include verification"
            )
        final_disposition = "execution_failed"
    elif verification is None:
        final_disposition = "verification_missing"
    else:
        if verification.dispatch_id != active_dispatch.dispatch_id:
            raise ProviderAdapterContractError(
                "Route outcome verification does not belong to the active dispatch"
            )
        if verification.verifier_model != active_dispatch.verification.implementation.model:
            raise ProviderAdapterContractError(
                "Route outcome verification was not performed by the assigned verifier"
            )
        verification_status = verification.status
        verification_dispatch_id = verification.dispatch_id
        if verification.status == "failed":
            final_disposition = "verification_failed"
        elif verification.status == "needs_human" or human_approval_required:
            final_disposition = "awaiting_human"
        else:
            final_disposition = "completed"

    source_dispatch_ids = [outcome.primary_dispatch.dispatch_id]
    if outcome.fallback_dispatch is not None:
        source_dispatch_ids.append(outcome.fallback_dispatch.dispatch_id)
    retry_assisted = bool(primary_route["retry_used"]) or bool(
        fallback_route and fallback_route["retry_used"]
    )

    payload = {
        "route_outcome_version": ROUTE_OUTCOME_VERSION,
        "record_type": "route_outcome",
        "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat(),
        "outcome_id": _outcome_id(
            outcome.primary_dispatch.dispatch_id,
            outcome.fallback_dispatch.dispatch_id if outcome.fallback_dispatch else None,
        ),
        "task_type": outcome.primary_dispatch.task_type,
        "risk_level": outcome.primary_dispatch.risk_level,
        "primary_route": primary_route,
        "fallback_route": fallback_route,
        "active_route_role": active_role,
        "final_disposition": final_disposition,
        "verification_status": verification_status,
        "human_approval_required": human_approval_required,
        "fallback_assisted": active_role == "fallback",
        "retry_assisted": retry_assisted,
        "versions": versions.to_dict(),
        "cost": {
            "status": "unknown",
            "amount": None,
            "currency": None,
            "source": None,
        },
        "provenance": {
            "source_dispatch_ids": source_dispatch_ids,
            "verification_dispatch_id": verification_dispatch_id,
            "telemetry_event_count": len(telemetry_events),
        },
        "abandonment_reason": None,
        "integrity_sha256": "",
    }
    return _finalize_payload(payload, repo_root=repo_root)


def build_abandoned_route_outcome(
    dispatch: DispatchRecord,
    telemetry_events: Sequence[RuntimeTelemetryEvent],
    *,
    repo_root: str | Path,
    versions: RouteOutcomeVersionContext,
    reason: str,
    role: RouteRole = "primary",
    recorded_at: str | None = None,
) -> RouteOutcomeRecord:
    reason = _require_text(reason, "abandonment_reason")
    unrelated = sorted(
        {event.dispatch_id for event in telemetry_events if event.dispatch_id != dispatch.dispatch_id}
    )
    if unrelated:
        raise ProviderAdapterContractError(
            f"Abandoned route outcome includes unrelated telemetry: {', '.join(unrelated)}"
        )
    route = _route_payload(
        dispatch,
        None,
        telemetry_events,
        role=role,
        execution_status="abandoned",
    )
    payload = {
        "route_outcome_version": ROUTE_OUTCOME_VERSION,
        "record_type": "route_outcome",
        "recorded_at": recorded_at or datetime.now(timezone.utc).isoformat(),
        "outcome_id": _outcome_id(dispatch.dispatch_id, None),
        "task_type": dispatch.task_type,
        "risk_level": dispatch.risk_level,
        "primary_route": route,
        "fallback_route": None,
        "active_route_role": None,
        "final_disposition": "abandoned",
        "verification_status": None,
        "human_approval_required": dispatch.verification.human_approval_required,
        "fallback_assisted": False,
        "retry_assisted": bool(route["retry_used"]),
        "versions": versions.to_dict(),
        "cost": {
            "status": "unknown",
            "amount": None,
            "currency": None,
            "source": None,
        },
        "provenance": {
            "source_dispatch_ids": [dispatch.dispatch_id],
            "verification_dispatch_id": None,
            "telemetry_event_count": len(telemetry_events),
        },
        "abandonment_reason": reason,
        "integrity_sha256": "",
    }
    return _finalize_payload(payload, repo_root=repo_root)


class JsonlRouteOutcomeSink:
    """Append-only single-process reference sink for content-minimized route outcomes."""

    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, record: RouteOutcomeRecord) -> None:
        validated = RouteOutcomeRecord.from_dict(
            record.to_dict(),
            repo_root=self.repo_root,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(validated.to_dict(), sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Route outcome evidence could not be persisted"
            ) from exc

    def read_all(self) -> list[RouteOutcomeRecord]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Route outcome evidence could not be read"
            ) from exc
        records: list[RouteOutcomeRecord] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError(
                    "Route outcome evidence contains invalid JSONL"
                ) from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError(
                    "Route outcome evidence line must be an object"
                )
            records.append(
                RouteOutcomeRecord.from_dict(raw, repo_root=self.repo_root)
            )
        return records
