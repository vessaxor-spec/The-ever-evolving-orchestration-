from __future__ import annotations

import argparse
import json
import os
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic
from typing import Any, Callable, Literal, Mapping

import yaml

from .anthropic_verifier import AnthropicLiveVerifier
from .google_verifier import GoogleLiveVerifier
from .openai_verifier import OpenAILiveVerifier
from .provider_connection import (
    HeaderProviderConnection,
    ProviderConnection,
    ProviderConnectionRequest,
    ProviderConnectionResponse,
)
from .verification_adapter import (
    LiveVerificationDecision,
    LiveVerificationError,
    LiveVerificationRequest,
)
from .verifier_calibration import (
    CalibrationError,
    CalibrationObservation,
    CalibrationPolicy,
    GoldCalibrationCase,
    assess_evidence_readiness,
    evaluate_calibration,
    load_calibration_policy,
    load_gold_cases,
    validate_gold_corpus,
)

ReviewerRole = Literal["reviewer", "adjudicator"]
COLLECTION_ROLE = "calibration_direct"
SUPPORTED_PROVIDERS = {"google", "anthropic", "openai"}


@dataclass(frozen=True, slots=True)
class CalibrationVerifierRoute:
    provider_family: str
    model: str
    reasoning: str | None

    @property
    def route_id(self) -> str:
        return f"{self.provider_family}/{self.model}/{self.reasoning or 'unspecified'}"


@dataclass(frozen=True, slots=True)
class EmpiricalCalibrationPolicy:
    version: str
    base_policy_path: str
    control_corpus_path: str
    rubric_version: str
    verification_policy_version: str
    risk_level: str
    verification_methods: tuple[str, ...]
    runs_per_case_per_route: int
    default_observations_path: str
    verifier_routes: tuple[CalibrationVerifierRoute, ...]
    minimum_independent_reviewers_per_case: int
    default_labels_path: str
    require_independent_residual_risk_review_after_collection: bool
    require_explicit_human_acceptance_after_metrics: bool


@dataclass(frozen=True, slots=True)
class HumanCalibrationLabel:
    case_id: str
    reviewer_id: str
    reviewer_role: ReviewerRole
    reviewed_at: str
    rubric_version: str
    observations_blinded: bool
    reference_control_labels_blinded: bool
    source_packet_id: str
    decision: LiveVerificationDecision

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HumanCalibrationLabel":
        fields = {
            "case_id",
            "reviewer_id",
            "reviewer_role",
            "reviewed_at",
            "rubric_version",
            "observations_blinded",
            "reference_control_labels_blinded",
            "source_packet_id",
            "decision",
        }
        _require_exact_fields(data, fields, "Human calibration label")
        role = data["reviewer_role"]
        if not isinstance(role, str) or role not in {"reviewer", "adjudicator"}:
            raise CalibrationError("Human calibration label reviewer_role is invalid")
        reviewer_id = _required_text(data["reviewer_id"], "reviewer_id")
        if not _opaque_reviewer_id(reviewer_id):
            raise CalibrationError(
                "Human calibration label reviewer_id must be an opaque identifier, not a name or email"
            )
        source_packet_id = _required_text(data["source_packet_id"], "source_packet_id")
        if not source_packet_id.startswith("packet-"):
            raise CalibrationError("Human calibration label source_packet_id must identify a blinded review packet")
        if data["observations_blinded"] is not True:
            raise CalibrationError(
                "Human calibration labels must attest that model observations were blinded"
            )
        if data["reference_control_labels_blinded"] is not True:
            raise CalibrationError(
                "Human calibration labels must attest that reference-control labels were blinded"
            )
        decision_raw = data["decision"]
        if not isinstance(decision_raw, dict):
            raise CalibrationError("Human calibration label decision must be an object")
        try:
            decision = LiveVerificationDecision.from_dict(decision_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            case_id=_required_text(data["case_id"], "case_id"),
            reviewer_id=reviewer_id,
            reviewer_role=role,  # type: ignore[arg-type]
            reviewed_at=_required_offset_datetime(data["reviewed_at"], "reviewed_at"),
            rubric_version=_required_text(data["rubric_version"], "rubric_version"),
            observations_blinded=True,
            reference_control_labels_blinded=True,
            source_packet_id=source_packet_id,
            decision=decision,
        )


@dataclass(frozen=True, slots=True)
class HumanLabelReadiness:
    human_label_requirements_met: bool
    minimum_independent_reviewers_per_case: int
    reviewer_ids: list[str]
    source_packet_id: str | None
    undercovered_cases: list[str]
    disagreement_cases: list[str]
    adjudication_missing_cases: list[str]
    label_window_start: str | None
    label_window_end: str | None
    quality_claims_authorized: bool = False
    scope_expansion_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class EmpiricalCalibrationObservation:
    case_id: str
    verifier_provider_family: str
    verifier_model: str
    verifier_reasoning: str | None
    run_id: str
    observed_at: str
    rubric_version: str
    verification_policy_version: str
    empirical_policy_version: str
    collector_revision: str
    duration_ms: float
    input_tokens: int
    output_tokens: int
    decision: LiveVerificationDecision
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
            "empirical_policy_version": self.empirical_policy_version,
            "collector_revision": self.collector_revision,
            "collection_role": self.collection_role,
            "duration_ms": self.duration_ms,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "decision": _decision_dict(self.decision),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EmpiricalCalibrationObservation":
        fields = {
            "case_id",
            "verifier_provider_family",
            "verifier_model",
            "verifier_reasoning",
            "run_id",
            "observed_at",
            "rubric_version",
            "verification_policy_version",
            "empirical_policy_version",
            "collector_revision",
            "collection_role",
            "duration_ms",
            "input_tokens",
            "output_tokens",
            "decision",
        }
        _require_exact_fields(data, fields, "Empirical calibration observation")
        if data["collection_role"] != COLLECTION_ROLE:
            raise CalibrationError(
                "Empirical calibration observations must use calibration_direct collection role"
            )
        provider = _required_text(
            data["verifier_provider_family"], "verifier_provider_family"
        )
        if provider not in SUPPORTED_PROVIDERS:
            raise CalibrationError("Empirical calibration observation provider is unsupported")
        reasoning = data["verifier_reasoning"]
        if reasoning is not None and (
            not isinstance(reasoning, str) or not reasoning.strip()
        ):
            raise CalibrationError("verifier_reasoning must be a non-empty string or null")
        decision_raw = data["decision"]
        if not isinstance(decision_raw, dict):
            raise CalibrationError("Empirical calibration observation decision must be an object")
        try:
            decision = LiveVerificationDecision.from_dict(decision_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            case_id=_required_text(data["case_id"], "case_id"),
            verifier_provider_family=provider,
            verifier_model=_required_text(data["verifier_model"], "verifier_model"),
            verifier_reasoning=reasoning.strip() if isinstance(reasoning, str) else None,
            run_id=_required_text(data["run_id"], "run_id"),
            observed_at=_required_offset_datetime(data["observed_at"], "observed_at"),
            rubric_version=_required_text(data["rubric_version"], "rubric_version"),
            verification_policy_version=_required_text(
                data["verification_policy_version"], "verification_policy_version"
            ),
            empirical_policy_version=_required_text(
                data["empirical_policy_version"], "empirical_policy_version"
            ),
            collector_revision=_required_text(
                data["collector_revision"], "collector_revision"
            ),
            duration_ms=_required_non_negative_float(data["duration_ms"], "duration_ms"),
            input_tokens=_required_non_negative_int(data["input_tokens"], "input_tokens"),
            output_tokens=_required_non_negative_int(data["output_tokens"], "output_tokens"),
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


class _UsageCaptureConnection:
    """Ephemeral usage extractor. Provider-native payloads are never persisted."""

    def __init__(self, delegate: ProviderConnection) -> None:
        self.provider_family = delegate.provider_family
        self._delegate = delegate
        self.input_tokens: int | None = None
        self.output_tokens: int | None = None

    def invoke(self, request: ProviderConnectionRequest) -> ProviderConnectionResponse:
        response = self._delegate.invoke(request)
        self.input_tokens, self.output_tokens = _extract_provider_usage(
            self.provider_family, response.body
        )
        return response


def _require_exact_fields(data: dict[str, Any], fields: set[str], label: str) -> None:
    missing = sorted(fields - set(data))
    unknown = sorted(set(data) - fields)
    if missing:
        raise CalibrationError(f"{label} is missing fields: " + ", ".join(missing))
    if unknown:
        raise CalibrationError(
            f"{label} contains unsupported fields: " + ", ".join(unknown)
        )


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CalibrationError(f"{name} must be a non-empty string")
    return value.strip()


def _required_bool(value: object, name: str, *, expected: bool | None = None) -> bool:
    if not isinstance(value, bool):
        raise CalibrationError(f"{name} must be a boolean")
    if expected is not None and value is not expected:
        raise CalibrationError(f"{name} must be {str(expected).lower()}")
    return value


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


def _opaque_reviewer_id(value: str) -> bool:
    return (
        3 <= len(value) <= 64
        and "@" not in value
        and " " not in value
        and value[0].isalnum()
        and all(character.isalnum() or character in {".", "_", "-"} for character in value)
    )


def _decision_dict(decision: LiveVerificationDecision) -> dict[str, str]:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def _route_from_dict(raw: object) -> CalibrationVerifierRoute:
    if not isinstance(raw, dict):
        raise CalibrationError("Empirical calibration verifier route must be an object")
    _require_exact_fields(raw, {"provider_family", "model", "reasoning"}, "Verifier route")
    provider = _required_text(raw["provider_family"], "route.provider_family")
    if provider not in SUPPORTED_PROVIDERS:
        raise CalibrationError(f"Unsupported empirical verifier provider: {provider}")
    reasoning = raw["reasoning"]
    if reasoning is not None and (
        not isinstance(reasoning, str) or not reasoning.strip()
    ):
        raise CalibrationError("route.reasoning must be a non-empty string or null")
    return CalibrationVerifierRoute(
        provider_family=provider,
        model=_required_text(raw["model"], "route.model"),
        reasoning=reasoning.strip() if isinstance(reasoning, str) else None,
    )


def load_empirical_policy(path: str | Path) -> EmpiricalCalibrationPolicy:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "active":
        raise CalibrationError("Empirical calibration policy must be an active mapping")
    base = payload.get("base_calibration")
    collection = payload.get("collection")
    human = payload.get("human_labeling")
    acceptance = payload.get("acceptance")
    routes_raw = payload.get("verifier_routes")
    if not all(isinstance(item, dict) for item in (base, collection, human, acceptance)):
        raise CalibrationError("Empirical calibration policy is missing required mappings")
    if not isinstance(routes_raw, list) or not routes_raw:
        raise CalibrationError("Empirical calibration policy requires verifier_routes")

    routes = tuple(_route_from_dict(raw) for raw in routes_raw)
    if len({route.route_id for route in routes}) != len(routes):
        raise CalibrationError("Empirical calibration verifier routes must be unique")
    if len({route.provider_family for route in routes}) != len(routes):
        raise CalibrationError("Empirical calibration routes must use distinct provider families")

    if collection.get("role") != COLLECTION_ROLE:
        raise CalibrationError("Empirical calibration collection role must be calibration_direct")
    if collection.get("risk_level") != "low":
        raise CalibrationError("Empirical calibration collection must remain low risk")
    methods = collection.get("verification_methods")
    if not isinstance(methods, list) or not methods or not all(
        isinstance(item, str) and item.strip() for item in methods
    ):
        raise CalibrationError("Empirical calibration verification_methods must be a non-empty list")

    for field in (
        "require_all_routes",
        "stop_on_verifier_infrastructure_error",
        "resume_without_duplicate_calls",
        "require_provider_reported_usage",
        "require_duration_measurement",
        "require_offset_aware_timestamp",
        "require_single_collector_revision_per_evidence_set",
    ):
        _required_bool(collection.get(field), f"collection.{field}", expected=True)
    for field in (
        "persist_prompt_or_candidate_content",
        "persist_provider_native_payload",
        "persist_credentials_or_authorization",
        "persist_connection_mechanism",
        "persist_provider_request_identifiers",
    ):
        _required_bool(collection.get(field), f"collection.{field}", expected=False)
    for field in (
        "reviewers_blinded_from_model_observations",
        "reviewers_blinded_from_reference_control_labels",
        "adjudication_required_on_disagreement",
        "adjudicator_must_be_distinct_from_case_reviewers",
        "require_offset_aware_timestamp",
    ):
        _required_bool(human.get(field), f"human_labeling.{field}", expected=True)
    for field in (
        "empirical_quality_claims_authorized",
        "live_scope_expansion_authorized",
        "routing_authority",
        "automatic_route_update",
    ):
        _required_bool(acceptance.get(field), f"acceptance.{field}", expected=False)
    for field in (
        "require_human_label_readiness_before_live_collection",
        "require_independent_residual_risk_review_after_collection",
        "require_explicit_human_acceptance_after_metrics",
    ):
        _required_bool(acceptance.get(field), f"acceptance.{field}", expected=True)

    return EmpiricalCalibrationPolicy(
        version=_required_text(payload.get("version"), "version"),
        base_policy_path=_required_text(base.get("policy"), "base_calibration.policy"),
        control_corpus_path=_required_text(
            base.get("control_corpus"), "base_calibration.control_corpus"
        ),
        rubric_version=_required_text(base.get("rubric_version"), "base_calibration.rubric_version"),
        verification_policy_version=_required_text(
            base.get("live_verification_policy_version"),
            "base_calibration.live_verification_policy_version",
        ),
        risk_level="low",
        verification_methods=tuple(item.strip() for item in methods),
        runs_per_case_per_route=_required_positive_int(
            collection.get("runs_per_case_per_route"), "collection.runs_per_case_per_route"
        ),
        default_observations_path=_required_text(
            collection.get("default_observations_path"), "collection.default_observations_path"
        ),
        verifier_routes=routes,
        minimum_independent_reviewers_per_case=_required_positive_int(
            human.get("minimum_independent_reviewers_per_case"),
            "human_labeling.minimum_independent_reviewers_per_case",
        ),
        default_labels_path=_required_text(
            human.get("default_labels_path"), "human_labeling.default_labels_path"
        ),
        require_independent_residual_risk_review_after_collection=True,
        require_explicit_human_acceptance_after_metrics=True,
    )


def validate_empirical_policy_against_base(
    empirical: EmpiricalCalibrationPolicy,
    base: CalibrationPolicy,
) -> None:
    if empirical.rubric_version != base.expected_rubric_version:
        raise CalibrationError("Empirical rubric version does not match base calibration policy")
    if empirical.verification_policy_version != base.expected_verification_policy_version:
        raise CalibrationError(
            "Empirical live-verification policy version does not match base calibration policy"
        )
    if empirical.runs_per_case_per_route < base.minimum_runs_per_case_per_verifier:
        raise CalibrationError("Empirical runs per case/route are below base calibration minimum")
    if len(empirical.verifier_routes) < base.minimum_distinct_verifier_routes:
        raise CalibrationError("Empirical verifier route count is below base calibration minimum")
    if len({route.provider_family for route in empirical.verifier_routes}) < (
        base.minimum_distinct_verifier_provider_families
    ):
        raise CalibrationError("Empirical provider-family count is below base calibration minimum")


def load_human_labels(path: str | Path) -> list[HumanCalibrationLabel]:
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CalibrationError(f"Human calibration labels could not be read: {path}") from exc
    labels: list[HumanCalibrationLabel] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CalibrationError(f"Human calibration label line {index} is invalid JSON") from exc
        if not isinstance(raw, dict):
            raise CalibrationError(f"Human calibration label line {index} must be an object")
        labels.append(HumanCalibrationLabel.from_dict(raw))
    if not labels:
        raise CalibrationError("Human calibration labels are empty")
    return labels


def _case_consensus(
    case: GoldCalibrationCase,
    labels: list[HumanCalibrationLabel],
    policy: EmpiricalCalibrationPolicy,
) -> tuple[LiveVerificationDecision | None, int, bool]:
    reviewers = [label for label in labels if label.reviewer_role == "reviewer"]
    reviewer_ids = {label.reviewer_id for label in reviewers}
    if len(reviewer_ids) < policy.minimum_independent_reviewers_per_case:
        return None, len(reviewer_ids), False
    reviewer_decisions = {label.decision for label in reviewers}
    if len(reviewer_decisions) == 1:
        return next(iter(reviewer_decisions)), len(reviewer_ids), False
    adjudicators = [label for label in labels if label.reviewer_role == "adjudicator"]
    if not adjudicators:
        return None, len(reviewer_ids), True
    if any(label.reviewer_id in reviewer_ids for label in adjudicators):
        raise CalibrationError(
            f"Calibration case {case.case_id} adjudicator must be distinct from case reviewers"
        )
    adjudicated = {label.decision for label in adjudicators}
    if len(adjudicated) != 1:
        raise CalibrationError(
            f"Calibration case {case.case_id} adjudicators do not agree on one decision"
        )
    return next(iter(adjudicated)), len(reviewer_ids), False


def assess_human_label_readiness(
    cases: list[GoldCalibrationCase],
    labels: list[HumanCalibrationLabel],
    policy: EmpiricalCalibrationPolicy,
) -> HumanLabelReadiness:
    known_cases = {case.case_id for case in cases}
    unknown = sorted({label.case_id for label in labels} - known_cases)
    if unknown:
        raise CalibrationError("Human labels reference unknown cases: " + ", ".join(unknown))
    packet_ids = {label.source_packet_id for label in labels}
    if len(packet_ids) != 1:
        raise CalibrationError(
            "Human calibration labels must originate from one blinded review packet"
        )
    seen: set[tuple[str, str, str]] = set()
    for label in labels:
        identity = (label.case_id, label.reviewer_id, label.reviewer_role)
        if identity in seen:
            raise CalibrationError("Duplicate human calibration label identity: " + "/".join(identity))
        seen.add(identity)
        if label.rubric_version != policy.rubric_version:
            raise CalibrationError(f"Human label for {label.case_id} uses unsupported rubric version")
        if not label.observations_blinded or not label.reference_control_labels_blinded:
            raise CalibrationError("Human calibration label blinding provenance is incomplete")

    by_case: dict[str, list[HumanCalibrationLabel]] = defaultdict(list)
    for label in labels:
        by_case[label.case_id].append(label)
    undercovered: list[str] = []
    disagreements: list[str] = []
    adjudication_missing: list[str] = []
    for case in cases:
        case_labels = by_case[case.case_id]
        consensus, reviewer_count, needs_adjudication = _case_consensus(
            case, case_labels, policy
        )
        if reviewer_count < policy.minimum_independent_reviewers_per_case:
            undercovered.append(
                f"{case.case_id}:{reviewer_count}/{policy.minimum_independent_reviewers_per_case}"
            )
        reviewer_decisions = {
            label.decision for label in case_labels if label.reviewer_role == "reviewer"
        }
        if len(reviewer_decisions) > 1:
            disagreements.append(case.case_id)
        if needs_adjudication:
            adjudication_missing.append(case.case_id)
        if reviewer_count >= policy.minimum_independent_reviewers_per_case and not needs_adjudication and consensus is None:
            raise CalibrationError(f"Human label consensus missing for {case.case_id}")

    times = sorted((_parsed_time(label.reviewed_at), label.reviewed_at) for label in labels)
    return HumanLabelReadiness(
        human_label_requirements_met=not undercovered and not adjudication_missing,
        minimum_independent_reviewers_per_case=policy.minimum_independent_reviewers_per_case,
        reviewer_ids=sorted({label.reviewer_id for label in labels}),
        source_packet_id=next(iter(packet_ids)),
        undercovered_cases=undercovered,
        disagreement_cases=sorted(disagreements),
        adjudication_missing_cases=sorted(adjudication_missing),
        label_window_start=times[0][1] if times else None,
        label_window_end=times[-1][1] if times else None,
    )


def build_human_gold_cases(
    cases: list[GoldCalibrationCase],
    labels: list[HumanCalibrationLabel],
    empirical_policy: EmpiricalCalibrationPolicy,
    base_policy: CalibrationPolicy,
) -> list[GoldCalibrationCase]:
    readiness = assess_human_label_readiness(cases, labels, empirical_policy)
    if not readiness.human_label_requirements_met:
        raise CalibrationError("Independent human labels are not ready for empirical calibration")
    by_case: dict[str, list[HumanCalibrationLabel]] = defaultdict(list)
    for label in labels:
        by_case[label.case_id].append(label)
    human_gold: list[GoldCalibrationCase] = []
    for case in cases:
        consensus, _, needs_adjudication = _case_consensus(
            case, by_case[case.case_id], empirical_policy
        )
        if needs_adjudication or consensus is None:
            raise CalibrationError(f"Human label consensus is incomplete for {case.case_id}")
        human_gold.append(replace(case, gold=consensus))
    validate_gold_corpus(human_gold, policy=base_policy)
    return human_gold


def load_empirical_observations(path: str | Path) -> list[EmpiricalCalibrationObservation]:
    source = Path(path)
    if not source.exists():
        return []
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CalibrationError(f"Empirical observations could not be read: {source}") from exc
    observations: list[EmpiricalCalibrationObservation] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CalibrationError(f"Empirical observation line {index} is invalid JSON") from exc
        if not isinstance(raw, dict):
            raise CalibrationError(f"Empirical observation line {index} must be an object")
        observations.append(EmpiricalCalibrationObservation.from_dict(raw))
    return observations


def validate_empirical_observations(
    cases: list[GoldCalibrationCase],
    observations: list[EmpiricalCalibrationObservation],
    labels: list[HumanCalibrationLabel],
    empirical_policy: EmpiricalCalibrationPolicy,
    base_policy: CalibrationPolicy,
) -> None:
    readiness = assess_human_label_readiness(cases, labels, empirical_policy)
    if not readiness.human_label_requirements_met:
        raise CalibrationError("Human labels must be complete before empirical observations")
    latest_label = max(_parsed_time(label.reviewed_at) for label in labels)
    known_cases = {case.case_id for case in cases}
    allowed_routes = {route.route_id for route in empirical_policy.verifier_routes}
    seen: set[tuple[str, str, str]] = set()
    revisions: set[str] = set()
    for observation in observations:
        if observation.case_id not in known_cases:
            raise CalibrationError(
                f"Empirical observation references unknown case {observation.case_id}"
            )
        if observation.identity in seen:
            raise CalibrationError(
                "Duplicate empirical observation identity: " + "/".join(observation.identity)
            )
        seen.add(observation.identity)
        revisions.add(observation.collector_revision)
        if observation.verifier_route not in allowed_routes:
            raise CalibrationError(
                f"Empirical observation uses unauthorized verifier route {observation.verifier_route}"
            )
        if observation.rubric_version != empirical_policy.rubric_version:
            raise CalibrationError("Empirical observation rubric version drifted")
        if observation.rubric_version != base_policy.expected_rubric_version:
            raise CalibrationError("Empirical observation rubric version mismatches base policy")
        if observation.verification_policy_version != empirical_policy.verification_policy_version:
            raise CalibrationError("Empirical observation live-verification policy version drifted")
        if observation.empirical_policy_version != empirical_policy.version:
            raise CalibrationError("Empirical observation empirical-policy version drifted")
        if _parsed_time(observation.observed_at) < latest_label:
            raise CalibrationError(
                "Empirical observation predates completion of the independent human labels"
            )
    if len(revisions) > 1:
        raise CalibrationError("Empirical evidence set mixes collector revisions")


def _optional_usage_int(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def _extract_provider_usage(provider: str, body: bytes) -> tuple[int | None, int | None]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None
    if not isinstance(payload, dict) or not isinstance(payload.get("usage"), dict):
        return None, None
    usage = payload["usage"]
    if provider == "google":
        return (
            _optional_usage_int(usage.get("total_input_tokens")),
            _optional_usage_int(usage.get("total_output_tokens")),
        )
    if provider == "openai":
        return (
            _optional_usage_int(usage.get("input_tokens")),
            _optional_usage_int(usage.get("output_tokens")),
        )
    if provider == "anthropic":
        parts = [
            value
            for value in (
                _optional_usage_int(usage.get("input_tokens")),
                _optional_usage_int(usage.get("cache_creation_input_tokens")),
                _optional_usage_int(usage.get("cache_read_input_tokens")),
            )
            if value is not None
        ]
        return (
            sum(parts) if parts else None,
            _optional_usage_int(usage.get("output_tokens")),
        )
    return None, None


def _verifier_for_route(
    route: CalibrationVerifierRoute,
    connections: Mapping[str, ProviderConnection],
):
    if route.provider_family == "google":
        return GoogleLiveVerifier(connections)
    if route.provider_family == "anthropic":
        return AnthropicLiveVerifier(connections)
    if route.provider_family == "openai":
        return OpenAILiveVerifier(connections)
    raise CalibrationError(f"No empirical verifier adapter exists for {route.provider_family}")


def _append_observation(path: Path, observation: EmpiricalCalibrationObservation) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(observation.to_dict(), sort_keys=True, separators=(",", ":"))
            + "\n"
        )
        handle.flush()
        os.fsync(handle.fileno())


def planned_collection(
    cases: list[GoldCalibrationCase],
    policy: EmpiricalCalibrationPolicy,
    *,
    providers: set[str] | None = None,
) -> dict[str, Any]:
    routes = [
        route
        for route in policy.verifier_routes
        if providers is None or route.provider_family in providers
    ]
    return {
        "case_count": len(cases),
        "runs_per_case_per_route": policy.runs_per_case_per_route,
        "routes": [route.route_id for route in routes],
        "provider_families": sorted({route.provider_family for route in routes}),
        "planned_live_calls": len(cases) * len(routes) * policy.runs_per_case_per_route,
        "collection_role": COLLECTION_ROLE,
        "quality_claims_authorized": False,
        "scope_expansion_authorized": False,
    }


def collect_live_observations(
    cases: list[GoldCalibrationCase],
    labels: list[HumanCalibrationLabel],
    empirical_policy: EmpiricalCalibrationPolicy,
    base_policy: CalibrationPolicy,
    connections: Mapping[str, ProviderConnection],
    *,
    collector_revision: str,
    output_path: str | Path,
    providers: set[str] | None = None,
    clock: Callable[[], float] = monotonic,
    now: Callable[[], str] = _utc_now,
) -> list[EmpiricalCalibrationObservation]:
    validate_empirical_policy_against_base(empirical_policy, base_policy)
    build_human_gold_cases(cases, labels, empirical_policy, base_policy)
    revision = _required_text(collector_revision, "collector_revision")
    if len(revision) < 7:
        raise CalibrationError("collector_revision must identify a concrete repository revision")

    collection_started_at = _required_offset_datetime(now(), "collection_started_at")
    latest_label = max(_parsed_time(label.reviewed_at) for label in labels)
    if _parsed_time(collection_started_at) < latest_label:
        raise CalibrationError(
            "Empirical collection cannot start before independent human labels are complete"
        )

    target = Path(output_path)
    existing = load_empirical_observations(target)
    if existing:
        validate_empirical_observations(
            cases, existing, labels, empirical_policy, base_policy
        )
        if {observation.collector_revision for observation in existing} != {revision}:
            raise CalibrationError(
                "Existing empirical evidence was collected at a different repository revision"
            )
    completed = {observation.identity for observation in existing}

    routes = [
        route
        for route in empirical_policy.verifier_routes
        if providers is None or route.provider_family in providers
    ]
    if not routes:
        raise CalibrationError("No empirical verifier routes were selected")
    missing_connections = sorted(
        {route.provider_family for route in routes} - set(connections)
    )
    if missing_connections:
        raise CalibrationError(
            "Missing provider connections for empirical collection: "
            + ", ".join(missing_connections)
        )

    collected = list(existing)
    for route in routes:
        delegate = connections[route.provider_family]
        if delegate.provider_family != route.provider_family:
            raise CalibrationError(
                f"Connection provider mismatch for empirical route {route.route_id}"
            )
        for case in cases:
            for run_number in range(1, empirical_policy.runs_per_case_per_route + 1):
                run_id = f"r{run_number:02d}"
                identity = (case.case_id, route.route_id, run_id)
                if identity in completed:
                    continue
                capture = _UsageCaptureConnection(delegate)
                request = LiveVerificationRequest(
                    dispatch_id=f"calibration-{case.case_id}-{route.provider_family}-{run_id}",
                    task_id=f"calibration-{case.case_id}",
                    verifier_provider_family=route.provider_family,
                    verifier_model=route.model,
                    verifier_reasoning_effort=route.reasoning,
                    risk_level=empirical_policy.risk_level,
                    verification_methods=empirical_policy.verification_methods,
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
                        f"Empirical verifier infrastructure failed for {identity[0]}@{identity[1]}:{identity[2]}"
                    ) from exc
                duration_ms = max(0.0, (clock() - started) * 1000.0)
                if response.provider_family != route.provider_family or response.model != route.model:
                    raise CalibrationError("Empirical verifier changed the authorized route")
                if capture.input_tokens is None or capture.output_tokens is None:
                    raise CalibrationError(
                        f"Empirical verifier did not return required provider usage for {route.route_id}"
                    )
                observed_at = _required_offset_datetime(now(), "observed_at")
                if _parsed_time(observed_at) < latest_label:
                    raise CalibrationError(
                        "Empirical observation predates completion of the independent human labels"
                    )
                observation = EmpiricalCalibrationObservation(
                    case_id=case.case_id,
                    verifier_provider_family=route.provider_family,
                    verifier_model=route.model,
                    verifier_reasoning=route.reasoning,
                    run_id=run_id,
                    observed_at=observed_at,
                    rubric_version=empirical_policy.rubric_version,
                    verification_policy_version=empirical_policy.verification_policy_version,
                    empirical_policy_version=empirical_policy.version,
                    collector_revision=revision,
                    duration_ms=duration_ms,
                    input_tokens=capture.input_tokens,
                    output_tokens=capture.output_tokens,
                    decision=response.decision,
                )
                _append_observation(target, observation)
                collected.append(observation)
                completed.add(observation.identity)

    validate_empirical_observations(
        cases, collected, labels, empirical_policy, base_policy
    )
    return collected


def evaluate_empirical_calibration(
    cases: list[GoldCalibrationCase],
    labels: list[HumanCalibrationLabel],
    observations: list[EmpiricalCalibrationObservation],
    empirical_policy: EmpiricalCalibrationPolicy,
    base_policy: CalibrationPolicy,
) -> dict[str, Any]:
    human_gold = build_human_gold_cases(cases, labels, empirical_policy, base_policy)
    validate_empirical_observations(
        cases, observations, labels, empirical_policy, base_policy
    )
    base_observations = [observation.to_base_observation() for observation in observations]
    metrics = evaluate_calibration(
        human_gold, base_observations, policy=base_policy
    ).to_dict()
    path_metrics = metrics.pop("by_execution_path")
    if set(path_metrics) - {"primary_no_retry"}:
        raise CalibrationError("Empirical calibration produced an invalid execution-path metric")
    metrics["by_collection_path"] = {
        COLLECTION_ROLE: path_metrics.get(
            "primary_no_retry", {"observations": 0, "exact_status_accuracy": 0.0}
        )
    }

    readiness = assess_evidence_readiness(
        human_gold, base_observations, base_policy
    ).to_dict()
    expected_routes = {route.route_id for route in empirical_policy.verifier_routes}
    observed_routes = {observation.verifier_route for observation in observations}
    readiness["empirical_required_routes_present"] = observed_routes == expected_routes
    readiness["data_requirements_met"] = bool(
        readiness["data_requirements_met"] and observed_routes == expected_routes
    )

    original = {case.case_id: case.gold for case in cases}
    human = {case.case_id: case.gold for case in human_gold}
    return {
        "metrics_against_independent_human_labels": metrics,
        "evidence_readiness": readiness,
        "human_label_readiness": assess_human_label_readiness(
            cases, labels, empirical_policy
        ).to_dict(),
        "reference_control_vs_human_disagreement_cases": sorted(
            case_id for case_id in original if original[case_id] != human[case_id]
        ),
        "authority": {
            "quality_claims_authorized": False,
            "scope_expansion_authorized": False,
            "routing_authority": False,
            "automatic_route_update": False,
            "independent_residual_risk_review_required": True,
            "explicit_human_acceptance_required": True,
        },
    }


def connections_from_environment(
    routes: tuple[CalibrationVerifierRoute, ...],
) -> dict[str, ProviderConnection]:
    required = {route.provider_family for route in routes}
    connections: dict[str, ProviderConnection] = {}
    if "google" in required and os.environ.get("GEMINI_API_KEY"):
        connections["google"] = HeaderProviderConnection(
            provider_family="google",
            authorization_headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        )
    if "anthropic" in required and os.environ.get("ANTHROPIC_API_KEY"):
        connections["anthropic"] = HeaderProviderConnection(
            provider_family="anthropic",
            authorization_headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"]},
        )
    if "openai" in required and os.environ.get("OPENAI_API_KEY"):
        connections["openai"] = HeaderProviderConnection(
            provider_family="openai",
            authorization_headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"},
        )
    missing = sorted(required - set(connections))
    if missing:
        raise CalibrationError(
            "Missing environment-backed provider connections: " + ", ".join(missing)
        )
    return connections


def resolve_collector_revision(explicit: str | None = None) -> str:
    if explicit:
        return _required_text(explicit, "collector_revision")
    if os.environ.get("GITHUB_SHA"):
        return _required_text(os.environ["GITHUB_SHA"], "collector_revision")
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise CalibrationError(
            "Collector revision is required when Git revision cannot be resolved"
        ) from exc
    return _required_text(completed.stdout, "collector_revision")


def _load_context(repo_root: Path, empirical_policy_path: str | Path):
    empirical = load_empirical_policy(repo_root / empirical_policy_path)
    base = load_calibration_policy(repo_root / empirical.base_policy_path)
    validate_empirical_policy_against_base(empirical, base)
    cases = load_gold_cases(repo_root / empirical.control_corpus_path, policy=base)
    return empirical, base, cases


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Collect and evaluate TEO empirical verifier calibration evidence"
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--empirical-policy",
        default="policy/verification/verifier-calibration-empirical.yaml",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="Show live-call plan without provider calls")
    plan_parser.add_argument("--provider", action="append", choices=sorted(SUPPORTED_PROVIDERS))

    labels_parser = subparsers.add_parser(
        "labels", help="Validate independent human labels without provider calls"
    )
    labels_parser.add_argument("--human-labels", required=True)

    collect_parser = subparsers.add_parser(
        "collect", help="Collect live verifier observations after human labels are ready"
    )
    collect_parser.add_argument("--human-labels", required=True)
    collect_parser.add_argument("--observations")
    collect_parser.add_argument("--collector-revision")
    collect_parser.add_argument("--provider", action="append", choices=sorted(SUPPORTED_PROVIDERS))
    collect_parser.add_argument(
        "--execute-live",
        action="store_true",
        help="Required acknowledgement that this command makes live provider calls",
    )

    evaluate_parser = subparsers.add_parser(
        "evaluate", help="Evaluate observations against independent human labels"
    )
    evaluate_parser.add_argument("--human-labels", required=True)
    evaluate_parser.add_argument("--observations", required=True)
    evaluate_parser.add_argument("--output")

    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        empirical, base, cases = _load_context(root, args.empirical_policy)
        if args.command == "plan":
            result = planned_collection(
                cases,
                empirical,
                providers=set(args.provider) if args.provider else None,
            )
        elif args.command == "labels":
            result = assess_human_label_readiness(
                cases, load_human_labels(args.human_labels), empirical
            ).to_dict()
        elif args.command == "collect":
            if not args.execute_live:
                raise CalibrationError(
                    "Live empirical collection requires explicit --execute-live acknowledgement"
                )
            labels = load_human_labels(args.human_labels)
            providers = set(args.provider) if args.provider else None
            selected_routes = tuple(
                route
                for route in empirical.verifier_routes
                if providers is None or route.provider_family in providers
            )
            observations_path = args.observations or str(
                root / empirical.default_observations_path
            )
            observations = collect_live_observations(
                cases,
                labels,
                empirical,
                base,
                connections_from_environment(selected_routes),
                collector_revision=resolve_collector_revision(args.collector_revision),
                output_path=observations_path,
                providers=providers,
            )
            result = {
                "observation_count": len(observations),
                "observations_path": observations_path,
                "plan": planned_collection(cases, empirical, providers=providers),
                "quality_claims_authorized": False,
                "scope_expansion_authorized": False,
            }
        else:
            observations = load_empirical_observations(args.observations)
            if not observations:
                raise CalibrationError("Empirical observations are empty")
            result = evaluate_empirical_calibration(
                cases,
                load_human_labels(args.human_labels),
                observations,
                empirical,
                base,
            )
            if args.output:
                output = Path(args.output)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(
                    json.dumps(result, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
    except (CalibrationError, OSError, yaml.YAMLError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
