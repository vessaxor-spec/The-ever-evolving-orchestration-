from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from teo_reference.evidence_refresh import load_refresh_records, validate_refresh_history

ROOT = Path(__file__).resolve().parents[1]
CYCLE_ONE_NAME = "regulated-specialist-evidence-refresh-cycle-2026-08-11.json"
CYCLE_TWO_NAME = "regulated-specialist-evidence-refresh-cycle-2026-08-16.json"
RECORD_NAMES = (CYCLE_ONE_NAME, CYCLE_TWO_NAME)


def _copy_refresh_fixture(tmp_path: Path) -> Path:
    relatives = [
        Path("policy/specialists/evidence-pilot.yaml"),
        Path("reference/schemas/specialist-evidence-refresh-cycle.schema.json"),
    ]
    relatives.extend(Path("docs/history/validation") / name for name in RECORD_NAMES)
    for relative in relatives:
        source = ROOT / relative
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return tmp_path


def _record_path(root: Path, name: str = CYCLE_TWO_NAME) -> Path:
    return root / "docs/history/validation" / name


def test_refresh_history_is_valid_and_bound_to_active_registry() -> None:
    errors = validate_refresh_history(ROOT)
    assert errors == []

    records = load_refresh_records(ROOT)
    assert len(records) == 2
    _, cycle_one = records[0]
    _, cycle_two = records[1]

    assert cycle_one["sequence"] == 1
    assert cycle_one["status"] == "completed"
    assert cycle_one["performed_at"] == "2026-08-11"
    assert cycle_one["maintenance_summary"] == {
        "claims_reviewed": 7,
        "authorities_resolved": 7,
        "claims_reaffirmed": 6,
        "claims_amended": 1,
        "authorities_moved": 0,
        "authority_conflicts": 0,
        "specialist_cards_changed": 0,
    }
    assert cycle_one["expansion_gate"]["refresh_cycles_completed"] == 1
    assert cycle_one["expansion_gate"]["refresh_cycles_required"] == 2
    assert cycle_one["expansion_gate"]["expansion_authorized"] is False

    assert cycle_two["sequence"] == 2
    assert cycle_two["status"] == "completed"
    assert cycle_two["performed_at"] == "2026-08-16"
    assert cycle_two["registry_before_blob_sha"] == cycle_one["registry_after_blob_sha"]
    assert cycle_two["maintenance_summary"] == {
        "claims_reviewed": 7,
        "authorities_resolved": 7,
        "claims_reaffirmed": 6,
        "claims_amended": 0,
        "authorities_moved": 1,
        "authority_conflicts": 0,
        "specialist_cards_changed": 0,
    }
    assert cycle_two["expansion_gate"]["refresh_cycles_completed"] == 2
    assert cycle_two["expansion_gate"]["refresh_cycles_required"] == 2
    assert cycle_two["expansion_gate"]["stable_authority_resolution_gate_satisfied"] is False
    assert cycle_two["expansion_gate"]["next_batch_approved"] is False
    assert cycle_two["expansion_gate"]["expansion_authorized"] is False

    embedded = next(
        review
        for review in cycle_two["claims_reviewed"]
        if review["claim_id"] == "embedded-c-language-current-standard"
    )
    assert embedded["outcome"] == "authority_moved"
    assert embedded["authority_url"] == "https://committee.iso.org/ru/standard/82075.html"
    assert embedded["statement_changed"] is False
    assert cycle_two["expansion_gate"]["controlled_change_handled"] is True
    assert cycle_two["expansion_gate"]["controlled_change_type"] == "authority_move"


def test_cycle_one_covers_all_seven_claims_and_records_controlled_amendment() -> None:
    _, cycle = load_refresh_records(ROOT)[0]
    reviews = cycle["claims_reviewed"]
    assert len(reviews) == 7
    assert len({review["claim_id"] for review in reviews}) == 7

    legal = next(
        review
        for review in reviews
        if review["claim_id"] == "legal-us-frcp-37e-preservation"
    )
    assert legal["outcome"] == "amended"
    assert legal["statement_changed"] is True
    assert cycle["expansion_gate"]["controlled_change_handled"] is True
    assert cycle["expansion_gate"]["controlled_change_type"] == "claim_amendment"


def test_active_registry_reflects_cycle_two_dates_authority_and_rule_37e() -> None:
    registry = yaml.safe_load(
        (ROOT / "policy/specialists/evidence-pilot.yaml").read_text(encoding="utf-8")
    )
    assert registry["reviewed_at"].isoformat() == "2026-08-16"

    legal = registry["pilot_specialists"]["legal-operations"]["claims"][0]
    assert "cannot be restored or replaced through additional discovery" in legal["statement"]

    embedded = registry["pilot_specialists"]["embedded-engineer"]["claims"][0]
    assert embedded["authority"]["url"] == "https://committee.iso.org/ru/standard/82075.html"
    assert embedded["authority"]["expected_hosts"] == ["committee.iso.org"]

    for specialist, entry in registry["pilot_specialists"].items():
        for claim in entry["claims"]:
            assert claim["verified_at"].isoformat() == "2026-08-16", specialist
            expected_expiry = (
                "2026-09-15"
                if claim["volatility_class"] == "fast_moving"
                else "2026-11-14"
            )
            assert claim["expires_at"].isoformat() == expected_expiry, claim["id"]


def test_forged_registry_binding_is_rejected(tmp_path: Path) -> None:
    root = _copy_refresh_fixture(tmp_path)
    record_path = _record_path(root)
    cycle = json.loads(record_path.read_text(encoding="utf-8"))
    cycle["registry_after_blob_sha"] = "0" * 40
    record_path.write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")

    errors = validate_refresh_history(root)
    assert any("registry_after_blob_sha must bind current active registry" in error for error in errors)


def test_expansion_authorization_without_remaining_gates_is_rejected(tmp_path: Path) -> None:
    root = _copy_refresh_fixture(tmp_path)
    record_path = _record_path(root)
    cycle = json.loads(record_path.read_text(encoding="utf-8"))
    cycle["expansion_gate"]["expansion_authorized"] = True
    record_path.write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")

    errors = validate_refresh_history(root)
    assert any("expansion authorization requires every declared gate" in error for error in errors)


def test_missing_claim_review_is_rejected(tmp_path: Path) -> None:
    root = _copy_refresh_fixture(tmp_path)
    record_path = _record_path(root)
    cycle = json.loads(record_path.read_text(encoding="utf-8"))
    cycle["claims_reviewed"].pop()
    cycle["maintenance_summary"]["claims_reviewed"] = 6
    cycle["maintenance_summary"]["authorities_resolved"] = 6
    cycle["maintenance_summary"]["claims_reaffirmed"] = 5
    record_path.write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")

    errors = validate_refresh_history(root)
    assert any("latest refresh must cover every and only active pilot claim" in error for error in errors)


def test_refresh_registry_hash_chain_is_enforced(tmp_path: Path) -> None:
    root = _copy_refresh_fixture(tmp_path)
    record_path = _record_path(root)
    cycle = json.loads(record_path.read_text(encoding="utf-8"))
    cycle["registry_before_blob_sha"] = "f" * 40
    record_path.write_text(json.dumps(cycle, indent=2) + "\n", encoding="utf-8")

    errors = validate_refresh_history(root)
    assert any(
        "registry_before_blob_sha must equal the prior cycle registry_after_blob_sha" in error
        for error in errors
    )
