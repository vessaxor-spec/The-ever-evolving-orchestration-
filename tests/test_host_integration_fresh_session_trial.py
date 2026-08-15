from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
from pathlib import Path
import runpy

import pytest


ROOT = Path(__file__).resolve().parents[1]
TRIAL = runpy.run_path(
    str(ROOT / "research" / "runtime" / "host_integration_fresh_session_trial.py")
)
FreshSessionChallenge = TRIAL["FreshSessionChallenge"]
FreshSessionExecutionEvidence = TRIAL["FreshSessionExecutionEvidence"]
FreshSessionTrialError = TRIAL["FreshSessionTrialError"]
REQUIRED_EVIDENCE_STAGES = TRIAL["REQUIRED_EVIDENCE_STAGES"]
SetupCommitment = TRIAL["SetupCommitment"]
validate_fresh_session_trial = TRIAL["validate_fresh_session_trial"]

BASE = datetime(2026, 8, 15, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
REV = "1" * 40


def iso(minutes: int) -> str:
    return (BASE + timedelta(minutes=minutes)).isoformat()


def setup() -> SetupCommitment:
    return SetupCommitment.create(
        trial_id="trial-001",
        host_id="host-alpha",
        teo_revision=REV,
        setup_session_id="session-setup",
        setup_ended_at=iso(10),
        standing_hook_id="teo-standing-hook",
        standing_hook_fingerprint=HEX_A,
        bootstrap_fingerprint=HEX_B,
        assimilation_declaration_digest=HEX_C,
    )


def challenge(s: SetupCommitment) -> FreshSessionChallenge:
    return FreshSessionChallenge.create(
        setup=s,
        task_id="ordinary-task-002",
        prompt="Summarize the supplied bounded record and return the three material findings.",
        issued_at=iso(20),
        nonce="fresh-challenge-001",
    )


def evidence(
    s: SetupCommitment,
    c: FreshSessionChallenge,
    **overrides,
) -> FreshSessionExecutionEvidence:
    values = {
        "trial_id": s.trial_id,
        "host_id": s.host_id,
        "teo_revision": s.teo_revision,
        "fresh_session_id": "session-fresh",
        "fresh_session_started_at": iso(15),
        "bootstrap_loaded_at": iso(16),
        "bootstrap_locked_before_challenge": True,
        "prior_conversation_context_available": False,
        "session_specific_teo_injection_present": False,
        "inherited_hook_id": s.standing_hook_id,
        "inherited_hook_fingerprint": s.standing_hook_fingerprint,
        "inherited_bootstrap_fingerprint": s.bootstrap_fingerprint,
        "task_id": c.task_id,
        "user_task_text": c.prompt,
        "user_task_digest": hashlib.sha256(c.prompt.encode()).hexdigest(),
        "challenge_digest": c.challenge_digest,
        "teo_dispatch_id": "dispatch-fresh-001",
        "verification_status": "passed",
        "finalization_status": "completed",
        "outcome_status": "completed",
        "evidence_stages": REQUIRED_EVIDENCE_STAGES,
    }
    values.update(overrides)
    return FreshSessionExecutionEvidence(**values)


def test_positive_cross_session_continuity_packet_passes() -> None:
    s = setup()
    c = challenge(s)
    fresh = evidence(s, c)

    verdict = validate_fresh_session_trial(s, c, fresh)

    assert verdict.passed is True
    assert verdict.setup_session_id != verdict.fresh_session_id
    assert verdict.verified_evidence_stages == REQUIRED_EVIDENCE_STAGES


def test_same_session_cannot_count_as_fresh() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="reuses the assimilation session"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, fresh_session_id=s.setup_session_id),
        )


def test_challenge_must_be_created_after_setup_session_ends() -> None:
    s = setup()
    with pytest.raises(FreshSessionTrialError, match="only after the assimilation session ended"):
        FreshSessionChallenge.create(
            setup=s,
            task_id="x",
            prompt="Classify this record.",
            issued_at=iso(9),
            nonce="n",
        )


@pytest.mark.parametrize(
    "prompt",
    [
        "Use TEO to summarize this record.",
        "Route through TEO and classify this record.",
        "Ask Mission Control to summarize this record.",
    ],
)
def test_challenge_cannot_remind_the_fresh_session_to_use_teo(prompt: str) -> None:
    s = setup()
    with pytest.raises(FreshSessionTrialError, match="TEO-specific reminder"):
        FreshSessionChallenge.create(
            setup=s,
            task_id="x",
            prompt=prompt,
            issued_at=iso(20),
            nonce="n",
        )


def test_prior_conversation_context_contaminates_trial() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="prior assimilation-conversation context"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, prior_conversation_context_available=True),
        )


def test_session_specific_teo_injection_contaminates_trial() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="session-specific TEO reminder"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, session_specific_teo_injection_present=True),
        )


def test_bootstrap_must_be_loaded_and_locked_before_challenge() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="loaded before the challenge"):
        validate_fresh_session_trial(s, c, evidence(s, c, bootstrap_loaded_at=iso(21)))
    with pytest.raises(FreshSessionTrialError, match="locked before challenge"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, bootstrap_locked_before_challenge=False),
        )


def test_persistent_hook_identity_must_survive_session_boundary() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="standing hook fingerprint changed"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, inherited_hook_fingerprint="d" * 64),
        )
    with pytest.raises(FreshSessionTrialError, match="bootstrap fingerprint changed"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, inherited_bootstrap_fingerprint="e" * 64),
        )


def test_challenge_binding_and_user_task_must_match_exactly() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="not bound to the issued challenge"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, challenge_digest="f" * 64),
        )
    with pytest.raises(FreshSessionTrialError, match="user task text"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, user_task_text="Different task"),
        )


def test_teo_revision_and_host_identity_cannot_drift() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="host_id mismatch"):
        validate_fresh_session_trial(s, c, evidence(s, c, host_id="host-beta"))
    with pytest.raises(FreshSessionTrialError, match="different TEO revision"):
        validate_fresh_session_trial(s, c, evidence(s, c, teo_revision="2" * 40))


def test_fresh_session_must_emit_real_teo_path_and_finalization() -> None:
    s = setup()
    c = challenge(s)
    with pytest.raises(FreshSessionTrialError, match="no TEO dispatch"):
        validate_fresh_session_trial(s, c, evidence(s, c, teo_dispatch_id=""))
    with pytest.raises(FreshSessionTrialError, match="verification did not pass"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, verification_status="failed"),
        )
    with pytest.raises(FreshSessionTrialError, match="finalization did not complete"):
        validate_fresh_session_trial(
            s,
            c,
            evidence(s, c, finalization_status="refused"),
        )


def test_missing_control_path_stage_fails_closed() -> None:
    s = setup()
    c = challenge(s)
    stages = tuple(
        stage for stage in REQUIRED_EVIDENCE_STAGES if stage != "authority_intersection"
    )
    with pytest.raises(FreshSessionTrialError, match="authority_intersection"):
        validate_fresh_session_trial(s, c, evidence(s, c, evidence_stages=stages))


def test_setup_commitment_tampering_is_detected() -> None:
    s = setup()
    c = challenge(s)
    tampered = replace(s, standing_hook_id="other-hook")
    with pytest.raises(FreshSessionTrialError, match="setup commitment digest mismatch"):
        validate_fresh_session_trial(tampered, c, evidence(s, c))


def test_trial_protocol_refuses_same_session_and_no_reminder_handwave() -> None:
    text = (
        ROOT
        / "research"
        / "roadmaps"
        / "host-integration-fresh-session-trial.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "This current conversation cannot count as the fresh-session evidence",
        "no session-specific instruction such as `use TEO`",
        "Correct output alone is not evidence of assimilation.",
        "The gate remains open until a real host completes Stage A",
    ):
        assert phrase in text


def test_trial_protocol_requires_independent_verification_and_inconclusive_state() -> None:
    text = (
        ROOT
        / "research"
        / "roadmaps"
        / "host-integration-fresh-session-trial.md"
    ).read_text(encoding="utf-8")
    for phrase in (
        "## Stage F: independent verification",
        "### PASS",
        "### FAIL",
        "### INCONCLUSIVE",
        "A compromised host can forge local evidence",
    ):
        assert phrase in text
