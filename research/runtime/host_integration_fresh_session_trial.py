from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


REQUIRED_EVIDENCE_STAGES = (
    "host_admission",
    "teo_dispatch",
    "authority_intersection",
    "execution_envelope",
    "artifact_binding",
    "independent_verification",
    "finalization",
    "evidence_bearing_outcome",
)

FORBIDDEN_CHALLENGE_HINTS = (
    "teo",
    "mission control",
    "use teo",
    "route through teo",
    "apply teo",
)


class FreshSessionTrialError(ValueError):
    """Raised when a Fresh-AI assimilation continuity claim is not supported."""


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise FreshSessionTrialError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise FreshSessionTrialError(f"timestamp must include timezone: {value}")
    return parsed.astimezone(timezone.utc)


def _canonical_digest(payload: dict) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _require_hex_digest(value: str, label: str) -> None:
    if len(value) != 64:
        raise FreshSessionTrialError(f"{label} must be a 64-character SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise FreshSessionTrialError(f"{label} must be hexadecimal") from exc


def _require_revision(value: str) -> None:
    if len(value) != 40:
        raise FreshSessionTrialError("teo_revision must be an exact 40-character commit SHA")
    try:
        int(value, 16)
    except ValueError as exc:
        raise FreshSessionTrialError("teo_revision must be hexadecimal") from exc


@dataclass(frozen=True)
class SetupCommitment:
    trial_id: str
    host_id: str
    teo_revision: str
    setup_session_id: str
    setup_ended_at: str
    standing_hook_id: str
    standing_hook_fingerprint: str
    bootstrap_fingerprint: str
    assimilation_declaration_digest: str
    commitment_digest: str

    @classmethod
    def create(
        cls,
        *,
        trial_id: str,
        host_id: str,
        teo_revision: str,
        setup_session_id: str,
        setup_ended_at: str,
        standing_hook_id: str,
        standing_hook_fingerprint: str,
        bootstrap_fingerprint: str,
        assimilation_declaration_digest: str,
    ) -> "SetupCommitment":
        _require_revision(teo_revision)
        _parse_utc(setup_ended_at)
        for label, digest in (
            ("standing_hook_fingerprint", standing_hook_fingerprint),
            ("bootstrap_fingerprint", bootstrap_fingerprint),
            ("assimilation_declaration_digest", assimilation_declaration_digest),
        ):
            _require_hex_digest(digest, label)
        if not all((trial_id, host_id, setup_session_id, standing_hook_id)):
            raise FreshSessionTrialError("setup identity fields must be non-empty")
        core = {
            "trial_id": trial_id,
            "host_id": host_id,
            "teo_revision": teo_revision,
            "setup_session_id": setup_session_id,
            "setup_ended_at": setup_ended_at,
            "standing_hook_id": standing_hook_id,
            "standing_hook_fingerprint": standing_hook_fingerprint,
            "bootstrap_fingerprint": bootstrap_fingerprint,
            "assimilation_declaration_digest": assimilation_declaration_digest,
        }
        return cls(**core, commitment_digest=_canonical_digest(core))

    def verify(self) -> None:
        expected = _canonical_digest({k: v for k, v in asdict(self).items() if k != "commitment_digest"})
        if expected != self.commitment_digest:
            raise FreshSessionTrialError("setup commitment digest mismatch")


@dataclass(frozen=True)
class FreshSessionChallenge:
    trial_id: str
    setup_commitment_digest: str
    task_id: str
    prompt: str
    issued_at: str
    nonce: str
    challenge_digest: str

    @classmethod
    def create(
        cls,
        *,
        setup: SetupCommitment,
        task_id: str,
        prompt: str,
        issued_at: str,
        nonce: str,
    ) -> "FreshSessionChallenge":
        setup.verify()
        issued = _parse_utc(issued_at)
        ended = _parse_utc(setup.setup_ended_at)
        if issued <= ended:
            raise FreshSessionTrialError("challenge must be issued only after the assimilation session ended")
        lowered = prompt.casefold()
        if any(hint in lowered for hint in FORBIDDEN_CHALLENGE_HINTS):
            raise FreshSessionTrialError("challenge prompt contains a TEO-specific reminder or hint")
        if not task_id or not prompt.strip() or not nonce:
            raise FreshSessionTrialError("challenge task_id, prompt, and nonce must be non-empty")
        core = {
            "trial_id": setup.trial_id,
            "setup_commitment_digest": setup.commitment_digest,
            "task_id": task_id,
            "prompt": prompt,
            "issued_at": issued_at,
            "nonce": nonce,
        }
        return cls(**core, challenge_digest=_canonical_digest(core))

    def verify(self, setup: SetupCommitment) -> None:
        if self.trial_id != setup.trial_id:
            raise FreshSessionTrialError("challenge trial_id does not match setup")
        if self.setup_commitment_digest != setup.commitment_digest:
            raise FreshSessionTrialError("challenge is not bound to the setup commitment")
        expected = _canonical_digest({k: v for k, v in asdict(self).items() if k != "challenge_digest"})
        if expected != self.challenge_digest:
            raise FreshSessionTrialError("challenge digest mismatch")
        if _parse_utc(self.issued_at) <= _parse_utc(setup.setup_ended_at):
            raise FreshSessionTrialError("challenge predates or overlaps the assimilation session")
        lowered = self.prompt.casefold()
        if any(hint in lowered for hint in FORBIDDEN_CHALLENGE_HINTS):
            raise FreshSessionTrialError("challenge prompt contains a TEO-specific reminder or hint")


@dataclass(frozen=True)
class FreshSessionExecutionEvidence:
    trial_id: str
    host_id: str
    teo_revision: str
    fresh_session_id: str
    fresh_session_started_at: str
    bootstrap_loaded_at: str
    bootstrap_locked_before_challenge: bool
    prior_conversation_context_available: bool
    session_specific_teo_injection_present: bool
    inherited_hook_id: str
    inherited_hook_fingerprint: str
    inherited_bootstrap_fingerprint: str
    task_id: str
    user_task_text: str
    user_task_digest: str
    challenge_digest: str
    teo_dispatch_id: str
    verification_status: str
    finalization_status: str
    outcome_status: str
    evidence_stages: tuple[str, ...]


@dataclass(frozen=True)
class FreshSessionTrialVerdict:
    trial_id: str
    passed: bool
    setup_session_id: str
    fresh_session_id: str
    task_id: str
    teo_dispatch_id: str
    verified_evidence_stages: tuple[str, ...]
    residual_boundaries: tuple[str, ...]


RESIDUAL_BOUNDARIES = (
    "session_identity_and_bootstrap_provenance_depend_on_host_evidence",
    "independent_operator_or_verifier_must_check_no_hidden_session_specific_reminder",
    "cross_process_or_remote_authenticity_not_proven_by_packet_validation",
    "compromised_host_can_forge_local_evidence_without_external_attestation",
)


def validate_fresh_session_trial(
    setup: SetupCommitment,
    challenge: FreshSessionChallenge,
    fresh: FreshSessionExecutionEvidence,
) -> FreshSessionTrialVerdict:
    setup.verify()
    challenge.verify(setup)
    _require_revision(fresh.teo_revision)

    if fresh.trial_id != setup.trial_id:
        raise FreshSessionTrialError("fresh-session evidence trial_id mismatch")
    if fresh.host_id != setup.host_id:
        raise FreshSessionTrialError("fresh-session evidence host_id mismatch")
    if fresh.teo_revision != setup.teo_revision:
        raise FreshSessionTrialError("fresh-session evidence uses a different TEO revision")
    if fresh.fresh_session_id == setup.setup_session_id:
        raise FreshSessionTrialError("fresh-session evidence reuses the assimilation session")

    started = _parse_utc(fresh.fresh_session_started_at)
    loaded = _parse_utc(fresh.bootstrap_loaded_at)
    ended = _parse_utc(setup.setup_ended_at)
    issued = _parse_utc(challenge.issued_at)
    if started <= ended:
        raise FreshSessionTrialError("fresh session must start after the assimilation session ended")
    if loaded < started:
        raise FreshSessionTrialError("bootstrap cannot be recorded as loaded before the fresh session starts")
    if loaded > issued:
        raise FreshSessionTrialError("bootstrap must be loaded before the challenge is issued")
    if not fresh.bootstrap_locked_before_challenge:
        raise FreshSessionTrialError("fresh-session bootstrap must be locked before challenge disclosure")
    if fresh.prior_conversation_context_available:
        raise FreshSessionTrialError("fresh session has prior assimilation-conversation context available")
    if fresh.session_specific_teo_injection_present:
        raise FreshSessionTrialError("fresh session contains a session-specific TEO reminder/injection")

    if fresh.inherited_hook_id != setup.standing_hook_id:
        raise FreshSessionTrialError("fresh session did not inherit the committed standing hook identity")
    if fresh.inherited_hook_fingerprint != setup.standing_hook_fingerprint:
        raise FreshSessionTrialError("fresh session standing hook fingerprint changed")
    if fresh.inherited_bootstrap_fingerprint != setup.bootstrap_fingerprint:
        raise FreshSessionTrialError("fresh session bootstrap fingerprint changed")

    if fresh.challenge_digest != challenge.challenge_digest:
        raise FreshSessionTrialError("fresh-session execution is not bound to the issued challenge")
    if fresh.task_id != challenge.task_id:
        raise FreshSessionTrialError("fresh-session task_id does not match the challenge")
    if fresh.user_task_text != challenge.prompt:
        raise FreshSessionTrialError("fresh-session user task text does not match the challenge")
    if fresh.user_task_digest != _text_digest(challenge.prompt):
        raise FreshSessionTrialError("fresh-session task digest mismatch")

    if not fresh.teo_dispatch_id:
        raise FreshSessionTrialError("fresh session produced no TEO dispatch evidence")
    if fresh.verification_status != "passed":
        raise FreshSessionTrialError("fresh-session independent verification did not pass")
    if fresh.finalization_status != "completed":
        raise FreshSessionTrialError("fresh-session finalization did not complete")
    if fresh.outcome_status != "completed":
        raise FreshSessionTrialError("fresh-session evidence-bearing outcome did not complete")

    missing = [stage for stage in REQUIRED_EVIDENCE_STAGES if stage not in fresh.evidence_stages]
    if missing:
        raise FreshSessionTrialError(f"fresh-session evidence is missing required stages: {', '.join(missing)}")

    return FreshSessionTrialVerdict(
        trial_id=setup.trial_id,
        passed=True,
        setup_session_id=setup.setup_session_id,
        fresh_session_id=fresh.fresh_session_id,
        task_id=fresh.task_id,
        teo_dispatch_id=fresh.teo_dispatch_id,
        verified_evidence_stages=REQUIRED_EVIDENCE_STAGES,
        residual_boundaries=RESIDUAL_BOUNDARIES,
    )


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: str, payload: object) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _tuple_field(payload: dict, key: str) -> dict:
    copied = dict(payload)
    copied[key] = tuple(copied.get(key, ()))
    return copied


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate TEO Fresh-AI cross-session assimilation evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    setup_parser = sub.add_parser("commit-setup")
    setup_parser.add_argument("--input", required=True)
    setup_parser.add_argument("--output", required=True)

    challenge_parser = sub.add_parser("issue-challenge")
    challenge_parser.add_argument("--setup", required=True)
    challenge_parser.add_argument("--input", required=True)
    challenge_parser.add_argument("--output", required=True)

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--setup", required=True)
    validate_parser.add_argument("--challenge", required=True)
    validate_parser.add_argument("--fresh", required=True)
    validate_parser.add_argument("--output", required=True)

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "commit-setup":
        setup = SetupCommitment.create(**_read_json(args.input))
        _write_json(args.output, asdict(setup))
        return 0

    setup = SetupCommitment(**_read_json(args.setup))
    if args.command == "issue-challenge":
        challenge = FreshSessionChallenge.create(setup=setup, **_read_json(args.input))
        _write_json(args.output, asdict(challenge))
        return 0

    challenge = FreshSessionChallenge(**_read_json(args.challenge))
    fresh = FreshSessionExecutionEvidence(**_tuple_field(_read_json(args.fresh), "evidence_stages"))
    verdict = validate_fresh_session_trial(setup, challenge, fresh)
    _write_json(args.output, asdict(verdict))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
