from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator

from .anthropic_verifier import AnthropicLiveVerifier
from .benchmark_lab import (
    BENCHMARK_LAB_VERSION,
    BenchmarkExperimentManifest,
    BenchmarkExperimentReport,
)
from .google_verifier import GoogleLiveVerifier
from .openai_verifier import OpenAILiveVerifier
from .provider_adapter import ProviderAdapterContractError
from .provider_connection import ProviderConnection
from .route_outcome import RouteOutcomeRecord
from .verification_adapter import (
    LiveVerificationDecision,
    LiveVerificationError,
    LiveVerificationRequest,
    LiveVerificationResponse,
)

BENCHMARK_VERIFIER_PANEL_PLAN_SCHEMA_PATH = (
    "reference/schemas/benchmark-verifier-panel-plan.schema.json"
)
BENCHMARK_VERIFIER_OBSERVATION_SCHEMA_PATH = (
    "reference/schemas/benchmark-verifier-observation.schema.json"
)


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
        raise ProviderAdapterContractError(f"Benchmark verifier schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(
            f"Benchmark verifier schema could not be loaded: {path}"
        ) from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Benchmark verifier schema must be an object")
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


def _validate_panel_semantics(data: dict[str, Any]) -> None:
    candidate_ids: set[str] = set()
    for panel in data["panels"]:
        candidate_id = str(panel["candidate_id"])
        if candidate_id in candidate_ids:
            raise ProviderAdapterContractError(
                f"Benchmark verifier panel candidate {candidate_id} is duplicated"
            )
        candidate_ids.add(candidate_id)
        observer_ids: set[str] = set()
        identities: set[tuple[str, str, str | None]] = set()
        providers: set[str] = set()
        for observer in panel["observers"]:
            observer_id = str(observer["observer_id"])
            if observer_id in observer_ids:
                raise ProviderAdapterContractError(
                    f"Benchmark verifier observer {observer_id} is duplicated for {candidate_id}"
                )
            observer_ids.add(observer_id)
            identity = (
                str(observer["provider_family"]),
                str(observer["model"]),
                str(observer["reasoning_effort"])
                if observer.get("reasoning_effort") is not None
                else None,
            )
            if identity in identities:
                raise ProviderAdapterContractError(
                    f"Benchmark verifier panel for {candidate_id} repeats an observer identity"
                )
            identities.add(identity)
            providers.add(str(observer["provider_family"]))
        if len(providers) < 2:
            raise ProviderAdapterContractError(
                f"Benchmark verifier panel for {candidate_id} requires at least two provider families"
            )


@dataclass(frozen=True, slots=True)
class BenchmarkVerifierPanelPlan:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], *, repo_root: str | Path
    ) -> "BenchmarkVerifierPanelPlan":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_VERIFIER_PANEL_PLAN_SCHEMA_PATH,
            label="Benchmark verifier panel plan",
        )
        _validate_panel_semantics(data)
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.payload)


@dataclass(frozen=True, slots=True)
class BenchmarkVerifierObservation:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], *, repo_root: str | Path
    ) -> "BenchmarkVerifierObservation":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_VERIFIER_OBSERVATION_SCHEMA_PATH,
            label="Benchmark verifier observation",
        )
        decision = data["decision"]
        checks = decision["checks"]
        LiveVerificationDecision(
            status=str(decision["status"]),  # type: ignore[arg-type]
            output_present=str(checks["output_present"]),  # type: ignore[arg-type]
            task_adherence=str(checks["task_adherence"]),  # type: ignore[arg-type]
            format_consistency=str(checks["format_consistency"]),  # type: ignore[arg-type]
            unsupported_claims_absent=str(checks["unsupported_claims_absent"]),  # type: ignore[arg-type]
            human_reason=str(decision["human_reason"]),  # type: ignore[arg-type]
        )
        if str(data["integrity_sha256"]) != _canonical_sha256(
            data, omit="integrity_sha256"
        ):
            raise ProviderAdapterContractError(
                "Benchmark verifier observation integrity hash does not match content"
            )
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def _panel_map(plan: BenchmarkVerifierPanelPlan) -> dict[str, dict[str, Any]]:
    return {
        str(panel["candidate_id"]): panel for panel in plan.to_dict()["panels"]
    }


def _active_route(outcome: dict[str, Any]) -> dict[str, Any]:
    if outcome.get("active_route_role") == "primary":
        return outcome["primary_route"]
    if outcome.get("active_route_role") == "fallback" and outcome.get("fallback_route"):
        return outcome["fallback_route"]
    raise ProviderAdapterContractError(
        "Benchmark verifier panel requires a successful active execution route"
    )


def _execute_observer(
    request: LiveVerificationRequest,
    connections: Mapping[str, ProviderConnection],
) -> LiveVerificationResponse:
    if request.verifier_provider_family == "google":
        response = GoogleLiveVerifier(connections).verify(request)
    elif request.verifier_provider_family == "anthropic":
        response = AnthropicLiveVerifier(connections).verify(request)
    elif request.verifier_provider_family == "openai":
        response = OpenAILiveVerifier(connections).verify(request)
    else:
        raise LiveVerificationError(
            f"No benchmark verifier adapter exists for {request.verifier_provider_family}"
        )
    if response.provider_family != request.verifier_provider_family:
        raise LiveVerificationError("Benchmark verifier changed the declared provider family")
    if response.model != request.verifier_model:
        raise LiveVerificationError("Benchmark verifier changed the declared model")
    return response


def execute_benchmark_verifier_panel(
    plan: BenchmarkVerifierPanelPlan,
    *,
    candidate_id: str,
    fixture_id: str,
    trial_index: int,
    outcome: RouteOutcomeRecord,
    task: str,
    output_text: str,
    connections: Mapping[str, ProviderConnection],
    repo_root: str | Path,
    observed_at: str | None = None,
) -> tuple[BenchmarkVerifierObservation, ...]:
    """Run a blinded diagnostic verifier panel without changing runtime disposition."""
    panel = _panel_map(plan).get(candidate_id)
    if panel is None:
        raise ProviderAdapterContractError(
            f"No benchmark verifier panel is declared for candidate {candidate_id}"
        )
    task_text = str(task or "").strip()
    output = str(output_text or "").strip()
    if not task_text or not output:
        raise ProviderAdapterContractError(
            "Benchmark verifier panel requires non-empty controlled task and output text"
        )
    if trial_index < 1:
        raise ProviderAdapterContractError("Benchmark verifier trial_index must be positive")

    outcome_data = outcome.to_dict()
    active = _active_route(outcome_data)
    executor = active["implementation"]
    runtime_verifier = active["verifier"]
    observers = panel["observers"]
    if any(str(item["model"]) == str(executor["model"]) for item in observers):
        raise ProviderAdapterContractError(
            "Benchmark verifier panel cannot reuse the active executor model as an observer"
        )

    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    output_sha256 = hashlib.sha256(output.encode("utf-8")).hexdigest()
    records: list[BenchmarkVerifierObservation] = []
    for observer in observers:
        request = LiveVerificationRequest(
            dispatch_id=str(active["dispatch_id"]),
            task_id=str(active["dispatch_id"]),
            verifier_provider_family=str(observer["provider_family"]),
            verifier_model=str(observer["model"]),
            verifier_reasoning_effort=(
                str(observer["reasoning_effort"])
                if observer.get("reasoning_effort") is not None
                else None
            ),
            risk_level=str(outcome_data["risk_level"]),
            verification_methods=("benchmark_panel_review",),
            task=task_text,
            output_text=output,
        )
        response = _execute_observer(request, connections)
        decision = response.decision
        seed = (
            f"{plan.sha256}|{outcome_data['outcome_id']}|{candidate_id}|"
            f"{fixture_id}|{trial_index}|{observer['observer_id']}"
        )
        payload: dict[str, Any] = {
            "benchmark_lab_version": BENCHMARK_LAB_VERSION,
            "record_type": "benchmark_verifier_observation",
            "observation_id": (
                "observation-"
                + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:20]
            ),
            "experiment_id": plan.to_dict()["experiment_id"],
            "fixture_id": fixture_id,
            "candidate_id": candidate_id,
            "trial_index": trial_index,
            "outcome_id": str(outcome_data["outcome_id"]),
            "panel_plan_sha256": plan.sha256,
            "observer_id": str(observer["observer_id"]),
            "provider_family": response.provider_family,
            "model": response.model,
            "reasoning_effort": request.verifier_reasoning_effort,
            "observed_at": timestamp,
            "decision": {
                "status": decision.status,
                "checks": decision.verdicts,
                "human_reason": decision.human_reason,
            },
            "executor_context": {
                "provider_family": str(executor["provider_family"]),
                "model": str(executor["model"]),
                "runtime_verifier_provider_family": str(
                    runtime_verifier["provider_family"]
                ),
                "runtime_verifier_model": str(runtime_verifier["model"]),
            },
            "output_sha256": output_sha256,
            "evidence": list(dict.fromkeys(response.evidence)),
        }
        payload["integrity_sha256"] = _canonical_sha256(payload)
        records.append(
            BenchmarkVerifierObservation.from_dict(payload, repo_root=repo_root)
        )
    return tuple(records)


def _trial_disagreement(
    observations: Sequence[dict[str, Any]],
) -> tuple[bool, bool, bool, bool]:
    statuses = {str(item["decision"]["status"]) for item in observations}
    reasons = {str(item["decision"]["human_reason"]) for item in observations}
    checks = (
        "output_present",
        "task_adherence",
        "format_consistency",
        "unsupported_claims_absent",
    )
    criterion = any(
        len({str(item["decision"]["checks"][name]) for item in observations}) > 1
        for name in checks
    )
    status = len(statuses) > 1
    human_reason = len(reasons) > 1
    return status or criterion or human_reason, status, criterion, human_reason


def attach_verifier_disagreement(
    report: BenchmarkExperimentReport,
    manifest: BenchmarkExperimentManifest,
    outcomes: Sequence[RouteOutcomeRecord],
    panel_plan: BenchmarkVerifierPanelPlan,
    observations: Sequence[BenchmarkVerifierObservation],
    *,
    repo_root: str | Path,
) -> BenchmarkExperimentReport:
    """Attach diagnostic multi-verifier disagreement evidence to an existing report."""
    report_data = report.to_dict()
    manifest_data = manifest.to_dict()
    plan_data = panel_plan.to_dict()
    if report_data["experiment_id"] != manifest_data["experiment_id"]:
        raise ProviderAdapterContractError(
            "Benchmark verifier disagreement report and manifest experiment IDs differ"
        )
    if plan_data["experiment_id"] != manifest_data["experiment_id"]:
        raise ProviderAdapterContractError(
            "Benchmark verifier panel plan targets a different experiment"
        )

    panels = _panel_map(panel_plan)
    candidate_ids = {str(item["candidate_id"]) for item in manifest_data["candidates"]}
    if set(panels) != candidate_ids:
        raise ProviderAdapterContractError(
            "Benchmark verifier panel plan must cover the exact manifest candidate set"
        )
    outcome_by_id = {
        str(record.to_dict()["outcome_id"]): record.to_dict() for record in outcomes
    }
    if len(outcome_by_id) != len(outcomes):
        raise ProviderAdapterContractError(
            "Benchmark verifier outcomes contain duplicate outcome IDs"
        )

    bindings: dict[tuple[str, str, int], dict[str, Any]] = {}
    expected: set[tuple[str, str, int, str]] = set()
    for binding in manifest_data["bindings"]:
        key = (
            str(binding["candidate_id"]),
            str(binding["fixture_id"]),
            int(binding["trial_index"]),
        )
        bindings[key] = binding
        outcome = outcome_by_id.get(str(binding["outcome_id"]))
        if outcome is None:
            continue
        try:
            _active_route(outcome)
        except ProviderAdapterContractError:
            continue
        for observer in panels[key[0]]["observers"]:
            expected.add((*key, str(observer["observer_id"])))

    issues: list[str] = []
    seen: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    output_hashes: dict[tuple[str, str, int], set[str]] = {}
    panel_sha = panel_plan.sha256
    for record in observations:
        item = record.to_dict()
        key3 = (
            str(item["candidate_id"]),
            str(item["fixture_id"]),
            int(item["trial_index"]),
        )
        key4 = (*key3, str(item["observer_id"]))
        label = ":".join(str(part) for part in key4)
        if key4 in seen:
            issues.append(f"duplicate_observation:{label}")
            continue
        seen[key4] = item
        if item["experiment_id"] != manifest_data["experiment_id"]:
            issues.append(f"experiment_mismatch:{label}")
        if item["panel_plan_sha256"] != panel_sha:
            issues.append(f"panel_plan_mismatch:{label}")
        if key4 not in expected:
            issues.append(f"unexpected_observation:{label}")
            continue
        binding = bindings[key3]
        if item["outcome_id"] != binding["outcome_id"]:
            issues.append(f"outcome_mismatch:{label}")
            continue
        outcome = outcome_by_id[str(binding["outcome_id"])]
        active = _active_route(outcome)
        spec = next(
            observer
            for observer in panels[key3[0]]["observers"]
            if str(observer["observer_id"]) == key4[3]
        )
        if item["provider_family"] != spec["provider_family"]:
            issues.append(f"observer_provider_mismatch:{label}")
        if item["model"] != spec["model"]:
            issues.append(f"observer_model_mismatch:{label}")
        if item["reasoning_effort"] != spec["reasoning_effort"]:
            issues.append(f"observer_effort_mismatch:{label}")
        executor = active["implementation"]
        runtime_verifier = active["verifier"]
        expected_context = {
            "provider_family": executor["provider_family"],
            "model": executor["model"],
            "runtime_verifier_provider_family": runtime_verifier["provider_family"],
            "runtime_verifier_model": runtime_verifier["model"],
        }
        if item["executor_context"] != expected_context:
            issues.append(f"executor_context_mismatch:{label}")
        if item["model"] == executor["model"]:
            issues.append(f"executor_model_reused:{label}")
        output_hashes.setdefault(key3, set()).add(str(item["output_sha256"]))

    for key in sorted(expected - set(seen)):
        issues.append("missing_observation:" + ":".join(str(part) for part in key))
    for key, hashes in output_hashes.items():
        if len(hashes) > 1:
            issues.append("output_hash_disagreement:" + ":".join(str(part) for part in key))

    if issues:
        disagreement: dict[str, Any] = {
            "status": "insufficient",
            "issues": sorted(set(issues)),
            "decision_use": "diagnostic_only",
            "canonical_runtime_verifier_override": False,
        }
    else:
        summaries: list[dict[str, Any]] = []
        totals = {
            "verifiable": 0,
            "observations": 0,
            "unanimous": 0,
            "disagreement": 0,
            "status": 0,
            "criterion": 0,
            "human_reason": 0,
        }
        for candidate_id in sorted(candidate_ids):
            trial_keys = sorted({key[:3] for key in expected if key[0] == candidate_id})
            panel_size = len(panels[candidate_id]["observers"])
            candidate_counts = {
                "disagreement": 0,
                "status": 0,
                "criterion": 0,
                "human_reason": 0,
            }
            for trial_key in trial_keys:
                trial_observations = [
                    seen[(*trial_key, str(observer["observer_id"]))]
                    for observer in panels[candidate_id]["observers"]
                ]
                values = _trial_disagreement(trial_observations)
                for name, value in zip(candidate_counts, values):
                    candidate_counts[name] += int(value)
            verifiable = len(trial_keys)
            observation_count = verifiable * panel_size
            unanimous = verifiable - candidate_counts["disagreement"]
            summaries.append(
                {
                    "candidate_id": candidate_id,
                    "panel_size": panel_size,
                    "verifiable_trials": verifiable,
                    "observation_count": observation_count,
                    "unanimous_trials": unanimous,
                    "disagreement_trials": candidate_counts["disagreement"],
                    "disagreement_rate": (
                        candidate_counts["disagreement"] / verifiable if verifiable else 0.0
                    ),
                    "status_disagreement_trials": candidate_counts["status"],
                    "criterion_disagreement_trials": candidate_counts["criterion"],
                    "human_reason_disagreement_trials": candidate_counts["human_reason"],
                }
            )
            totals["verifiable"] += verifiable
            totals["observations"] += observation_count
            totals["unanimous"] += unanimous
            for name in ("disagreement", "status", "criterion", "human_reason"):
                totals[name] += candidate_counts[name]

        disagreement = {
            "status": "measured",
            "panel_plan_id": plan_data["panel_plan_id"],
            "panel_plan_version": plan_data["panel_plan_version"],
            "observation_count": totals["observations"],
            "verifiable_trials": totals["verifiable"],
            "unanimous_trials": totals["unanimous"],
            "disagreement_trials": totals["disagreement"],
            "disagreement_rate": (
                totals["disagreement"] / totals["verifiable"]
                if totals["verifiable"]
                else 0.0
            ),
            "status_disagreement_trials": totals["status"],
            "criterion_disagreement_trials": totals["criterion"],
            "human_reason_disagreement_trials": totals["human_reason"],
            "candidate_summaries": summaries,
            "decision_use": "diagnostic_only",
            "canonical_runtime_verifier_override": False,
        }

    report_data["verifier_disagreement"] = disagreement
    report_data["limitations"] = [
        item
        for item in report_data["limitations"]
        if "Multi-verifier disagreement measurement" not in item
    ]
    note = (
        "Benchmark verifier disagreement is diagnostic only. No majority vote, panel pass rate, or observer preference overrides the canonical runtime verifier or route-outcome disposition."
    )
    if note not in report_data["limitations"]:
        report_data["limitations"].append(note)
    report_data["provenance"]["panel_plan_sha256"] = panel_sha
    report_data["provenance"]["source_verifier_observation_ids"] = sorted(
        str(item.to_dict()["observation_id"]) for item in observations
    )
    report_data["integrity_sha256"] = _canonical_sha256(
        report_data, omit="integrity_sha256"
    )
    return BenchmarkExperimentReport.from_dict(report_data, repo_root=repo_root)


class JsonlBenchmarkVerifierObservationSink:
    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, observation: BenchmarkVerifierObservation) -> None:
        payload = observation.to_dict()
        BenchmarkVerifierObservation.from_dict(payload, repo_root=self.repo_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Benchmark verifier observation could not be persisted"
            ) from exc

    def read_all(self) -> list[BenchmarkVerifierObservation]:
        if not self.path.exists():
            return []
        try:
            lines = self.path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Benchmark verifier observation JSONL could not be read"
            ) from exc
        records: list[BenchmarkVerifierObservation] = []
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ProviderAdapterContractError(
                    f"Invalid benchmark verifier observation JSONL at line {index}"
                ) from exc
            if not isinstance(raw, dict):
                raise ProviderAdapterContractError(
                    f"Benchmark verifier observation JSONL line {index} must be an object"
                )
            records.append(
                BenchmarkVerifierObservation.from_dict(raw, repo_root=self.repo_root)
            )
        return records
