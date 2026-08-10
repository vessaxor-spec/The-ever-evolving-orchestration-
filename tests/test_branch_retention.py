from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/branch-retention.yml"
STEWARDSHIP = REPO_ROOT / "docs/stewardship/branch-retention.md"
AUDIT = REPO_ROOT / "docs/history/audits/branch-cleanup-2026-08-10.md"


def _legacy_snapshot() -> list[str]:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(
        r"# BEGIN LEGACY_AGENT_BRANCH_SNAPSHOT(?P<body>.*?)# END LEGACY_AGENT_BRANCH_SNAPSHOT",
        text,
        re.DOTALL,
    )
    assert match is not None
    return re.findall(r'"(agent/[^"]+)"', match.group("body"))


def test_branch_retention_is_guarded_to_merged_same_repo_agent_prs() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "types: [closed]" in text
    assert "contents: write" in text
    assert "pull-requests: read" in text
    assert "github.event.pull_request.merged == true" in text
    assert "github.event.pull_request.head.repo.full_name == github.repository" in text
    assert "startsWith(github.event.pull_request.head.ref, 'agent/')" in text
    assert 'if [[ "$branch" != agent/* ]]' in text
    assert "has_open_pr" in text
    assert "Preserving $branch because it backs an open pull request" in text


def test_legacy_cleanup_is_fixed_reviewed_snapshot() -> None:
    branches = _legacy_snapshot()
    assert len(branches) == 104
    assert len(set(branches)) == 104
    assert all(branch.startswith("agent/") for branch in branches)

    text = WORKFLOW.read_text(encoding="utf-8")
    assert 'if [[ "$HEAD_REF" == "agent/branch-retention-hygiene" ]]' in text
    assert 'delete_if_safe "$HEAD_REF"' in text


def test_branch_cleanup_audit_accounts_for_every_snapshot_ref() -> None:
    audit = AUDIT.read_text(encoding="utf-8")
    assert "**104** retained `agent/*` refs" in audit
    assert "no open pull requests" in audit.lower()
    for branch in _legacy_snapshot():
        assert f"`{branch}`" in audit


def test_stewardship_keeps_branch_hygiene_out_of_runtime_authority() -> None:
    text = STEWARDSHIP.read_text(encoding="utf-8")
    assert "working branches as temporary delivery references" in text
    assert "protected `main`" in text
    assert "accepted Capsules" in text
    assert "Branch retention is repository hygiene only" in text
    assert "routing or model-selection policy" in text
    assert "runtime or verification behavior" in text
