from __future__ import annotations

from pathlib import Path
import subprocess


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old[:120]!r}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


README = "README.md"
ROADMAP = "research/roadmaps/host-integration-contract.md"
TRACKER = "docs/stewardship/progress-tracker.md"
HOST_TEST = "tests/test_host_integration_summary_truth.py"
DOC_TEST = "tests/test_documentation_control_plane_truth.py"

# README: latest Host Integration evidence, slice count, bounded result, residuals, and link.
replace_once(
    README,
    "The latest Host Integration executable research validation is Reference Implementation CI #644: **842 automated tests**, **525 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the static runtime-wired authority-surface reconciliation slice after red-canary CI #643 corrected a research assumption about the still-present empty `runtime-worker-overrides.yaml` authority surface. It remains non-normative evidence and does not close dynamic executable-hook or plugin discovery, transitive-code identity, production authenticity, or distributed authenticity boundaries.",
    "The latest Host Integration executable research validation is Reference Implementation CI #658: **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the process-lifetime recursion-resistance slice after a Security and Authority Boundaries review replaced an unnecessary pending-authorization store with stateless HMAC-bound admission claims. It remains non-normative evidence and does not close restart-durable or distributed recursion state, production scheduler containment, compromised-host bypass, dynamic executable-hook discovery, transitive-code identity, or production authenticity boundaries."
)
replace_once(
    README,
    "Since those validation rounds, eight provider-independent adversarial slices have converted several previously open integration questions into executable evidence:",
    "Since those validation rounds, nine provider-independent adversarial slices have converted several previously open integration questions into executable evidence:"
)
replace_once(
    README,
    "- static runtime-wired authority-surface reconciliation derives canonical authority configuration and policy paths from executable Python source, fingerprints present files, retains dormant-but-wired paths, and rejects tested omissions, unwired additions, aliases, stale declarations, content changes, and repository-root escape while dynamic executable hooks, plugins/loaders, constructed paths, and transitive-code identity remain open.",
    "- static runtime-wired authority-surface reconciliation derives canonical authority configuration and policy paths from executable Python source, fingerprints present files, retains dormant-but-wired paths, and rejects tested omissions, unwired additions, aliases, stale declarations, content changes, and repository-root escape while dynamic executable hooks, plugins/loaders, constructed paths, and transitive-code identity remain open;\n- process-lifetime recursion resistance binds one root dispatch to immutable depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC-bound admission claims reject tested forgery, replay, stale-state claims, cross-root reuse, release-based budget reset, and raced same-revision claims while restart-durable, distributed, production-scheduler, and compromised-host boundaries remain open."
)
replace_once(
    README,
    "The static authority-surface reconciliation slice passed corrected executable Reference Implementation CI #644 with **842 automated tests**, **525 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. Red-canary CI #643 first exposed two research-test assumptions, including that the still-present empty `runtime-worker-overrides.yaml` file had been mistaken for an absent surface. The correction followed repository truth and did not change production routing or authority.",
    "The static authority-surface reconciliation slice passed corrected executable Reference Implementation CI #644 with **842 automated tests**, **525 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. Red-canary CI #643 first exposed two research-test assumptions, including that the still-present empty `runtime-worker-overrides.yaml` file had been mistaken for an absent surface. The correction followed repository truth and did not change production routing or authority.\n\nThe process-lifetime recursion-resistance slice passed corrected executable Reference Implementation CI #658 with **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. The research authority binds a root dispatch and immutable recursion limits to TEO-side state, uses revision-bound stateless HMAC admission claims, and preserves consumed descendant/spawn budget across release and recovery. This does not prove restart-durable or distributed recursion coordination, remote host authenticity, production scheduler containment, or compromised-host resistance."
)
replace_once(
    README,
    "dynamic authority-surface discovery for executable hooks, plugins/loaders, and constructed paths, recursion/recovery failure paths, and independent review against a parallel routing or authority plane.",
    "dynamic authority-surface discovery for executable hooks, plugins/loaders, and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane."
)
replace_once(
    README,
    "[`research/runtime/host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md), and [`research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md).",
    "[`research/runtime/host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md), [`research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), and [`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md)."
)
replace_once(
    README,
    "The static runtime-wired authority-surface reconciliation research head passed Reference Implementation CI #644 with **842 tests**, **525 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. It remains non-normative evidence and leaves dynamic executable-hook and plugin discovery, transitive-code identity, and production authenticity open.",
    "The static runtime-wired authority-surface reconciliation research head passed Reference Implementation CI #644 with **842 tests**, **525 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. It remains non-normative evidence and leaves dynamic executable-hook and plugin discovery, transitive-code identity, and production authenticity open.\n\nThe corrected process-lifetime recursion-resistance research head passed Reference Implementation CI #658 with **863 tests**, **528 tracked-file layout checks**, **41 parsed JSON Schemas**, regulated specialist evidence validation, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. It remains non-normative evidence and leaves restart-durable and distributed recursion coordination, production scheduler containment, remote host identity/authenticity, and compromised-host bypass resistance open."
)

# Host Integration roadmap: evidence list, recursion design status, evidence table, gate status, and validation chain.
replace_once(
    ROADMAP,
    "- [`../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), runtime-derived reconciliation of statically wired authority configuration and policy surfaces, with dynamic executable-hook discovery explicitly kept open.",
    "- [`../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), runtime-derived reconciliation of statically wired authority configuration and policy surfaces, with dynamic executable-hook discovery explicitly kept open;\n- [`../runtime/host-integration-recursion-resistance-2026-08-14.md`](../runtime/host-integration-recursion-resistance-2026-08-14.md), process-lifetime root-scoped recursion admission with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings."
)
replace_once(
    ROADMAP,
    "orchestration_budget:\n  maximum_teo_reentry_depth: 1\n  maximum_specialist_spawns: <bounded>\n  maximum_parallel_branches: <bounded>\n  maximum_attempts: <bounded>\n  deadline: <optional>\n  normalized_usage_budget: <optional>\n  source_backed_cost_budget: <optional>",
    "orchestration_budget:\n  maximum_teo_reentry_depth: 1\n  maximum_descendants: <bounded>\n  maximum_specialist_spawns: <bounded>\n  maximum_parallel_branches: <bounded>\n  maximum_recovery_generations: <bounded>\n  maximum_attempts: <bounded>\n  deadline: <optional>\n  normalized_usage_budget: <optional>\n  source_backed_cost_budget: <optional>"
)
replace_once(
    ROADMAP,
    "Recursion and recovery failure behavior remain open evidence gates.",
    "Process-lifetime recursion admission is now supported at the non-normative research layer. The tested TEO-side authority binds one root dispatch to immutable re-entry depth, total descendant, specialist-spawn, active-branch, and recovery-generation ceilings. Descendant admission uses stateless HMAC-bound claims tied to the exact root revision so host forgery, replay, stale claims, cross-root reuse, release-based budget reset, and raced same-revision claims fail closed. Same-dispatch provider retry remains governed separately by the existing retry policy. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host recursion/recovery boundaries remain open."
)
replace_once(
    ROADMAP,
    "| Authority-surface reconciliation | **Static runtime-wired slice satisfied** | runtime-derived canonical YAML/JSON authority paths, presence and content fingerprinting, exact declaration reconciliation, and tested stale/omitted/extra/aliased path resistance; dynamic executable hooks/plugins/transitive code remain open |",
    "| Authority-surface reconciliation | **Static runtime-wired slice satisfied** | runtime-derived canonical YAML/JSON authority paths, presence and content fingerprinting, exact declaration reconciliation, and tested stale/omitted/extra/aliased path resistance; dynamic executable hooks/plugins/transitive code remain open |\n| Recursion resistance | **Process-lifetime slice satisfied** | root dispatch/budget binding with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC authorization plus replay/stale/cross-root/race/release-reset resistance; restart-durable, distributed, scheduler, and compromised-host boundaries remain open |"
)
replace_once(
    ROADMAP,
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, and #644.",
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, and #658."
)
replace_once(
    ROADMAP,
    "12. **Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**",
    "12. **Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Process-lifetime slice satisfied by the 2026-08-14 recursion-resistance harness and CI #658; restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open.**"
)
replace_once(
    ROADMAP,
    "  orchestration_budget:\n    maximum_teo_reentry_depth: 1\n    maximum_specialist_spawns: <int>\n    maximum_parallel_branches: <int>",
    "  orchestration_budget:\n    maximum_teo_reentry_depth: 1\n    maximum_descendants: <int>\n    maximum_specialist_spawns: <int>\n    maximum_parallel_branches: <int>\n    maximum_recovery_generations: <int>"
)

# Tracker: executable Host Integration proof, bounded recursion state, NOW history, LATER status, and evidence link.
replace_once(
    TRACKER,
    "| Host-integration research validation | CI #644: 842 tests, 525 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the executable authority-surface research head |",
    "| Host-integration research validation | CI #658: 863 tests, 528 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected executable process-lifetime recursion-resistance research head |"
)
replace_once(
    TRACKER,
    "brokered conformant process-lifetime cross-process authority/replay resistance, and static runtime-wired authority-surface reconciliation research slices satisfied; contract remains non-normative and production/dynamic/distributed authenticity remains open",
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, and process-lifetime recursion-resistance research slices satisfied; contract remains non-normative and restart-durable/distributed recursion, production scheduler containment, dynamic authority discovery, and production/distributed authenticity remain open"
)
replace_once(
    TRACKER,
    "brokered conformant process-lifetime cross-process authority/replay resistance, or static runtime-wired authority-surface reconciliation research slices does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage. Dynamic executable-hook discovery, production/distributed authenticity, host identity, effect-evidence, restart, and remote-transport gates remain open.",
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, or process-lifetime recursion-resistance research slices does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage. Dynamic executable-hook discovery, production/distributed authenticity, host identity, effect-evidence, restart-durable/distributed recursion state, production scheduler containment, and remote-transport gates remain open."
)
replace_once(
    TRACKER,
    "This supports only static runtime-wired YAML/JSON authority-surface reconciliation; dynamic path construction, arbitrary executable hooks/plugins/loaders, transitive code identity, signer/origin authenticity, and compromised-host bypass resistance remain open. See [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md).",
    "This supports only static runtime-wired YAML/JSON authority-surface reconciliation; dynamic path construction, arbitrary executable hooks/plugins/loaders, transitive code identity, signer/origin authenticity, and compromised-host bypass resistance remain open. See [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md).\n\nThe next provider-independent Host Integration slice then bounded process-lifetime orchestration recursion independently from same-dispatch provider retry. A TEO-side root authority binds the exact dispatch snapshot to immutable ceilings for re-entry depth, total descendants, specialist spawns, concurrently active descendant branches, and recovery generations. A Security and Authority Boundaries review removed an unnecessary pending-authorization store before acceptance; the corrected design uses stateless HMAC-bound admission claims tied to the exact root revision. Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Tested forgery, replay, stale claims, cross-root reuse, release-based budget reset, recursive recovery, and raced same-revision claims fail closed. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open. See [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md)."
)
replace_once(
    TRACKER,
    "The candidate Host Integration Contract has completed its two-host architecture-diversity research gate, the bounded-context static-payload slice, process-local dispatch provenance, bundled-adapter payload self-expansion testing, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, a brokered conformant process-lifetime cross-process authority/replay slice, and a static runtime-wired authority-surface reconciliation slice.",
    "The candidate Host Integration Contract has completed its two-host architecture-diversity research gate, the bounded-context static-payload slice, process-local dispatch provenance, bundled-adapter payload self-expansion testing, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, a brokered conformant process-lifetime cross-process authority/replay slice, a static runtime-wired authority-surface reconciliation slice, and a process-lifetime recursion-resistance slice."
)
replace_once(
    TRACKER,
    "dynamic authority-surface discovery for executable hooks/plugins/loaders and constructed paths, recursion/recovery failure behavior, and independent review against a parallel routing or authority plane.",
    "dynamic authority-surface discovery for executable hooks/plugins/loaders and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane."
)
replace_once(
    TRACKER,
    "- [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md): runtime-derived static authority-surface reconciliation, red-canary correction, CI #644 evidence, and remaining dynamic executable-hook boundary",
    "- [`../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](../../research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md): runtime-derived static authority-surface reconciliation, red-canary correction, CI #644 evidence, and remaining dynamic executable-hook boundary\n- [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md): process-lifetime recursion admission, security-review hardening, CI #658 evidence, and remaining restart/distributed/scheduler boundary"
)

# Public-summary truth canary.
replace_once(HOST_TEST, '"eight provider-independent adversarial slices",', '"nine provider-independent adversarial slices",')
replace_once(HOST_TEST, '"Reference Implementation CI #644",', '"Reference Implementation CI #658",')
replace_once(HOST_TEST, '"842 automated tests",', '"863 automated tests",')
replace_once(HOST_TEST, '"525 tracked-file layout checks",', '"528 tracked-file layout checks",')
replace_once(
    HOST_TEST,
    '        "static runtime-wired authority-surface reconciliation",\n',
    '        "static runtime-wired authority-surface reconciliation",\n        "process-lifetime recursion resistance",\n'
)
replace_once(
    HOST_TEST,
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n',
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n'
)
replace_once(
    HOST_TEST,
    '    assert "seven provider-independent adversarial slices" not in text\n',
    '    assert "eight provider-independent adversarial slices" not in text\n    assert "seven provider-independent adversarial slices" not in text\n'
)
replace_once(
    HOST_TEST,
    '        "CI #644",\n',
    '        "CI #644",\n        "Recursion resistance",\n        "Process-lifetime slice satisfied",\n        "CI #658",\n'
)
replace_once(
    HOST_TEST,
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n',
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n'
)
replace_once(
    HOST_TEST,
    '    assert "Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Open.**" not in text\n',
    '    assert "Authority-surface reconciliation:** derive or reconcile authority surfaces against executable runtime wiring and fail on omissions. **Open.**" not in text\n    assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text\n'
)

# Broader documentation truth canary. Keep current validated scale on CI #651 until a fully reconciled docs tree proves a newer scale.
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_CI_RUN = 644", "EXPECTED_HOST_INTEGRATION_CI_RUN = 658")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TESTS = 842", "EXPECTED_HOST_INTEGRATION_TESTS = 863")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 525", "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 528")
replace_once(
    DOC_TEST,
    '        "static runtime-wired authority-surface reconciliation",\n',
    '        "static runtime-wired authority-surface reconciliation",\n        "process-lifetime recursion-resistance",\n'
)
replace_once(
    DOC_TEST,
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n',
    '        "host-integration-authority-surface-reconciliation-2026-08-14.md",\n        "host-integration-recursion-resistance-2026-08-14.md",\n'
)
replace_once(
    DOC_TEST,
    '        "Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644",\n',
    '        "Exact corrected head `9cc5694474d310bc50bac1aa342b61f45fb17e10` then passed CI #644",\n        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",\n'
)

subprocess.run(
    [
        "git",
        "diff",
        "--",
        README,
        ROADMAP,
        TRACKER,
        HOST_TEST,
        DOC_TEST,
    ],
    check=True,
    stdout=Path("recursion-doc-reconciliation.diff").open("w", encoding="utf-8"),
)
