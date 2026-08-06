from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import yaml

MANDATED_REFUSAL = "refuse_consequential_claim"
MANDATED_CONFLICT = "escalate_and_present_conflict"
EXPECTED_PILOT = {
    "legal-operations",
    "tax-strategist",
    "loan-officer-assistant",
    "compliance-auditor",
    "civil-engineer",
    "embedded-engineer",
}


def parse_date(value: object, field: str) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"{field} must be an ISO date") from exc
    raise ValueError(f"{field} must be an ISO date")


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def load_registry(root: Path) -> dict[str, Any]:
    path = root / "policy" / "specialists" / "evidence-pilot.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("evidence pilot registry must be an object")
    return payload


def load_freshness_policy(root: Path) -> dict[str, Any]:
    path = root / "policy" / "specialists" / "freshness.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("freshness policy must be an object")
    return payload


def resolve_authority(url: str, expected_hosts: set[str], timeout: float = 20.0) -> str | None:
    request = Request(
        url,
        headers={
            "User-Agent": "TEO-evidence-validator/0.1 (+https://github.com/vessaxor-spec/The-ever-evolving-orchestration-)",
            "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.1",
            "Range": "bytes=0-1023",
        },
        method="GET",
    )
    with urlopen(request, timeout=timeout) as response:
        status = getattr(response, "status", 200)
        if status >= 400:
            return f"authority returned HTTP {status}: {url}"
        final_host = (urlparse(response.geturl()).hostname or "").lower()
        if final_host not in expected_hosts:
            return f"authority redirected to undeclared host {final_host}: {url}"
        response.read(1)
    return None


def validate_registry(
    registry: dict[str, Any],
    root: Path,
    *,
    as_of: dt.date | None = None,
    resolve: bool = False,
    resolver: Callable[[str, set[str]], str | None] = resolve_authority,
) -> list[str]:
    errors: list[str] = []
    as_of = as_of or dt.date.today()

    controls = registry.get("controls")
    if not isinstance(controls, dict):
        return ["controls must be an object"]

    required_controls = {
        "consequential_use_requires_unexpired_evidence": True,
        "high_and_critical_require_independent_verification": True,
        "stale_or_unavailable_behavior": MANDATED_REFUSAL,
        "conflicting_authorities_behavior": MANDATED_CONFLICT,
    }
    for key, expected in required_controls.items():
        if controls.get(key) != expected:
            errors.append(f"control {key} must remain {expected!r}")

    cadence = controls.get("source_resolution_cadence_days")
    if not isinstance(cadence, int) or isinstance(cadence, bool) or not 1 <= cadence <= 30:
        errors.append("source_resolution_cadence_days must be an integer from 1 to 30")

    specialists = registry.get("pilot_specialists")
    if not isinstance(specialists, dict):
        return errors + ["pilot_specialists must be an object"]

    actual_pilot = set(specialists)
    if actual_pilot != EXPECTED_PILOT:
        errors.append(
            "pilot scope must remain exactly the six regulated cards; "
            f"expected {sorted(EXPECTED_PILOT)}, got {sorted(actual_pilot)}"
        )

    freshness = load_freshness_policy(root)
    volatility = freshness.get("volatility_classes", {})
    if not isinstance(volatility, dict):
        return errors + ["freshness volatility_classes must be an object"]

    seen_claims: set[str] = set()
    for specialist, entry in specialists.items():
        prefix = specialist
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue

        card_path_value = entry.get("card_path")
        if not isinstance(card_path_value, str) or not card_path_value.startswith("community/specialists/"):
            errors.append(f"{prefix}: card_path must point into community/specialists")
            continue
        card_path = root / card_path_value
        if not card_path.is_file():
            errors.append(f"{prefix}: card_path does not exist")
        else:
            expected_sha = entry.get("canonical_blob_sha")
            actual_sha = git_blob_sha(card_path)
            if expected_sha != actual_sha:
                errors.append(
                    f"{prefix}: canonical card changed; expected blob {expected_sha}, got {actual_sha}"
                )

        risk_tier = entry.get("risk_tier")
        if risk_tier not in {"high", "critical"}:
            errors.append(f"{prefix}: pilot risk_tier must be high or critical")

        claims = entry.get("claims")
        if not isinstance(claims, list) or not claims:
            errors.append(f"{prefix}: claims must be a non-empty list")
            continue

        for index, claim in enumerate(claims):
            claim_prefix = f"{prefix}.claims[{index}]"
            if not isinstance(claim, dict):
                errors.append(f"{claim_prefix}: claim must be an object")
                continue

            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append(f"{claim_prefix}: id must be a non-empty string")
            elif claim_id in seen_claims:
                errors.append(f"{claim_prefix}: duplicate claim id {claim_id}")
            else:
                seen_claims.add(claim_id)

            statement = claim.get("statement")
            if not isinstance(statement, str) or len(statement.strip()) < 20:
                errors.append(f"{claim_prefix}: statement must be substantive")

            consequential = claim.get("consequential_use")
            if consequential is not True:
                errors.append(f"{claim_prefix}: pilot claims must declare consequential_use: true")

            applicability = claim.get("applicability")
            if not isinstance(applicability, dict):
                errors.append(f"{claim_prefix}: applicability must be an object")
            else:
                for field in ("jurisdiction", "scope"):
                    if not isinstance(applicability.get(field), str) or not applicability[field].strip():
                        errors.append(f"{claim_prefix}: applicability.{field} is required")

            class_name = claim.get("volatility_class")
            class_policy = volatility.get(class_name)
            if not isinstance(class_name, str) or not isinstance(class_policy, dict):
                errors.append(f"{claim_prefix}: unknown volatility_class {class_name!r}")
                max_age = None
            else:
                max_age = class_policy.get("maximum_evidence_age_days")
                if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 0:
                    errors.append(f"{claim_prefix}: volatility class has invalid maximum age")
                    max_age = None

            try:
                verified_at = parse_date(claim.get("verified_at"), f"{claim_prefix}.verified_at")
                expires_at = parse_date(claim.get("expires_at"), f"{claim_prefix}.expires_at")
            except ValueError as exc:
                errors.append(str(exc))
                verified_at = None
                expires_at = None

            if verified_at and expires_at:
                if verified_at > expires_at:
                    errors.append(f"{claim_prefix}: expires_at precedes verified_at")
                if max_age is not None and (expires_at - verified_at).days > max_age:
                    errors.append(
                        f"{claim_prefix}: evidence lifetime exceeds {max_age} days for {class_name}"
                    )
                if consequential and as_of > expires_at:
                    errors.append(f"{claim_prefix}: consequential evidence expired on {expires_at}")

            authority = claim.get("authority")
            if not isinstance(authority, dict):
                errors.append(f"{claim_prefix}: authority must be an object")
            else:
                if authority.get("tier") != 1:
                    errors.append(f"{claim_prefix}: consequential pilot evidence requires tier 1 authority")
                for field in ("organization", "source_type", "locator"):
                    if not isinstance(authority.get(field), str) or not authority[field].strip():
                        errors.append(f"{claim_prefix}: authority.{field} is required")
                url = authority.get("url")
                hosts = authority.get("expected_hosts")
                parsed_host = (urlparse(url).hostname or "").lower() if isinstance(url, str) else ""
                normalized_hosts = {
                    host.lower() for host in hosts if isinstance(host, str)
                } if isinstance(hosts, list) else set()
                if not isinstance(url, str) or urlparse(url).scheme != "https":
                    errors.append(f"{claim_prefix}: authority.url must use https")
                if not normalized_hosts or parsed_host not in normalized_hosts:
                    errors.append(f"{claim_prefix}: authority host must be explicitly declared")
                try:
                    parse_date(
                        authority.get("published_or_effective_at"),
                        f"{claim_prefix}.authority.published_or_effective_at",
                    )
                except ValueError as exc:
                    errors.append(str(exc))
                if resolve and isinstance(url, str) and normalized_hosts:
                    try:
                        resolution_error = resolver(url, normalized_hosts)
                    except Exception as exc:  # network failure is a validation failure in resolution CI
                        resolution_error = f"authority could not be resolved: {url}: {exc}"
                    if resolution_error:
                        errors.append(f"{claim_prefix}: {resolution_error}")

            verification = claim.get("verification")
            if not isinstance(verification, dict):
                errors.append(f"{claim_prefix}: verification must be an object")
            else:
                prepared_by = verification.get("prepared_by")
                verified_by = verification.get("verified_by")
                if verification.get("independent") is not True:
                    errors.append(f"{claim_prefix}: verification must remain independent")
                if not isinstance(prepared_by, str) or not isinstance(verified_by, str):
                    errors.append(f"{claim_prefix}: prepared_by and verified_by are required")
                elif prepared_by == verified_by:
                    errors.append(f"{claim_prefix}: verifier must differ from preparer")

            behavior = claim.get("required_behavior")
            if not isinstance(behavior, dict):
                errors.append(f"{claim_prefix}: required_behavior must be an object")
            else:
                if behavior.get("stale_or_unavailable") != MANDATED_REFUSAL:
                    errors.append(f"{claim_prefix}: stale evidence must require refusal")
                if behavior.get("conflict") != MANDATED_CONFLICT:
                    errors.append(f"{claim_prefix}: authoritative conflict must require escalation")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate regulated specialist evidence pilot")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--as-of", help="Validation date in YYYY-MM-DD format")
    parser.add_argument("--resolve", action="store_true", help="Resolve declared authority URLs")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    try:
        as_of = parse_date(args.as_of, "--as-of") if args.as_of else dt.date.today()
        errors = validate_registry(load_registry(root), root, as_of=as_of, resolve=args.resolve)
    except Exception as exc:
        print(f"evidence validation failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    mode = "structural and authority-resolution" if args.resolve else "structural"
    print(f"Regulated specialist evidence pilot passed {mode} validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
