from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github/workflows/documentation-replay-evidence.yml"


def test_documentation_replay_workflow_is_owner_bound_and_trusted_base_only() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    for phrase in (
        "issue_comment:",
        "pull_request:",
        "github.event.issue.number == 121",
        "github.event.issue.pull_request != null",
        "github.event.comment.user.login == 'vessaxor-spec'",
        "github.event.comment.body == '/run-documentation-replay'",
        "github.event.pull_request.user.login == 'vessaxor-spec'",
        "github.event.pull_request.head.repo.full_name == github.repository",
        "github.event.pull_request.head.ref == 'evidence/documentation-replay-trigger-v1'",
        "github.event.pull_request.base.ref == 'main'",
        "github.event.pull_request.base.sha || github.sha",
        "permissions:\n  contents: read",
        "persist-credentials: false",
        "ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}",
        "OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}",
        "--execute-live",
        "activation_authorized",
        "live_scope_widened",
        "telemetry_persisted",
        "teo-documentation-replay-${{ github.run_id }}",
        "teo-documentation-replay-audit-${{ github.run_id }}",
        "GITHUB_STEP_SUMMARY",
        '"record_type": "live_scope_replay_audit_start"',
        '"record_type": "live_scope_replay_audit_result"',
        '"provider_backed_evidence_accepted": accepted',
        'audit_dir = Path(".teo/runtime/live-scope-replay/audit")',
        '(audit_dir / "start.json")',
        ".teo/runtime/live-scope-replay/audit/",
    ):
        assert phrase in text

    for forbidden in (
        "pull_request_target",
        "github.event.pull_request.head.sha",
        "refs/pull/",
        "gh pr checkout",
        "gh issue comment",
        "gh api --method POST",
        "GH_TOKEN:",
        "issues: write",
        "pull-requests: write",
        "git fetch",
        "allow-unsafe-pr-checkout",
    ):
        assert forbidden not in text


def test_documentation_replay_workflow_preserves_evidence_and_recovery_boundaries() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")

    for phrase in (
        '"fallback_mode": "disabled_until_recovery_gate"',
        '"selection_mode": "canonical_candidate_route"',
        '"verification_mode": "assigned_candidate_verifier"',
        '"authority_mode": "staged_evidence_only"',
        '"tool_access_profile": "none"',
        'summary["total_trials"] != 4',
        'summary["completed"] != 4',
        'record["candidate_state"] != "staged"',
        'record["activation_authorized"] is not False',
        'record["live_scope_widened"] is not False',
        'record["telemetry_persisted"] is not False',
        'primary["model"] != "claude-sonnet-5"',
        'verifier["model"] != "gpt-5.6-terra"',
        "No empirical success is claimed from this run.",
    ):
        assert phrase in text
