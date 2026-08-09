from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCKFILE = REPO_ROOT / "ci/requirements-ci.lock"
WORKFLOWS = (
    REPO_ROOT / ".github/workflows/reference-ci.yml",
    REPO_ROOT / ".github/workflows/specialist-evidence-resolution.yml",
)
HASH_PATTERN = re.compile(r"--hash=sha256:[0-9a-f]{64}$")


def _locked_requirements() -> list[list[str]]:
    groups: list[list[str]] = []
    current: list[str] = []
    for raw in LOCKFILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if current:
            current.append(line)
            if not line.endswith("\\"):
                groups.append(current)
                current = []
            continue
        current = [line]
        if not line.endswith("\\"):
            groups.append(current)
            current = []
    assert not current, "CI lockfile ended with an incomplete continued requirement"
    return groups


def test_ci_lockfile_exactly_pins_each_requirement_and_artifact_hash() -> None:
    groups = _locked_requirements()
    assert groups
    for group in groups:
        requirement = group[0].removesuffix("\\").strip()
        assert "==" in requirement, f"Requirement is not exactly version-pinned: {requirement}"
        hashes = [part.removesuffix("\\").strip() for part in group[1:]]
        assert hashes, f"Requirement has no artifact hash: {requirement}"
        assert all(HASH_PATTERN.fullmatch(item) for item in hashes)


def test_all_ci_lockfile_installs_require_hash_verification() -> None:
    expected = "--require-hashes --no-deps -r ci/requirements-ci.lock"
    for workflow in WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        assert expected in text, f"{workflow.name} does not require lockfile hashes"
        assert "--no-deps -r ci/requirements-ci.lock" not in text.replace(expected, "")
