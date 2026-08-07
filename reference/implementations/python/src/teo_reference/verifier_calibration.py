from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
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
class GoldCalibrationCase:
    case_id: str
    category: str
    task: str
    candidate_output: str
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
    run_id: str
    decision: LiveVerificationDecision
    execution_role: ExecutionRole = "primary"
    retry_count: int = 0
    fallback_used: bool = False
    duration_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CalibrationObservation":
        allowed = {
            "case_id",
            "verifier_provider_family",
            "verifier_model",
            "run_id",
            "decision",
            "execution_role",
            "retry_count",
            "fallback_used",
            "duration_ms",
            "input_tokens",
            "output_tokens",
        }
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise CalibrationError(
                "Calibration observation contains unsupported fields: " + ", ".join(unknown)
            )
        decision = data.get("decision")
        if not isinstance(decision, dict):
            raise CalibrationError("Calibration observation decision must be an object")
        role = str(data.get("execution_role", "primary"))
        if role not in {"primary", "fallback"}:
            raise CalibrationError("Calibration observation execution_role must be primary or fallback")
        retry_count = int(data.get("retry_count", 0))
        if retry_count < 0:
            raise CalibrationError("Calibration observation retry_count cannot be negative")
        duration = _optional_non_negative_float(data.get("duration_ms"), "duration_ms")
        input_tokens = _optional_non_negative_int(data.get("input_tokens"), "input_tokens")
        output_tokens = _optional_non_negative_int(data.get("output_tokens"), "output_tokens")
        try:
            parsed_decision = LiveVerificationDecision.from_dict(decision)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            case_id=_required_text(data.get("case_id"), "case_id"),
            verifier_provider_family=_required_text(
                data.get("verifier_provider_family"), "verifier_provider_family"
            ),
            verifier_model=_required_text(data.get("verifier_model"), "verifier_model"),
            run_id=_required_text(data.get("run_id"), "run_id"),
            decision=parsed_decision,
            execution_role=role,  # type: ignore[arg-type]
            retry_count=retry_count,
            fallback_used=bool(data.get("fallback_used", False)),
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
    false_pass_rate: float
    false_fail_count: int
    false_fail_rate: float
    missed_human_count: int
    missed_human_rate: float
    unnecessary_human_count: int
    unnecessary_human_rate: float
    needs_human_prediction_rate: float
    criterion_accuracy: dict[str, float]
    repeatability_agreement_rate: float | None
    repeatability_groups: int
    cross_verifier_disagreement_cases: list[str]
    average_duration_ms: float | None
    p95_duration_ms: float | None
    total_input_tokens: int
    total_output_tokens: int
    by_execution_path: dict[str, dict[str, float | int]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _required_text(value: object, name: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise CalibrationError(f"{name} is required")
    return text


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


def load_gold_cases(path: str | Path) -> list[GoldCalibrationCase]:
    source = Path(path)
    payload = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("status") != "active":
        raise CalibrationError("Calibration gold corpus must be an active mapping")
    rubric = payload.get("rubric")
    if not isinstance(rubric, dict) or tuple(rubric.get("checks", [])) != VERIFICATION_CHECKS:
        raise CalibrationError("Calibration gold corpus must use the guarded verifier rubric")
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
        if not isinstance(gold_raw, dict) or not isinstance(deterministic, dict):
            raise CalibrationError(f"Calibration case {case_id} requires gold and deterministic mappings")
        rules = deterministic.get("rules", {})
        if not isinstance(rules, dict):
            raise CalibrationError(f"Calibration case {case_id} deterministic.rules must be a mapping")
        try:
            gold = LiveVerificationDecision.from_dict(gold_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(f"Calibration case {case_id}: {exc}") from exc
        cases.append(
            GoldCalibrationCase(
                case_id=case_id,
                category=_required_text(raw.get("category"), f"{case_id}.category"),
                task=_required_text(raw.get("task"), f"{case_id}.task"),
                candidate_output=str(raw.get("candidate_output") or ""),
                gold=gold,
                deterministic_complete=bool(deterministic.get("complete", False)),
                deterministic_rules=dict(rules),
            )
        )
    validate_gold_corpus(cases)
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
            raise CalibrationError(f"Calibration case {case.case_id} exact_lines must be a string list")
        checks["task_adherence"] = "pass" if lines == expected else "fail"

    if "line_count" in rules:
        expected_count = rules["line_count"]
        if isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 0:
            raise CalibrationError(f"Calibration case {case.case_id} line_count must be non-negative")
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


def validate_gold_corpus(cases: list[GoldCalibrationCase]) -> None:
    required_categories = {
        "correct",
        "subtly_wrong",
        "incomplete",
        "wrong_format",
        "unsupported_claim",
        "ambiguous",
        "unverifiable",
        "adversarial",
    }
    categories = {case.category for case in cases}
    missing = sorted(required_categories - categories)
    if missing:
        raise CalibrationError(
            "Calibration gold corpus is missing required categories: " + ", ".join(missing)
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
            raise CalibrationError(f"Calibration observation line {index} is invalid JSON") from exc
        if not isinstance(raw, dict):
            raise CalibrationError(f"Calibration observation line {index} must be an object")
        observations.append(CalibrationObservation.from_dict(raw))
    if not observations:
        raise CalibrationError("Calibration observations are empty")
    return observations


def evaluate_calibration(
    cases: list[GoldCalibrationCase],
    observations: list[CalibrationObservation],
) -> CalibrationReport:
    by_case = {case.case_id: case for case in cases}
    unknown = sorted({observation.case_id for observation in observations} - set(by_case))
    if unknown:
        raise CalibrationError("Observations reference unknown calibration cases: " + ", ".join(unknown))

    status_correct = 0
    false_pass = 0
    false_fail = 0
    missed_human = 0
    unnecessary_human = 0
    needs_human_predictions = 0
    criterion_correct = Counter()
    criterion_total = Counter()
    durations: list[float] = []
    total_input_tokens = 0
    total_output_tokens = 0
    repeatability: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    cross_verifier: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    path_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"observations": 0, "correct": 0})

    for observation in observations:
        gold = by_case[observation.case_id].gold
        predicted = observation.decision
        correct = predicted.status == gold.status
        status_correct += int(correct)
        false_pass += int(predicted.status == "passed" and gold.status != "passed")
        false_fail += int(predicted.status == "failed" and gold.status == "passed")
        missed_human += int(gold.status == "needs_human" and predicted.status != "needs_human")
        unnecessary_human += int(gold.status != "needs_human" and predicted.status == "needs_human")
        needs_human_predictions += int(predicted.status == "needs_human")

        for check in VERIFICATION_CHECKS:
            criterion_total[check] += 1
            criterion_correct[check] += int(predicted.verdicts[check] == gold.verdicts[check])

        if observation.duration_ms is not None:
            durations.append(observation.duration_ms)
        total_input_tokens += observation.input_tokens or 0
        total_output_tokens += observation.output_tokens or 0

        identity = (observation.case_id, observation.verifier_provider_family, observation.verifier_model)
        repeatability[identity].append(predicted.status)
        cross_verifier[observation.case_id].append(
            (observation.verifier_provider_family, observation.verifier_model, predicted.status)
        )

        if observation.execution_role == "fallback" or observation.fallback_used:
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
        repeatability_scores.append(max(counts.values()) / len(statuses))

    disagreement_cases: list[str] = []
    for case_id, results in cross_verifier.items():
        identities = {(provider, model) for provider, model, _ in results}
        statuses = {status for _, _, status in results}
        if len(identities) > 1 and len(statuses) > 1:
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
            "exact_status_accuracy": (
                counts["correct"] / observations_count if observations_count else 0.0
            ),
        }

    return CalibrationReport(
        total_gold_cases=len(cases),
        total_observations=total,
        exact_status_accuracy=status_correct / total,
        false_pass_count=false_pass,
        false_pass_rate=false_pass / total,
        false_fail_count=false_fail,
        false_fail_rate=false_fail / total,
        missed_human_count=missed_human,
        missed_human_rate=missed_human / total,
        unnecessary_human_count=unnecessary_human,
        unnecessary_human_rate=unnecessary_human / total,
        needs_human_prediction_rate=needs_human_predictions / total,
        criterion_accuracy=criterion_accuracy,
        repeatability_agreement_rate=(mean(repeatability_scores) if repeatability_scores else None),
        repeatability_groups=len(repeatability_scores),
        cross_verifier_disagreement_cases=sorted(disagreement_cases),
        average_duration_ms=(mean(durations) if durations else None),
        p95_duration_ms=_percentile(durations, 0.95) if durations else None,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        by_execution_path=by_execution_path,
    )


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise CalibrationError("Cannot calculate percentile of empty values")
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * percentile + 0.5)))
    return ordered[index]


def gold_summary(cases: list[GoldCalibrationCase]) -> dict[str, Any]:
    deterministic = [deterministic_validate(case) for case in cases]
    return {
        "status": "gold_corpus_valid",
        "case_count": len(cases),
        "categories": sorted({case.category for case in cases}),
        "deterministically_resolved_cases": sum(result.status is not None for result in deterministic),
        "semantic_or_human_cases": sum(result.status is None for result in deterministic),
        "quality_claims_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate TEO verifier calibration observations")
    parser.add_argument(
        "--gold",
        default="reference/datasets/verifier-calibration-gold.yaml",
        help="Gold-label calibration corpus",
    )
    parser.add_argument("--observations", help="JSONL verifier observations to evaluate")
    parser.add_argument("--output", help="Optional JSON report path")
    args = parser.parse_args(argv)

    try:
        cases = load_gold_cases(args.gold)
        report = (
            evaluate_calibration(cases, load_observations(args.observations)).to_dict()
            if args.observations
            else gold_summary(cases)
        )
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
