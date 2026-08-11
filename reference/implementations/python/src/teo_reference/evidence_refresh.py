from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .evidence import EXPECTED_PILOT, git_blob_sha, load_registry, normalize_for_schema, parse_date

REFRESH_HISTORY_GLOB = "regulated-specialist-evidence-refresh-cycle-*.json"
REFRESH_HISTORY_DIR = Path("docs/history/validation")
REFRESH_SCHEMA = Path("reference/schemas/specialist-evidence-refresh-cycle.schema.json")


def load_refresh_schema(root: Path) -> dict[str, Any]:
    payload = json.loads((root / REFRESH_SCHEMA).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("refresh-cycle schema must be an object")
    Draft202012Validator.check_schema(payload)
    return payload


def load_refresh_records(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((root / REFRESH_HISTORY_DIR).glob(REFRESH_HISTORY_GLOB)):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError(f"refresh-cycle record must be an object: {path}")
        records.append((path, payload))
    return records


def _schema_errors(
    payload: dict[str, Any], schema: dict[str, Any], label: str
) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = sorted(
        validator.iter_errors(normalize_for_schema(payload)),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    errors: list[str] = []
    for failure in failures:
        location = ".".join(str(part) for part in failure.absolute_path) or "$"
        errors.append(f"{label}: schema {location}: {failure.message}")
    return errors


def _active_claims(registry: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    result: dict[str, tuple[str, dict[str, Any]]] = {}
    specialists = registry.get("pilot_specialists", {})
    if not isinstance(specialists, dict):
        return result
    for specialist, entry in specialists.items():
        if not isinstance(entry, dict):
            continue
        claims = entry.get("claims", [])
        if not isinstance(claims, list):
            continue
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("id")
            if isinstance(claim_id, str) and claim_id:
                result[claim_id] = (specialist, claim)
    return result


def validate_refresh_history(root: Path) -> list[str]:
    errors: list[str] = []
    registry = load_registry(root)
    schema = load_refresh_schema(root)
    records = load_refresh_records(root)

    if not records:
        return ["regulated evidence pilot has no completed refresh-cycle history"]

    previous_date: dt.date | None = None
    previous_registry_after: str | None = None
    for expected_sequence, (path, record) in enumerate(records, start=1):
        label = path.relative_to(root).as_posix()
        errors.extend(_schema_errors(record, schema, label))

        if record.get("sequence") != expected_sequence:
            errors.append(
                f"{label}: refresh-cycle sequence must be contiguous; "
                f"expected {expected_sequence}, got {record.get('sequence')!r}"
            )
        expected_cycle_id = f"regulated-specialist-evidence-refresh-cycle-{expected_sequence:04d}"
        if record.get("cycle_id") != expected_cycle_id:
            errors.append(
                f"{label}: cycle_id must match sequence {expected_sequence}: {expected_cycle_id}"
            )

        if (
            previous_registry_after is not None
            and record.get("registry_before_blob_sha") != previous_registry_after
        ):
            errors.append(
                f"{label}: registry_before_blob_sha must equal the prior cycle registry_after_blob_sha"
            )
        registry_after = record.get("registry_after_blob_sha")
        if isinstance(registry_after, str):
            previous_registry_after = registry_after

        try:
            performed_at = parse_date(record.get("performed_at"), f"{label}.performed_at")
        except ValueError as exc:
            errors.append(str(exc))
            performed_at = None
        if performed_at is not None and previous_date is not None and performed_at <= previous_date:
            errors.append(f"{label}: refresh cycles must advance strictly in date order")
        if performed_at is not None:
            previous_date = performed_at

        specialists = record.get("pilot_specialists")
        if isinstance(specialists, list):
            normalized_specialists = {
                specialist for specialist in specialists if isinstance(specialist, str)
            }
            if normalized_specialists != EXPECTED_PILOT or len(specialists) != len(EXPECTED_PILOT):
                errors.append(f"{label}: refresh cycle must cover the exact six-card pilot")

        reviews = record.get("claims_reviewed")
        if not isinstance(reviews, list):
            continue
        review_ids: list[str] = []
        for index, review in enumerate(reviews):
            if not isinstance(review, dict):
                continue
            claim_id = review.get("claim_id")
            if isinstance(claim_id, str):
                review_ids.append(claim_id)
            ownership = review.get("ownership")
            if isinstance(ownership, dict):
                prepared_by = ownership.get("prepared_by")
                verified_by = ownership.get("verified_by")
                if prepared_by == verified_by:
                    errors.append(
                        f"{label}.claims_reviewed[{index}]: verifier must differ from preparer"
                    )
        if len(review_ids) != len(set(review_ids)):
            errors.append(f"{label}: claim reviews must not contain duplicate claim IDs")

        summary = record.get("maintenance_summary")
        if isinstance(summary, dict):
            resolved = sum(
                1
                for review in reviews
                if isinstance(review, dict) and review.get("resolution_status") == "resolved"
            )
            reaffirmed = sum(
                1
                for review in reviews
                if isinstance(review, dict) and review.get("outcome") == "reaffirmed"
            )
            amended = sum(
                1
                for review in reviews
                if isinstance(review, dict) and review.get("outcome") == "amended"
            )
            moved = sum(
                1
                for review in reviews
                if isinstance(review, dict) and review.get("outcome") == "authority_moved"
            )
            conflicts = sum(
                1
                for review in reviews
                if isinstance(review, dict) and review.get("resolution_status") == "conflict"
            )
            expected_counts = {
                "claims_reviewed": len(reviews),
                "authorities_resolved": resolved,
                "claims_reaffirmed": reaffirmed,
                "claims_amended": amended,
                "authorities_moved": moved,
                "authority_conflicts": conflicts,
            }
            for key, expected in expected_counts.items():
                if summary.get(key) != expected:
                    errors.append(
                        f"{label}: maintenance_summary.{key} must equal observed count {expected}"
                    )

        gate = record.get("expansion_gate")
        if isinstance(gate, dict):
            if gate.get("refresh_cycles_completed") != expected_sequence:
                errors.append(
                    f"{label}: expansion_gate.refresh_cycles_completed must equal cycle sequence"
                )
            controlled_type = gate.get("controlled_change_type")
            controlled_handled = gate.get("controlled_change_handled")
            if controlled_handled != (controlled_type != "none"):
                errors.append(
                    f"{label}: controlled_change_handled must match controlled_change_type"
                )
            required = gate.get("refresh_cycles_required")
            expansion_authorized = gate.get("expansion_authorized")
            if isinstance(required, int) and expected_sequence < required and expansion_authorized is True:
                errors.append(
                    f"{label}: expansion cannot be authorized before required refresh cycles complete"
                )
            if expansion_authorized is True and not all(
                (
                    gate.get("stable_authority_resolution_gate_satisfied") is True,
                    gate.get("controlled_change_handled") is True,
                    gate.get("next_batch_approved") is True,
                )
            ):
                errors.append(f"{label}: expansion authorization requires every declared gate")

    latest_path, latest = records[-1]
    latest_label = latest_path.relative_to(root).as_posix()
    registry_path = root / "policy/specialists/evidence-pilot.yaml"
    if latest.get("registry_after_blob_sha") != git_blob_sha(registry_path):
        errors.append(f"{latest_label}: registry_after_blob_sha must bind current active registry")

    try:
        reviewed_at = parse_date(registry.get("reviewed_at"), "evidence-pilot.reviewed_at")
        performed_at = parse_date(latest.get("performed_at"), f"{latest_label}.performed_at")
        if reviewed_at != performed_at:
            errors.append(f"{latest_label}: latest cycle date must equal active registry reviewed_at")
    except ValueError as exc:
        errors.append(str(exc))

    active_claims = _active_claims(registry)
    latest_reviews = latest.get("claims_reviewed")
    if isinstance(latest_reviews, list):
        latest_by_id = {
            review.get("claim_id"): review
            for review in latest_reviews
            if isinstance(review, dict) and isinstance(review.get("claim_id"), str)
        }
        if set(latest_by_id) != set(active_claims):
            errors.append(
                f"{latest_label}: latest refresh must cover every and only active pilot claim"
            )
        for claim_id, (specialist, claim) in active_claims.items():
            review = latest_by_id.get(claim_id)
            if not isinstance(review, dict):
                continue
            if review.get("specialist") != specialist:
                errors.append(f"{latest_label}: {claim_id} specialist binding drifted")
            authority = claim.get("authority")
            if isinstance(authority, dict):
                for active_key, review_key in (
                    ("url", "authority_url"),
                    ("source_date_basis", "source_date_basis"),
                ):
                    if review.get(review_key) != authority.get(active_key):
                        errors.append(
                            f"{latest_label}: {claim_id} {review_key} does not match active evidence"
                        )
                try:
                    active_source_date = parse_date(
                        authority.get("source_date"), f"{claim_id}.authority.source_date"
                    ).isoformat()
                except ValueError as exc:
                    errors.append(str(exc))
                else:
                    if review.get("source_date") != active_source_date:
                        errors.append(
                            f"{latest_label}: {claim_id} source_date does not match active evidence"
                        )
            verification = claim.get("verification")
            ownership = review.get("ownership")
            if isinstance(verification, dict) and isinstance(ownership, dict):
                for key in ("prepared_by", "verified_by", "independent"):
                    if ownership.get(key) != verification.get(key):
                        errors.append(
                            f"{latest_label}: {claim_id} ownership.{key} does not match active evidence"
                        )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate regulated evidence refresh-cycle history")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    try:
        errors = validate_refresh_history(root)
    except Exception as exc:
        print(f"refresh-history validation failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Regulated specialist evidence refresh history passed validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
