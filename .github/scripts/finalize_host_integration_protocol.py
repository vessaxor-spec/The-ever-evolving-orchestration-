from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"guard failed for {path}: expected 1 occurrence, got {count}: {old[:120]!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "docs/stewardship/progress-tracker.md",
    "967 tests passed, 552 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #799",
    "993 tests passed, 558 tracked-file layout checks, 42 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass; established by CI #806",
)

replace_once(
    "tests/test_documentation_control_plane_truth.py",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 967",
    "EXPECTED_CURRENT_VALIDATED_TESTS = 993",
)
replace_once(
    "tests/test_documentation_control_plane_truth.py",
    "EXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 552",
    "EXPECTED_CURRENT_VALIDATED_TRACKED_FILES = 558",
)
replace_once(
    "tests/test_documentation_control_plane_truth.py",
    "EXPECTED_CURRENT_VALIDATED_CI_RUN = 799",
    "EXPECTED_CURRENT_VALIDATED_CI_RUN = 806",
)

replace_once(
    "research/runtime/host-integration-protocol-0-1-2026-08-17.md",
    "**Status:** verification pending",
    "**Status:** verification passed, merge pending",
)
replace_once(
    "research/runtime/host-integration-protocol-0-1-2026-08-17.md",
    '''## Verification

Pending on this reconstructed branch:

- full Reference Implementation CI on the current base;
- targeted mutation campaign for the corrected controls;
- final exact-head CI after evidence and stewardship reconciliation.

The eventual PASS, if achieved, qualifies only the non-production reference candidate. Production transport authenticity, host/account/tenant identity, restart-persistent replay state, policy-snapshot retry binding, credential scope, containment, distributed coordination, effect authenticity, and full selected-executor/verifier live-provider assimilation remain open.
''',
    '''## Verification

The reconstructed candidate passed both clean full-suite validation and targeted mutation verification before merge.

### Clean baseline

Reference Implementation CI #806 (`32066910438`, job `95501344408`) validated head `f188df4b6f8eaa2a784b7ffd992fbd9b8db5982b` through synthetic PR merge `1fbf4e08d172a4360e396fdfa5e99a7387d96b7d` with:

- 993 passing tests;
- 558 tracked-file layout checks;
- 42 parsed JSON Schemas;
- regulated specialist evidence structural validation passed;
- linked configuration valid with zero issues;
- provider-diverse end-to-end reference verification passed using OpenAI `gpt-5.6-terra` execution and Anthropic `claude-sonnet-5` independent verification, with Google `gemini-3.6-flash` preserved as routine cross-provider fallback.

### Targeted mutation campaign

One-shot mutation run `32066827411` (job `95500782309`) executed on head `9c33d2addf9bbfb16741865ad4e579128eb74e12` and killed 5 of 5 targeted weakened controls:

1. `retry_budget_integer`;
2. `receipt_attempt_integer`;
3. `single_outstanding_instruction`;
4. `monotonic_fallback`;
5. `terminal_phase_closure`.

The mutation runner restored the production source after every mutant and the final source-restoration check passed.

### Disposition

The evidence qualifies only the bounded, non-production `teo-host-integration/0.1` reference candidate for reviewed merge. It does not promote the Host Integration Contract to normative or production status and does not widen live execution, routing, provider access, specialist authority, Task Request/Dispatch authority, or qualified-human authority.

Production transport authenticity, host/account/tenant identity, restart-persistent replay state, policy-snapshot retry binding, credential scope, containment, distributed coordination, effect authenticity, dynamic authority discovery, and full selected-executor/verifier live-provider assimilation remain open research gates.
''',
)

replace_once(
    "CHANGELOG.md",
    "### Validation\n\n- repository layout tests reject undeclared root files",
    "### Validation\n\n- reconstructed Host Integration Protocol 0.1 candidate passed clean CI #806 with 993 tests, 558 tracked-file layout checks, 42 parsed JSON Schemas, regulated-specialist evidence validation, zero linked-config issues, and provider-diverse end-to-end verification; targeted mutation run `32066827411` killed 5 of 5 sequencing/type-control mutants without widening live or production authority\n- repository layout tests reject undeclared root files",
)
