from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/branch-retention.yml"
STEWARDSHIP = REPO_ROOT / "docs/stewardship/branch-retention.md"
AUDIT = REPO_ROOT / "docs/history/audits/branch-cleanup-2026-08-10.md"
RECONCILIATION = (
    REPO_ROOT / "docs/history/audits/branch-retention-reconciliation-2026-08-11.md"
)
TEMPORARY_PREFIXES = ("agent/", "audit/", "capsule/", "cleanup/", "governance/")
RESERVED_REPLAY_BRANCH = "evidence/documentation-replay-trigger-v1"


def _legacy_snapshot() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"# BEGIN LEGACY_AGENT_BRANCH_SNAPSHOT(?P<body>.*?)# END LEGACY_AGENT_BRANCH_SNAPSHOT",
        text,
        re.DOTALL,
    )
    assert match is not None
    return re.findall(r'"(agent/[^"]+)"', match.group("body"))


def _post_v1_snapshot() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"# BEGIN POST_V1_TEMPORARY_BRANCH_SNAPSHOT(?P<body>.*?)# END POST_V1_TEMPORARY_BRANCH_SNAPSHOT",
        text,
        re.DOTALL,
    )
    assert match is not None
    return re.findall(r'"([^"]+)"', match.group("body"))


def test_branch_retention_is_guarded_to_merged_same_repo_temporary_prs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "types: [closed]" in text
    assert "contents: write" in text
    assert "pull-requests: read" in text
    assert "github.event.pull_request.merged == true" in text
    assert "github.event.pull_request.head.repo.full_name == github.repository" in text
    for prefix in TEMPORARY_PREFIXES:
        assert f"startsWith(github.event.pull_request.head.ref, '{prefix}')" in text
    assert "agent/*|audit/*|capsule/*|cleanup/*|governance/*" in text
    assert "has_open_pr" in text
    assert "Preserving $branch because it backs an open pull request" in text
    assert RESERVED_REPLAY_BRANCH not in _post_v1_snapshot()


def test_legacy_cleanup_is_fixed_reviewed_snapshot() -> None:
    branches = _legacy_snapshot()
    assert len(branches) == 104
    assert len(set(branches)) == 104
    assert all(branch.startswith("agent/") for branch in branches)

    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'if [[ "$HEAD_REF" == "agent/branch-retention-hygiene" ]]' in text
    assert 'delete_if_safe "$HEAD_REF"' in text


def test_post_v1_cleanup_is_fixed_reviewed_snapshot() -> None:
    branches = _post_v1_snapshot()
    assert branches == [
        "agent/pr108-progress-reconcile",
        "audit/authority-temporal-causality",
        "audit/mission-control-finalization-authority-recovery-mutations",
        "capsule/0009-evidence-becomes-authority",
        "cleanup/remove-specialist-origin-references",
        "governance/reframe-human-calibration",
    ]
    assert len(set(branches)) == len(branches)
    assert all(branch.startswith(TEMPORARY_PREFIXES) for branch in branches)

    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'if [[ "$HEAD_REF" == "agent/branch-retention-v2" ]]' in text
    assert 'delete_exact_probe_if_safe "noop-check"' in text
    assert 'if [[ "$branch" != "noop-check" ]]' in text


def test_branch_cleanup_audit_accounts_for_every_snapshot_ref() -> None:
    audit = AUDIT.read_text(encoding="utf-8")
    assert "**104** retained `agent/*` refs" in audit
    assert "no open pull requests" in audit.lower()
    for branch in _legacy_snapshot():
        assert f"`{branch}`" in audit


def test_post_v1_reconciliation_accounts_for_every_cleanup_ref() -> None:
    audit = RECONCILIATION.read_text(encoding="utf-8")
    for branch in _post_v1_snapshot():
        assert f"`{branch}`" in audit
    assert "`noop-check`" in audit
    assert f"`{RESERVED_REPLAY_BRANCH}`" in audit
    assert "intentionally retained" in audit


def test_stewardship_keeps_branch_hygiene_out_of_runtime_authority() -> None:
    text = STEWARDSHIP.read_text(encoding="utf-8")
    assert "working branches as temporary delivery references" in text
    assert "protected `main`" in text
    assert "accepted Capsules" in text
    for prefix in TEMPORARY_PREFIXES:
        assert f"`{prefix}*`" in text
    assert f"`{RESERVED_REPLAY_BRANCH}`" in text
    assert "Branch retention is repository hygiene only" in text
    assert "routing or model-selection policy" in text
    assert "runtime or verification behavior" in text
