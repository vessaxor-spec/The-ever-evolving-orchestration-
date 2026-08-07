from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = REPO_ROOT / "policy/verification/verifier-calibration-empirical.yaml"


def test_human_review_policy_requires_reference_label_blinding() -> None:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    human = policy["human_labeling"]
    assert human["reviewers_blinded_from_model_observations"] is True
    assert human["reviewers_blinded_from_reference_control_labels"] is True
    assert human["minimum_independent_reviewers_per_case"] >= 2
    assert human["adjudication_required_on_disagreement"] is True
    assert human["adjudicator_must_be_distinct_from_case_reviewers"] is True
    assert human["default_review_packet_path"].startswith(".teo/")
    assert human["default_labels_path"].startswith(".teo/")
    assert human["persist_reviewer_name_or_email"] is False
    assert human["persist_task_or_candidate_content"] is False
