from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any, Callable, Mapping

import yaml

from .provider_connection import ProviderConnection
from .verification_adapter import LiveVerificationDecision, LiveVerificationError, LiveVerificationRequest
from .verifier_calibration import (
    CalibrationError,
    CalibrationObservation,
    CalibrationPolicy,
    GoldCalibrationCase,
    assess_evidence_readiness,
    evaluate_calibration,
    load_calibration_policy,
    load_gold_cases,
)
from .verifier_calibration_empirical import (
    COLLECTION_ROLE,
    CalibrationVerifierRoute,
    EmpiricalCalibrationPolicy,
    _UsageCaptureConnection,
    _verifier_for_route,
    connections_from_environment,
    load_empirical_policy,
    resolve_collector_revision,
    validate_empirical_policy_against_base,
)
from .verifier_calibration_human_review import build_review_materials, validate_review_packet_is_blinded


EVIDENCE_TIER = "provisional_machine_panel"
PANEL_COLLECTION_ROLE = "calibration_panel_direct"
SUPPORTED_PROVIDERS = {"google", "anthropic", "openai"}


@dataclass(frozen=True, slots=True)
class MachinePanelRoute:
    provider_family: str
    model: str
    reasoning: str | None
    rationale: str
    preview_acknowledged: bool = False

    @property
    def route_id(self) -> str:
        return f"{self.provider_family}/{self.model}/{self.reasoning or 'unspecified'}"

    def as_calibration_route(self) -> CalibrationVerifierRoute:
        return CalibrationVerifierRoute(
            provider_family=self.provider_family,
            model=self.model,
            reasoning=self.reasoning,
        )


@dataclass(frozen=True, slots=True)
class MachinePanelPolicy:
    version: str
    empirical_policy_path: str
    control_corpus_path: str
    rubric_version: str
    verification_policy_version: str
    minimum_distinct_provider_families: int
    panel_routes: tuple[MachinePanelRoute, ...]
    default_panel_labels_path: str
    default_provisional_observations_path: str
    runs_per_case_per_route: int


@dataclass(frozen=True, slots=True)
class MachinePanelLabel:
    review_item_id: str
    judge_provider_family: str
    judge_model: str
    judge_reasoning: str | None
    observed_at: str
    rubric_version: str
    duration_ms: float
    input_tokens: int
    output_tokens: int
    decision: LiveVerificationDecision
    evidence_tier: str = EVIDENCE_TIER
    collection_role: str = PANEL_COLLECTION_ROLE
    reference_control_labels_blinded: bool = True
    model_observations_blinded: bool = True

    @property
    def route_id(self) -> str:
        return (
            f"{self.judge_provider_family}/{self.judge_model}/"
            f"{self.judge_reasoning or 'unspecified'}"
        )

    @property
    def identity(self) -> tuple[str, str]:
        return self.review_item_id, self.route_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_item_id": self.review_item_id,
            "judge_provider_family": self.judge_provider_family,
            "judge_model": self.judge_model,
            "judge_reasoning": self.judge_reasoning,
            "observed_at": self.observed_at,
            "rubric_version": self.rubric_version,
            "evidence_tier": self.evidence_tier,
            "collection_role": self.collection_role,
            "reference_control_labels_blinded": self.reference_control_labels_blinded,
            "model_observations_blinded": self.model_observations_blinded,
            "duration_ms": self.duration_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "decision": _decision_dict(self.decision),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MachinePanelLabel":
        expected = {
            "review_item_id",
            "judge_provider_family",
            "judge_model",
            "judge_reasoning",
            "observed_at",
            "rubric_version",
            "evidence_tier",
            "collection_role",
            "reference_control_labels_blinded",
            "model_observations_blinded",
            "duration_ms",
            "input_tokens",
            "output_tokens",
            "decision",
        }
        _require_exact_fields(raw, expected, "Machine-panel label")
        if raw["evidence_tier"] != EVIDENCE_TIER:
            raise CalibrationError("Machine-panel label evidence_tier is invalid")
        if raw["collection_role"] != PANEL_COLLECTION_ROLE:
            raise CalibrationError("Machine-panel label collection_role is invalid")
        if raw["reference_control_labels_blinded"] is not True:
            raise CalibrationError("Machine-panel judge must be blinded from reference-control labels")
        if raw["model_observations_blinded"] is not True:
            raise CalibrationError("Machine-panel judge must be blinded from verifier observations")
        provider = _required_text(raw["judge_provider_family"], "judge_provider_family")
        if provider not in SUPPORTED_PROVIDERS:
            raise CalibrationError("Machine-panel judge provider is unsupported")
        reasoning = raw["judge_reasoning"]
        if reasoning is not None and (not isinstance(reasoning, str) or not reasoning.strip()):
            raise CalibrationError("judge_reasoning must be a non-empty string or null")
        decision_raw = raw["decision"]
        if not isinstance(decision_raw, dict):
            raise CalibrationError("Machine-panel label decision must be an object")
        try:
            decision = LiveVerificationDecision.from_dict(decision_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            review_item_id=_required_text(raw["review_item_id"], "review_item_id"),
            judge_provider_family=provider,
            judge_model=_required_text(raw["judge_model"], "judge_model"),
            judge_reasoning=reasoning.strip() if isinstance(reasoning, str) else None,
            observed_at=_required_offset_datetime(raw["observed_at"], "observed_at"),
            rubric_version=_required_text(raw["rubric_version"], "rubric_version"),
            duration_ms=_required_non_negative_float(raw["duration_ms"], "duration_ms"),
            input_tokens=_required_non_negative_int(raw["input_tokens"], "input_tokens"),
            output_tokens=_required_non_negative_int(raw["output_tokens"], "output_tokens"),
            decision=decision,
        )


@dataclass(frozen=True, slots=True)
class MachinePanelReadiness:
    panel_coverage_requirements_met: bool
    expected_routes: list[str]
    observed_routes: list[str]
    undercovered_items: list[str]
    unresolved_items: list[str]
    majority_items: int
    item_count: int
    human_ground_truth_claim_authorized: bool = False
    quality_claims_authorized: bool = False
    routing_authority: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ProvisionalCalibrationObservation:
    case_id: str
    verifier_provider_family: str
    verifier_model: str
    verifier_reasoning: str | None
    run_id: str
    observed_at: str
    rubric_version: str
    verification_policy_version: str
    machine_panel_policy_version: str
    collector_revision: str
    duration_ms: float
    input_tokens: int
    output_tokens: int
    decision: LiveVerificationDecision
    evidence_tier: str = EVIDENCE_TIER
    collection_role: str = COLLECTION_ROLE

    @property
    def verifier_route(self) -> str:
        return (
            f"{self.verifier_provider_family}/{self.verifier_model}/"
            f"{self.verifier_reasoning or 'unspecified'}"
        )

    @property
    def identity(self) -> tuple[str, str, str]:
        return self.case_id, self.verifier_route, self.run_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "verifier_provider_family": self.verifier_provider_family,
            "verifier_model": self.verifier_model,
            "verifier_reasoning": self.verifier_reasoning,
            "run_id": self.run_id,
            "observed_at": self.observed_at,
            "rubric_version": self.rubric_version,
            "verification_policy_version": self.verification_policy_version,
            "machine_panel_policy_version": self.machine_panel_policy_version,
            "collector_revision": self.collector_revision,
            "evidence_tier": self.evidence_tier,
            "collection_role": self.collection_role,
            "duration_ms": self.duration_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "decision": _decision_dict(self.decision),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ProvisionalCalibrationObservation":
        expected = {
            "case_id",
            "verifier_provider_family",
            "verifier_model",
            "verifier_reasoning",
            "run_id",
            "observed_at",
            "rubric_version",
            "verification_policy_version",
            "machine_panel_policy_version",
            "collector_revision",
            "evidence_tier",
            "collection_role",
            "duration_ms",
            "input_tokens",
            "output_tokens",
            "decision",
        }
        _require_exact_fields(raw, expected, "Provisional observation")
        if raw["evidence_tier"] != EVIDENCE_TIER:
            raise CalibrationError("Provisional observation evidence_tier is invalid")
        if raw["collection_role"] != COLLECTION_ROLE:
            raise CalibrationError("Provisional observation collection_role is invalid")
        provider = _required_text(raw["verifier_provider_family"], "verifier_provider_family")
        if provider not in SUPPORTED_PROVIDERS:
            raise CalibrationError("Provisional observation provider is unsupported")
        reasoning = raw["verifier_reasoning"]
        if reasoning is not None and (not isinstance(reasoning, str) or not reasoning.strip()):
            raise CalibrationError("verifier_reasoning must be a non-empty string or null")
        decision_raw = raw["decision"]
        if not isinstance(decision_raw, dict):
            raise CalibrationError("Provisional observation decision must be an object")
        try:
            decision = LiveVerificationDecision.from_dict(decision_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            case_id=_required_text(raw["case_id"], "case_id"),
            verifier_provider_family=provider,
            verifier_model=_required_text(raw["verifier_model"], "verifier_model"),
            verifier_reasoning=reasoning.strip() if isinstance(reasoning, str) else None,
            run_id=_required_text(raw["run_id"], "run_id"),
            observed_at=_required_offset_datetime(raw["observed_at"], "observed_at"),
            rubric_version=_required_text(raw["rubric_version"], "rubric_version"),
            verification_policy_version=_required_text(
                raw["verification_policy_version"], "verification_policy_version"
            ),
            machine_panel_policy_version=_required_text(
                raw["machine_panel_policy_version"], "machine_panel_policy_version"
            ),
            collector_revision=_required_text(raw["collector_revision"], "collector_revision"),
            duration_ms=_required_non_negative_float(raw["duration_ms"], "duration_ms"),
            input_tokens=_required_non_negative_int(raw["input_tokens"], "input_tokens"),
            output_tokens=_required_non_negative_int(raw["output_tokens"], "output_tokens"),
            decision=decision,
        )

    def to_base_observation(self) -> CalibrationObservation:
        return CalibrationObservation(
            case_id=self.case_id,
            verifier_provider_family=self.verifier_provider_family,
            verifier_model=self.verifier_model,
            verifier_reasoning=self.verifier_reasoning,
            run_id=self.run_id,
            observed_at=self.observed_at,
            rubric_version=self.rubric_version,
            verification_policy_version=self.verification_policy_version,
            decision=self.decision,
            execution_role="primary",
            retry_count=0,
            fallback_used=False,
            duration_ms=self.duration_ms,
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens,
        )


def _require_exact_fields(raw: dict[str, Any], expected: set[str], label: str) -> None:
    missing = sorted(expected - set(raw))
    unknown = sorted(set(raw) - expected)
    if missing:
        raise CalibrationError(f"{label} is missing fields: " + ", ".join(missing))
    if unknown:
        raise CalibrationError(f"{label} contains unsupported fields: " + ", ".join(unknown))


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CalibrationError(f"{name} must be a non-empty string")
    return value.strip()


def _required_positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise CalibrationError(f"{name} must be a positive integer")
    return value


def _required_non_negative_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CalibrationError(f"{name} must be a non-negative integer")
    return value


def _required_non_negative_float(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0:
        raise CalibrationError(f"{name} must be a non-negative number")
    return float(value)


def _required_offset_datetime(value: object, name: str) -> str:
    text = _required_text(value, name)
    parsed = _parsed_time(text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CalibrationError(f"{name} must include a UTC offset")
    return text


def _parsed_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CalibrationError("timestamp must be RFC 3339-compatible") from exc


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _decision_dict(decision: LiveVerificationDecision) -> dict[str, str]:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def _panel_route_from_dict(raw: object) -> MachinePanelRoute:
    if not isinstance(raw, dict):
        raise CalibrationError("Machine-panel route must be an object")
    allowed = {"provider_family", "model", "reasoning", "rationale", "preview_acknowledged"}
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise CalibrationError("Machine-panel route contains unsupported fields: " + ", ".join(unknown))
    required = {"provider_family", "model", "reasoning", "rationale"}
    missing = sorted(required - set(raw))
    if missing:
        raise CalibrationError("Machine-panel route is missing fields: " + ", ".join(missing))
    provider = _required_text(raw["provider_family"], "panel_route.provider_family")
    if provider not in SUPPORTED_PROVIDERS:
        raise CalibrationError(f"Unsupported machine-panel provider: {provider}")
    model = _required_text(raw["model"], "panel_route.model")
    reasoning = raw["reasoning"]
    if reasoning is not None and (not isinstance(reasoning, str) or not reasoning.strip()):
        raise CalibrationError("panel_route.reasoning must be a non-empty string or null")
    preview_acknowledged = raw.get("preview_acknowledged", False)
    if not isinstance(preview_acknowledged, bool):
        raise CalibrationError("panel_route.preview_acknowledged must be boolean")
    if "preview" in model and preview_acknowledged is not True:
        raise CalibrationError("Preview machine-panel model requires explicit acknowledgement")
    return MachinePanelRoute(
        provider_family=provider,
        model=model,
        reasoning=reasoning.strip() if isinstance(reasoning, str) else None,
        rationale=_required_text(raw["rationale"], "panel_route.rationale"),
        preview_acknowledged=preview_acknowledged,
    )


def load_machine_panel_policy(path: str | Path) -> MachinePanelPolicy:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "provisional":
        raise CalibrationError("Machine-panel policy must be a provisional mapping")
    if payload.get("evidence_tier") != EVIDENCE_TIER:
        raise CalibrationError("Machine-panel policy evidence_tier is invalid")
    base = payload.get("base_calibration")
    panel = payload.get("panel")
    provisional = payload.get("provisional_collection")
    acceptance = payload.get("acceptance")
    routes_raw = payload.get("panel_routes")
    if not all(isinstance(item, dict) for item in (base, panel, provisional, acceptance)):
        raise CalibrationError("Machine-panel policy is missing required mappings")
    if not isinstance(routes_raw, list) or not routes_raw:
        raise CalibrationError("Machine-panel policy requires panel_routes")
    routes = tuple(_panel_route_from_dict(raw) for raw in routes_raw)
    if len({route.route_id for route in routes}) != len(routes):
        raise CalibrationError("Machine-panel routes must be unique")
    if len({route.provider_family for route in routes}) != len(routes):
        raise CalibrationError("Machine-panel routes must use distinct provider families")
    if panel.get("collection_role") != PANEL_COLLECTION_ROLE:
        raise CalibrationError("Machine-panel collection role must be calibration_panel_direct")
    true_panel_fields = (
        "require_all_routes",
        "require_blinded_packet",
        "require_reference_control_labels_blinded_during_judging",
        "require_model_observations_blinded_during_judging",
        "require_distinct_exact_models_from_evaluated_verifier_routes",
        "require_provider_reported_usage",
        "require_duration_measurement",
        "require_offset_aware_timestamp",
        "unresolved_if_no_majority",
    )
    for field in true_panel_fields:
        if panel.get(field) is not True:
            raise CalibrationError(f"panel.{field} must remain true")
    for field in (
        "persist_prompt_or_candidate_content",
        "persist_provider_native_payload",
        "persist_credentials_or_authorization",
        "persist_connection_mechanism",
        "persist_provider_request_identifiers",
    ):
        if panel.get(field) is not False:
            raise CalibrationError(f"panel.{field} must remain false")
    for field in (
        "require_panel_readiness_before_live_collection",
        "require_single_collector_revision_per_evidence_set",
        "resume_without_duplicate_calls",
        "stop_on_verifier_infrastructure_error",
    ):
        if provisional.get(field) is not True:
            raise CalibrationError(f"provisional_collection.{field} must remain true")
    if provisional.get("evaluated_routes_source") != "empirical_policy":
        raise CalibrationError("Provisional evaluated routes must come from empirical policy")
    false_acceptance_fields = (
        "human_ground_truth_claim_authorized",
        "empirical_quality_claims_authorized",
        "live_scope_expansion_authorized",
        "routing_authority",
        "automatic_route_update",
        "human_review_tier_replaced",
    )
    for field in false_acceptance_fields:
        if acceptance.get(field) is not False:
            raise CalibrationError(f"acceptance.{field} must remain false")
    for field in (
        "may_collect_provisional_live_evidence",
        "require_explicit_human_acceptance_for_any_future_route_change",
        "require_independent_residual_risk_review_before_any_future_route_change",
    ):
        if acceptance.get(field) is not True:
            raise CalibrationError(f"acceptance.{field} must remain true")
    return MachinePanelPolicy(
        version=_required_text(payload.get("version"), "version"),
        empirical_policy_path=_required_text(
            base.get("empirical_policy"), "base_calibration.empirical_policy"
        ),
        control_corpus_path=_required_text(
            base.get("control_corpus"), "base_calibration.control_corpus"
        ),
        rubric_version=_required_text(base.get("rubric_version"), "base_calibration.rubric_version"),
        verification_policy_version=_required_text(
            base.get("live_verification_policy_version"),
            "base_calibration.live_verification_policy_version",
        ),
        minimum_distinct_provider_families=_required_positive_int(
            panel.get("minimum_distinct_provider_families"),
            "panel.minimum_distinct_provider_families",
        ),
        panel_routes=routes,
        default_panel_labels_path=_required_text(
            panel.get("default_panel_labels_path"), "panel.default_panel_labels_path"
        ),
        default_provisional_observations_path=_required_text(
            panel.get("default_provisional_observations_path"),
            "panel.default_provisional_observations_path",
        ),
        runs_per_case_per_route=_required_positive_int(
            provisional.get("runs_per_case_per_route"),
            "provisional_collection.runs_per_case_per_route",
        ),
    )


def validate_machine_panel_policy(
    panel: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
    base: CalibrationPolicy,
) -> None:
    validate_empirical_policy_against_base(empirical, base)
    if panel.rubric_version != empirical.rubric_version:
        raise CalibrationError("Machine-panel rubric version mismatches empirical policy")
    if panel.verification_policy_version != empirical.verification_policy_version:
        raise CalibrationError("Machine-panel verification policy version mismatches empirical policy")
    if panel.runs_per_case_per_route != empirical.runs_per_case_per_route:
        raise CalibrationError("Machine-panel provisional run count must match empirical study")
    if len({route.provider_family for route in panel.panel_routes}) < panel.minimum_distinct_provider_families:
        raise CalibrationError("Machine-panel provider-family floor is not met")
    evaluated_models = {route.model for route in empirical.verifier_routes}
    overlap = sorted({route.model for route in panel.panel_routes} & evaluated_models)
    if overlap:
        raise CalibrationError(
            "Machine-panel exact models must differ from evaluated verifier models: "
            + ", ".join(overlap)
        )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CalibrationError(f"{label} could not be read: {path}") from exc
    if not isinstance(raw, dict):
        raise CalibrationError(f"{label} must be an object")
    return raw


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def ensure_blinded_materials(
    cases: list[GoldCalibrationCase],
    rubric_version: str,
    packet_path: str | Path,
    mapping_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    packet_target = Path(packet_path)
    map_target = Path(mapping_path)
    if packet_target.exists() != map_target.exists():
        raise CalibrationError("Blinded packet and private map must either both exist or both be absent")
    if packet_target.exists():
        packet = _read_json(packet_target, "Blinded review packet")
        private_map = _read_json(map_target, "Private review map")
    else:
        packet, private_map = build_review_materials(cases, rubric_version)
        _write_json(packet_target, packet)
        _write_json(map_target, private_map)
    validate_review_packet_is_blinded(packet)
    if packet.get("packet_id") != private_map.get("packet_id"):
        raise CalibrationError("Blinded packet and private map packet_id do not match")
    if packet.get("rubric_version") != rubric_version or private_map.get("rubric_version") != rubric_version:
        raise CalibrationError("Blinded packet rubric version drifted")
    packet_items = packet.get("items")
    map_items = private_map.get("items")
    if not isinstance(packet_items, list) or not isinstance(map_items, list):
        raise CalibrationError("Blinded packet and private map require items")
    packet_ids = {item.get("review_item_id") for item in packet_items if isinstance(item, dict)}
    map_ids = {item.get("review_item_id") for item in map_items if isinstance(item, dict)}
    if packet_ids != map_ids or len(packet_ids) != len(cases):
        raise CalibrationError("Blinded packet and private map do not cover the calibration corpus")
    return packet, private_map


def load_machine_panel_labels(path: str | Path) -> list[MachinePanelLabel]:
    source = Path(path)
    if not source.exists():
        return []
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CalibrationError(f"Machine-panel labels could not be read: {source}") from exc
    labels: list[MachinePanelLabel] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CalibrationError(f"Machine-panel label line {index} is invalid JSON") from exc
        if not isinstance(raw, dict):
            raise CalibrationError(f"Machine-panel label line {index} must be an object")
        labels.append(MachinePanelLabel.from_dict(raw))
    return labels


def _majority_decision(labels: list[MachinePanelLabel]) -> LiveVerificationDecision | None:
    counts = Counter(label.decision for label in labels)
    if not counts:
        return None
    decision, votes = counts.most_common(1)[0]
    return decision if votes >= 2 else None


def assess_machine_panel_readiness(
    packet: dict[str, Any],
    labels: list[MachinePanelLabel],
    policy: MachinePanelPolicy,
) -> MachinePanelReadiness:
    validate_review_packet_is_blinded(packet)
    items = packet.get("items")
    if not isinstance(items, list) or not items:
        raise CalibrationError("Blinded review packet requires items")
    known_items = {
        _required_text(item.get("review_item_id"), "review_item_id")
        for item in items
        if isinstance(item, dict)
    }
    if len(known_items) != len(items):
        raise CalibrationError("Blinded review packet contains invalid or duplicate review items")
    expected_routes = {route.route_id for route in policy.panel_routes}
    unknown_items = sorted({label.review_item_id for label in labels} - known_items)
    if unknown_items:
        raise CalibrationError("Machine-panel labels reference unknown items: " + ", ".join(unknown_items))
    seen: set[tuple[str, str]] = set()
    by_item: dict[str, list[MachinePanelLabel]] = defaultdict(list)
    for label in labels:
        if label.identity in seen:
            raise CalibrationError("Duplicate machine-panel label identity: " + "/".join(label.identity))
        seen.add(label.identity)
        if label.route_id not in expected_routes:
            raise CalibrationError("Machine-panel label uses unauthorized judge route " + label.route_id)
        if label.rubric_version != policy.rubric_version:
            raise CalibrationError("Machine-panel label rubric version drifted")
        by_item[label.review_item_id].append(label)
    undercovered: list[str] = []
    unresolved: list[str] = []
    majority_items = 0
    for item_id in sorted(known_items):
        routes = {label.route_id for label in by_item[item_id]}
        if routes != expected_routes:
            undercovered.append(f"{item_id}:{len(routes)}/{len(expected_routes)}")
        if routes == expected_routes:
            majority = _majority_decision(by_item[item_id])
            if majority is None:
                unresolved.append(item_id)
            else:
                majority_items += 1
    observed_routes = sorted({label.route_id for label in labels})
    return MachinePanelReadiness(
        panel_coverage_requirements_met=not undercovered and set(observed_routes) == expected_routes,
        expected_routes=sorted(expected_routes),
        observed_routes=observed_routes,
        undercovered_items=undercovered,
        unresolved_items=unresolved,
        majority_items=majority_items,
        item_count=len(known_items),
    )


def collect_machine_panel_labels(
    packet: dict[str, Any],
    policy: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
    connections: Mapping[str, ProviderConnection],
    *,
    output_path: str | Path,
    clock: Callable[[], float] = monotonic,
    now: Callable[[], str] = _utc_now,
) -> list[MachinePanelLabel]:
    target = Path(output_path)
    existing = load_machine_panel_labels(target)
    assess_machine_panel_readiness(packet, existing, policy) if existing else None
    completed = {label.identity for label in existing}
    missing_connections = sorted({route.provider_family for route in policy.panel_routes} - set(connections))
    if missing_connections:
        raise CalibrationError(
            "Missing provider connections for machine panel: " + ", ".join(missing_connections)
        )
    items = packet.get("items")
    if not isinstance(items, list):
        raise CalibrationError("Blinded review packet requires items")
    collected = list(existing)
    for route in policy.panel_routes:
        delegate = connections[route.provider_family]
        if delegate.provider_family != route.provider_family:
            raise CalibrationError("Machine-panel connection provider mismatch")
        calibration_route = route.as_calibration_route()
        for item in items:
            if not isinstance(item, dict):
                raise CalibrationError("Blinded review packet item must be an object")
            review_item_id = _required_text(item.get("review_item_id"), "review_item_id")
            identity = (review_item_id, route.route_id)
            if identity in completed:
                continue
            task = _required_text(item.get("task"), "task")
            candidate = _required_text(item.get("candidate_output"), "candidate_output")
            capture = _UsageCaptureConnection(delegate)
            request = LiveVerificationRequest(
                dispatch_id=f"machine-panel-{review_item_id}-{route.provider_family}",
                task_id=f"machine-panel-{review_item_id}",
                verifier_provider_family=route.provider_family,
                verifier_model=route.model,
                verifier_reasoning_effort=route.reasoning,
                risk_level=empirical.risk_level,
                verification_methods=empirical.verification_methods,
                task=task,
                output_text=candidate,
            )
            started = clock()
            try:
                response = _verifier_for_route(
                    calibration_route, {route.provider_family: capture}
                ).verify(request)
            except LiveVerificationError as exc:
                raise CalibrationError(
                    f"Machine-panel judge infrastructure failed for {review_item_id}@{route.route_id}"
                ) from exc
            duration_ms = max(0.0, (clock() - started) * 1000.0)
            if response.provider_family != route.provider_family or response.model != route.model:
                raise CalibrationError("Machine-panel judge changed the authorized route")
            if capture.input_tokens is None or capture.output_tokens is None:
                raise CalibrationError(
                    f"Machine-panel judge did not return required provider usage for {route.route_id}"
                )
            label = MachinePanelLabel(
                review_item_id=review_item_id,
                judge_provider_family=route.provider_family,
                judge_model=route.model,
                judge_reasoning=route.reasoning,
                observed_at=_required_offset_datetime(now(), "observed_at"),
                rubric_version=policy.rubric_version,
                duration_ms=duration_ms,
                input_tokens=capture.input_tokens,
                output_tokens=capture.output_tokens,
                decision=response.decision,
            )
            _append_jsonl(target, label.to_dict())
            collected.append(label)
            completed.add(label.identity)
    readiness = assess_machine_panel_readiness(packet, collected, policy)
    if not readiness.panel_coverage_requirements_met:
        raise CalibrationError("Machine-panel coverage is incomplete after collection")
    return collected


def load_provisional_observations(path: str | Path) -> list[ProvisionalCalibrationObservation]:
    source = Path(path)
    if not source.exists():
        return []
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CalibrationError(f"Provisional observations could not be read: {source}") from exc
    observations: list[ProvisionalCalibrationObservation] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CalibrationError(f"Provisional observation line {index} is invalid JSON") from exc
        if not isinstance(raw, dict):
            raise CalibrationError(f"Provisional observation line {index} must be an object")
        observations.append(ProvisionalCalibrationObservation.from_dict(raw))
    return observations


def validate_provisional_observations(
    cases: list[GoldCalibrationCase],
    observations: list[ProvisionalCalibrationObservation],
    panel_labels: list[MachinePanelLabel],
    panel_policy: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
) -> None:
    known_cases = {case.case_id for case in cases}
    allowed_routes = {route.route_id for route in empirical.verifier_routes}
    panel_completed_at = max(_parsed_time(label.observed_at) for label in panel_labels)
    seen: set[tuple[str, str, str]] = set()
    revisions: set[str] = set()
    for observation in observations:
        if observation.case_id not in known_cases:
            raise CalibrationError("Provisional observation references unknown case " + observation.case_id)
        if observation.identity in seen:
            raise CalibrationError("Duplicate provisional observation identity: " + "/".join(observation.identity))
        seen.add(observation.identity)
        revisions.add(observation.collector_revision)
        if observation.verifier_route not in allowed_routes:
            raise CalibrationError("Provisional observation uses unauthorized verifier route " + observation.verifier_route)
        if observation.rubric_version != panel_policy.rubric_version:
            raise CalibrationError("Provisional observation rubric version drifted")
        if observation.verification_policy_version != panel_policy.verification_policy_version:
            raise CalibrationError("Provisional observation verification policy version drifted")
        if observation.machine_panel_policy_version != panel_policy.version:
            raise CalibrationError("Provisional observation machine-panel policy version drifted")
        if _parsed_time(observation.observed_at) < panel_completed_at:
            raise CalibrationError("Provisional observation predates completion of machine-panel coverage")
    if len(revisions) > 1:
        raise CalibrationError("Provisional evidence set mixes collector revisions")


def collect_provisional_observations(
    cases: list[GoldCalibrationCase],
    packet: dict[str, Any],
    panel_labels: list[MachinePanelLabel],
    panel_policy: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
    connections: Mapping[str, ProviderConnection],
    *,
    collector_revision: str,
    output_path: str | Path,
    providers: set[str] | None = None,
    clock: Callable[[], float] = monotonic,
    now: Callable[[], str] = _utc_now,
) -> list[ProvisionalCalibrationObservation]:
    readiness = assess_machine_panel_readiness(packet, panel_labels, panel_policy)
    if not readiness.panel_coverage_requirements_met:
        raise CalibrationError("Machine-panel coverage must be complete before provisional live collection")
    revision = _required_text(collector_revision, "collector_revision")
    if len(revision) < 7:
        raise CalibrationError("collector_revision must identify a concrete repository revision")
    panel_completed_at = max(_parsed_time(label.observed_at) for label in panel_labels)
    collection_started_at = _parsed_time(_required_offset_datetime(now(), "collection_started_at"))
    if collection_started_at < panel_completed_at:
        raise CalibrationError("Provisional collection cannot start before machine-panel coverage is complete")
    target = Path(output_path)
    existing = load_provisional_observations(target)
    if existing:
        validate_provisional_observations(
            cases, existing, panel_labels, panel_policy, empirical
        )
        if {observation.collector_revision for observation in existing} != {revision}:
            raise CalibrationError("Existing provisional evidence uses a different collector revision")
    completed = {observation.identity for observation in existing}
    routes = [
        route
        for route in empirical.verifier_routes
        if providers is None or route.provider_family in providers
    ]
    if not routes:
        raise CalibrationError("No provisional verifier routes were selected")
    missing_connections = sorted({route.provider_family for route in routes} - set(connections))
    if missing_connections:
        raise CalibrationError(
            "Missing provider connections for provisional collection: " + ", ".join(missing_connections)
        )
    collected = list(existing)
    for route in routes:
        delegate = connections[route.provider_family]
        if delegate.provider_family != route.provider_family:
            raise CalibrationError("Provisional connection provider mismatch")
        for case in cases:
            for run_number in range(1, panel_policy.runs_per_case_per_route + 1):
                run_id = f"r{run_number:02d}"
                identity = (case.case_id, route.route_id, run_id)
                if identity in completed:
                    continue
                capture = _UsageCaptureConnection(delegate)
                request = LiveVerificationRequest(
                    dispatch_id=f"provisional-{case.case_id}-{route.provider_family}-{run_id}",
                    task_id=f"provisional-{case.case_id}",
                    verifier_provider_family=route.provider_family,
                    verifier_model=route.model,
                    verifier_reasoning_effort=route.reasoning,
                    risk_level=empirical.risk_level,
                    verification_methods=empirical.verification_methods,
                    task=case.task,
                    output_text=case.candidate_output,
                )
                started = clock()
                try:
                    response = _verifier_for_route(
                        route, {route.provider_family: capture}
                    ).verify(request)
                except LiveVerificationError as exc:
                    raise CalibrationError(
                        f"Provisional verifier infrastructure failed for {case.case_id}@{route.route_id}:{run_id}"
                    ) from exc
                duration_ms = max(0.0, (clock() - started) * 1000.0)
                if response.provider_family != route.provider_family or response.model != route.model:
                    raise CalibrationError("Provisional verifier changed the authorized route")
                if capture.input_tokens is None or capture.output_tokens is None:
                    raise CalibrationError(
                        f"Provisional verifier did not return required provider usage for {route.route_id}"
                    )
                observed_at = _required_offset_datetime(now(), "observed_at")
                if _parsed_time(observed_at) < panel_completed_at:
                    raise CalibrationError("Provisional observation predates machine-panel completion")
                observation = ProvisionalCalibrationObservation(
                    case_id=case.case_id,
                    verifier_provider_family=route.provider_family,
                    verifier_model=route.model,
                    verifier_reasoning=route.reasoning,
                    run_id=run_id,
                    observed_at=observed_at,
                    rubric_version=panel_policy.rubric_version,
                    verification_policy_version=panel_policy.verification_policy_version,
                    machine_panel_policy_version=panel_policy.version,
                    collector_revision=revision,
                    duration_ms=duration_ms,
                    input_tokens=capture.input_tokens,
                    output_tokens=capture.output_tokens,
                    decision=response.decision,
                )
                _append_jsonl(target, observation.to_dict())
                collected.append(observation)
                completed.add(observation.identity)
    validate_provisional_observations(
        cases, collected, panel_labels, panel_policy, empirical
    )
    return collected


def _mapping_aliases(private_map: dict[str, Any]) -> dict[str, str]:
    items = private_map.get("items")
    if not isinstance(items, list):
        raise CalibrationError("Private review map requires items")
    aliases: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {"review_item_id", "case_id"}:
            raise CalibrationError("Private review map item is invalid")
        review_item_id = _required_text(item["review_item_id"], "review_item_id")
        if review_item_id in aliases:
            raise CalibrationError("Private review map contains duplicate review item")
        aliases[review_item_id] = _required_text(item["case_id"], "case_id")
    return aliases


def _panel_comparison(
    cases: list[GoldCalibrationCase],
    labels: list[MachinePanelLabel],
    private_map: dict[str, Any],
) -> dict[str, Any]:
    aliases = _mapping_aliases(private_map)
    gold = {case.case_id: case.gold for case in cases}
    by_item: dict[str, list[MachinePanelLabel]] = defaultdict(list)
    for label in labels:
        by_item[label.review_item_id].append(label)
    majority_cases = 0
    agreement_cases = 0
    disagreements: list[str] = []
    unresolved: list[str] = []
    for item_id, case_id in sorted(aliases.items()):
        majority = _majority_decision(by_item[item_id])
        if majority is None:
            unresolved.append(case_id)
            continue
        majority_cases += 1
        if majority == gold[case_id]:
            agreement_cases += 1
        else:
            disagreements.append(case_id)
    return {
        "majority_cases": majority_cases,
        "case_count": len(cases),
        "majority_coverage_rate": majority_cases / len(cases) if cases else 0.0,
        "reference_control_exact_agreement_rate": (
            agreement_cases / majority_cases if majority_cases else 0.0
        ),
        "reference_control_disagreement_cases": disagreements,
        "unresolved_no_majority_cases": unresolved,
        "human_ground_truth": False,
    }


def evaluate_provisional_calibration(
    cases: list[GoldCalibrationCase],
    packet: dict[str, Any],
    private_map: dict[str, Any],
    panel_labels: list[MachinePanelLabel],
    observations: list[ProvisionalCalibrationObservation],
    panel_policy: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
    base: CalibrationPolicy,
) -> dict[str, Any]:
    panel_readiness = assess_machine_panel_readiness(packet, panel_labels, panel_policy)
    if not panel_readiness.panel_coverage_requirements_met:
        raise CalibrationError("Machine-panel coverage is incomplete")
    validate_provisional_observations(
        cases, observations, panel_labels, panel_policy, empirical
    )
    base_observations = [observation.to_base_observation() for observation in observations]
    metrics = evaluate_calibration(cases, base_observations, policy=base).to_dict()
    path_metrics = metrics.pop("by_execution_path")
    metrics["by_collection_path"] = {
        COLLECTION_ROLE: path_metrics.get(
            "primary_no_retry", {"observations": 0, "exact_status_accuracy": 0.0}
        )
    }
    by_route: dict[str, dict[str, Any]] = {}
    for route in empirical.verifier_routes:
        route_observations = [
            observation.to_base_observation()
            for observation in observations
            if observation.verifier_route == route.route_id
        ]
        if route_observations:
            route_metrics = evaluate_calibration(cases, route_observations, policy=base).to_dict()
            route_metrics.pop("by_execution_path", None)
            by_route[route.route_id] = route_metrics
    readiness = assess_evidence_readiness(cases, base_observations, base).to_dict()
    expected_routes = {route.route_id for route in empirical.verifier_routes}
    observed_routes = {observation.verifier_route for observation in observations}
    route_complete = observed_routes == expected_routes
    readiness["provisional_required_routes_present"] = route_complete
    readiness["data_requirements_met"] = bool(readiness["data_requirements_met"] and route_complete)
    return {
        "evidence_tier": EVIDENCE_TIER,
        "metrics_against_reference_control": metrics,
        "metrics_by_verifier_route_against_reference_control": by_route,
        "machine_panel": _panel_comparison(cases, panel_labels, private_map),
        "machine_panel_readiness": panel_readiness.to_dict(),
        "reference_control_readiness": readiness,
        "provisional_evidence_complete": bool(
            panel_readiness.panel_coverage_requirements_met and readiness["data_requirements_met"]
        ),
        "authority": {
            "human_ground_truth_claim_authorized": False,
            "quality_claims_authorized": False,
            "scope_expansion_authorized": False,
            "routing_authority": False,
            "automatic_route_update": False,
            "human_review_tier_replaced": False,
            "explicit_human_acceptance_required_for_future_route_change": True,
            "independent_residual_risk_review_required_for_future_route_change": True,
        },
    }


def planned_machine_panel_study(
    cases: list[GoldCalibrationCase],
    panel_policy: MachinePanelPolicy,
    empirical: EmpiricalCalibrationPolicy,
) -> dict[str, Any]:
    panel_calls = len(cases) * len(panel_policy.panel_routes)
    provisional_calls = (
        len(cases) * len(empirical.verifier_routes) * panel_policy.runs_per_case_per_route
    )
    return {
        "evidence_tier": EVIDENCE_TIER,
        "case_count": len(cases),
        "panel_routes": [route.route_id for route in panel_policy.panel_routes],
        "evaluated_verifier_routes": [route.route_id for route in empirical.verifier_routes],
        "planned_machine_panel_calls": panel_calls,
        "planned_provisional_verifier_calls": provisional_calls,
        "planned_total_live_calls": panel_calls + provisional_calls,
        "human_ground_truth_claim_authorized": False,
        "quality_claims_authorized": False,
        "routing_authority": False,
    }


def _load_context(repo_root: Path, policy_path: str | Path):
    panel = load_machine_panel_policy(repo_root / policy_path)
    empirical = load_empirical_policy(repo_root / panel.empirical_policy_path)
    base = load_calibration_policy(repo_root / empirical.base_policy_path)
    validate_machine_panel_policy(panel, empirical, base)
    cases = load_gold_cases(repo_root / panel.control_corpus_path, policy=base)
    return panel, empirical, base, cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect provisional provider-diverse machine-panel verifier calibration evidence"
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--machine-panel-policy",
        default="policy/verification/verifier-calibration-machine-panel.yaml",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("plan", help="Show the provisional study plan without provider calls")

    panel_parser = subparsers.add_parser(
        "collect-panel", help="Collect blinded provider-diverse machine-panel judgments"
    )
    panel_parser.add_argument("--packet")
    panel_parser.add_argument("--mapping")
    panel_parser.add_argument("--labels")
    panel_parser.add_argument("--execute-live", action="store_true")

    observations_parser = subparsers.add_parser(
        "collect-observations", help="Collect provisional verifier observations after panel coverage"
    )
    observations_parser.add_argument("--packet", required=True)
    observations_parser.add_argument("--panel-labels", required=True)
    observations_parser.add_argument("--observations")
    observations_parser.add_argument("--collector-revision")
    observations_parser.add_argument("--provider", action="append", choices=sorted(SUPPORTED_PROVIDERS))
    observations_parser.add_argument("--execute-live", action="store_true")

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate provisional observations and panel consensus"
    )
    evaluate_parser.add_argument("--packet", required=True)
    evaluate_parser.add_argument("--mapping", required=True)
    evaluate_parser.add_argument("--panel-labels", required=True)
    evaluate_parser.add_argument("--observations", required=True)
    evaluate_parser.add_argument("--output")

    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        panel_policy, empirical, base, cases = _load_context(root, args.machine_panel_policy)
        if args.command == "plan":
            result = planned_machine_panel_study(cases, panel_policy, empirical)
        elif args.command == "collect-panel":
            if not args.execute_live:
                raise CalibrationError("Machine-panel collection requires explicit --execute-live acknowledgement")
            packet_path = Path(args.packet or root / ".teo/runtime/verifier-calibration/machine-panel-packet.json")
            mapping_path = Path(args.mapping or root / ".teo/runtime/verifier-calibration/machine-panel-map.json")
            labels_path = Path(args.labels or root / panel_policy.default_panel_labels_path)
            packet, _ = ensure_blinded_materials(
                cases, panel_policy.rubric_version, packet_path, mapping_path
            )
            routes = tuple(route.as_calibration_route() for route in panel_policy.panel_routes)
            labels = collect_machine_panel_labels(
                packet,
                panel_policy,
                empirical,
                connections_from_environment(routes),
                output_path=labels_path,
            )
            result = {
                "label_count": len(labels),
                "labels_path": str(labels_path),
                "packet_path": str(packet_path),
                "private_map_path": str(mapping_path),
                "readiness": assess_machine_panel_readiness(packet, labels, panel_policy).to_dict(),
                "human_ground_truth_claim_authorized": False,
                "quality_claims_authorized": False,
            }
        elif args.command == "collect-observations":
            if not args.execute_live:
                raise CalibrationError("Provisional live collection requires explicit --execute-live acknowledgement")
            packet = _read_json(Path(args.packet), "Blinded review packet")
            panel_labels = load_machine_panel_labels(args.panel_labels)
            if not panel_labels:
                raise CalibrationError("Machine-panel labels are empty")
            providers = set(args.provider) if args.provider else None
            selected_routes = tuple(
                route
                for route in empirical.verifier_routes
                if providers is None or route.provider_family in providers
            )
            observations_path = Path(
                args.observations or root / panel_policy.default_provisional_observations_path
            )
            observations = collect_provisional_observations(
                cases,
                packet,
                panel_labels,
                panel_policy,
                empirical,
                connections_from_environment(selected_routes),
                collector_revision=resolve_collector_revision(args.collector_revision),
                output_path=observations_path,
                providers=providers,
            )
            result = {
                "observation_count": len(observations),
                "observations_path": str(observations_path),
                "quality_claims_authorized": False,
                "routing_authority": False,
            }
        else:
            packet = _read_json(Path(args.packet), "Blinded review packet")
            private_map = _read_json(Path(args.mapping), "Private review map")
            panel_labels = load_machine_panel_labels(args.panel_labels)
            observations = load_provisional_observations(args.observations)
            if not panel_labels:
                raise CalibrationError("Machine-panel labels are empty")
            if not observations:
                raise CalibrationError("Provisional observations are empty")
            result = evaluate_provisional_calibration(
                cases,
                packet,
                private_map,
                panel_labels,
                observations,
                panel_policy,
                empirical,
                base,
            )
            if args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (CalibrationError, OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        parser.error(str(exc))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
