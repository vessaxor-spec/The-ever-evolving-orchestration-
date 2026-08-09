from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any, Literal

import yaml

from .verification_adapter import (
    LiveVerificationDecision,
    LiveVerificationError,
    VERIFICATION_CHECKS,
)

CalibrationStatus = Literal["passed", "failed", "needs_human"]
ExecutionRole = Literal["primary", "fallback"]


class CalibrationError(RuntimeError):
    """Raised when calibration evidence or gold labels are invalid."""


@dataclass(frozen=True, slots=True)
class CalibrationPolicy:
    minimum_cases: int
    required_categories: frozenset[str]
    minimum_runs_per_case_per_verifier: int
    minimum_distinct_verifier_routes: int
    minimum_distinct_verifier_provider_families: int
    expected_rubric_version: str
    expected_verification_policy_version: str
    require_independent_human_review: bool


@dataclass(frozen=True, slots=True)
class GoldCalibrationCase:
    case_id: str
    category: str
    task: str
    candidate_output: str
    rubric_version: str
    gold: LiveVerificationDecision
    deterministic_complete: bool
    deterministic_rules: dict[str, Any]


@dataclass(frozen=True, slots=True)
class DeterministicValidationResult:
    status: CalibrationStatus | None
    checks: dict[str, str | None]


@dataclass(frozen=True, slots=True)
class CalibrationObservation:
    case_id: str
    verifier_provider_family: str
    verifier_model: str
    verifier_reasoning: str | None
    run_id: str
    observed_at: str
    rubric_version: str
    verification_policy_version: str
    decision: LiveVerificationDecision
    execution_role: ExecutionRole
    retry_count: int
    fallback_used: bool
    duration_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    @property
    def verifier_route(self) -> str:
        effort = self.verifier_reasoning or "unspecified"
        return f"{self.verifier_provider_family}/{self.verifier_model}/{effort}"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CalibrationObservation":
        allowed = {
            "case_id",
            "verifier_provider_family",
            "verifier_model",
            "verifier_reasoning",
            "run_id",
            "observed_at",
            "rubric_version",
            "verification_policy_version",
            "decision",
            "execution_role",
            "retry_count",
            "fallback_used",
            "duration_ms",
            "input_tokens",
            "output_tokens",
        }
        required = {
            "case_id",
            "verifier_provider_family",
            "verifier_model",
            "verifier_reasoning",
            "run_id",
            "observed_at",
            "rubric_version",
            "verification_policy_version",
            "decision",
            "execution_role",
            "retry_count",
            "fallback_used",
        }
        unknown = sorted(set(data) - allowed)
        missing = sorted(required - set(data))
        if unknown:
            raise CalibrationError(
                "Calibration observation contains unsupported fields: " + ", ".join(unknown)
            )
        if missing:
            raise CalibrationError(
                "Calibration observation is missing required fields: " + ", ".join(missing)
            )

        decision = data["decision"]
        if not isinstance(decision, dict):
            raise CalibrationError("Calibration observation decision must be an object")

        role_raw = data["execution_role"]
        if not isinstance(role_raw, str) or role_raw not in {"primary", "fallback"}:
            raise CalibrationError(
                "Calibration observation execution_role must be primary or fallback"
            )

        retry_raw = data["retry_count"]
        if isinstance(retry_raw, bool) or not isinstance(retry_raw, int) or retry_raw < 0:
            raise CalibrationError(
                "Calibration observation retry_count must be a non-negative integer"
            )

        fallback_raw = data["fallback_used"]
        if not isinstance(fallback_raw, bool):
            raise CalibrationError("Calibration observation fallback_used must be a boolean")
        if (role_raw == "fallback") != fallback_raw:
            raise CalibrationError(
                "Calibration observation execution_role and fallback_used must agree"
            )

        reasoning_raw = data["verifier_reasoning"]
        if reasoning_raw is not None and (
            not isinstance(reasoning_raw, str) or not reasoning_raw.strip()
        ):
            raise CalibrationError(
                "Calibration observation verifier_reasoning must be a non-empty string or null"
            )

        duration = _optional_non_negative_float(data.get("duration_ms"), "duration_ms")
        input_tokens = _optional_non_negative_int(data.get("input_tokens"), "input_tokens")
        output_tokens = _optional_non_negative_int(data.get("output_tokens"), "output_tokens")
        try:
            parsed_decision = LiveVerificationDecision.from_dict(decision)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc

        return cls(
            case_id=_required_text(data["case_id"], "case_id"),
            verifier_provider_family=_required_text(
                data["verifier_provider_family"], "verifier_provider_family"
            ),
            verifier_model=_required_text(data["verifier_model"], "verifier_model"),
            verifier_reasoning=(reasoning_raw.strip() if reasoning_raw is not None else None),
            run_id=_required_text(data["run_id"], "run_id"),
            observed_at=_required_offset_datetime(data["observed_at"], "observed_at"),
            rubric_version=_required_text(data["rubric_version"], "rubric_version"),
            verification_policy_version=_required_text(
                data["verification_policy_version"], "verification_policy_version"
            ),
            decision=parsed_decision,
            execution_role=role_raw,  # type: ignore[arg-type]
            retry_count=retry_raw,
            fallback_used=fallback_raw,
            duration_ms=duration,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    total_gold_cases: int
    total_observations: int
    exact_status_accuracy: float
    false_pass_count: int
    false_pass_opportunities: int
    false_pass_rate: float | None
    false_fail_count: int
    false_fail_opportunities: int
    false_fail_rate: float | None
    missed_human_count: int
    human_required_opportunities: int
    missed_human_rate: float | None
    unnecessary_human_count: int
    non_human_opportunities: int
    unnecessary_human_rate: float | None
    needs_human_prediction_rate: float
    criterion_accuracy: dict[str, float]
    repeatability_agreement_rate: float | None
    repeatability_groups: int
    cross_verifier_disagreement_cases: list[str]
    verifier_routes: list[str]
    verifier_provider_families: list[str]
    observation_window_start: str
    observation_window_end: str
    average_duration_ms: float | None
    p95_duration_ms: float | None
    total_input_tokens: int
    total_output_tokens: int
    by_execution_path: dict[str, dict[str, float | int]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class CalibrationEvidenceReadiness:
    data_requirements_met: bool
    distinct_verifier_routes: int
    required_distinct_verifier_routes: int
    distinct_verifier_provider_families: int
    required_distinct_verifier_provider_families: int
    minimum_runs_per_case_per_verifier: int
    undercovered_case_routes: list[str]
    independent_human_review_required: bool
    quality_claims_authorized: bool = False
    scope_expansion_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CalibrationError(f"{name} must be a non-empty string")
    return value.strip()


def _required_offset_datetime(value: object, name: str) -> str:
    text = _required_text(value, name)
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise CalibrationError(f"{name} must be an RFC 3339-compatible timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise CalibrationError(f"{name} must include a UTC offset")
    return text


def _required_bool(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise CalibrationError(f"{name} must be a boolean")
    return value


def _required_positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise CalibrationError(f"{name} must be a positive integer")
    return value


def _optional_non_negative_int(value: object, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CalibrationError(f"{name} must be a non-negative integer or null")
    return value


def _optional_non_negative_float(value: object, name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) < 0:
        raise CalibrationError(f"{name} must be a non-negative number or null")
    return float(value)


def _conditional_rate(count: int, opportunities: int) -> float | None:
    return count / opportunities if opportunities else None


def load_calibration_policy(path: str | Path) -> CalibrationPolicy:
    source = Path(path)
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "active":
        raise CalibrationError("Calibration policy must be an active mapping")

    scope = payload.get("scope")
    gold = payload.get("gold_corpus")
    observations = payload.get("observation_requirements")
    expansion = payload.get("expansion_gate")
    if not all(isinstance(item, dict) for item in (scope, gold, observations, expansion)):
        raise CalibrationError(
            "Calibration policy requires scope, gold_corpus, observation_requirements, and expansion_gate mappings"
        )

    if _required_bool(scope.get("live_scope_expansion_authorized"), "scope.live_scope_expansion_authorized"):
        raise CalibrationError("Calibration policy must not authorize live scope expansion")
    if _required_bool(scope.get("routing_authority"), "scope.routing_authority"):
        raise CalibrationError("Calibration policy must not have routing authority")
    if _required_bool(scope.get("quality_claims_authorized"), "scope.quality_claims_authorized"):
        raise CalibrationError("Calibration policy must not authorize quality claims")
    if _required_bool(expansion.get("automatic_expansion"), "expansion_gate.automatic_expansion"):
        raise CalibrationError("Calibration policy must not authorize automatic expansion")

    categories_raw = gold.get("required_categories")
    if not isinstance(categories_raw, list) or not categories_raw:
        raise CalibrationError("Calibration policy required_categories must be a non-empty list")
    categories = frozenset(_required_text(item, "required_category") for item in categories_raw)

    return CalibrationPolicy(
        minimum_cases=_required_positive_int(gold.get("minimum_cases"), "gold_corpus.minimum_cases"),
        required_categories=categories,
        minimum_runs_per_case_per_verifier=_required_positive_int(
            observations.get("minimum_runs_per_case_per_verifier"),
            "observation_requirements.minimum_runs_per_case_per_verifier",
        ),
        minimum_distinct_verifier_routes=_required_positive_int(
            observations.get("minimum_distinct_verifier_routes"),
            "observation_requirements.minimum_distinct_verifier_routes",
        ),
        minimum_distinct_verifier_provider_families=_required_positive_int(
            observations.get("minimum_distinct_verifier_provider_families"),
            "observation_requirements.minimum_distinct_verifier_provider_families",
        ),
        expected_rubric_version=_required_text(
            observations.get("rubric_version"), "observation_requirements.rubric_version"
        ),
        expected_verification_policy_version=_required_text(
            observations.get("verification_policy_version"),
            "observation_requirements.verification_policy_version",
        ),
        require_independent_human_review=_required_bool(
            expansion.get("require_independent_human_review"),
            "expansion_gate.require_independent_human_review",
        ),
    )


def load_gold_cases(
    path: str | Path,
    *,
    policy: CalibrationPolicy | None = None,
) -> list[GoldCalibrationCase]:
    source = Path(path)
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "active":
        raise CalibrationError("Calibration gold corpus must be an active mapping")

    rubric = payload.get("rubric")
    if not isinstance(rubric, dict) or tuple(rubric.get("checks", [])) != VERIFICATION_CHECKS:
        raise CalibrationError("Calibration gold corpus must use the guarded verifier rubric")
    rubric_version = _required_text(rubric.get("version"), "rubric.version")
    expected_precedence = [
        "any_fail_means_failed",
        "otherwise_any_uncertain_means_needs_human",
        "otherwise_passed",
    ]
    if rubric.get("status_precedence") != expected_precedence:
        raise CalibrationError("Calibration gold corpus must preserve verifier status precedence")

    raw_cases = payload.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise CalibrationError("Calibration gold corpus requires cases")

    cases: list[GoldCalibrationCase] = []
    seen: set[str] = set()
    for raw in raw_cases:
        if not isinstance(raw, dict):
            raise CalibrationError("Calibration case must be an object")
        case_id = _required_text(raw.get("id"), "case.id")
        if case_id in seen:
            raise CalibrationError(f"Duplicate calibration case id: {case_id}")
        seen.add(case_id)

        gold_raw = raw.get("gold")
        deterministic = raw.get("deterministic")
        candidate_output = raw.get("candidate_output")
        if not isinstance(gold_raw, dict) or not isinstance(deterministic, dict):
            raise CalibrationError(
                f"Calibration case {case_id} requires gold and deterministic mappings"
            )
        if not isinstance(candidate_output, str):
            raise CalibrationError(
                f"Calibration case {case_id} candidate_output must be a string"
            )
        rules = deterministic.get("rules", {})
        if not isinstance(rules, dict):
            raise CalibrationError(
                f"Calibration case {case_id} deterministic.rules must be a mapping"
            )
        complete = deterministic.get("complete")
        if not isinstance(complete, bool):
            raise CalibrationError(
                f"Calibration case {case_id} deterministic.complete must be a boolean"
            )
        try:
            gold_decision = LiveVerificationDecision.from_dict(gold_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(f"Calibration case {case_id}: {exc}") from exc

        cases.append(
            GoldCalibrationCase(
                case_id=case_id,
                category=_required_text(raw.get("category"), f"{case_id}.category"),
                task=_required_text(raw.get("task"), f"{case_id}.task"),
                candidate_output=candidate_output,
                rubric_version=rubric_version,
                gold=gold_decision,
                deterministic_complete=complete,
                deterministic_rules=dict(rules),
            )
        )

    validate_gold_corpus(cases, policy=policy)
    return cases


def deterministic_validate(case: GoldCalibrationCase) -> DeterministicValidationResult:
    checks: dict[str, str | None] = {name: None for name in VERIFICATION_CHECKS}
    rules = case.deterministic_rules
    output = case.candidate_output
    lines = output.splitlines()

    if rules.get("non_empty") is True:
        checks["output_present"] = "pass" if output.strip() else "fail"

    if "exact_lines" in rules:
        expected = rules["exact_lines"]
        if not isinstance(expected, list) or not all(isinstance(item, str) for item in expected):
            raise CalibrationError(
                f"Calibration case {case.case_id} exact_lines must be a string list"
            )
        checks["task_adherence"] = "pass" if lines == expected else "fail"

    if "line_count" in rules:
        expected_count = rules["line_count"]
        if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 0:
            raise CalibrationError(
                f"Calibration case {case.case_id} line_count must be non-negative"
            )
        checks["format_consistency"] = "pass" if len(lines) == expected_count else "fail"

    if "forbidden_substrings" in rules:
        forbidden = rules["forbidden_substrings"]
        if not isinstance(forbidden, list) or not all(isinstance(item, str) for item in forbidden):
            raise CalibrationError(
                f"Calibration case {case.case_id} forbidden_substrings must be a string list"
            )
        lowered = output.lower()
        checks["unsupported_claims_absent"] = (
            "fail" if any(item.lower() in lowered for item in forbidden) else "pass"
        )

    present = [value for value in checks.values() if value is not None]
    if any(value == "fail" for value in present):
        status: CalibrationStatus | None = "failed"
    elif case.deterministic_complete:
        if any(value is None for value in checks.values()):
            raise CalibrationError(
                f"Calibration case {case.case_id} declares complete deterministic coverage but leaves checks unresolved"
            )
        status = "passed"
    else:
        status = None
    return DeterministicValidationResult(status=status, checks=checks)


def validate_gold_corpus(
    cases: list[GoldCalibrationCase],
    *,
    policy: CalibrationPolicy | None = None,
) -> None:
    default_categories = {
        "correct",
        "subtly_wrong",
        "incomplete",
        "wrong_format",
        "unsupported_claim",
        "ambiguous",
        "unverifiable",
        "adversarial",
    }
    required_categories = set(policy.required_categories) if policy else default_categories
    minimum_cases = policy.minimum_cases if policy else len(required_categories)

    if len(cases) < minimum_cases:
        raise CalibrationError(
            f"Calibration gold corpus has {len(cases)} cases but requires at least {minimum_cases}"
        )
    categories = {case.category for case in cases}
    missing = sorted(required_categories - categories)
    if missing:
        raise CalibrationError(
            "Calibration gold corpus is missing required categories: " + ", ".join(missing)
        )
    rubric_versions = {case.rubric_version for case in cases}
    if len(rubric_versions) != 1:
        raise CalibrationError("Calibration gold corpus must use one rubric version")
    if policy and rubric_versions != {policy.expected_rubric_version}:
        raise CalibrationError(
            "Calibration gold corpus rubric version does not match calibration policy"
        )

    for case in cases:
        result = deterministic_validate(case)
        for check, verdict in result.checks.items():
            if verdict is not None and verdict != case.gold.verdicts[check]:
                raise CalibrationError(
                    f"Calibration case {case.case_id} deterministic {check}={verdict} conflicts with gold {case.gold.verdicts[check]}"
                )
        if result.status is not None and result.status != case.gold.status:
            raise CalibrationError(
                f"Calibration case {case.case_id} deterministic status {result.status} conflicts with gold {case.gold.status}"
            )


def load_observations(path: str | Path) -> list[CalibrationObservation]:
    source = Path(path)
    observations: list[CalibrationObservation] = []
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise CalibrationError(f"Calibration observations could not be read: {source}") from exc

    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CalibrationError(
                f"Calibration observation line {index} is invalid JSON"
            ) from exc
        if not isinstance(raw, dict):
            raise CalibrationError(
                f"Calibration observation line {index} must be an object"
            )
        observations.append(CalibrationObservation.from_dict(raw))

    if not observations:
        raise CalibrationError("Calibration observations are empty")
    return observations


def _validate_observation_set(
    cases: list[GoldCalibrationCase],
    observations: list[CalibrationObservation],
    *,
    policy: CalibrationPolicy | None,
) -> None:
    if not observations:
        raise CalibrationError("Calibration observations are empty")

    by_case = {case.case_id: case for case in cases}
    unknown = sorted({observation.case_id for observation in observations} - set(by_case))
    if unknown:
        raise CalibrationError(
            "Observations reference unknown calibration cases: " + ", ".join(unknown)
        )

    seen: set[tuple[str, str, str, str | None, str]] = set()
    for observation in observations:
        identity = (
            observation.case_id,
            observation.verifier_provider_family,
            observation.verifier_model,
            observation.verifier_reasoning,
            observation.run_id,
        )
        if identity in seen:
            raise CalibrationError(
                "Duplicate calibration observation identity: " + "/".join(str(item) for item in identity)
            )
        seen.add(identity)

        gold_case = by_case[observation.case_id]
        if observation.rubric_version != gold_case.rubric_version:
            raise CalibrationError(
                f"Calibration observation {observation.run_id} rubric version does not match gold case {observation.case_id}"
            )
        if policy:
            if observation.rubric_version != policy.expected_rubric_version:
                raise CalibrationError(
                    f"Calibration observation {observation.run_id} uses an unsupported rubric version"
                )
            if observation.verification_policy_version != policy.expected_verification_policy_version:
                raise CalibrationError(
                    f"Calibration observation {observation.run_id} uses an unsupported verification policy version"
                )


def evaluate_calibration(
    cases: list[GoldCalibrationCase],
    observations: list[CalibrationObservation],
    *,
    policy: CalibrationPolicy | None = None,
) -> CalibrationReport:
    _validate_observation_set(cases, observations, policy=policy)
    by_case = {case.case_id: case for case in cases}

    status_correct = 0
    false_pass = 0
    false_pass_opportunities = 0
    false_fail = 0
    false_fail_opportunities = 0
    missed_human = 0
    human_required_opportunities = 0
    unnecessary_human = 0
    non_human_opportunities = 0
    needs_human_predictions = 0
    criterion_correct = Counter()
    criterion_total = Counter()
    durations: list[float] = []
    total_input_tokens = 0
    total_output_tokens = 0
    repeatability: dict[tuple[str, str], list[str]] = defaultdict(list)
    cross_verifier: dict[str, list[tuple[str, str]]] = defaultdict(list)
    path_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: {"observations": 0, "correct": 0}
    )
    verifier_routes: set[str] = set()
    provider_families: set[str] = set()
    observed_times: list[tuple[datetime, str]] = []

    for observation in observations:
        gold = by_case[observation.case_id].gold
        predicted = observation.decision
        correct = predicted.status == gold.status
        status_correct += int(correct)

        if gold.status != "passed":
            false_pass_opportunities += 1
            false_pass += int(predicted.status == "passed")
        if gold.status == "passed":
            false_fail_opportunities += 1
            false_fail += int(predicted.status == "failed")
        if gold.status == "needs_human":
            human_required_opportunities += 1
            missed_human += int(predicted.status != "needs_human")
        else:
            non_human_opportunities += 1
            unnecessary_human += int(predicted.status == "needs_human")
        needs_human_predictions += int(predicted.status == "needs_human")

        for check in VERIFICATION_CHECKS:
            criterion_total[check] += 1
            criterion_correct[check] += int(
                predicted.verdicts[check] == gold.verdicts[check]
            )

        if observation.duration_ms is not None:
            durations.append(observation.duration_ms)
        total_input_tokens += observation.input_tokens or 0
        total_output_tokens += observation.output_tokens or 0

        route = observation.verifier_route
        verifier_routes.add(route)
        provider_families.add(observation.verifier_provider_family)
        repeatability[(observation.case_id, route)].append(predicted.status)
        cross_verifier[observation.case_id].append((route, predicted.status))
        normalized_time = (
            observation.observed_at[:-1] + "+00:00"
            if observation.observed_at.endswith("Z")
            else observation.observed_at
        )
        observed_times.append((datetime.fromisoformat(normalized_time), observation.observed_at))

        if observation.execution_role == "fallback":
            path = "fallback"
        elif observation.retry_count > 0:
            path = "primary_retry"
        else:
            path = "primary_no_retry"
        path_counts[path]["observations"] += 1
        path_counts[path]["correct"] += int(correct)

    total = len(observations)
    repeatability_scores: list[float] = []
    for statuses in repeatability.values():
        if len(statuses) < 2:
            continue
        counts = Counter(statuses)
        total_pairs = len(statuses) * (len(statuses) - 1) // 2
        agreeing_pairs = sum(count * (count - 1) // 2 for count in counts.values())
        repeatability_scores.append(agreeing_pairs / total_pairs)

    disagreement_cases: list[str] = []
    for case_id, results in cross_verifier.items():
        by_route: dict[str, set[str]] = defaultdict(set)
        for route, status in results:
            by_route[route].add(status)
        routes = sorted(by_route)
        disagreement = any(
            by_route[left] != by_route[right]
            for index, left in enumerate(routes)
            for right in routes[index + 1 :]
        )
        if len(routes) > 1 and disagreement:
            disagreement_cases.append(case_id)

    criterion_accuracy = {
        check: criterion_correct[check] / criterion_total[check]
        for check in VERIFICATION_CHECKS
    }
    by_execution_path: dict[str, dict[str, float | int]] = {}
    for path, counts in sorted(path_counts.items()):
        observations_count = counts["observations"]
        by_execution_path[path] = {
            "observations": observations_count,
            "exact_status_accuracy": counts["correct"] / observations_count,
        }

    observed_times.sort(key=lambda item: item[0])
    return CalibrationReport(
        total_gold_cases=len(cases),
        total_observations=total,
        exact_status_accuracy=status_correct / total,
        false_pass_count=false_pass,
        false_pass_opportunities=false_pass_opportunities,
        false_pass_rate=_conditional_rate(false_pass, false_pass_opportunities),
        false_fail_count=false_fail,
        false_fail_opportunities=false_fail_opportunities,
        false_fail_rate=_conditional_rate(false_fail, false_fail_opportunities),
        missed_human_count=missed_human,
        human_required_opportunities=human_required_opportunities,
        missed_human_rate=_conditional_rate(missed_human, human_required_opportunities),
        unnecessary_human_count=unnecessary_human,
        non_human_opportunities=non_human_opportunities,
        unnecessary_human_rate=_conditional_rate(unnecessary_human, non_human_opportunities),
        needs_human_prediction_rate=needs_human_predictions / total,
        criterion_accuracy=criterion_accuracy,
        repeatability_agreement_rate=(
            mean(repeatability_scores) if repeatability_scores else None
        ),
        repeatability_groups=len(repeatability_scores),
        cross_verifier_disagreement_cases=sorted(disagreement_cases),
        verifier_routes=sorted(verifier_routes),
        verifier_provider_families=sorted(provider_families),
        observation_window_start=observed_times[0][1],
        observation_window_end=observed_times[-1][1],
        average_duration_ms=(mean(durations) if durations else None),
        p95_duration_ms=_percentile(durations, 0.95) if durations else None,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        by_execution_path=by_execution_path,
    )


def assess_evidence_readiness(
    cases: list[GoldCalibrationCase],
    observations: list[CalibrationObservation],
    policy: CalibrationPolicy,
) -> CalibrationEvidenceReadiness:
    _validate_observation_set(cases, observations, policy=policy)

    routes = sorted({observation.verifier_route for observation in observations})
    provider_families = sorted(
        {observation.verifier_provider_family for observation in observations}
    )
    counts: Counter[tuple[str, str]] = Counter(
        (observation.case_id, observation.verifier_route)
        for observation in observations
    )
    undercovered: list[str] = []
    for case in cases:
        for route in routes:
            observed = counts[(case.case_id, route)]
            if observed < policy.minimum_runs_per_case_per_verifier:
                undercovered.append(
                    f"{case.case_id}@{route}:{observed}/{policy.minimum_runs_per_case_per_verifier}"
                )

    data_requirements_met = (
        len(routes) >= policy.minimum_distinct_verifier_routes
        and len(provider_families) >= policy.minimum_distinct_verifier_provider_families
        and not undercovered
        and len(cases) >= policy.minimum_cases
        and policy.required_categories.issubset({case.category for case in cases})
    )
    return CalibrationEvidenceReadiness(
        data_requirements_met=data_requirements_met,
        distinct_verifier_routes=len(routes),
        required_distinct_verifier_routes=policy.minimum_distinct_verifier_routes,
        distinct_verifier_provider_families=len(provider_families),
        required_distinct_verifier_provider_families=policy.minimum_distinct_verifier_provider_families,
        minimum_runs_per_case_per_verifier=policy.minimum_runs_per_case_per_verifier,
        undercovered_case_routes=undercovered,
        independent_human_review_required=policy.require_independent_human_review,
    )


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise CalibrationError("Cannot calculate percentile of empty values")
    index = max(
        0,
        min(len(ordered) - 1, int((len(ordered) - 1) * percentile + 0.5)),
    )
    return ordered[index]


def gold_summary(
    cases: list[GoldCalibrationCase],
    *,
    policy: CalibrationPolicy | None = None,
) -> dict[str, Any]:
    validate_gold_corpus(cases, policy=policy)
    deterministic = [deterministic_validate(case) for case in cases]
    return {
        "status": "gold_corpus_valid",
        "case_count": len(cases),
        "categories": sorted({case.category for case in cases}),
        "rubric_version": cases[0].rubric_version if cases else None,
        "deterministically_resolved_cases": sum(
            result.status is not None for result in deterministic
        ),
        "semantic_or_human_cases": sum(
            result.status is None for result in deterministic
        ),
        "quality_claims_authorized": False,
        "scope_expansion_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate TEO verifier calibration observations"
    )
    parser.add_argument(
        "--gold",
        default="reference/datasets/verifier-calibration-gold.yaml",
        help="Gold-label calibration corpus",
    )
    parser.add_argument(
        "--policy",
        default="policy/verification/verifier-calibration.yaml",
        help="Calibration evidence policy",
    )
    parser.add_argument(
        "--observations",
        help="JSONL verifier observations to evaluate",
    )
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args(argv)

    try:
        policy = load_calibration_policy(args.policy)
        cases = load_gold_cases(args.gold, policy=policy)
        if args.observations:
            observations = load_observations(args.observations)
            report: dict[str, Any] = {
                "metrics": evaluate_calibration(
                    cases,
                    observations,
                    policy=policy,
                ).to_dict(),
                "evidence_readiness": assess_evidence_readiness(
                    cases,
                    observations,
                    policy,
                ).to_dict(),
            }
        else:
            report = gold_summary(cases, policy=policy)
    except (CalibrationError, OSError, yaml.YAMLError) as exc:
        parser.error(str(exc))
        return 2

    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
