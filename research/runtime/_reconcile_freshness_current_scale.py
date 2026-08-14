from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one match, found {count}: {old!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "docs/stewardship/progress-tracker.md",
    "| Current validated scale | 863 tests passed, 529 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #669 |",
    "| Current validated scale | 891 tests passed, 532 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #689 |",
)
replace_once(
    "tests/test_documentation_control_plane_truth.py",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 863\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 529\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 669",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 891\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 532\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 689",
)
