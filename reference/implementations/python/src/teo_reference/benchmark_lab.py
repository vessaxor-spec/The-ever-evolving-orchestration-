from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from jsonschema import Draft202012Validator

from .provider_adapter import ProviderAdapterContractError
from .route_outcome import RouteOutcomeRecord

BENCHMARK_LAB_VERSION = "1"
BENCHMARK_FIXTURE_SCHEMA_PATH = "reference/schemas/benchmark-fixture.schema.json"
BENCHMARK_EXPERIMENT_SCHEMA_PATH = "reference/schemas/benchmark-experiment.schema.json"
BENCHMARK_REPORT_SCHEMA_PATH = "reference/schemas/benchmark-report.schema.json"

StudyType = Literal["benchmark", "replay", "regression"]
ClaimScope = Literal["system_to_system", "executor_only"]


def _require_text(value: Any, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise ProviderAdapterContractError(f"Benchmark Lab {name} is required")
    return text


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
        raise ProviderAdapterContractError(f"Benchmark Lab schema not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProviderAdapterContractError(f"Benchmark Lab schema could not be loaded: {path}") from exc
    if not isinstance(raw, dict):
        raise ProviderAdapterContractError("Benchmark Lab schema must be an object")
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


@dataclass(frozen=True, slots=True)
class BenchmarkFixtureRecord:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkFixtureRecord":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_FIXTURE_SCHEMA_PATH,
            label="Benchmark fixture",
        )
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError("Benchmark fixture integrity hash does not match content")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


@dataclass(frozen=True, slots=True)
class BenchmarkExperimentManifest:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkExperimentManifest":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_EXPERIMENT_SCHEMA_PATH,
            label="Benchmark experiment",
        )
        _validate_manifest_semantics(data)
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))

    @property
    def sha256(self) -> str:
        return _canonical_sha256(self.payload)


@dataclass(frozen=True, slots=True)
class BenchmarkExperimentReport:
    payload: dict[str, Any]

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
        *,
        repo_root: str | Path,
    ) -> "BenchmarkExperimentReport":
        _validate_schema(
            data,
            repo_root=repo_root,
            relative_path=BENCHMARK_REPORT_SCHEMA_PATH,
            label="Benchmark report",
        )
        expected = str(data["integrity_sha256"])
        actual = _canonical_sha256(data, omit="integrity_sha256")
        if expected != actual:
            raise ProviderAdapterContractError("Benchmark report integrity hash does not match content")
        return cls(payload=json.loads(json.dumps(data)))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(json.dumps(self.payload))


def _validate_manifest_semantics(data: dict[str, Any]) -> None:
    candidates = data["candidates"]
    candidate_ids = [str(item["candidate_id"]) for item in candidates]
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ProviderAdapterContractError("Benchmark experiment candidate IDs must be unique")

    if data["study_type"] == "regression":
        baseline = data.get("regression_baseline_candidate_id")
        if baseline not in candidate_ids:
            raise ProviderAdapterContractError(
                "Regression experiment requires regression_baseline_candidate_id from candidates"
            )
    elif data.get("regression_baseline_candidate_id") is not None:
        raise ProviderAdapterContractError(
            "Only regression experiments may declare regression_baseline_candidate_id"
        )

    if data["claim_scope"] == "executor_only":
        first = candidates[0]
        fixed_fields = (
            "verifier_provider_family",
            "verifier_model",
            "runtime_version",
            "routing_policy_revision",
            "registry_revision",
            "tool_versions",
        )
        for candidate in candidates[1:]:
            for field in fixed_fields:
                if candidate[field] != first[field]:
                    raise ProviderAdapterContractError(
                        f"executor_only comparison changed non-executor field {field}"
                    )

    seen_bindings: set[tuple[str, str, int]] = set()
    seen_outcomes: set[str] = set()
    for binding in data["bindings"]:
        candidate_id = str(binding["candidate_id"])
        if candidate_id not in candidate_ids:
            raise ProviderAdapterContractError(
                f"Benchmark binding references unknown candidate {candidate_id}"
            )
        key = (
            str(binding["fixture_id"]),
            candidate_id,
            int(binding["trial_index"]),
        )
        if key in seen_bindings:
            raise ProviderAdapterContractError("Benchmark binding keys must be unique")
        seen_bindings.add(key)
        outcome_id = str(binding["outcome_id"])
        if outcome_id in seen_outcomes:
            raise ProviderAdapterContractError(
                "One route-outcome record cannot satisfy multiple benchmark trials"
            )
        seen_outcomes.add(outcome_id)


def load_benchmark_fixtures(
    path: str | Path,
    *,
    repo_root: str | Path,
) -> list[BenchmarkFixtureRecord]:
    records: list[BenchmarkFixtureRecord] = []
    for raw in _read_jsonl(path, label="benchmark fixture"):
        records.append(BenchmarkFixtureRecord.from_dict(raw, repo_root=repo_root))
    return records


def load_route_outcomes(
    path: str | Path,
    *,
    repo_root: str | Path,
) -> list[RouteOutcomeRecord]:
    records: list[RouteOutcomeRecord] = []
    for raw in _read_jsonl(path, label="route outcome"):
        records.append(RouteOutcomeRecord.from_dict(raw, repo_root=repo_root))
    return records


def _read_jsonl(path: str | Path, *, label: str) -> list[dict[str, Any]]:
    file_path = Path(path)
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ProviderAdapterContractError(f"Could not read {label} JSONL: {file_path}") from exc
    records: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProviderAdapterContractError(
                f"Invalid {label} JSONL at line {index}"
            ) from exc
        if not isinstance(raw, dict):
            raise ProviderAdapterContractError(
                f"{label.capitalize()} JSONL line {index} must be an object"
            )
        records.append(raw)
    return records


def _total_duration_ms(outcome: dict[str, Any]) -> float:
    total = sum(float(item["duration_ms"]) for item in outcome["primary_route"]["attempts"])
    fallback = outcome.get("fallback_route")
    if fallback is not None:
        total += sum(float(item["duration_ms"]) for item in fallback["attempts"])
    return total


def _token_observation(outcome: dict[str, Any]) -> tuple[int | None, bool]:
    observed = 0
    any_usage = False
    complete = True
    routes = [outcome["primary_route"]]
    if outcome.get("fallback_route") is not None:
        routes.append(outcome["fallback_route"])
    for route in routes:
        for attempt in route["attempts"]:
            usage = attempt.get("usage")
            if usage is None:
                complete = False
                continue
            any_usage = True
            total_tokens = usage.get("total_tokens")
            if total_tokens is None:
                complete = False
            else:
                observed += int(total_tokens)
    if not any_usage:
        return None, False
    return observed, complete


def _wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    proportion = successes / total
    denominator = 1.0 + (z * z / total)
    center = (proportion + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt((proportion * (1.0 - proportion) + z * z / (4.0 * total)) / total)
        / denominator
    )
    return max(0.0, center - radius), min(1.0, center + radius)


def _fixture_map(fixtures: Sequence[BenchmarkFixtureRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for fixture_record in fixtures:
        fixture = fixture_record.to_dict()
        fixture_id = str(fixture["fixture_id"])
        if fixture_id in result:
            raise ProviderAdapterContractError(f"Duplicate benchmark fixture {fixture_id}")
        result[fixture_id] = fixture
    return result


def _outcome_map(outcomes: Sequence[RouteOutcomeRecord]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for outcome_record in outcomes:
        outcome = outcome_record.to_dict()
        outcome_id = str(outcome["outcome_id"])
        if outcome_id in result:
            raise ProviderAdapterContractError(f"Duplicate route outcome {outcome_id}")
        result[outcome_id] = outcome
    return result


def _candidate_map(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): item for item in manifest["candidates"]}


def _validate_fixture_suite(
    manifest: dict[str, Any],
    fixtures: Mapping[str, dict[str, Any]],
) -> list[str]:
    issues: list[str] = []
    suite_fixture_ids = sorted(fixtures)
    if not suite_fixture_ids:
        issues.append("no_fixtures")
        return issues
    for fixture in fixtures.values():
        if fixture["suite_id"] != manifest["suite_id"]:
            issues.append(f"fixture_suite_mismatch:{fixture['fixture_id']}")
        if fixture["suite_version"] != manifest["suite_version"]:
            issues.append(f"fixture_suite_version_mismatch:{fixture['fixture_id']}")
    return issues


def _validate_binding_and_outcome(
    *,
    fixture: dict[str, Any],
    candidate: dict[str, Any],
    binding: dict[str, Any],
    outcome: dict[str, Any],
) -> list[str]:
    issues: list[str] = []
    label = f"{binding['candidate_id']}:{binding['fixture_id']}:{binding['trial_index']}"
    if outcome["task_type"] != fixture["task_type"]:
        issues.append(f"task_type_mismatch:{label}")
    if outcome["risk_level"] != fixture["risk_level"]:
        issues.append(f"risk_level_mismatch:{label}")
    if sorted(outcome["primary_route"]["required_capabilities"]) != sorted(
        fixture["required_capabilities"]
    ):
        issues.append(f"capability_mismatch:{label}")

    implementation = outcome["primary_route"]["implementation"]
    if implementation["provider_family"] != candidate["provider_family"]:
        issues.append(f"provider_mismatch:{label}")
    if implementation["model"] != candidate["model"]:
        issues.append(f"model_mismatch:{label}")
    if implementation["reasoning_effort"] != candidate["reasoning_effort"]:
        issues.append(f"reasoning_effort_mismatch:{label}")

    verifier = outcome["primary_route"]["verifier"]
    if verifier["provider_family"] != candidate["verifier_provider_family"]:
        issues.append(f"verifier_provider_mismatch:{label}")
    if verifier["model"] != candidate["verifier_model"]:
        issues.append(f"verifier_model_mismatch:{label}")

    versions = outcome["versions"]
    if versions["runtime_version"] != candidate["runtime_version"]:
        issues.append(f"runtime_version_mismatch:{label}")
    if versions["routing_policy_revision"] != candidate["routing_policy_revision"]:
        issues.append(f"routing_policy_revision_mismatch:{label}")
    if versions["registry_revision"] != candidate["registry_revision"]:
        issues.append(f"registry_revision_mismatch:{label}")
    if versions["tool_versions"] != candidate["tool_versions"]:
        issues.append(f"tool_versions_mismatch:{label}")
    return issues


def _balanced_bindings(
    manifest: dict[str, Any],
    fixture_ids: Sequence[str],
) -> tuple[list[str], dict[str, list[dict[str, Any]]]]:
    candidate_ids = [str(item["candidate_id"]) for item in manifest["candidates"]]
    grouped: dict[str, list[dict[str, Any]]] = {candidate_id: [] for candidate_id in candidate_ids}
    for binding in manifest["bindings"]:
        grouped[str(binding["candidate_id"])].append(binding)

    issues: list[str] = []
    expected_trials = int(manifest["trials_per_fixture"])
    expected_keys = {
        (fixture_id, trial_index)
        for fixture_id in fixture_ids
        for trial_index in range(1, expected_trials + 1)
    }
    for candidate_id, bindings in grouped.items():
        actual_keys = {
            (str(binding["fixture_id"]), int(binding["trial_index"]))
            for binding in bindings
        }
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        if missing:
            issues.append(f"missing_trials:{candidate_id}:{missing}")
        if extra:
            issues.append(f"extra_trials:{candidate_id}:{extra}")
    return issues, grouped


def _candidate_metrics(
    *,
    candidate_id: str,
    bindings: Sequence[dict[str, Any]],
    outcomes: Mapping[str, dict[str, Any]],
    fixture_ids: Sequence[str],
) -> dict[str, Any]:
    ordered = sorted(
        bindings,
        key=lambda item: (str(item["fixture_id"]), int(item["trial_index"])),
    )
    bound_outcomes = [outcomes[str(binding["outcome_id"])] for binding in ordered]
    trials = len(bound_outcomes)
    completed = sum(item["final_disposition"] == "completed" for item in bound_outcomes)
    primary_completed = sum(
        item["final_disposition"] == "completed" and item["active_route_role"] == "primary"
        for item in bound_outcomes
    )
    fallback_completed = sum(
        item["final_disposition"] == "completed" and item["fallback_assisted"]
        for item in bound_outcomes
    )
    retry_completed = sum(
        item["final_disposition"] == "completed" and item["retry_assisted"]
        for item in bound_outcomes
    )
    dispositions = {
        name: sum(item["final_disposition"] == name for item in bound_outcomes)
        for name in (
            "verification_failed",
            "awaiting_human",
            "verification_missing",
            "execution_failed",
            "abandoned",
        )
    }
    durations = [_total_duration_ms(item) for item in bound_outcomes]
    token_values: list[int] = []
    token_complete_count = 0
    token_any_count = 0
    for item in bound_outcomes:
        tokens, complete = _token_observation(item)
        if tokens is not None:
            token_values.append(tokens)
            token_any_count += 1
            if complete:
                token_complete_count += 1
    if token_any_count == 0:
        token_status = "unknown"
        total_tokens_observed = None
    elif token_complete_count == trials:
        token_status = "complete"
        total_tokens_observed = sum(token_values)
    else:
        token_status = "partial"
        total_tokens_observed = sum(token_values)

    fixture_completion: dict[str, list[bool]] = {fixture_id: [] for fixture_id in fixture_ids}
    for binding, outcome in zip(ordered, bound_outcomes):
        fixture_completion[str(binding["fixture_id"])].append(
            outcome["final_disposition"] == "completed"
        )
    pass_any = sum(any(values) for values in fixture_completion.values())
    pass_all = sum(bool(values) and all(values) for values in fixture_completion.values())
    low, high = _wilson_interval(completed, trials)
    primary_low, primary_high = _wilson_interval(primary_completed, trials)

    return {
        "candidate_id": candidate_id,
        "trials": trials,
        "completed": completed,
        "primary_completed": primary_completed,
        "fallback_assisted_completed": fallback_completed,
        "retry_assisted_completed": retry_completed,
        **dispositions,
        "verified_completion_rate": completed / trials if trials else 0.0,
        "verified_completion_wilson95": {"low": low, "high": high},
        "primary_verified_completion_rate": primary_completed / trials if trials else 0.0,
        "primary_verified_completion_wilson95": {
            "low": primary_low,
            "high": primary_high,
        },
        "fallback_assistance_rate": fallback_completed / trials if trials else 0.0,
        "retry_assistance_rate": retry_completed / trials if trials else 0.0,
        "pass_any_trial_fixture_rate": pass_any / len(fixture_ids) if fixture_ids else 0.0,
        "pass_all_trials_fixture_rate": pass_all / len(fixture_ids) if fixture_ids else 0.0,
        "mean_total_duration_ms": sum(durations) / trials if trials else 0.0,
        "token_observation_status": token_status,
        "total_tokens_observed": total_tokens_observed,
    }


def _regression_signals(
    manifest: dict[str, Any],
    metrics: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    if manifest["study_type"] != "regression":
        return []
    baseline_id = str(manifest["regression_baseline_candidate_id"])
    metric_map = {str(item["candidate_id"]): item for item in metrics}
    baseline = metric_map[baseline_id]
    signals: list[dict[str, Any]] = []
    for candidate_id, candidate in metric_map.items():
        if candidate_id == baseline_id:
            continue
        for metric_name in (
            "verified_completion_rate",
            "primary_verified_completion_rate",
        ):
            delta = float(candidate[metric_name]) - float(baseline[metric_name])
            if delta < 0:
                signals.append(
                    {
                        "candidate_id": candidate_id,
                        "metric": metric_name,
                        "baseline_candidate_id": baseline_id,
                        "delta": delta,
                        "classification": "descriptive_drop",
                    }
                )
    return signals


def evaluate_benchmark(
    manifest: BenchmarkExperimentManifest,
    fixtures: Sequence[BenchmarkFixtureRecord],
    outcomes: Sequence[RouteOutcomeRecord],
    *,
    repo_root: str | Path,
    generated_at: str | None = None,
) -> BenchmarkExperimentReport:
    manifest_data = manifest.to_dict()
    fixture_by_id = _fixture_map(fixtures)
    outcome_by_id = _outcome_map(outcomes)
    candidate_by_id = _candidate_map(manifest_data)

    issues = _validate_fixture_suite(manifest_data, fixture_by_id)
    binding_issues, grouped_bindings = _balanced_bindings(
        manifest_data, sorted(fixture_by_id)
    )
    issues.extend(binding_issues)

    for binding in manifest_data["bindings"]:
        fixture_id = str(binding["fixture_id"])
        candidate_id = str(binding["candidate_id"])
        outcome_id = str(binding["outcome_id"])
        if fixture_id not in fixture_by_id:
            issues.append(f"unknown_fixture:{fixture_id}")
            continue
        if outcome_id not in outcome_by_id:
            issues.append(f"missing_outcome:{outcome_id}")
            continue
        issues.extend(
            _validate_binding_and_outcome(
                fixture=fixture_by_id[fixture_id],
                candidate=candidate_by_id[candidate_id],
                binding=binding,
                outcome=outcome_by_id[outcome_id],
            )
        )

    comparability_status = "passed" if not issues else "failed"
    if issues:
        metrics: list[dict[str, Any]] = []
        evidence_sufficiency = "insufficient"
        regression_signals: list[dict[str, Any]] = []
    else:
        metrics = [
            _candidate_metrics(
                candidate_id=candidate_id,
                bindings=grouped_bindings[candidate_id],
                outcomes=outcome_by_id,
                fixture_ids=sorted(fixture_by_id),
            )
            for candidate_id in sorted(grouped_bindings)
        ]
        evidence_sufficiency = "descriptive_only"
        regression_signals = _regression_signals(manifest_data, metrics)

    payload: dict[str, Any] = {
        "benchmark_lab_version": BENCHMARK_LAB_VERSION,
        "record_type": "benchmark_report",
        "experiment_id": manifest_data["experiment_id"],
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "study_type": manifest_data["study_type"],
        "claim_scope": manifest_data["claim_scope"],
        "suite_id": manifest_data["suite_id"],
        "suite_version": manifest_data["suite_version"],
        "fixture_count": len(fixture_by_id),
        "trials_per_fixture": manifest_data["trials_per_fixture"],
        "primary_metric": manifest_data["primary_metric"],
        "comparability_status": comparability_status,
        "comparability_issues": sorted(set(issues)),
        "evidence_sufficiency": evidence_sufficiency,
        "candidate_metrics": metrics,
        "regression_signals": regression_signals,
        "verifier_disagreement": {
            "status": "not_measured",
            "reason": (
                "This report has not been enriched with a declared multi-verifier "
                "observation set."
            ),
        },
        "limitations": [
            "Metrics are controlled descriptive evidence, not automatic routing authority.",
            "No source-backed monetary cost attribution is performed.",
            "This base evaluator consumes completed route-outcome evidence. Controlled live replay and multi-verifier observation collection are separate executable layers.",
        ],
        "provenance": {
            "manifest_sha256": manifest.sha256,
            "fixture_integrity_sha256": [
                fixture_by_id[fixture_id]["integrity_sha256"]
                for fixture_id in sorted(fixture_by_id)
            ],
            "source_outcome_ids": [
                str(binding["outcome_id"])
                for binding in sorted(
                    manifest_data["bindings"],
                    key=lambda item: (
                        str(item["candidate_id"]),
                        str(item["fixture_id"]),
                        int(item["trial_index"]),
                    ),
                )
            ],
        },
    }
    payload["integrity_sha256"] = _canonical_sha256(payload, omit="integrity_sha256")
    return BenchmarkExperimentReport.from_dict(payload, repo_root=repo_root)


class JsonlBenchmarkReportSink:
    def __init__(self, path: str | Path, *, repo_root: str | Path) -> None:
        self.path = Path(path)
        self.repo_root = Path(repo_root)

    def append(self, report: BenchmarkExperimentReport) -> None:
        payload = report.to_dict()
        BenchmarkExperimentReport.from_dict(payload, repo_root=self.repo_root)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")
        except OSError as exc:
            raise ProviderAdapterContractError(
                "Benchmark report could not be persisted"
            ) from exc

    def read_all(self) -> list[BenchmarkExperimentReport]:
        if not self.path.exists():
            return []
        return [
            BenchmarkExperimentReport.from_dict(raw, repo_root=self.repo_root)
            for raw in _read_jsonl(self.path, label="benchmark report")
        ]