from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RULESET_PATH = REPO_ROOT / ".github/rulesets/protect-main.json"


def _rules_by_type() -> dict[str, dict[str, object]]:
    payload = json.loads(RULESET_PATH.read_text(encoding="utf-8"))
    assert payload["name"] == "Protect main"
    assert payload["target"] == "branch"
    assert payload["enforcement"] == "active"
    assert payload["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    assert payload["conditions"]["ref_name"]["exclude"] == []
    return {rule["type"]: rule for rule in payload["rules"]}


def test_main_ruleset_blocks_history_rewrite_and_deletion() -> None:
    rules = _rules_by_type()

    assert "deletion" in rules
    assert "non_fast_forward" in rules
    assert "required_linear_history" in rules


def test_main_ruleset_requires_reviewable_squash_pull_requests() -> None:
    rules = _rules_by_type()
    parameters = rules["pull_request"]["parameters"]

    assert parameters["allowed_merge_methods"] == ["squash"]
    assert parameters["required_approving_review_count"] == 0
    assert parameters["required_review_thread_resolution"] is True
    assert parameters["require_code_owner_review"] is False
    assert parameters["require_last_push_approval"] is False


def test_main_ruleset_requires_strict_reference_validation() -> None:
    rules = _rules_by_type()
    parameters = rules["required_status_checks"]["parameters"]

    assert parameters["strict_required_status_checks_policy"] is True
    assert parameters["do_not_enforce_on_create"] is True
    assert parameters["required_status_checks"] == [
        {"context": "Validate reference router"}
    ]
