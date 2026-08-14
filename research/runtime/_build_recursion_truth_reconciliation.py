from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one contextual match, found {count}: {old[:140]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


HOST_TEST = "tests/test_host_integration_summary_truth.py"
DOC_TEST = "tests/test_documentation_control_plane_truth.py"

replace_once(HOST_TEST, '"eight provider-independent adversarial slices",', '"nine provider-independent adversarial slices",')
replace_once(HOST_TEST, '"Reference Implementation CI #644",', '"Reference Implementation CI #658",')
replace_once(HOST_TEST, '"842 automated tests",', '"863 automated tests",')
replace_once(HOST_TEST, '"525 tracked-file layout checks",', '"528 tracked-file layout checks",')
replace_once(
    HOST_TEST,
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "The next gate is provider-backed controlled documentation replay evidence",',
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n        "process-lifetime recursion resistance",\n        "The next gate is provider-backed controlled documentation replay evidence",'
)
replace_once(
    HOST_TEST,
    '    assert "seven provider-independent adversarial slices" not in text\n',
    '    assert "eight provider-independent adversarial slices" not in text\n    assert "seven provider-independent adversarial slices" not in text\n'
)
replace_once(
    HOST_TEST,
    '        "Authority-surface reconciliation",\n        "Static runtime-wired slice satisfied",\n        "CI #644",',
    '        "Authority-surface reconciliation",\n        "Static runtime-wired slice satisfied",\n        "CI #644",\n        "Recursion resistance",\n        "Process-lifetime slice satisfied",\n        "CI #658",'
)
replace_once(
    HOST_TEST,
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "dynamic executable hooks/plugins/transitive code remain open",',
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n        "dynamic executable hooks/plugins/transitive code remain open",'
)
replace_once(
    HOST_TEST,
    '    assert "Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Open.**" not in text\n',
    '    assert "Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Open.**" not in text\n    assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text\n'
)

replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_CI_RUN = 644", "EXPECTED_HOST_INTEGRATION_CI_RUN = 658")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TESTS = 842", "EXPECTED_HOST_INTEGRATION_TESTS = 863")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 525", "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 528")
replace_once(
    DOC_TEST,
    '        "brokered conformant process-lifetime",\n        "static runtime-wired authority-surface reconciliation",\n        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "final execution provenance",',
    '        "brokered conformant process-lifetime",\n        "static runtime-wired authority-surface reconciliation",\n        "process-lifetime recursion resistance",\n        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n        "final execution provenance",'
)
replace_once(
    DOC_TEST,
    '        "brokered conformant process-lifetime cross-process authority/replay resistance",\n        "static runtime-wired authority-surface reconciliation",\n        "Dynamic executable-hook discovery",',
    '        "brokered conformant process-lifetime cross-process authority/replay resistance",\n        "static runtime-wired authority-surface reconciliation",\n        "process-lifetime recursion-resistance",\n        "Dynamic executable-hook discovery",'
)
replace_once(
    DOC_TEST,
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |",',
    '        "host-integration-cross-process-authority-2026-08-13.md",\n        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n        "| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |",'
)
replace_once(
    DOC_TEST,
    '        "Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644",\n',
    '        "Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644",\n        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",\n'
)
