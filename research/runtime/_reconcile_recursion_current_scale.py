from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "docs/stewardship/progress-tracker.md",
    "| Current validated scale | 842 tests passed, 526 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #651 |",
    "| Current validated scale | 863 tests passed, 529 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #669 |",
)
replace_once(
    "tests/test_documentation_control_plane_truth.py",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 842\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 526\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 651",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 863\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 529\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 669",
)
