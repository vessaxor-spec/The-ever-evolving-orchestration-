from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .benchmark_conclusion import (
    BenchmarkConclusionHandoffRecord,
    BenchmarkConclusionRecord,
    BenchmarkConclusionVerificationRecord,
)
from .benchmark_lab import BenchmarkExperimentManifest, BenchmarkExperimentReport
from .cost_attribution import RouteCostAttributionRecord
from .provider_adapter import ProviderAdapterContractError
from .route_outcome import RouteOutcomeRecord

SHADOW_EVALUATION_VERSION = "1"
SHADOW_EVALUATION_INPUT_SCHEMA_PATH = "reference/schemas/shadow-evaluation-input.schema.json"
SHADOW_RECOMMENDATION_SCHEMA_PATH = "reference/schemas/shadow-route-recommendation.schema.json"
SHADOW_VERIFICATION_SCHEMA_PATH = "reference/schemas/shadow-recommendation-verification.schema.json"
SHADOW_HANDOFF_SCHEMA_PATH = "reference/schemas/shadow-recommendation-handoff.schema.json"
SPECIALIST_ID = "orchestration-evaluation-analyst"
RECOMMENDATION_STATES = {
    "NO_CHANGE_JUSTIFIED",
    "INSUFFICIENT_EVIDENCE",
    "SHADOW_CHANGE_CANDIDATE",
    "REGRESSION_INVESTIGATION",
    "POLICY_OR_CONTROL_CONCERN",
}


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
        raise ProviderAdapterContractError(f"Shadow evaluation schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Shadow evaluation schema could not be loaded: {path}"
        ) from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Shadow evaluation schema must be an object")
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


def _require_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(f"Shadow evaluation {name} is required")
    return text


def _authority_denials() -> dict[str, bool]:
    return {
        "policy_write_authority": False,
        "live_routing_authority": False,
        "live_scope_change_authority": False,
        "effective_risk_lowering_authority": False,
        "capability_bypass_authority": False,
        "verifier_bypass_authority": False,
        "preview_acceptance_authority": False,
        "provider_access_change_authority": False,
        "qualified_human_approval_satisfied": False,
    }


def _validate_input_semantics(data: dict[str, Any]) -> None:
    if data["candidate_id"] == data["baseline_candidate_id"]:
        raise ProviderAdapterContractError(
            "Shadow evaluation candidate and baseline must be different"
        )
    refs = [
        (str(item["record_type"]), str(item["record_id"]))
        for item in data["evidence_refs"]
    ]
    if len(refs) != len(set(refs)):
        raise ProviderAdapterContractError("Shadow evaluation evidence references must be unique")
    types = {item[0] for item in refs}
    if "benchmark_experiment" not in types or "benchmark_report" not in types:
        raise ProviderAdapterContractError(
            "Shadow evaluation requires benchmark experiment and report evidence"
        )
    if "route_outcome" not in types:
        raise ProviderAdapterContractError("Shadow evaluation requires route-outcome evidence")
    if data["consequence_level"] == "consequential":
        required = {
            "benchmark_conclusion",
            "benchmark_conclusion_verification",
            "benchmark_conclusion_handoff",
        }
        if not required.issubset(types):
            raise ProviderAdapterContractError(
                "Consequential shadow evaluation requires conclusion, verification, and handoff evidence"
            )


def _validate_recommendation_semantics(data: dict[str, Any]) -> None:
    disposition = str(data["disposition"])
    if disposition not in RECOMMENDATION_STATES:
        raise ProviderAdapterContractError(
            f"Unsupported shadow recommendation disposition: {disposition}"
        )
    sufficient = data["evidence_sufficiency"] == "sufficient_for_shadow_review"
    proposed = data["proposed_change"]
    if disposition == "INSUFFICIENT_EVIDENCE":
        if sufficient or proposed is not None:
            raise ProviderAdapterContractError(
                "INSUFFICIENT_EVIDENCE cannot publish a sufficient or proposed-change state"
            )
    elif not sufficient:
        raise ProviderAdapterContractError(
            "Non-insufficient shadow recommendation requires sufficient evidence for shadow review"
        )
    if disposition == "SHADOW_CHANGE_CANDIDATE":
        if proposed is None:
            raise ProviderAdapterContractError(
                "SHADOW_CHANGE_CANDIDATE requires a shadow-only proposed change"
            )
    elif proposed is not None:
        raise ProviderAdapterContractError(
            "Only SHADOW_CHANGE_CANDIDATE may contain a proposed change"
        )
    cost = data["cost_evidence"]
    if cost["status"] == "known":
        if any(
            cost[key] is None
            for key in ("candidate_total_amount", "baseline_total_amount", "delta_amount", "currency")
        ):
            raise ProviderAdapterContractError("Known shadow cost evidence requires complete totals")
    elif any(
        cost[key] is not None
        for key in ("candidate_total_amount", "baseline_total_amount", "delta_amount", "currency")
    ):
        raise ProviderAdapterContractError(
            "Non-known shadow cost evidence cannot publish monetary totals"
        )


def _validate_verification_semantics(data: dict[str, Any]) -> None:
    actor = data["verifier"]
    provider = actor.get("provider_family")
    model = actor.get("model")
    actor_type = actor["actor_type"]
    if (provider is None) != (model is None):
        raise ProviderAdapterContractError(
            "Shadow verifier provider_family and model must both be present or both be null"
        )
    if actor_type in {"human", "system"} and provider is not None:
        raise ProviderAdapterContractError(
            "Human or system shadow verifier cannot declare a model"
        )
    if actor_type == "specialist" and provider is None:
        raise ProviderAdapterContractError(
            "Specialist shadow verifier must declare provider_family and model"
        )
    verdicts = list(data["checks"].values())
    failures = [item for item in verdicts if item == "fail"]
    uncertain = [item for item in verdicts if item == "uncertain"]
    decision = data["decision"]
    reason = data["human_reason"]
    if decision == "verified":
        if failures or uncertain or reason != "none":
            raise ProviderAdapterContractError(
                "Verified shadow recommendation requires all checks to pass and no human reason"
            )
    elif decision == "rejected":
        if not failures or reason != "none":
            raise ProviderAdapterContractError(
                "Rejected shadow recommendation requires a failed check and no human reason"
            )
    elif decision == "needs_human":
        if failures or not uncertain or reason == "none":
            raise ProviderAdapterContractError(
                "needs_human shadow verification requires uncertainty, no failed checks, and a reason"
            )


def _validate_handoff_semantics(data: dict[str, Any]) -> None:
    if not data["independent_verification_performed"]:
        raise ProviderAdapterContractError(
            "Shadow recommendation cannot advance without independent verification"
        )


@dataclass(frozen=True, slots=True)
class ShadowEvaluationInputRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "ShadowEvaluationInputRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=SHADOW_EVALUATION_INPUT_SCHEMA_PATH,
            label="Shadow evaluation input",
        )
        _validate_input_semantics(data)
        if data["integrity_sha256"] != _canonical_sha256(data, omit="integrity_sha256"):
            raise ProviderAdapterContractError(
                "Shadow evaluation input integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class ShadowRecommendationRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "ShadowRecommendationRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=SHADOW_RECOMMENDATION_SCHEMA_PATH,
            label="Shadow recommendation",
        )
        _validate_recommendation_semantics(data)
        if data["integrity_sha256"] != _canonical_sha256(data, omit="integrity_sha256"):
            raise ProviderAdapterContractError(
                "Shadow recommendation integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class ShadowRecommendationVerificationRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "ShadowRecommendationVerificationRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=SHADOW_VERIFICATION_SCHEMA_PATH,
            label="Shadow recommendation verification",
        )
        _validate_verification_semantics(data)
        if data["integrity_sha256"] != _canonical_sha256(data, omit="integrity_sha256"):
            raise ProviderAdapterContractError(
                "Shadow recommendation verification integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class ShadowRecommendationHandoffRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "ShadowRecommendationHandoffRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=SHADOW_HANDOFF_SCHEMA_PATH,
            label="Shadow recommendation handoff",
        )
        _validate_handoff_semantics(data)
        if data["integrity_sha256"] != _canonical_sha256(data, omit="integrity_sha256"):
            raise ProviderAdapterContractError(
                "Shadow recommendation handoff integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def _ref(record_type: str, record_id: str, integrity: str) -> dict[str, str]:
    return {
        "record_type": record_type,
        "record_id": _require_text(record_id, f"{record_type} record_id"),
        "integrity_sha256": _require_text(integrity, f"{record_type} integrity_sha256"),
    }


def _outcome_map(records: Sequence[RouteOutcomeRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        payload = record.to_dict()
        outcome_id = str(payload["outcome_id"])
        if outcome_id in result:
            raise ProviderAdapterContractError(f"Duplicate shadow route outcome {outcome_id}")
        result[outcome_id] = payload
    return result


def _cost_map(records: Sequence[RouteCostAttributionRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        payload = record.to_dict()
        outcome_id = str(payload["outcome_id"])
        if outcome_id in result:
            raise ProviderAdapterContractError(
                f"Duplicate shadow cost attribution for outcome {outcome_id}"
            )
        result[outcome_id] = payload
    return result


def _candidate_map(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): dict(item) for item in manifest["candidates"]}


def _candidate_outcome_ids(manifest: Mapping[str, Any], candidate_id: str) -> list[str]:
    return [
        str(item["outcome_id"])
        for item in manifest["bindings"]
        if str(item["candidate_id"]) == candidate_id
    ]


def _validate_core_bindings(
    manifest: BenchmarkExperimentManifest,
    report: BenchmarkExperimentReport,
    route_outcomes: Sequence[RouteOutcomeRecord],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    manifest_data = manifest.to_dict()
    report_data = report.to_dict()
    outcomes = _outcome_map(route_outcomes)
    if report_data["experiment_id"] != manifest_data["experiment_id"]:
        raise ProviderAdapterContractError(
            "Shadow evaluation benchmark report and manifest experiment IDs do not match"
        )
    if report_data["provenance"]["manifest_sha256"] != manifest.sha256:
        raise ProviderAdapterContractError(
            "Shadow evaluation report does not bind the exact benchmark manifest"
        )
    source_ids = set(str(item) for item in report_data["provenance"]["source_outcome_ids"])
    if source_ids != set(outcomes):
        raise ProviderAdapterContractError(
            "Shadow evaluation must receive exactly the route outcomes bound by the benchmark report"
        )
    bound_ids = {str(item["outcome_id"]) for item in manifest_data["bindings"]}
    if source_ids != bound_ids:
        raise ProviderAdapterContractError(
            "Shadow evaluation benchmark manifest and report route-outcome sets do not match"
        )
    return manifest_data, report_data, outcomes


def _validate_cost_bindings(
    costs: Sequence[RouteCostAttributionRecord],
    outcomes: Mapping[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    cost_map = _cost_map(costs)
    for outcome_id, cost in cost_map.items():
        outcome = outcomes.get(outcome_id)
        if outcome is None:
            raise ProviderAdapterContractError(
                f"Shadow cost attribution references undeclared outcome {outcome_id}"
            )
        if cost["outcome_integrity_sha256"] != outcome["integrity_sha256"]:
            raise ProviderAdapterContractError(
                f"Shadow cost attribution does not bind exact route outcome {outcome_id}"
            )
    return cost_map


def _validate_consequential_chain(
    report: Mapping[str, Any],
    conclusion: BenchmarkConclusionRecord | None,
    conclusion_verification: BenchmarkConclusionVerificationRecord | None,
    conclusion_handoff: BenchmarkConclusionHandoffRecord | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if conclusion is None or conclusion_verification is None or conclusion_handoff is None:
        raise ProviderAdapterContractError(
            "Consequential shadow evaluation requires the complete benchmark conclusion challenge chain"
        )
    c = conclusion.to_dict()
    v = conclusion_verification.to_dict()
    h = conclusion_handoff.to_dict()
    if c["experiment_id"] != report["experiment_id"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark conclusion belongs to a different experiment"
        )
    if c["report_integrity_sha256"] != report["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark conclusion does not bind the exact benchmark report"
        )
    if c["consequence_level"] != "consequential":
        raise ProviderAdapterContractError(
            "Consequential shadow evaluation requires a consequential benchmark conclusion"
        )
    if v["conclusion_id"] != c["conclusion_id"] or v["conclusion_integrity_sha256"] != c["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark conclusion verification does not bind the exact conclusion"
        )
    if v["decision"] != "verified" or not v["independent"]:
        raise ProviderAdapterContractError(
            "Consequential shadow evaluation requires verified independent benchmark conclusion challenge"
        )
    if h["conclusion_id"] != c["conclusion_id"] or h["conclusion_integrity_sha256"] != c["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark handoff does not bind the exact conclusion"
        )
    if h["verification_id"] != v["verification_id"] or h["verification_integrity_sha256"] != v["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark handoff does not bind the exact independent verification"
        )
    if h["status"] != "ready_for_review" or not h["independent_verification_performed"]:
        raise ProviderAdapterContractError(
            "Consequential shadow evaluation requires a benchmark conclusion ready for review"
        )
    if h["policy_write_authority"] or h["qualified_human_approval_satisfied"]:
        raise ProviderAdapterContractError(
            "Shadow benchmark handoff cannot carry policy-write or qualified-human authority"
        )
    return c, v, h


def build_shadow_evaluation_input(
    manifest: BenchmarkExperimentManifest,
    report: BenchmarkExperimentReport,
    route_outcomes: Sequence[RouteOutcomeRecord],
    *,
    candidate_id: str,
    baseline_candidate_id: str,
    analyst_actor: Mapping[str, Any],
    question: str,
    consequence_level: str,
    decision_dimensions: Sequence[str],
    repo_root: str | Path,
    cost_attributions: Sequence[RouteCostAttributionRecord] = (),
    conclusion: BenchmarkConclusionRecord | None = None,
    conclusion_verification: BenchmarkConclusionVerificationRecord | None = None,
    conclusion_handoff: BenchmarkConclusionHandoffRecord | None = None,
    created_at: str | None = None,
) -> ShadowEvaluationInputRecord:
    manifest_data, report_data, outcomes = _validate_core_bindings(
        manifest, report, route_outcomes
    )
    candidate_id = _require_text(candidate_id, "candidate_id")
    baseline_candidate_id = _require_text(baseline_candidate_id, "baseline_candidate_id")
    candidates = _candidate_map(manifest_data)
    if candidate_id not in candidates or baseline_candidate_id not in candidates:
        raise ProviderAdapterContractError(
            "Shadow evaluation candidate and baseline must exist in the benchmark manifest"
        )
    if candidate_id == baseline_candidate_id:
        raise ProviderAdapterContractError(
            "Shadow evaluation candidate and baseline must be different"
        )
    dimensions = list(dict.fromkeys(str(item).strip() for item in decision_dimensions if str(item).strip()))
    if not dimensions:
        raise ProviderAdapterContractError("Shadow evaluation requires decision dimensions")
    cost_map = _validate_cost_bindings(cost_attributions, outcomes)
    if "source_backed_cost" in dimensions:
        required_cost_ids = set(_candidate_outcome_ids(manifest_data, candidate_id)) | set(
            _candidate_outcome_ids(manifest_data, baseline_candidate_id)
        )
        missing = sorted(required_cost_ids - set(cost_map))
        if missing:
            raise ProviderAdapterContractError(
                "Source-backed cost decision dimension requires attribution records for every candidate and baseline outcome: "
                + ", ".join(missing)
            )

    actor = {
        "actor_type": analyst_actor.get("actor_type"),
        "actor_id": analyst_actor.get("actor_id"),
        "provider_family": analyst_actor.get("provider_family"),
        "model": analyst_actor.get("model"),
    }
    if actor["actor_type"] != "specialist" or actor["actor_id"] != SPECIALIST_ID:
        raise ProviderAdapterContractError(
            "Shadow evaluation must be originated by orchestration-evaluation-analyst"
        )
    _require_text(actor["provider_family"], "analyst provider_family")
    _require_text(actor["model"], "analyst model")

    refs = [
        _ref("benchmark_experiment", manifest_data["experiment_id"], manifest.sha256),
        _ref("benchmark_report", report_data["experiment_id"], report_data["integrity_sha256"]),
    ]
    for outcome_id in sorted(outcomes):
        refs.append(_ref("route_outcome", outcome_id, outcomes[outcome_id]["integrity_sha256"]))
    for outcome_id in sorted(cost_map):
        cost = cost_map[outcome_id]
        refs.append(_ref("route_cost_attribution", cost["attribution_id"], cost["integrity_sha256"]))

    if consequence_level == "consequential":
        c, v, h = _validate_consequential_chain(
            report_data, conclusion, conclusion_verification, conclusion_handoff
        )
        refs.extend(
            [
                _ref("benchmark_conclusion", c["conclusion_id"], c["integrity_sha256"]),
                _ref(
                    "benchmark_conclusion_verification",
                    v["verification_id"],
                    v["integrity_sha256"],
                ),
                _ref("benchmark_conclusion_handoff", h["handoff_id"], h["integrity_sha256"]),
            ]
        )
    elif consequence_level != "routine":
        raise ProviderAdapterContractError(
            f"Unsupported shadow evaluation consequence level: {consequence_level}"
        )

    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "manifest": manifest.sha256,
            "report": report_data["integrity_sha256"],
            "candidate": candidate_id,
            "baseline": baseline_candidate_id,
            "question": question,
            "actor": actor,
            "refs": refs,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "shadow_evaluation_version": SHADOW_EVALUATION_VERSION,
        "record_type": "shadow_evaluation_input",
        "evaluation_id": f"shadow-input-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}",
        "created_at": timestamp,
        "specialist_id": SPECIALIST_ID,
        "analyst_actor": actor,
        "question": _require_text(question, "question"),
        "consequence_level": consequence_level,
        "candidate_id": candidate_id,
        "baseline_candidate_id": baseline_candidate_id,
        "decision_owner": "mission_control_or_maintainer_review",
        "decision_dimensions": dimensions,
        "evidence_refs": refs,
        "policy_write_authority": False,
        "live_routing_authority": False,
        "qualified_human_approval_satisfied": False,
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return ShadowEvaluationInputRecord.from_dict(payload, repo_root=repo_root)


def _expected_refs(
    manifest: BenchmarkExperimentManifest,
    report: BenchmarkExperimentReport,
    outcomes: Mapping[str, dict[str, Any]],
    costs: Mapping[str, dict[str, Any]],
    *,
    consequence_level: str,
    conclusion: BenchmarkConclusionRecord | None,
    conclusion_verification: BenchmarkConclusionVerificationRecord | None,
    conclusion_handoff: BenchmarkConclusionHandoffRecord | None,
) -> list[dict[str, str]]:
    report_data = report.to_dict()
    refs = [
        _ref("benchmark_experiment", manifest.to_dict()["experiment_id"], manifest.sha256),
        _ref("benchmark_report", report_data["experiment_id"], report_data["integrity_sha256"]),
    ]
    for outcome_id in sorted(outcomes):
        refs.append(_ref("route_outcome", outcome_id, outcomes[outcome_id]["integrity_sha256"]))
    for outcome_id in sorted(costs):
        item = costs[outcome_id]
        refs.append(_ref("route_cost_attribution", item["attribution_id"], item["integrity_sha256"]))
    if consequence_level == "consequential":
        c, v, h = _validate_consequential_chain(
            report_data, conclusion, conclusion_verification, conclusion_handoff
        )
        refs.extend(
            [
                _ref("benchmark_conclusion", c["conclusion_id"], c["integrity_sha256"]),
                _ref("benchmark_conclusion_verification", v["verification_id"], v["integrity_sha256"]),
                _ref("benchmark_conclusion_handoff", h["handoff_id"], h["integrity_sha256"]),
            ]
        )
    return refs


def _metric_map(report: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): dict(item) for item in report["candidate_metrics"]}


def _delta(candidate: Mapping[str, Any], baseline: Mapping[str, Any], field: str) -> float:
    return float(candidate[field]) - float(baseline[field])


def _cost_summary(
    manifest: Mapping[str, Any],
    costs: Mapping[str, dict[str, Any]],
    candidate_id: str,
    baseline_candidate_id: str,
    *,
    requested: bool,
) -> dict[str, Any]:
    if not requested:
        return {
            "status": "not_requested",
            "candidate_total_amount": None,
            "baseline_total_amount": None,
            "delta_amount": None,
            "currency": None,
        }

    def total_for(candidate: str) -> tuple[str, Decimal | None]:
        outcome_ids = _candidate_outcome_ids(manifest, candidate)
        records = [costs.get(outcome_id) for outcome_id in outcome_ids]
        if not records or any(item is None for item in records):
            return "unknown", None
        statuses = [str(item["status"]) for item in records if item is not None]
        if any(status == "unknown" for status in statuses):
            return "unknown", None
        if any(status == "partial" for status in statuses):
            return "partial", None
        amounts = [Decimal(str(item["total_amount"])) for item in records if item is not None]
        return "known", sum(amounts, Decimal("0"))

    candidate_status, candidate_total = total_for(candidate_id)
    baseline_status, baseline_total = total_for(baseline_candidate_id)
    if candidate_status == baseline_status == "known":
        assert candidate_total is not None and baseline_total is not None
        delta = candidate_total - baseline_total
        return {
            "status": "known",
            "candidate_total_amount": format(candidate_total, "f"),
            "baseline_total_amount": format(baseline_total, "f"),
            "delta_amount": format(delta, "f"),
            "currency": "USD",
        }
    status = "partial" if "partial" in {candidate_status, baseline_status} else "unknown"
    return {
        "status": status,
        "candidate_total_amount": None,
        "baseline_total_amount": None,
        "delta_amount": None,
        "currency": None,
    }


def evaluate_shadow_routes(
    evaluation: ShadowEvaluationInputRecord,
    manifest: BenchmarkExperimentManifest,
    report: BenchmarkExperimentReport,
    route_outcomes: Sequence[RouteOutcomeRecord],
    *,
    repo_root: str | Path,
    cost_attributions: Sequence[RouteCostAttributionRecord] = (),
    conclusion: BenchmarkConclusionRecord | None = None,
    conclusion_verification: BenchmarkConclusionVerificationRecord | None = None,
    conclusion_handoff: BenchmarkConclusionHandoffRecord | None = None,
    generated_at: str | None = None,
) -> ShadowRecommendationRecord:
    input_data = evaluation.to_dict()
    manifest_data, report_data, outcomes = _validate_core_bindings(
        manifest, report, route_outcomes
    )
    costs = _validate_cost_bindings(cost_attributions, outcomes)
    expected_refs = _expected_refs(
        manifest,
        report,
        outcomes,
        costs,
        consequence_level=input_data["consequence_level"],
        conclusion=conclusion,
        conclusion_verification=conclusion_verification,
        conclusion_handoff=conclusion_handoff,
    )
    if input_data["evidence_refs"] != expected_refs:
        raise ProviderAdapterContractError(
            "Shadow evaluation input does not bind the exact supplied evidence set"
        )

    candidates = _candidate_map(manifest_data)
    candidate_id = str(input_data["candidate_id"])
    baseline_id = str(input_data["baseline_candidate_id"])
    if candidate_id not in candidates or baseline_id not in candidates:
        raise ProviderAdapterContractError(
            "Shadow evaluation candidate or baseline is absent from benchmark manifest"
        )

    metrics = _metric_map(report_data)
    issues: list[str] = []
    if report_data["comparability_status"] != "passed":
        issues.append("benchmark_comparability_failed")
    if report_data["evidence_sufficiency"] == "insufficient":
        issues.append("benchmark_evidence_insufficient")
    if candidate_id not in metrics or baseline_id not in metrics:
        issues.append("candidate_metrics_missing")
    disagreement_status = str(report_data["verifier_disagreement"]["status"])
    if input_data["consequence_level"] == "consequential" and disagreement_status != "measured":
        issues.append("consequential_verifier_disagreement_not_measured")

    candidate_outcome_ids = set(_candidate_outcome_ids(manifest_data, candidate_id))
    baseline_outcome_ids = set(_candidate_outcome_ids(manifest_data, baseline_id))
    relevant_ids = candidate_outcome_ids | baseline_outcome_ids
    relevant = [outcomes[item] for item in relevant_ids]
    control_concerns = sorted(
        {
            str(item["final_disposition"])
            for item in relevant
            if item["final_disposition"] in {"awaiting_human", "verification_missing"}
        }
    )

    regression = any(
        str(item["candidate_id"]) == candidate_id
        for item in report_data["regression_signals"]
    )

    comparison = {
        "verified_completion_rate_delta": None,
        "primary_verified_completion_rate_delta": None,
        "fallback_assistance_rate_delta": None,
        "retry_assistance_rate_delta": None,
        "mean_total_duration_ms_delta": None,
        "verifier_disagreement_status": disagreement_status,
        "candidate_regression_signal": regression,
    }
    supporting: list[str] = []
    contradictory: list[str] = []
    dominance = False
    if candidate_id in metrics and baseline_id in metrics:
        candidate = metrics[candidate_id]
        baseline = metrics[baseline_id]
        comparison.update(
            {
                "verified_completion_rate_delta": _delta(
                    candidate, baseline, "verified_completion_rate"
                ),
                "primary_verified_completion_rate_delta": _delta(
                    candidate, baseline, "primary_verified_completion_rate"
                ),
                "fallback_assistance_rate_delta": _delta(
                    candidate, baseline, "fallback_assistance_rate"
                ),
                "retry_assistance_rate_delta": _delta(
                    candidate, baseline, "retry_assistance_rate"
                ),
                "mean_total_duration_ms_delta": _delta(
                    candidate, baseline, "mean_total_duration_ms"
                ),
            }
        )
        quality_delta = float(comparison["verified_completion_rate_delta"])
        primary_delta = float(comparison["primary_verified_completion_rate_delta"])
        fallback_delta = float(comparison["fallback_assistance_rate_delta"])
        retry_delta = float(comparison["retry_assistance_rate_delta"])
        dominance = quality_delta > 0 and primary_delta >= 0 and fallback_delta <= 0 and retry_delta <= 0
        if quality_delta > 0:
            supporting.append("candidate_verified_completion_rate_is_higher")
        elif quality_delta < 0:
            contradictory.append("candidate_verified_completion_rate_is_lower")
        if primary_delta > 0:
            supporting.append("candidate_primary_verified_completion_rate_is_higher")
        elif primary_delta < 0:
            contradictory.append("candidate_primary_verified_completion_rate_is_lower")
        if fallback_delta > 0:
            contradictory.append("candidate_has_higher_fallback_dependence")
        if retry_delta > 0:
            contradictory.append("candidate_has_higher_retry_dependence")

    cost = _cost_summary(
        manifest_data,
        costs,
        candidate_id,
        baseline_id,
        requested="source_backed_cost" in input_data["decision_dimensions"],
    )
    if cost["status"] == "known":
        cost_delta = Decimal(str(cost["delta_amount"]))
        if cost_delta < 0:
            supporting.append("candidate_source_backed_cohort_cost_is_lower")
        elif cost_delta > 0:
            contradictory.append("candidate_source_backed_cohort_cost_is_higher")
    elif cost["status"] in {"partial", "unknown"}:
        contradictory.append("monetary_comparison_is_not_fully_known")

    if issues:
        disposition = "INSUFFICIENT_EVIDENCE"
        evidence_sufficiency = "insufficient"
    elif control_concerns:
        disposition = "POLICY_OR_CONTROL_CONCERN"
        evidence_sufficiency = "sufficient_for_shadow_review"
        contradictory.extend(f"control_disposition:{item}" for item in control_concerns)
    elif regression:
        disposition = "REGRESSION_INVESTIGATION"
        evidence_sufficiency = "sufficient_for_shadow_review"
        contradictory.append("candidate_has_declared_regression_signal")
    elif dominance:
        disposition = "SHADOW_CHANGE_CANDIDATE"
        evidence_sufficiency = "sufficient_for_shadow_review"
    else:
        disposition = "NO_CHANGE_JUSTIFIED"
        evidence_sufficiency = "sufficient_for_shadow_review"

    limitations = list(dict.fromkeys(str(item) for item in report_data["limitations"]))
    limitations.extend(
        [
            "Shadow evaluation is recommendation-only and cannot modify live routing or policy.",
            "Cost is diagnostic evidence and cannot override quality, risk, capability, verification, provider diversity, or human authority.",
            "A shadow change candidate is a review candidate, not a causal superiority claim or deployment authorization.",
        ]
    )
    if issues:
        limitations.extend(issues)

    proposed_change = None
    if disposition == "SHADOW_CHANGE_CANDIDATE":
        proposed_change = {
            "candidate_id": candidate_id,
            "baseline_candidate_id": baseline_id,
            "description": (
                f"Review {candidate_id} as a shadow alternative to {baseline_id} under the exact benchmark and evidence scope bound by this record."
            ),
            "status": "shadow_only_not_authorized",
        }

    timestamp = generated_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "evaluation": input_data["integrity_sha256"],
            "disposition": disposition,
            "comparison": comparison,
            "cost": cost,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "shadow_evaluation_version": SHADOW_EVALUATION_VERSION,
        "record_type": "shadow_route_recommendation",
        "recommendation_id": (
            "shadow-recommendation-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "generated_at": timestamp,
        "evaluation_id": input_data["evaluation_id"],
        "evaluation_integrity_sha256": input_data["integrity_sha256"],
        "specialist_id": SPECIALIST_ID,
        "candidate_id": candidate_id,
        "baseline_candidate_id": baseline_id,
        "disposition": disposition,
        "evidence_sufficiency": evidence_sufficiency,
        "comparison": comparison,
        "cost_evidence": cost,
        "supporting_evidence": list(dict.fromkeys(supporting)),
        "contradictory_evidence": list(dict.fromkeys(contradictory)),
        "limitations": list(dict.fromkeys(limitations)),
        "proposed_change": proposed_change,
        "review_destination": "independent_challenge_then_mission_control_or_maintainer_review",
        "authority": _authority_denials(),
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return ShadowRecommendationRecord.from_dict(payload, repo_root=repo_root)


def _assert_independent_verifier(
    evaluation: ShadowEvaluationInputRecord,
    verifier: Mapping[str, Any],
) -> None:
    analyst = evaluation.to_dict()["analyst_actor"]
    actor_id = _require_text(verifier.get("actor_id"), "verifier actor_id")
    if actor_id == analyst["actor_id"]:
        raise ProviderAdapterContractError(
            "Shadow recommendation verifier must be independent from the analyst"
        )
    provider = verifier.get("provider_family")
    model = verifier.get("model")
    if provider is not None and str(provider) == str(analyst["provider_family"]):
        raise ProviderAdapterContractError(
            "Model-originated shadow recommendation requires provider-diverse verification"
        )
    if model is not None and str(model) == str(analyst["model"]):
        raise ProviderAdapterContractError(
            "Shadow recommendation verifier cannot reuse the analyst model"
        )


def build_shadow_recommendation_verification(
    evaluation: ShadowEvaluationInputRecord,
    recommendation: ShadowRecommendationRecord,
    *,
    verifier: Mapping[str, Any],
    decision: str,
    checks: Mapping[str, str],
    human_reason: str,
    evidence: Sequence[str],
    repo_root: str | Path,
    verified_at: str | None = None,
) -> ShadowRecommendationVerificationRecord:
    evaluation_data = evaluation.to_dict()
    recommendation_data = recommendation.to_dict()
    if recommendation_data["evaluation_id"] != evaluation_data["evaluation_id"] or recommendation_data["evaluation_integrity_sha256"] != evaluation_data["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow recommendation verification received a recommendation from a different evaluation"
        )
    _assert_independent_verifier(evaluation, verifier)
    evidence_items = list(dict.fromkeys(str(item).strip() for item in evidence if str(item).strip()))
    if not evidence_items:
        raise ProviderAdapterContractError(
            "Shadow recommendation verification requires evidence"
        )
    verifier_payload = {
        "actor_type": verifier.get("actor_type"),
        "actor_id": verifier.get("actor_id"),
        "provider_family": verifier.get("provider_family"),
        "model": verifier.get("model"),
    }
    timestamp = verified_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "recommendation": recommendation_data["integrity_sha256"],
            "verifier": verifier_payload,
            "decision": decision,
            "verified_at": timestamp,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "shadow_evaluation_version": SHADOW_EVALUATION_VERSION,
        "record_type": "shadow_recommendation_verification",
        "verification_id": (
            "shadow-verification-"
            + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
        ),
        "verified_at": timestamp,
        "recommendation_id": recommendation_data["recommendation_id"],
        "recommendation_integrity_sha256": recommendation_data["integrity_sha256"],
        "verifier": verifier_payload,
        "independent": True,
        "decision": decision,
        "checks": {
            "source_binding": checks.get("source_binding"),
            "evidence_sufficiency": checks.get("evidence_sufficiency"),
            "uncertainty_preserved": checks.get("uncertainty_preserved"),
            "authority_boundary_preserved": checks.get("authority_boundary_preserved"),
            "cost_not_primary_authority": checks.get("cost_not_primary_authority"),
            "unsupported_causality_absent": checks.get("unsupported_causality_absent"),
        },
        "human_reason": human_reason,
        "evidence": evidence_items,
        "policy_write_authority": False,
        "qualified_human_approval_satisfied": False,
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return ShadowRecommendationVerificationRecord.from_dict(payload, repo_root=repo_root)


def advance_shadow_recommendation(
    recommendation: ShadowRecommendationRecord,
    verification: ShadowRecommendationVerificationRecord,
    *,
    repo_root: str | Path,
    created_at: str | None = None,
) -> ShadowRecommendationHandoffRecord:
    recommendation_data = recommendation.to_dict()
    verification_data = verification.to_dict()
    if verification_data["recommendation_id"] != recommendation_data["recommendation_id"] or verification_data["recommendation_integrity_sha256"] != recommendation_data["integrity_sha256"]:
        raise ProviderAdapterContractError(
            "Shadow recommendation handoff verification does not bind the exact recommendation"
        )
    status = {
        "verified": "ready_for_review",
        "rejected": "rejected",
        "needs_human": "needs_human",
    }[str(verification_data["decision"])]
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    seed = json.dumps(
        {
            "recommendation": recommendation_data["integrity_sha256"],
            "verification": verification_data["integrity_sha256"],
            "status": status,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    payload: dict[str, Any] = {
        "shadow_evaluation_version": SHADOW_EVALUATION_VERSION,
        "record_type": "shadow_recommendation_handoff",
        "handoff_id": f"shadow-handoff-{hashlib.sha256(seed.encode('utf-8')).hexdigest()[:20]}",
        "created_at": timestamp,
        "recommendation_id": recommendation_data["recommendation_id"],
        "recommendation_integrity_sha256": recommendation_data["integrity_sha256"],
        "disposition": recommendation_data["disposition"],
        "destination": "mission_control_or_maintainer_review",
        "status": status,
        "verification_id": verification_data["verification_id"],
        "verification_integrity_sha256": verification_data["integrity_sha256"],
        "independent_verification_performed": True,
        "policy_write_authority": False,
        "live_routing_authority": False,
        "qualified_human_approval_satisfied": False,
        "notes": [
            "Shadow recommendation review handoff is evidence only and cannot modify routing or policy.",
            "This handoff does not satisfy any qualified-human approval requirement.",
            "Any later policy proposal requires Mission Control and maintainer review followed by normal policy, CI, and deployment controls.",
        ],
        "integrity_sha256": "",
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return ShadowRecommendationHandoffRecord.from_dict(payload, repo_root=repo_root)


class JsonlShadowRecommendationSink:
    """Append-only reference sink for non-authoritative shadow recommendations."""

    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, record: ShadowRecommendationRecord) -> None:
        validated = ShadowRecommendationRecord.from_dict(
            record.to_dict(), repo_root=self.repo_root
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(validated.to_dict(), sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Shadow recommendation evidence could not be persisted"
            ) from exc

    def read_all(self) -> list[ShadowRecommendationRecord]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Shadow recommendation evidence could not be read"
            ) from exc
        records: list[ShadowRecommendationRecord] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError(
                    "Shadow recommendation evidence contains invalid JSONL"
                ) from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError(
                    "Shadow recommendation evidence line must be an object"
                )
            records.append(
                ShadowRecommendationRecord.from_dict(raw, repo_root=self.repo_root)
            )
        return records
