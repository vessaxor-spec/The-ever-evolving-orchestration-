from __future__ import annotations

import runpy
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "research" / "runtime" / "host_integration_freshness_binding.py"
FRESHNESS = runpy.run_path(str(HARNESS))
AuthorityOwnedBindingCatalog = FRESHNESS["AuthorityOwnedBindingCatalog"]
FreshnessStatus = FRESHNESS["FreshnessStatus"]
HistoricalBindingRecord = FRESHNESS["HistoricalBindingRecord"]
HistoricalDisposition = FRESHNESS["HistoricalDisposition"]
IntegrationFreshnessError = FRESHNESS["IntegrationFreshnessError"]
build_binding_snapshot = FRESHNESS["build_binding_snapshot"]
assess_host_binding = FRESHNESS["assess_host_binding"]
sha256_payload = FRESHNESS["_sha256_payload"]

MAIN_REVISION = "bff9991917af31b8a3b8bae7cc5f79a2deec65d2"


@pytest.fixture(scope="module")
def current_binding():
    return build_binding_snapshot(
        ROOT,
        release="v1.0.0",
        revision=MAIN_REVISION,
    )


def historical(binding, *, revision: str, **changes):
    return replace(binding, revision=revision, **changes)


def catalog_with_states(current_binding):
    compatible = historical(
        current_binding,
        revision="1" * 40,
        runtime_version="1.0.0",
    )
    update_available = historical(
        current_binding,
        revision="2" * 40,
        runtime_version="1.0.0.post1",
    )
    unsupported = historical(
        current_binding,
        revision="3" * 40,
        runtime_version="0.9.0",
    )
    return AuthorityOwnedBindingCatalog(
        current_binding,
        (
            HistoricalBindingRecord(
                compatible, HistoricalDisposition.COMPATIBLE
            ),
            HistoricalBindingRecord(
                update_available, HistoricalDisposition.UPDATE_AVAILABLE
            ),
            HistoricalBindingRecord(
                unsupported, HistoricalDisposition.UNSUPPORTED
            ),
        ),
    ), compatible, update_available, unsupported


def test_typed_date_scalar_does_not_collapse_to_same_text_string() -> None:
    assert sha256_payload(date(2026, 2, 16)) != sha256_payload("2026-02-16")


def test_current_binding_is_derived_from_executable_repository_truth(current_binding) -> None:
    assert current_binding.release == "v1.0.0"
    assert current_binding.runtime_version == "1.0.1.dev0"
    assert current_binding.revision == MAIN_REVISION
    payload = current_binding.to_dict()
    for field_name, value in payload.items():
        if field_name in {"release", "runtime_version", "revision"}:
            continue
        assert len(value) == 64
        int(value, 16)
    assert len(current_binding.binding_id) == 64


def test_exact_current_binding_classifies_as_pinned_current(current_binding) -> None:
    assessment = assess_host_binding(
        current_binding,
        AuthorityOwnedBindingCatalog(current_binding),
        claimed_status="PINNED_CURRENT",
    )

    assert assessment.status is FreshnessStatus.PINNED_CURRENT
    assert assessment.claim_matches is True
    assert assessment.acceptable is True


def test_exact_mapping_round_trip_preserves_current_status(current_binding) -> None:
    assessment = assess_host_binding(
        current_binding.to_dict(),
        AuthorityOwnedBindingCatalog(current_binding),
    )

    assert assessment.status is FreshnessStatus.PINNED_CURRENT
    assert assessment.binding_id == current_binding.binding_id


@pytest.mark.parametrize(
    ("field_name", "replacement"),
    [
        ("release", "v9.9.9"),
        ("runtime_version", "9.9.9"),
        ("authority_surface_fingerprint", "0" * 64),
        ("team_routing_fingerprint", "0" * 64),
        ("implementation_routing_fingerprint", "0" * 64),
        ("worker_registry_fingerprint", "0" * 64),
        ("specialist_registry_fingerprint", "0" * 64),
        ("capability_registry_fingerprint", "0" * 64),
        ("model_registry_fingerprint", "0" * 64),
        ("model_evidence_fingerprint", "0" * 64),
        ("executable_composition_id", "0" * 64),
    ],
)
def test_current_revision_with_any_bound_component_change_is_mismatched(
    current_binding, field_name: str, replacement: str
) -> None:
    tampered = replace(current_binding, **{field_name: replacement})
    assessment = assess_host_binding(
        tampered,
        AuthorityOwnedBindingCatalog(current_binding),
        claimed_status="PINNED_CURRENT",
    )

    assert assessment.status is FreshnessStatus.MISMATCHED
    assert assessment.claim_matches is False
    assert assessment.acceptable is False


def test_exact_authority_catalog_record_can_be_pinned_compatible(current_binding) -> None:
    catalog, compatible, _, _ = catalog_with_states(current_binding)
    assessment = assess_host_binding(
        compatible,
        catalog,
        claimed_status="PINNED_COMPATIBLE",
    )

    assert assessment.status is FreshnessStatus.PINNED_COMPATIBLE
    assert assessment.claim_matches is True
    assert assessment.acceptable is True


def test_exact_authority_catalog_record_can_report_update_available(current_binding) -> None:
    catalog, _, update_available, _ = catalog_with_states(current_binding)
    assessment = assess_host_binding(
        update_available,
        catalog,
        claimed_status="UPDATE_AVAILABLE",
    )

    assert assessment.status is FreshnessStatus.UPDATE_AVAILABLE
    assert assessment.claim_matches is True
    assert assessment.acceptable is True


def test_exact_authority_catalog_record_can_be_stale_unsupported(current_binding) -> None:
    catalog, _, _, unsupported = catalog_with_states(current_binding)
    assessment = assess_host_binding(
        unsupported,
        catalog,
        claimed_status="STALE_UNSUPPORTED",
    )

    assert assessment.status is FreshnessStatus.STALE_UNSUPPORTED
    assert assessment.claim_matches is True
    assert assessment.acceptable is False


def test_unknown_revision_cannot_self_classify_as_compatible(current_binding) -> None:
    unknown = historical(current_binding, revision="4" * 40)
    assessment = assess_host_binding(
        unknown,
        AuthorityOwnedBindingCatalog(current_binding),
        claimed_status="PINNED_COMPATIBLE",
    )

    assert assessment.status is FreshnessStatus.MISMATCHED
    assert assessment.claim_matches is False
    assert assessment.acceptable is False


def test_known_historical_revision_with_mixed_components_is_mismatched(current_binding) -> None:
    catalog, compatible, _, _ = catalog_with_states(current_binding)
    frankenstein = replace(
        compatible,
        specialist_registry_fingerprint="f" * 64,
    )
    assessment = assess_host_binding(
        frankenstein,
        catalog,
        claimed_status="PINNED_COMPATIBLE",
    )

    assert assessment.status is FreshnessStatus.MISMATCHED
    assert assessment.claim_matches is False
    assert assessment.acceptable is False


def test_host_claim_cannot_override_authority_owned_disposition(current_binding) -> None:
    catalog, compatible, _, _ = catalog_with_states(current_binding)
    assessment = assess_host_binding(
        compatible,
        catalog,
        claimed_status="PINNED_CURRENT",
    )

    assert assessment.status is FreshnessStatus.PINNED_COMPATIBLE
    assert assessment.claim_matches is False
    assert assessment.acceptable is False


def test_unknown_or_widening_binding_fields_are_rejected(current_binding) -> None:
    payload = current_binding.to_dict()
    payload["freshness_state"] = "PINNED_CURRENT"

    with pytest.raises(IntegrationFreshnessError, match="extra=freshness_state"):
        assess_host_binding(payload, AuthorityOwnedBindingCatalog(current_binding))


def test_missing_binding_field_is_rejected(current_binding) -> None:
    payload = current_binding.to_dict()
    del payload["executable_composition_id"]

    with pytest.raises(IntegrationFreshnessError, match="missing=executable_composition_id"):
        assess_host_binding(payload, AuthorityOwnedBindingCatalog(current_binding))


def test_malformed_digest_and_revision_fail_closed(current_binding) -> None:
    payload = current_binding.to_dict()
    payload["authority_surface_fingerprint"] = "not-a-digest"
    with pytest.raises(IntegrationFreshnessError, match="64 lowercase hexadecimal"):
        assess_host_binding(payload, AuthorityOwnedBindingCatalog(current_binding))

    payload = current_binding.to_dict()
    payload["revision"] = "not-a-commit"
    with pytest.raises(IntegrationFreshnessError, match="40-character"):
        assess_host_binding(payload, AuthorityOwnedBindingCatalog(current_binding))


def test_duplicate_historical_revision_is_rejected(current_binding) -> None:
    first = historical(current_binding, revision="5" * 40, runtime_version="1.0.0")
    second = historical(current_binding, revision="5" * 40, runtime_version="1.0.0.post1")

    with pytest.raises(IntegrationFreshnessError, match="duplicate revision"):
        AuthorityOwnedBindingCatalog(
            current_binding,
            (
                HistoricalBindingRecord(first, HistoricalDisposition.COMPATIBLE),
                HistoricalBindingRecord(second, HistoricalDisposition.UNSUPPORTED),
            ),
        )


def test_historical_catalog_rejects_wrong_binding_type(current_binding) -> None:
    malformed = HistoricalBindingRecord(
        "host-supplied-not-a-binding",
        HistoricalDisposition.COMPATIBLE,
    )

    with pytest.raises(IntegrationFreshnessError, match="historical binding"):
        AuthorityOwnedBindingCatalog(current_binding, (malformed,))


def test_historical_catalog_cannot_reuse_current_revision(current_binding) -> None:
    altered = replace(current_binding, runtime_version="1.0.0")

    with pytest.raises(IntegrationFreshnessError, match="reuse the current revision"):
        AuthorityOwnedBindingCatalog(
            current_binding,
            (HistoricalBindingRecord(altered, HistoricalDisposition.COMPATIBLE),),
        )


def test_invalid_claimed_freshness_label_is_rejected(current_binding) -> None:
    with pytest.raises(IntegrationFreshnessError, match="unknown claimed freshness"):
        assess_host_binding(
            current_binding,
            AuthorityOwnedBindingCatalog(current_binding),
            claimed_status="CURRENT_ENOUGH",
        )
