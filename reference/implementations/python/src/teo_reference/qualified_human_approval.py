from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .provider_adapter import ProviderAdapterContractError
from .route_outcome import RouteOutcomeRecord
from .schemas import DispatchRecord

QUALIFIED_HUMAN_APPROVAL_VERSION = "1"
AUTHORITY_GRANT_SCHEMA_PATH = "reference/schemas/qualified-human-authority-grant.schema.json"
APPROVAL_REQUEST_SCHEMA_PATH = "reference/schemas/qualified-human-approval-request.schema.json"
APPROVAL_DISPOSITION_SCHEMA_PATH = (
    "reference/schemas/qualified-human-approval-disposition.schema.json"
)
HUMAN_FINALIZATION_SCHEMA_PATH = "reference/schemas/qualified-human-finalization.schema.json"


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


def _parse_datetime(value: str, name: str) -> datetime:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(f"Qualified-human approval {name} is required")
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ProviderAdapterContractError(
            f"Qualified-human approval {name} must be ISO-8601"
        ) from exc
    if parsed.tzinfo is None:
        raise ProviderAdapterContractError(
            f"Qualified-human approval {name} must include a timezone"
        )
    return parsed.astimezone(timezone.utc)


def _load_schema(repo_root: str | Path, relative_path: str) -> dict[str, Any]:
    path = Path(repo_root) / relative_path
    if not path.is_file():
        raise ProviderAdapterContractError(
            f"Qualified-human approval schema not found: {path}"
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Qualified-human approval schema could not be loaded: {path}"
        ) from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError(
            "Qualified-human approval schema must be an object"
        )
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


def _require_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(
            f"Qualified-human approval {name} is required"
        )
    return text


def _unique_text(values: Sequence[str], name: str) -> list[str]:
    result = list(dict.fromkeys(_require_text(item, name) for item in values))
    if not result:
        raise ProviderAdapterContractError(
            f"Qualified-human approval {name} requires at least one value"
        )
    return result


def _validate_integrity(data: dict[str, Any], label: str) -> None:
    expected = str(data["integrity_sha256"])
    actual = _canonical_sha256(data, omit="integrity_sha256")
    if expected != actual:
        raise ProviderAdapterContractError(f"{label} integrity hash does not match content")


def _validate_grant_semantics(data: dict[str, Any]) -> None:
    issued_at = _parse_datetime(data["issued_at"], "authority grant issued_at")
    valid_from = _parse_datetime(data["valid_from"], "authority grant valid_from")
    valid_until = (
        _parse_datetime(data["valid_until"], "authority grant valid_until")
        if data["valid_until"] is not None
        else None
    )
    verified_at = _parse_datetime(
        data["source"]["verified_at"], "authority grant source verified_at"
    )
    if valid_until is not None and valid_until <= valid_from:
        raise ProviderAdapterContractError(
            "Qualified-human authority grant valid_until must be later than valid_from"
        )
    if verified_at > issued_at:
        raise ProviderAdapterContractError(
            "Qualified-human authority grant source cannot be verified after grant issuance"
        )


def _validate_request_semantics(data: dict[str, Any]) -> None:
    requested_at = _parse_datetime(data["requested_at"], "approval request requested_at")
    expires_at = (
        _parse_datetime(data["expires_at"], "approval request expires_at")
        if data["expires_at"] is not None
        else None
    )
    if expires_at is not None and expires_at <= requested_at:
        raise ProviderAdapterContractError(
            "Qualified-human approval request expires_at must be later than requested_at"
        )


def _validate_disposition_semantics(data: dict[str, Any]) -> None:
    _parse_datetime(data["effective_at"], "approval disposition effective_at")
    previous_id = data["previous_disposition_id"]
    previous_hash = data["previous_disposition_integrity_sha256"]
    if (previous_id is None) != (previous_hash is None):
        raise ProviderAdapterContractError(
            "Qualified-human approval previous disposition references must be both present or both null"
        )

    state = str(data["state"])
    actor = data["actor"]
    grant_ref = data["authority_grant_ref"]
    approval_expires_at = data["approval_expires_at"]

    if state == "expired":
        if actor["actor_type"] != "system" or actor["subject_ref"] is not None:
            raise ProviderAdapterContractError(
                "Expired qualified-human approval disposition must be system-generated"
            )
        if grant_ref is not None or approval_expires_at is not None:
            raise ProviderAdapterContractError(
                "Expired qualified-human approval disposition cannot carry human grant or approval expiry"
            )
    else:
        if actor["actor_type"] != "human" or actor["subject_ref"] is None:
            raise ProviderAdapterContractError(
                "Qualified-human approval decisions and revocations require a human actor"
            )
        if grant_ref is None:
            raise ProviderAdapterContractError(
                "Qualified-human approval human actor requires an authority grant"
            )
        if state == "approved":
            if approval_expires_at is None:
                raise ProviderAdapterContractError(
                    "Approved qualified-human approval disposition requires approval_expires_at"
                )
            if _parse_datetime(
                approval_expires_at, "approval disposition approval_expires_at"
            ) <= _parse_datetime(data["effective_at"], "approval disposition effective_at"):
                raise ProviderAdapterContractError(
                    "Approved qualified-human approval disposition must expire after effective_at"
                )
        elif approval_expires_at is not None:
            raise ProviderAdapterContractError(
                "Only approved qualified-human approval disposition may carry approval_expires_at"
            )


def _validate_finalization_semantics(data: dict[str, Any]) -> None:
    _parse_datetime(data["finalized_at"], "human finalization finalized_at")
    status = str(data["status"])
    approval_state = str(data["approval_state"])
    block_reason = str(data["block_reason"])
    satisfied = bool(data["qualified_human_approval_satisfied"])
    subject_ref = data["approver_subject_ref"]
    authority_class = data["authority_class"]

    if status == "completed":
        if approval_state != "approved" or block_reason != "none" or not satisfied:
            raise ProviderAdapterContractError(
                "Completed qualified-human finalization requires a current approved state"
            )
        if subject_ref is None or authority_class is None:
            raise ProviderAdapterContractError(
                "Completed qualified-human finalization requires approver authority evidence"
            )
        if data["current_disposition_ref"] is None:
            raise ProviderAdapterContractError(
                "Completed qualified-human finalization requires an approval disposition reference"
            )
    else:
        if satisfied or block_reason == "none":
            raise ProviderAdapterContractError(
                "Blocked qualified-human finalization must preserve its blocking reason"
            )
        if subject_ref is not None or authority_class is not None:
            raise ProviderAdapterContractError(
                "Blocked qualified-human finalization cannot claim approver authority"
            )


@dataclass(frozen=True, slots=True)
class QualifiedHumanAuthorityGrantRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "QualifiedHumanAuthorityGrantRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=AUTHORITY_GRANT_SCHEMA_PATH,
            label="Qualified-human authority grant",
        )
        _validate_grant_semantics(data)
        _validate_integrity(data, "Qualified-human authority grant")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class QualifiedHumanApprovalRequestRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "QualifiedHumanApprovalRequestRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=APPROVAL_REQUEST_SCHEMA_PATH,
            label="Qualified-human approval request",
        )
        _validate_request_semantics(data)
        _validate_integrity(data, "Qualified-human approval request")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class QualifiedHumanApprovalDispositionRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "QualifiedHumanApprovalDispositionRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=APPROVAL_DISPOSITION_SCHEMA_PATH,
            label="Qualified-human approval disposition",
        )
        _validate_disposition_semantics(data)
        _validate_integrity(data, "Qualified-human approval disposition")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class QualifiedHumanFinalizationRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "QualifiedHumanFinalizationRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=HUMAN_FINALIZATION_SCHEMA_PATH,
            label="Qualified-human finalization",
        )
        _validate_finalization_semantics(data)
        _validate_integrity(data, "Qualified-human finalization")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def build_qualified_human_authority_grant(
    *,
    subject_ref: str,
    authority_class: str,
    authority_requirement_ids: Sequence[str],
    risk_levels: Sequence[str],
    task_types: Sequence[str],
    issuer: str,
    evidence_ref: str,
    repo_root: str | Path,
    issued_at: str | None = None,
    valid_from: str | None = None,
    valid_until: str | None = None,
    source_verified_at: str | None = None,
) -> QualifiedHumanAuthorityGrantRecord:
    subject = _require_text(subject_ref, "authority grant subject_ref")
    authority = _require_text(authority_class, "authority grant authority_class")
    requirements = _unique_text(authority_requirement_ids, "authority_requirement_ids")
    risks = _unique_text(risk_levels, "risk_levels")
    unsupported_risks = sorted(set(risks).difference({"low", "medium", "high", "critical"}))
    if unsupported_risks:
        raise ProviderAdapterContractError(
            "Qualified-human authority grant contains unsupported risk level: "
            + ", ".join(unsupported_risks)
        )
    tasks = _unique_text(task_types, "task_types")
    issued = issued_at or datetime.now(timezone.utc).isoformat()
    starts = valid_from or issued
    verified = source_verified_at or issued
    _parse_datetime(issued, "authority grant issued_at")
    _parse_datetime(starts, "authority grant valid_from")
    if valid_until is not None:
        _parse_datetime(valid_until, "authority grant valid_until")
    _parse_datetime(verified, "authority grant source verified_at")

    seed = json.dumps(
        {
            "subject_ref": subject,
            "authority_class": authority,
            "requirements": requirements,
            "risks": risks,
            "tasks": tasks,
            "issuer": issuer,
            "evidence_ref": evidence_ref,
            "issued_at": issued,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "qualified_human_approval_version": QUALIFIED_HUMAN_APPROVAL_VERSION,
        "record_type": "qualified_human_authority_grant",
        "grant_id": f"authority-grant-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}",
        "issued_at": issued,
        "valid_from": starts,
        "valid_until": valid_until,
        "subject_ref": subject,
        "authority_class": authority,
        "scope": {
            "authority_requirement_ids": requirements,
            "risk_levels": risks,
            "task_types": tasks,
        },
        "source": {
            "issuer": _require_text(issuer, "authority grant issuer"),
            "evidence_ref": _require_text(evidence_ref, "authority grant evidence_ref"),
            "verified_at": verified,
        },
        "identity_is_routing_signal": False,
        "model_selection_is_qualification_signal": False,
        "provider_access_is_qualification_signal": False,
        "billing_identity_is_qualification_signal": False,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return QualifiedHumanAuthorityGrantRecord.from_dict(payload, repo_root=repo_root)


def _active_route(outcome: Mapping[str, Any]) -> Mapping[str, Any] | None:
    role = outcome.get("active_route_role")
    if role == "primary":
        return outcome.get("primary_route")
    if role == "fallback":
        return outcome.get("fallback_route")
    return None


def _normalize_review_refs(
    review_evidence_refs: Sequence[Mapping[str, str]] | None,
) -> list[dict[str, str]]:
    allowed = {
        "benchmark_conclusion_handoff",
        "shadow_route_recommendation",
        "shadow_recommendation_handoff",
    }
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()
    for item in review_evidence_refs or ():
        record_type = _require_text(item.get("record_type"), "review evidence record_type")
        if record_type not in allowed:
            raise ProviderAdapterContractError(
                f"Unsupported qualified-human review evidence type: {record_type}"
            )
        record_id = _require_text(item.get("record_id"), "review evidence record_id")
        integrity = _require_text(
            item.get("integrity_sha256"), "review evidence integrity_sha256"
        )
        if len(integrity) != 64 or any(char not in "0123456789abcdef" for char in integrity):
            raise ProviderAdapterContractError(
                "Qualified-human review evidence integrity_sha256 must be lowercase SHA-256"
            )
        key = (record_type, record_id, integrity)
        if key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "record_type": record_type,
                "record_id": record_id,
                "integrity_sha256": integrity,
            }
        )
    return result


def _validate_request_binding(
    dispatch: DispatchRecord,
    route_outcome: RouteOutcomeRecord,
    request: QualifiedHumanApprovalRequestRecord | None = None,
) -> None:
    outcome = route_outcome.to_dict()
    if not dispatch.verification.human_approval_required:
        raise ProviderAdapterContractError(
            "Qualified-human approval request requires a dispatch already marked human_approval_required"
        )
    if not outcome["human_approval_required"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval request requires human-required Route-Outcome Evidence"
        )
    if outcome["final_disposition"] != "awaiting_human":
        raise ProviderAdapterContractError(
            "Qualified-human approval request requires awaiting_human Route-Outcome Evidence"
        )
    active_route = _active_route(outcome)
    if active_route is None or active_route["dispatch_id"] != dispatch.dispatch_id:
        raise ProviderAdapterContractError(
            "Qualified-human approval request dispatch must be the active route dispatch"
        )
    if outcome["task_type"] != dispatch.task_type or outcome["risk_level"] != dispatch.risk_level:
        raise ProviderAdapterContractError(
            "Qualified-human approval request cannot change task type or effective risk"
        )
    if outcome["provenance"]["verification_dispatch_id"] != dispatch.dispatch_id:
        raise ProviderAdapterContractError(
            "Qualified-human approval request requires verification evidence for the active dispatch"
        )
    if outcome["verification_status"] not in {"passed", "needs_human"}:
        raise ProviderAdapterContractError(
            "Qualified-human approval request requires passed or needs_human verification evidence"
        )

    if request is None:
        return
    request_data = request.to_dict()
    if request_data["dispatch_id"] != dispatch.dispatch_id:
        raise ProviderAdapterContractError(
            "Qualified-human approval request references a different dispatch"
        )
    if request_data["dispatch_sha256"] != _canonical_sha256(dispatch.to_dict()):
        raise ProviderAdapterContractError(
            "Qualified-human approval request does not bind the exact dispatch content"
        )
    if request_data["task_id"] != dispatch.task_id:
        raise ProviderAdapterContractError(
            "Qualified-human approval request references a different task"
        )
    if request_data["task_type"] != dispatch.task_type:
        raise ProviderAdapterContractError(
            "Qualified-human approval request references a different task type"
        )
    if request_data["effective_risk"] != dispatch.risk_level:
        raise ProviderAdapterContractError(
            "Qualified-human approval request references a different effective risk"
        )
    if request_data["route_outcome_ref"] != {
        "outcome_id": outcome["outcome_id"],
        "integrity_sha256": outcome["integrity_sha256"],
    }:
        raise ProviderAdapterContractError(
            "Qualified-human approval request does not bind the exact Route-Outcome Evidence"
        )
    if request_data["verification"] != {
        "dispatch_id": outcome["provenance"]["verification_dispatch_id"],
        "status": outcome["verification_status"],
    }:
        raise ProviderAdapterContractError(
            "Qualified-human approval request verification evidence does not match Route-Outcome Evidence"
        )


def build_qualified_human_approval_request(
    dispatch: DispatchRecord,
    route_outcome: RouteOutcomeRecord,
    *,
    authority_requirement_id: str,
    required_authority_class: str,
    reason: str,
    policy_source: str,
    repo_root: str | Path,
    review_evidence_refs: Sequence[Mapping[str, str]] | None = None,
    requested_at: str | None = None,
    expires_at: str | None = None,
) -> QualifiedHumanApprovalRequestRecord:
    _validate_request_binding(dispatch, route_outcome)
    outcome = route_outcome.to_dict()
    requested = requested_at or datetime.now(timezone.utc).isoformat()
    requested_dt = _parse_datetime(requested, "approval request requested_at")
    if expires_at is not None and _parse_datetime(
        expires_at, "approval request expires_at"
    ) <= requested_dt:
        raise ProviderAdapterContractError(
            "Qualified-human approval request expires_at must be later than requested_at"
        )
    requirement_id = _require_text(
        authority_requirement_id, "authority requirement id"
    )
    authority_class = _require_text(
        required_authority_class, "required authority class"
    )
    review_refs = _normalize_review_refs(review_evidence_refs)
    dispatch_hash = _canonical_sha256(dispatch.to_dict())
    seed = json.dumps(
        {
            "dispatch": dispatch_hash,
            "outcome": outcome["integrity_sha256"],
            "requirement": requirement_id,
            "authority_class": authority_class,
            "requested_at": requested,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "qualified_human_approval_version": QUALIFIED_HUMAN_APPROVAL_VERSION,
        "record_type": "qualified_human_approval_request",
        "approval_request_id": (
            "approval-request-" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "requested_at": requested,
        "expires_at": expires_at,
        "request_state": "requested",
        "requested_by": "teo_control_plane",
        "dispatch_id": dispatch.dispatch_id,
        "dispatch_sha256": dispatch_hash,
        "task_id": dispatch.task_id,
        "task_type": dispatch.task_type,
        "effective_risk": dispatch.risk_level,
        "authority_requirement": {
            "requirement_id": requirement_id,
            "required_authority_class": authority_class,
            "reason": _require_text(reason, "authority requirement reason"),
            "policy_source": _require_text(policy_source, "authority requirement policy_source"),
        },
        "route_outcome_ref": {
            "outcome_id": outcome["outcome_id"],
            "integrity_sha256": outcome["integrity_sha256"],
        },
        "verification": {
            "dispatch_id": outcome["provenance"]["verification_dispatch_id"],
            "status": outcome["verification_status"],
        },
        "review_evidence_refs": review_refs,
        "policy_write_authority": False,
        "live_routing_authority": False,
        "live_scope_change_authority": False,
        "qualified_human_approval_satisfied": False,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return QualifiedHumanApprovalRequestRecord.from_dict(payload, repo_root=repo_root)


def _grant_for_ref(
    ref: Mapping[str, Any],
    grants: Mapping[str, QualifiedHumanAuthorityGrantRecord],
) -> QualifiedHumanAuthorityGrantRecord:
    grant_id = str(ref["grant_id"])
    grant = grants.get(grant_id)
    if grant is None:
        raise ProviderAdapterContractError(
            f"Qualified-human approval authority grant evidence missing: {grant_id}"
        )
    grant_data = grant.to_dict()
    if grant_data["integrity_sha256"] != ref["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant integrity reference does not match"
        )
    if grant_data["authority_class"] != ref["authority_class"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority class reference does not match grant"
        )
    return grant


def _assert_grant_covers_request(
    grant: QualifiedHumanAuthorityGrantRecord,
    request: QualifiedHumanApprovalRequestRecord,
    *,
    at: datetime,
    subject_ref: str,
) -> None:
    grant_data = grant.to_dict()
    request_data = request.to_dict()
    requirement = request_data["authority_requirement"]
    if grant_data["subject_ref"] != subject_ref:
        raise ProviderAdapterContractError(
            "Qualified-human approval actor does not match authority grant subject"
        )
    if grant_data["authority_class"] != requirement["required_authority_class"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority class is outside the request requirement"
        )
    if requirement["requirement_id"] not in grant_data["scope"]["authority_requirement_ids"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant does not cover the required authority requirement"
        )
    if request_data["effective_risk"] not in grant_data["scope"]["risk_levels"]:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant does not cover the effective risk"
        )
    task_types = set(str(item) for item in grant_data["scope"]["task_types"])
    if "*" not in task_types and request_data["task_type"] not in task_types:
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant does not cover the task type"
        )
    valid_from = _parse_datetime(grant_data["valid_from"], "authority grant valid_from")
    valid_until = (
        _parse_datetime(grant_data["valid_until"], "authority grant valid_until")
        if grant_data["valid_until"] is not None
        else None
    )
    if at < valid_from or (valid_until is not None and at >= valid_until):
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant is not valid at disposition time"
        )


def _assert_request_not_expired(
    request: QualifiedHumanApprovalRequestRecord,
    *,
    at: datetime,
) -> None:
    request_data = request.to_dict()
    if request_data["expires_at"] is None:
        return
    if at >= _parse_datetime(request_data["expires_at"], "approval request expires_at"):
        raise ProviderAdapterContractError(
            "Qualified-human approval request is expired"
        )


def _validate_transition(
    request: QualifiedHumanApprovalRequestRecord,
    state: str,
    effective_at: datetime,
    previous: QualifiedHumanApprovalDispositionRecord | None,
) -> None:
    request_data = request.to_dict()
    requested_at = _parse_datetime(
        request_data["requested_at"], "approval request requested_at"
    )
    if effective_at < requested_at:
        raise ProviderAdapterContractError(
            "Qualified-human approval disposition cannot predate its approval request"
        )
    allowed_initial = {"approved", "rejected", "unable_to_determine", "expired"}
    if previous is None:
        if state not in allowed_initial:
            raise ProviderAdapterContractError(
                f"Qualified-human approval cannot transition requested -> {state}"
            )
        if state == "expired":
            if request_data["expires_at"] is None:
                raise ProviderAdapterContractError(
                    "Qualified-human approval request without expires_at cannot expire explicitly"
                )
            expiry = _parse_datetime(
                request_data["expires_at"], "approval request expires_at"
            )
            if effective_at < expiry:
                raise ProviderAdapterContractError(
                    "Qualified-human approval request cannot expire before expires_at"
                )
        return

    previous_data = previous.to_dict()
    previous_time = _parse_datetime(
        previous_data["effective_at"], "previous approval disposition effective_at"
    )
    if effective_at < previous_time:
        raise ProviderAdapterContractError(
            "Qualified-human approval disposition time cannot move backwards"
        )
    previous_state = str(previous_data["state"])
    if previous_state != "approved" or state not in {"revoked", "expired"}:
        raise ProviderAdapterContractError(
            f"Qualified-human approval cannot transition {previous_state} -> {state}"
        )
    approval_expiry = _parse_datetime(
        previous_data["approval_expires_at"], "previous approval approval_expires_at"
    )
    if state == "expired" and effective_at < approval_expiry:
        raise ProviderAdapterContractError(
            "Qualified-human approval cannot expire before approval_expires_at"
        )
    if state == "revoked" and effective_at >= approval_expiry:
        raise ProviderAdapterContractError(
            "Expired qualified-human approval must be recorded as expired, not revoked"
        )


def build_qualified_human_approval_disposition(
    request: QualifiedHumanApprovalRequestRecord,
    *,
    state: str,
    reason: str,
    evidence: Sequence[str],
    repo_root: str | Path,
    actor_subject_ref: str | None = None,
    authority_grant: QualifiedHumanAuthorityGrantRecord | None = None,
    previous_disposition: QualifiedHumanApprovalDispositionRecord | None = None,
    effective_at: str | None = None,
    approval_expires_at: str | None = None,
) -> QualifiedHumanApprovalDispositionRecord:
    if state not in {"approved", "rejected", "unable_to_determine", "expired", "revoked"}:
        raise ProviderAdapterContractError(
            f"Unsupported qualified-human approval disposition state: {state}"
        )
    timestamp = effective_at or datetime.now(timezone.utc).isoformat()
    effective = _parse_datetime(timestamp, "approval disposition effective_at")
    _validate_transition(request, state, effective, previous_disposition)
    request_data = request.to_dict()
    previous_data = previous_disposition.to_dict() if previous_disposition else None
    evidence_items = _unique_text(evidence, "approval disposition evidence")

    grant_ref: dict[str, Any] | None = None
    if state == "expired":
        if actor_subject_ref is not None or authority_grant is not None:
            raise ProviderAdapterContractError(
                "Expired qualified-human approval disposition must be system-generated"
            )
        actor = {"actor_type": "system", "subject_ref": None}
        if approval_expires_at is not None:
            raise ProviderAdapterContractError(
                "Expired qualified-human approval disposition cannot define approval_expires_at"
            )
    else:
        subject = _require_text(actor_subject_ref, "approval disposition actor_subject_ref")
        if authority_grant is None:
            raise ProviderAdapterContractError(
                "Qualified-human approval decision requires authority grant evidence"
            )
        _assert_request_not_expired(request, at=effective)
        _assert_grant_covers_request(
            authority_grant,
            request,
            at=effective,
            subject_ref=subject,
        )
        grant_data = authority_grant.to_dict()
        grant_ref = {
            "grant_id": grant_data["grant_id"],
            "integrity_sha256": grant_data["integrity_sha256"],
            "authority_class": grant_data["authority_class"],
        }
        actor = {"actor_type": "human", "subject_ref": subject}

        if state == "approved":
            if approval_expires_at is None:
                raise ProviderAdapterContractError(
                    "Approved qualified-human approval requires approval_expires_at"
                )
            approval_expiry = _parse_datetime(
                approval_expires_at, "approval disposition approval_expires_at"
            )
            if approval_expiry <= effective:
                raise ProviderAdapterContractError(
                    "Approved qualified-human approval must expire after effective_at"
                )
            if request_data["expires_at"] is not None and approval_expiry > _parse_datetime(
                request_data["expires_at"], "approval request expires_at"
            ):
                raise ProviderAdapterContractError(
                    "Qualified-human approval cannot outlive its approval request"
                )
            if grant_data["valid_until"] is not None and approval_expiry > _parse_datetime(
                grant_data["valid_until"], "authority grant valid_until"
            ):
                raise ProviderAdapterContractError(
                    "Qualified-human approval cannot outlive its authority grant"
                )
        elif approval_expires_at is not None:
            raise ProviderAdapterContractError(
                "Only approved qualified-human approval may define approval_expires_at"
            )

    seed = json.dumps(
        {
            "request": request_data["integrity_sha256"],
            "state": state,
            "effective_at": timestamp,
            "previous": previous_data["integrity_sha256"] if previous_data else None,
            "actor": actor,
            "reason": reason,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "qualified_human_approval_version": QUALIFIED_HUMAN_APPROVAL_VERSION,
        "record_type": "qualified_human_approval_disposition",
        "disposition_id": (
            "approval-disposition-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "effective_at": timestamp,
        "state": state,
        "approval_request_id": request_data["approval_request_id"],
        "approval_request_integrity_sha256": request_data["integrity_sha256"],
        "previous_disposition_id": (
            previous_data["disposition_id"] if previous_data else None
        ),
        "previous_disposition_integrity_sha256": (
            previous_data["integrity_sha256"] if previous_data else None
        ),
        "actor": actor,
        "authority_grant_ref": grant_ref,
        "approval_expires_at": approval_expires_at if state == "approved" else None,
        "reason": _require_text(reason, "approval disposition reason"),
        "evidence": evidence_items,
        "identity_is_routing_signal": False,
        "policy_write_authority": False,
        "live_routing_authority": False,
        "live_scope_change_authority": False,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return QualifiedHumanApprovalDispositionRecord.from_dict(payload, repo_root=repo_root)


def _validate_disposition_chain(
    request: QualifiedHumanApprovalRequestRecord,
    dispositions: Sequence[QualifiedHumanApprovalDispositionRecord],
    authority_grants: Sequence[QualifiedHumanAuthorityGrantRecord],
) -> list[dict[str, Any]]:
    request_data = request.to_dict()
    grants = {
        record.to_dict()["grant_id"]: record for record in authority_grants
    }
    if len(grants) != len(authority_grants):
        raise ProviderAdapterContractError(
            "Qualified-human approval authority grant IDs must be unique"
        )

    result: list[dict[str, Any]] = []
    previous_record: QualifiedHumanApprovalDispositionRecord | None = None
    seen_ids: set[str] = set()
    for disposition in dispositions:
        data = disposition.to_dict()
        if data["disposition_id"] in seen_ids:
            raise ProviderAdapterContractError(
                "Qualified-human approval disposition IDs must be unique"
            )
        seen_ids.add(data["disposition_id"])
        if data["approval_request_id"] != request_data["approval_request_id"]:
            raise ProviderAdapterContractError(
                "Qualified-human approval disposition references a different request"
            )
        if data["approval_request_integrity_sha256"] != request_data["integrity_sha256"]:
            raise ProviderAdapterContractError(
                "Qualified-human approval disposition does not bind the exact request content"
            )

        previous_data = previous_record.to_dict() if previous_record else None
        expected_previous = (
            (
                previous_data["disposition_id"],
                previous_data["integrity_sha256"],
            )
            if previous_data
            else (None, None)
        )
        actual_previous = (
            data["previous_disposition_id"],
            data["previous_disposition_integrity_sha256"],
        )
        if actual_previous != expected_previous:
            raise ProviderAdapterContractError(
                "Qualified-human approval disposition chain is not contiguous"
            )
        effective = _parse_datetime(data["effective_at"], "approval disposition effective_at")
        _validate_transition(request, str(data["state"]), effective, previous_record)

        if data["actor"]["actor_type"] == "human":
            grant_ref = data["authority_grant_ref"]
            if grant_ref is None:
                raise ProviderAdapterContractError(
                    "Qualified-human approval human disposition lost authority grant evidence"
                )
            grant = _grant_for_ref(grant_ref, grants)
            _assert_grant_covers_request(
                grant,
                request,
                at=effective,
                subject_ref=str(data["actor"]["subject_ref"]),
            )
        result.append(data)
        previous_record = disposition
    return result


def evaluate_qualified_human_finalization(
    dispatch: DispatchRecord,
    route_outcome: RouteOutcomeRecord,
    request: QualifiedHumanApprovalRequestRecord,
    dispositions: Sequence[QualifiedHumanApprovalDispositionRecord],
    *,
    authority_grants: Sequence[QualifiedHumanAuthorityGrantRecord],
    repo_root: str | Path,
    finalized_at: str | None = None,
) -> QualifiedHumanFinalizationRecord:
    _validate_request_binding(dispatch, route_outcome, request)
    request_data = request.to_dict()
    outcome = route_outcome.to_dict()
    chain = _validate_disposition_chain(request, dispositions, authority_grants)
    timestamp = finalized_at or datetime.now(timezone.utc).isoformat()
    finalized = _parse_datetime(timestamp, "human finalization finalized_at")
    if finalized < _parse_datetime(request_data["requested_at"], "approval request requested_at"):
        raise ProviderAdapterContractError(
            "Qualified-human finalization cannot predate its approval request"
        )

    latest = chain[-1] if chain else None
    if latest is not None and finalized < _parse_datetime(
        latest["effective_at"], "current approval disposition effective_at"
    ):
        raise ProviderAdapterContractError(
            "Qualified-human finalization cannot predate its current approval disposition"
        )
    approval_state = "requested"
    block_reason = "missing_approval"
    status = "blocked"
    satisfied = False
    subject_ref: str | None = None
    authority_class: str | None = None

    if latest is not None:
        approval_state = str(latest["state"])
        if approval_state == "approved":
            expiry = _parse_datetime(
                latest["approval_expires_at"], "approval disposition approval_expires_at"
            )
            if finalized >= expiry:
                approval_state = "expired"
                block_reason = "expired"
            else:
                status = "completed"
                block_reason = "none"
                satisfied = True
                subject_ref = str(latest["actor"]["subject_ref"])
                authority_class = str(latest["authority_grant_ref"]["authority_class"])
        elif approval_state == "rejected":
            block_reason = "rejected"
        elif approval_state == "unable_to_determine":
            block_reason = "unable_to_determine"
        elif approval_state == "expired":
            block_reason = "expired"
        elif approval_state == "revoked":
            block_reason = "revoked"

    current_ref = (
        {
            "disposition_id": latest["disposition_id"],
            "integrity_sha256": latest["integrity_sha256"],
        }
        if latest
        else None
    )
    seed = json.dumps(
        {
            "request": request_data["integrity_sha256"],
            "disposition": latest["integrity_sha256"] if latest else None,
            "outcome": outcome["integrity_sha256"],
            "finalized_at": timestamp,
            "status": status,
            "approval_state": approval_state,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "qualified_human_approval_version": QUALIFIED_HUMAN_APPROVAL_VERSION,
        "record_type": "qualified_human_finalization",
        "finalization_id": (
            "human-finalization-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "finalized_at": timestamp,
        "status": status,
        "approval_state": approval_state,
        "block_reason": block_reason,
        "approval_request_ref": {
            "approval_request_id": request_data["approval_request_id"],
            "integrity_sha256": request_data["integrity_sha256"],
        },
        "current_disposition_ref": current_ref,
        "route_outcome_ref": {
            "outcome_id": outcome["outcome_id"],
            "integrity_sha256": outcome["integrity_sha256"],
        },
        "dispatch_id": dispatch.dispatch_id,
        "task_id": dispatch.task_id,
        "qualified_human_approval_satisfied": satisfied,
        "approver_subject_ref": subject_ref,
        "authority_class": authority_class,
        "route_outcome_mutated": False,
        "identity_is_routing_signal": False,
        "model_selection_is_qualification_signal": False,
        "provider_access_is_qualification_signal": False,
        "billing_identity_is_qualification_signal": False,
        "policy_write_authority": False,
        "live_routing_authority": False,
        "live_scope_change_authority": False,
    }
    payload["integrity_sha256"] = _canonical_sha256(payload)
    return QualifiedHumanFinalizationRecord.from_dict(payload, repo_root=repo_root)


ApprovalLedgerRecord = (
    QualifiedHumanAuthorityGrantRecord
    | QualifiedHumanApprovalRequestRecord
    | QualifiedHumanApprovalDispositionRecord
    | QualifiedHumanFinalizationRecord
)


class JsonlQualifiedHumanApprovalLedger:
    """Append-only single-process reference ledger for qualified-human authority evidence."""

    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, record: ApprovalLedgerRecord) -> None:
        data = record.to_dict()
        validated = self._record_from_dict(data)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(validated.to_dict(), sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Qualified-human approval ledger could not be persisted"
            ) from exc

    def read_all(self) -> list[ApprovalLedgerRecord]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Qualified-human approval ledger could not be read"
            ) from exc
        records: list[ApprovalLedgerRecord] = []
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError(
                    f"Qualified-human approval ledger contains invalid JSONL at line {index}"
                ) from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError(
                    f"Qualified-human approval ledger line {index} must be an object"
                )
            records.append(self._record_from_dict(raw))
        return records

    def _record_from_dict(self, data: dict[str, Any]) -> ApprovalLedgerRecord:
        record_type = data.get("record_type")
        if record_type == "qualified_human_authority_grant":
            return QualifiedHumanAuthorityGrantRecord.from_dict(
                data, repo_root=self.repo_root
            )
        if record_type == "qualified_human_approval_request":
            return QualifiedHumanApprovalRequestRecord.from_dict(
                data, repo_root=self.repo_root
            )
        if record_type == "qualified_human_approval_disposition":
            return QualifiedHumanApprovalDispositionRecord.from_dict(
                data, repo_root=self.repo_root
            )
        if record_type == "qualified_human_finalization":
            return QualifiedHumanFinalizationRecord.from_dict(
                data, repo_root=self.repo_root
            )
        raise ProviderAdapterContractError(
            f"Unsupported qualified-human approval ledger record type: {record_type}"
        )
