from __future__ import annotations

import copy
import datetime as dt
from pathlib import Path
from typing import Any, Callable

import pytest

from teo_reference.evidence import EXPECTED_PILOT, load_registry, validate_registry

ROOT = Path(__file__).resolve().parents[1]
AS_OF = dt.date(2026, 8, 6)


def test_regulated_evidence_pilot_is_valid_and_scoped() -> None:
    registry = load_registry(ROOT)
    errors = validate_registry(registry, ROOT, as_of=AS_OF)

    assert errors == []
    assert set(registry["pilot_specialists"]) == EXPECTED_PILOT
    assert len(registry["pilot_specialists"]) == 6


def test_every_pilot_card_has_dated_authoritative_claims() -> None:
    registry = load_registry(ROOT)

    for specialist, entry in registry["pilot_specialists"].items():
        assert entry["claims"], specialist
        for claim in entry["claims"]:
            authority = claim["authority"]
            assert claim["consequential_use"] is True
            assert authority["tier"] == 1
            assert authority["url"].startswith("https://")
            assert authority["source_date_basis"] in {
                "published",
                "effective",
                "last_updated",
                "observed",
            }
            assert authority["source_date"]
            assert claim["verified_at"]
            assert claim["expires_at"]
            assert claim["applicability"]["jurisdiction"]
            assert claim["applicability"]["scope"]


def test_schema_rejects_unknown_evidence_fields() -> None:
    mutant = copy.deepcopy(load_registry(ROOT))
    claim = mutant["pilot_specialists"]["legal-operations"]["claims"][0]
    claim["unsupported_field"] = True

    errors = validate_registry(mutant, ROOT, as_of=AS_OF)

    assert any(
        "Additional properties are not allowed" in error and "unsupported_field" in error
        for error in errors
    )


def test_authority_resolution_path_checks_every_declared_source_without_live_network() -> None:
    registry = load_registry(ROOT)
    resolved: list[str] = []

    def resolver(url: str, expected_hosts: set[str]) -> str | None:
        resolved.append(url)
        assert expected_hosts
        return None

    errors = validate_registry(registry, ROOT, as_of=AS_OF, resolve=True, resolver=resolver)

    assert errors == []
    expected_urls = sum(
        len(entry["claims"]) for entry in registry["pilot_specialists"].values()
    )
    assert len(resolved) == expected_urls


def weaken_expiry(registry: dict[str, Any]) -> None:
    claim = registry["pilot_specialists"]["loan-officer-assistant"]["claims"][0]
    claim["expires_at"] = dt.date(2026, 8, 5)


def weaken_verification_independence(registry: dict[str, Any]) -> None:
    verification = registry["pilot_specialists"]["compliance-auditor"]["claims"][0][
        "verification"
    ]
    verification["independent"] = False
    verification["verified_by"] = verification["prepared_by"]


def weaken_refusal_behavior(registry: dict[str, Any]) -> None:
    registry["controls"]["stale_or_unavailable_behavior"] = "warn_and_continue"
    for entry in registry["pilot_specialists"].values():
        for claim in entry["claims"]:
            claim["required_behavior"]["stale_or_unavailable"] = "warn_and_continue"


@pytest.mark.parametrize(
    ("mutator", "expected_error"),
    [
        (weaken_expiry, "consequential evidence expired"),
        (weaken_verification_independence, "verification must remain independent"),
        (weaken_refusal_behavior, "must remain 'refuse_consequential_claim'"),
    ],
)
def test_control_weakening_mutants_are_killed(
    mutator: Callable[[dict[str, Any]], None], expected_error: str
) -> None:
    mutant = copy.deepcopy(load_registry(ROOT))
    mutator(mutant)

    errors = validate_registry(mutant, ROOT, as_of=AS_OF)

    assert errors, "a weakened control survived the evidence contract suite"
    assert any(expected_error in error for error in errors)


def test_expiry_cannot_be_extended_beyond_volatility_policy() -> None:
    mutant = copy.deepcopy(load_registry(ROOT))
    claim = mutant["pilot_specialists"]["loan-officer-assistant"]["claims"][0]
    claim["expires_at"] = dt.date(2026, 12, 31)

    errors = validate_registry(mutant, ROOT, as_of=AS_OF)

    assert any("evidence lifetime exceeds 30 days" in error for error in errors)
