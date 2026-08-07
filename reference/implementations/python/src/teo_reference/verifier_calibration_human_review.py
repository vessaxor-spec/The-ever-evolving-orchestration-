from __future__ import annotations

import argparse
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from .verification_adapter import LiveVerificationDecision, LiveVerificationError
from .verifier_calibration import CalibrationError, load_calibration_policy, load_gold_cases
from .verifier_calibration_empirical import load_empirical_policy


CHECKS = [
    {
        "id": "output_present",
        "description": "Output is present and usable.",
    },
    {
        "id": "task_adherence",
        "description": "Output follows the observable instructions in the task.",
    },
    {
        "id": "format_consistency",
        "description": "Output structure is internally consistent with the requested work.",
    },
    {
        "id": "unsupported_claims_absent",
        "description": "Output does not claim completion, correctness, or evidence unsupported by the supplied task and output.",
    },
]
STATUS_PRECEDENCE = [
    "any_fail_means_failed",
    "otherwise_any_uncertain_means_needs_human",
    "otherwise_passed",
]


@dataclass(frozen=True, slots=True)
class BlindedReviewLabel:
    review_item_id: str
    reviewer_id: str
    reviewer_role: str
    reviewed_at: str
    rubric_version: str
    observations_blinded: bool
    reference_control_labels_blinded: bool
    decision: LiveVerificationDecision

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "BlindedReviewLabel":
        expected = {
            "review_item_id",
            "reviewer_id",
            "reviewer_role",
            "reviewed_at",
            "rubric_version",
            "observations_blinded",
            "reference_control_labels_blinded",
            "decision",
        }
        if set(raw) != expected:
            missing = sorted(expected - set(raw))
            unknown = sorted(set(raw) - expected)
            details = []
            if missing:
                details.append("missing=" + ",".join(missing))
            if unknown:
                details.append("unknown=" + ",".join(unknown))
            raise CalibrationError("Blinded review label fields are invalid: " + " ".join(details))
        if raw["reviewer_role"] not in {"reviewer", "adjudicator"}:
            raise CalibrationError("Blinded review label reviewer_role is invalid")
        if raw["observations_blinded"] is not True:
            raise CalibrationError("Reviewer must be blinded from model observations")
        if raw["reference_control_labels_blinded"] is not True:
            raise CalibrationError("Reviewer must be blinded from reference-control labels")
        decision_raw = raw["decision"]
        if not isinstance(decision_raw, dict):
            raise CalibrationError("Blinded review label decision must be an object")
        try:
            decision = LiveVerificationDecision.from_dict(decision_raw)
        except LiveVerificationError as exc:
            raise CalibrationError(str(exc)) from exc
        return cls(
            review_item_id=_text(raw["review_item_id"], "review_item_id"),
            reviewer_id=_text(raw["reviewer_id"], "reviewer_id"),
            reviewer_role=_text(raw["reviewer_role"], "reviewer_role"),
            reviewed_at=_text(raw["reviewed_at"], "reviewed_at"),
            rubric_version=_text(raw["rubric_version"], "rubric_version"),
            observations_blinded=True,
            reference_control_labels_blinded=True,
            decision=decision,
        )


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CalibrationError(f"{name} must be a non-empty string")
    return value.strip()


def _decision_dict(decision: LiveVerificationDecision) -> dict[str, str]:
    return {
        "status": decision.status,
        "output_present": decision.output_present,
        "task_adherence": decision.task_adherence,
        "format_consistency": decision.format_consistency,
        "unsupported_claims_absent": decision.unsupported_claims_absent,
        "human_reason": decision.human_reason,
    }


def build_review_materials(
    cases,
    rubric_version: str,
    *,
    token_factory: Callable[[], str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    make_token = token_factory or (lambda: secrets.token_hex(8))
    packet_id = "packet-" + _text(make_token(), "packet token")
    pairs = []
    used: set[str] = set()
    for case in cases:
        review_id = "item-" + _text(make_token(), "review item token")
        if review_id in used:
            raise CalibrationError("Blinded review item tokens must be unique")
        used.add(review_id)
        pairs.append((review_id, case))
    pairs.sort(key=lambda item: item[0])

    packet = {
        "packet_id": packet_id,
        "rubric_version": rubric_version,
        "checks": CHECKS,
        "status_precedence": STATUS_PRECEDENCE,
        "items": [
            {
                "review_item_id": review_id,
                "task": case.task,
                "candidate_output": case.candidate_output,
            }
            for review_id, case in pairs
        ],
    }
    private_map = {
        "packet_id": packet_id,
        "rubric_version": rubric_version,
        "items": [
            {"review_item_id": review_id, "case_id": case.case_id}
            for review_id, case in pairs
        ],
    }
    validate_review_packet_is_blinded(packet)
    return packet, private_map


def validate_review_packet_is_blinded(packet: dict[str, Any]) -> None:
    forbidden = {"case_id", "category", "gold", "deterministic"}
    for item in packet.get("items", []):
        if not isinstance(item, dict):
            raise CalibrationError("Review packet item must be an object")
        leaked = sorted(forbidden & set(item))
        if leaked:
            raise CalibrationError(
                "Review packet leaks reference-control fields: " + ", ".join(leaked)
            )


def load_blinded_labels(paths: list[str | Path]) -> list[BlindedReviewLabel]:
    labels: list[BlindedReviewLabel] = []
    for source_value in paths:
        source = Path(source_value)
        try:
            lines = source.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise CalibrationError(f"Blinded review labels could not be read: {source}") from exc
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise CalibrationError(
                    f"Blinded review label {source}:{index} is invalid JSON"
                ) from exc
            if not isinstance(raw, dict):
                raise CalibrationError(
                    f"Blinded review label {source}:{index} must be an object"
                )
            labels.append(BlindedReviewLabel.from_dict(raw))
    if not labels:
        raise CalibrationError("Blinded review labels are empty")
    return labels


def normalize_blinded_labels(
    private_map: dict[str, Any],
    labels: list[BlindedReviewLabel],
) -> list[dict[str, Any]]:
    packet_id = _text(private_map.get("packet_id"), "packet_id")
    rubric_version = _text(private_map.get("rubric_version"), "rubric_version")
    items = private_map.get("items")
    if not isinstance(items, list) or not items:
        raise CalibrationError("Private review map requires items")
    alias_to_case: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {"review_item_id", "case_id"}:
            raise CalibrationError("Private review map item is invalid")
        review_id = _text(item["review_item_id"], "review_item_id")
        if review_id in alias_to_case:
            raise CalibrationError("Private review map contains duplicate review_item_id")
        alias_to_case[review_id] = _text(item["case_id"], "case_id")

    normalized = []
    for label in labels:
        case_id = alias_to_case.get(label.review_item_id)
        if case_id is None:
            raise CalibrationError(
                f"Blinded label references unknown review item {label.review_item_id}"
            )
        if label.rubric_version != rubric_version:
            raise CalibrationError("Blinded review label rubric version does not match packet")
        normalized.append(
            {
                "case_id": case_id,
                "reviewer_id": label.reviewer_id,
                "reviewer_role": label.reviewer_role,
                "reviewed_at": label.reviewed_at,
                "rubric_version": label.rubric_version,
                "observations_blinded": True,
                "decision": _decision_dict(label.decision),
            }
        )
    return normalized


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create blinded human-review materials for TEO verifier calibration"
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--empirical-policy",
        default="policy/verification/verifier-calibration-empirical.yaml",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    packet_parser = subparsers.add_parser("packet")
    packet_parser.add_argument("--packet-out")
    packet_parser.add_argument("--map-out")

    normalize_parser = subparsers.add_parser("normalize")
    normalize_parser.add_argument("--mapping", required=True)
    normalize_parser.add_argument("--raw-labels", action="append", required=True)
    normalize_parser.add_argument("--output", required=True)

    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    try:
        empirical = load_empirical_policy(root / args.empirical_policy)
        raw_policy = yaml.safe_load((root / args.empirical_policy).read_text(encoding="utf-8"))
        human_policy = raw_policy.get("human_labeling") if isinstance(raw_policy, dict) else None
        if not isinstance(human_policy, dict) or human_policy.get(
            "reviewers_blinded_from_reference_control_labels"
        ) is not True:
            raise CalibrationError(
                "Empirical policy must require blinding from reference-control labels"
            )
        base = load_calibration_policy(root / empirical.base_policy_path)
        cases = load_gold_cases(root / empirical.control_corpus_path, policy=base)

        if args.command == "packet":
            packet, private_map = build_review_materials(
                cases,
                empirical.rubric_version,
            )
            packet_out = Path(
                args.packet_out
                or root / human_policy["default_review_packet_path"]
            )
            map_out = Path(
                args.map_out
                or root / ".teo/runtime/verifier-calibration/human-review-map.json"
            )
            _write_json(packet_out, packet)
            _write_json(map_out, private_map)
            result = {
                "packet_id": packet["packet_id"],
                "item_count": len(packet["items"]),
                "packet_path": str(packet_out),
                "private_map_path": str(map_out),
                "reference_control_labels_exposed": False,
                "model_observations_exposed": False,
            }
        else:
            private_map = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
            if not isinstance(private_map, dict):
                raise CalibrationError("Private review map must be an object")
            labels = load_blinded_labels(args.raw_labels)
            normalized = normalize_blinded_labels(private_map, labels)
            _write_jsonl(Path(args.output), normalized)
            result = {
                "normalized_label_count": len(normalized),
                "output": args.output,
                "source_packet_id": private_map.get("packet_id"),
                "reference_control_labels_blinded": True,
                "model_observations_blinded": True,
            }
    except (CalibrationError, OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
