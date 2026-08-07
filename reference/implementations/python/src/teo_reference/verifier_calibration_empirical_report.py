from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from .verifier_calibration import (
    CalibrationError,
    evaluate_calibration,
    load_calibration_policy,
    load_gold_cases,
)
from .verifier_calibration_empirical import (
    COLLECTION_ROLE,
    EmpiricalCalibrationObservation,
    build_human_gold_cases,
    evaluate_empirical_calibration,
    load_empirical_observations,
    load_empirical_policy,
    load_human_labels,
    validate_empirical_observations,
    validate_empirical_policy_against_base,
)


def _route_metrics(
    human_gold,
    observations: list[EmpiricalCalibrationObservation],
    base_policy,
) -> dict[str, dict[str, Any]]:
    by_route: dict[str, list[EmpiricalCalibrationObservation]] = {}
    for observation in observations:
        by_route.setdefault(observation.verifier_route, []).append(observation)

    metrics: dict[str, dict[str, Any]] = {}
    for route, route_observations in sorted(by_route.items()):
        report = evaluate_calibration(
            human_gold,
            [observation.to_base_observation() for observation in route_observations],
            policy=base_policy,
        ).to_dict()
        execution_paths = report.pop("by_execution_path")
        unexpected = sorted(set(execution_paths) - {"primary_no_retry"})
        if unexpected:
            raise CalibrationError(
                "Direct calibration produced unexpected execution-path metrics: "
                + ", ".join(unexpected)
            )
        report["by_collection_path"] = {
            COLLECTION_ROLE: execution_paths.get(
                "primary_no_retry",
                {"observations": 0, "exact_status_accuracy": 0.0},
            )
        }
        metrics[route] = report
    return metrics


def build_empirical_report(
    cases,
    labels,
    observations: list[EmpiricalCalibrationObservation],
    empirical_policy,
    base_policy,
) -> dict[str, Any]:
    human_gold = build_human_gold_cases(
        cases,
        labels,
        empirical_policy,
        base_policy,
    )
    validate_empirical_observations(
        cases,
        observations,
        labels,
        empirical_policy,
        base_policy,
    )
    report = evaluate_empirical_calibration(
        cases,
        labels,
        observations,
        empirical_policy,
        base_policy,
    )
    route_metrics = _route_metrics(human_gold, observations, base_policy)
    expected_routes = {route.route_id for route in empirical_policy.verifier_routes}
    if set(route_metrics) != expected_routes:
        report["evidence_readiness"]["data_requirements_met"] = False
    report["metrics_by_verifier_route"] = route_metrics
    report["route_specific_evidence_complete"] = set(route_metrics) == expected_routes
    report["authority"]["quality_claims_authorized"] = False
    report["authority"]["scope_expansion_authorized"] = False
    report["authority"]["routing_authority"] = False
    report["authority"]["automatic_route_update"] = False
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the route-specific TEO empirical verifier calibration report"
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--empirical-policy",
        default="policy/verification/verifier-calibration-empirical.yaml",
    )
    parser.add_argument("--human-labels", required=True)
    parser.add_argument("--observations", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    try:
        empirical = load_empirical_policy(root / args.empirical_policy)
        base = load_calibration_policy(root / empirical.base_policy_path)
        validate_empirical_policy_against_base(empirical, base)
        cases = load_gold_cases(root / empirical.control_corpus_path, policy=base)
        labels = load_human_labels(args.human_labels)
        observations = load_empirical_observations(args.observations)
        if not observations:
            raise CalibrationError("Empirical observations are empty")
        report = build_empirical_report(
            cases,
            labels,
            observations,
            empirical,
            base,
        )
    except (CalibrationError, OSError, yaml.YAMLError) as exc:
        parser.error(str(exc))
        return 2

    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
