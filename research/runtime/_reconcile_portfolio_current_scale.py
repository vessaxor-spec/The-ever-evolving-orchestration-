from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


tracker_path = Path("docs/stewardship/progress-tracker.md")
tracker = tracker_path.read_text(encoding="utf-8")
tracker = replace_once(
    tracker,
    "| Current validated scale | 891 tests passed, 532 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #689 |",
    "| Current validated scale | 915 tests passed, 535 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #710 |",
    "progress tracker current validated scale",
)
tracker_path.write_text(tracker, encoding="utf-8")


test_path = Path("tests/test_documentation_control_plane_truth.py")
tests = test_path.read_text(encoding="utf-8")
tests = replace_once(
    tests,
    "EXPECTED_CURRENT_VALIDATED_TESTS = 891\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 532\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 689",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 915\nEXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 535\nEXPECTED_CURRENT_VALIDATED_CI_RUN = 710",
    "documentation truth current validated constants",
)
test_path.write_text(tests, encoding="utf-8")
