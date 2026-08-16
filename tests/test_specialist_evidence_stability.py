import copy
import datetime as dt
from pathlib import Path

from teo_reference.evidence import load_registry
from teo_reference.evidence_stability import (
    REQUIRED_MUTATIONS,
    load_qualification_policy,
    run_stability_qualification,
    validate_qualification_policy,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EXTERNAL_NETWORK_OBSERVATION = {
    "workflow": "ISO Resolution Probe",
    "run_number": 5,
    "run_id": 31961987236,
    "head_sha": "633a8572b6417c3f61ff3baba67bfbb5534bf604",
    "conclusion": "success",
    "resolved_authorities": 7,
    "runner": "ubuntu-24.04",
    "purpose": "unchanged production evidence resolver after the ISO authority repair",
}


def test_regulated_evidence_stability_qualification_passes_current_pilot() -> None:
    result = run_stability_qualification(
        REPO_ROOT,
        as_of=dt.date(2026, 8, 16),
        external_network_observation=EXTERNAL_NETWORK_OBSERVATION,
    )

    assert result["qualified"] is True
    assert result["baseline_claim_count"] == 7
    assert len(result["clean_resolution_replays"]) == 5
    assert all(item["passed"] for item in result["clean_resolution_replays"])
    assert all(
        item["resolved_authorities"] == 7
        and len(item["observations"]) == 7
        for item in result["clean_resolution_replays"]
    )
    assert result["repeatability"]["runs"] == 3
    assert result["repeatability"]["passed"] is True
    assert len(result["repeatability"]["results"]) == 3
    assert len(result["repeatability"]["digests"]) == 3
    assert len(set(result["repeatability"]["digests"])) == 1
    assert all(
        item["passed"]
        and item["resolved_authorities"] == 7
        and len(item["observations"]) == 7
        for item in result["repeatability"]["results"]
    )
    assert (
        result["mutations_killed"]
        == result["mutations_total"]
        == len(REQUIRED_MUTATIONS)
        == 15
    )
    assert result["controlled_authority_move"]["passed"] is True
    assert result["external_network_errors"] == []
    assert result["continuous_monitoring"] == {
        "source_resolution_cadence_days": 7,
        "calendar_wait_gate": False,
    }
    assert result["expansion_authority"] == {
        "explicit_next_batch_approval_required": True,
        "expansion_auto_authorized": False,
    }

    calls = 0

    def unstable_resolver(_url: str, _expected_hosts: set[str]) -> str | None:
        nonlocal calls
        calls += 1
        # Five clean replays consume calls 1-35. Repeatability run 1 consumes
        # 36-42. Inject one failure into repeatability run 2 to prove the
        # qualification actually re-executes instead of re-hashing one result.
        if calls == 43:
            return "authority could not be resolved: repeatability canary"
        return None

    unstable = run_stability_qualification(
        REPO_ROOT,
        as_of=dt.date(2026, 8, 16),
        resolver=unstable_resolver,
        external_network_observation=EXTERNAL_NETWORK_OBSERVATION,
    )
    assert unstable["qualified"] is False
    assert unstable["repeatability"]["passed"] is False
    assert len(set(unstable["repeatability"]["digests"])) > 1


def test_qualification_policy_rejects_calendar_wait_and_weakened_matrix() -> None:
    registry = load_registry(REPO_ROOT)
    policy = load_qualification_policy(REPO_ROOT)
    assert validate_qualification_policy(policy, registry) == []

    calendar_wait = copy.deepcopy(policy)
    calendar_wait["qualification"]["calendar_wait_required"] = True
    assert "calendar waiting must not be a qualification requirement" in (
        validate_qualification_policy(calendar_wait, registry)
    )

    weakened = copy.deepcopy(policy)
    weakened["qualification"]["required_mutation_classes"] = list(
        REQUIRED_MUTATIONS[:-1]
    )
    assert "required_mutation_classes must match the governed mutation matrix" in (
        validate_qualification_policy(weakened, registry)
    )


def test_external_network_observation_and_expansion_authority_fail_closed() -> None:
    missing_network = run_stability_qualification(
        REPO_ROOT,
        as_of=dt.date(2026, 8, 16),
        external_network_observation=None,
    )
    assert missing_network["qualified"] is False
    assert missing_network["external_network_errors"] == [
        "external network resolution observation is required"
    ]
    assert missing_network["expansion_authority"]["expansion_auto_authorized"] is False
