from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    target = Path(path)
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}: {old[:160]!r}"
        )
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


README = "README.md"
ROADMAP = "research/roadmaps/host-integration-contract.md"
TRACKER = "docs/stewardship/progress-tracker.md"
HOST_TEST = "tests/test_host_integration_summary_truth.py"
DOC_TEST = "tests/test_documentation_control_plane_truth.py"

# README: advance only the non-normative Host Integration research summary.
replace_once(
    README,
    "The latest Host Integration executable research validation is Reference Implementation CI #658: **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the process-lifetime recursion-resistance slice after a Security and Authority Boundaries review replaced an unnecessary pending-authorization store with stateless HMAC-bound admission claims. It remains non-normative evidence and does not close restart-durable or distributed recursion state, production scheduler containment, compromised-host bypass, dynamic executable-hook discovery, transitive-code identity, or production authenticity boundaries.",
    "The latest Host Integration executable research validation is Reference Implementation CI #678: **891 automated tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the corrected exact local freshness-binding slice after red-canary CI #676 exposed a typed YAML date scalar that the first fingerprint encoder could not canonicalize. The correction preserves date-versus-string type identity rather than flattening values to text. It remains non-normative evidence and does not close production compatibility-catalog provenance, remote freshness authenticity, downgrade resistance, distributed freshness coordination, dynamic executable-hook discovery, transitive-code identity, or production authenticity boundaries."
)
replace_once(
    README,
    "Since those validation rounds, nine provider-independent adversarial slices have converted several previously open integration questions into executable evidence:",
    "Since those validation rounds, ten provider-independent adversarial slices have converted several previously open integration questions into executable evidence:"
)
replace_once(
    README,
    "- process-lifetime recursion resistance binds one root dispatch to immutable depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC-bound admission claims reject tested forgery, replay, stale-state claims, cross-root reuse, release-based budget reset, and raced same-revision claims while restart-durable, distributed, production-scheduler, and compromised-host boundaries remain open.",
    "- process-lifetime recursion resistance binds one root dispatch to immutable depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC-bound admission claims reject tested forgery, replay, stale-state claims, cross-root reuse, release-based budget reset, and raced same-revision claims while restart-durable, distributed, production-scheduler, and compromised-host boundaries remain open;\n- exact local freshness binding derives release/runtime/revision plus authority-surface and effective routing, registry, model, evidence, and executable-composition fingerprints; it rejects tested unknown, mixed, malformed, stale, and host-mislabeled snapshots while production compatibility-catalog provenance, remote authenticity, downgrade resistance, and distributed freshness remain open."
)
replace_once(
    README,
    "The process-lifetime recursion-resistance slice passed corrected executable Reference Implementation CI #658 with **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. The research authority binds a root dispatch and immutable recursion limits to TEO-side state, uses revision-bound stateless HMAC admission claims, and preserves consumed descendant/spawn budget across release and recovery. This does not prove restart-durable or distributed recursion coordination, remote host authenticity, production scheduler containment, or compromised-host resistance.\n\nBefore normative promotion, remaining evidence includes provider/model input economics, end-to-end latency and task adherence, production-grade external-adapter package provenance and authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch and exact-action authenticity/replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, revision freshness and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks, plugins/loaders, and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane.",
    "The process-lifetime recursion-resistance slice passed corrected executable Reference Implementation CI #658 with **863 automated tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. The research authority binds a root dispatch and immutable recursion limits to TEO-side state, uses revision-bound stateless HMAC admission claims, and preserves consumed descendant/spawn budget across release and recovery. This does not prove restart-durable or distributed recursion coordination, remote host authenticity, production scheduler containment, or compromised-host resistance.\n\nThe exact local freshness-binding slice first produced red-canary CI #676: repository layout and compilation passed, but pytest ended with **863 passed and 26 errors** because a YAML date scalar loaded as a typed Python date and falsified the first encoder's assumption that effective configuration was directly JSON serializable. The correction uses deterministic typed canonicalization, so a YAML date remains distinct from an ordinary string with the same visible text and unsupported value types fail closed. Corrected Reference Implementation CI #678 passed **891 automated tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. This supports exact local current, compatible, update-available, stale-unsupported, and mismatched classification only; a production compatibility catalog and its provenance remain unproven.\n\nBefore normative promotion, remaining evidence includes provider/model input economics, end-to-end latency and task adherence, production-grade external-adapter package provenance and authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch and exact-action authenticity/replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, production compatibility-catalog provenance and governance, remote freshness authenticity, downgrade resistance, distributed/restart-durable freshness coordination and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks, plugins/loaders, and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane."
)
replace_once(
    README,
    "[`research/runtime/host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md), [`research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), and [`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md).",
    "[`research/runtime/host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md), [`research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md), [`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md), and [`research/runtime/host-integration-freshness-binding-2026-08-14.md`](research/runtime/host-integration-freshness-binding-2026-08-14.md)."
)

# Host Integration roadmap: add executable local freshness evidence without promoting production freshness.
replace_once(
    ROADMAP,
    "- [`../runtime/host-integration-recursion-resistance-2026-08-14.md`](../runtime/host-integration-recursion-resistance-2026-08-14.md), process-lifetime root-scoped recursion admission with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings.",
    "- [`../runtime/host-integration-recursion-resistance-2026-08-14.md`](../runtime/host-integration-recursion-resistance-2026-08-14.md), process-lifetime root-scoped recursion admission with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings;\n- [`../runtime/host-integration-freshness-binding-2026-08-14.md`](../runtime/host-integration-freshness-binding-2026-08-14.md), exact local freshness classification bound to release/runtime/revision plus authority-surface and effective routing/registry/model/composition fingerprints."
)
replace_once(
    ROADMAP,
    "A revision pin and a freshness judgment are separate claims. A host may intentionally remain on a reproducible compatible revision while a newer TEO revision exists. The integration should state that condition explicitly rather than calling every valid pin current.",
    "A revision pin and a freshness judgment are separate claims. A host may intentionally remain on a reproducible compatible revision while a newer TEO revision exists. The integration should state that condition explicitly rather than calling every valid pin current.\n\nExact local classification is now executable at the non-normative research layer. The TEO-side harness derives an exact current binding and classifies host snapshots only against an authority-owned current binding plus explicitly recorded historical bindings as `PINNED_CURRENT`, `PINNED_COMPATIBLE`, `UPDATE_AVAILABLE`, `STALE_UNSUPPORTED`, or `MISMATCHED`. CI #676 preserved a red canary when a typed YAML date exposed a naïve JSON-fingerprinting assumption; typed canonicalization corrected that issue without collapsing dates into strings, and CI #678 passed the corrected slice. Production compatibility-catalog provenance, remote authenticity, downgrade resistance, distributed freshness coordination, and automated update authority remain open."
)
replace_once(
    ROADMAP,
    "| Recursion resistance | **Process-lifetime slice satisfied** | root dispatch/budget binding with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC authorization plus replay/stale/cross-root/race/release-reset resistance; restart-durable, distributed, scheduler, and compromised-host boundaries remain open |",
    "| Recursion resistance | **Process-lifetime slice satisfied** | root dispatch/budget binding with depth, descendant, specialist-spawn, active-branch, and recovery-generation ceilings; stateless HMAC authorization plus replay/stale/cross-root/race/release-reset resistance; restart-durable, distributed, scheduler, and compromised-host boundaries remain open |\n| Freshness binding | **Exact local classification slice satisfied** | current/compatible/update-available/stale-unsupported/mismatched classification from exact authority-owned bindings; typed configuration canonicalization and tested mixed/unknown/host-mislabeled rejection; production catalog provenance, remote authenticity, downgrade, expiry, and distributed coordination remain open |"
)
replace_once(
    ROADMAP,
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, and #658. CI evidence proves the tested repository research boundary only; it does not promote the contract into normative runtime authority.",
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, #658, and corrected freshness validation CI #678. Red-canary CI #676 is retained as evidence that the first freshness encoder failed on a typed YAML date before typed canonicalization was introduced. CI evidence proves the tested repository research boundary only; it does not promote the contract into normative runtime authority."
)
replace_once(
    ROADMAP,
    "13. **Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected. **Open.**",
    "13. **Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected. **Exact local stale/mismatch detection slice satisfied by the 2026-08-14 freshness-binding harness and corrected CI #678; production compatibility-catalog provenance, remote authenticity, downgrade resistance, expiry, and distributed coordination remain open.**"
)
replace_once(
    ROADMAP,
    "19. **Integration freshness state:** distinguish current, compatible, update-available, unsupported, and mismatched TEO pins/vendorized copies. **Open.**",
    "19. **Integration freshness state:** distinguish current, compatible, update-available, unsupported, and mismatched TEO pins/vendorized copies. **Exact local classification semantics satisfied by the 2026-08-14 freshness-binding harness and corrected CI #678; production catalog governance/provenance, remote authenticity, downgrade resistance, expiry, and distributed coordination remain open.**"
)
replace_once(
    ROADMAP,
    "- **Specialist Execution Envelope:** host embedding now has concrete process-local and brokered process-lifetime evidence for scoped context, dispatch authorization, exact action binding, replay resistance on the conformant path, verifier-context separation, and static runtime-wired authority-surface reconciliation.",
    "- **Specialist Execution Envelope:** host embedding now has concrete process-local and brokered process-lifetime evidence for scoped context, dispatch authorization, exact action binding, replay resistance on the conformant path, verifier-context separation, static runtime-wired authority-surface reconciliation, and exact local freshness binding."
)

# Progress Tracker: record freshness proof while preserving the live-execution sequencing.
replace_once(
    TRACKER,
    "| Host-integration research validation | CI #658: 863 tests, 528 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected executable process-lifetime recursion-resistance research head |",
    "| Host-integration research validation | CI #678: 891 tests, 532 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected executable exact local freshness-binding research head |"
)
replace_once(
    TRACKER,
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, and process-lifetime recursion-resistance research slices satisfied; contract remains non-normative and restart-durable/distributed recursion, production scheduler containment, dynamic authority discovery, and production/distributed authenticity remain open",
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, process-lifetime recursion resistance, and exact local freshness-binding research slices satisfied; contract remains non-normative and production compatibility-catalog provenance, remote/distributed freshness authenticity, downgrade/expiry, restart-durable/distributed recursion, production scheduler containment, dynamic authority discovery, and production/distributed authenticity remain open"
)
replace_once(
    TRACKER,
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, or process-lifetime recursion-resistance research slices does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage. Dynamic executable-hook discovery, production/distributed authenticity, host identity, effect-evidence, restart-durable/distributed recursion state, production scheduler containment, and remote-transport gates remain open.",
    "brokered conformant process-lifetime cross-process authority/replay resistance, static runtime-wired authority-surface reconciliation, process-lifetime recursion resistance, or exact local freshness-binding research slices does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage. Dynamic executable-hook discovery, production/distributed authenticity, host identity, effect-evidence, production compatibility-catalog provenance, remote freshness authenticity, downgrade/expiry, distributed freshness coordination, restart-durable/distributed recursion state, production scheduler containment, and remote-transport gates remain open."
)
replace_once(
    TRACKER,
    "The next provider-independent Host Integration slice then bounded process-lifetime orchestration recursion independently from same-dispatch provider retry. A TEO-side root authority binds the exact dispatch snapshot to immutable ceilings for re-entry depth, total descendants, specialist spawns, concurrently active descendant branches, and recovery generations. A Security and Authority Boundaries review removed an unnecessary pending-authorization store before acceptance; the corrected design uses stateless HMAC-bound admission claims tied to the exact root revision. Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Tested forgery, replay, stale claims, cross-root reuse, release-based budget reset, recursive recovery, and raced same-revision claims fail closed. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open. See [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md).",
    "The next provider-independent Host Integration slice then bounded process-lifetime orchestration recursion independently from same-dispatch provider retry. A TEO-side root authority binds the exact dispatch snapshot to immutable ceilings for re-entry depth, total descendants, specialist spawns, concurrently active descendant branches, and recovery generations. A Security and Authority Boundaries review removed an unnecessary pending-authorization store before acceptance; the corrected design uses stateless HMAC-bound admission claims tied to the exact root revision. Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Tested forgery, replay, stale claims, cross-root reuse, release-based budget reset, recursive recovery, and raced same-revision claims fail closed. Restart-durable, multi-process/distributed, production-scheduler, remote-authenticity, and compromised-host boundaries remain open. See [`../../research/runtime/host-integration-recursion-resistance-2026-08-14.md`](../../research/runtime/host-integration-recursion-resistance-2026-08-14.md).\n\nThe following provider-independent Host Integration slice made exact local integration freshness classification executable. The TEO-side research binding combines release, runtime version, exact revision, runtime-derived authority-surface identity, and effective Team, implementation, Worker, Specialist, Capability, model, model-evidence, and executable-composition fingerprints. Red-canary CI #676 preserved a real research assumption failure: repository layout and compilation passed, but pytest ended with **863 passed and 26 errors** because a typed YAML date scalar could not be encoded by the first naïve JSON fingerprint path. The correction uses deterministic typed canonicalization so dates and same-text strings remain distinct, unsupported value types fail closed, and malformed historical catalog bindings are rejected explicitly. Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Exact local `PINNED_CURRENT`, `PINNED_COMPATIBLE`, `UPDATE_AVAILABLE`, `STALE_UNSUPPORTED`, and `MISMATCHED` semantics are now supported by research evidence, while production compatibility-catalog provenance, remote authenticity, downgrade resistance, expiry, distributed freshness coordination, and automatic update authority remain open. See [`../../research/runtime/host-integration-freshness-binding-2026-08-14.md`](../../research/runtime/host-integration-freshness-binding-2026-08-14.md)."
)
replace_once(
    TRACKER,
    "The candidate Host Integration Contract has completed its two-host architecture-diversity research gate, the bounded-context static-payload slice, process-local dispatch provenance, bundled-adapter payload self-expansion testing, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, a brokered conformant process-lifetime cross-process authority/replay slice, a static runtime-wired authority-surface reconciliation slice, and a process-lifetime recursion-resistance slice.",
    "The candidate Host Integration Contract has completed its two-host architecture-diversity research gate, the bounded-context static-payload slice, process-local dispatch provenance, bundled-adapter payload self-expansion testing, process-local third-party adapter trust, restrictive host/TEO authority intersection and host execution-scope binding, exact host execution-envelope integrity, verifier-context independence, exact artifact/change-set stale-PASS resistance, a brokered conformant process-lifetime cross-process authority/replay slice, a static runtime-wired authority-surface reconciliation slice, a process-lifetime recursion-resistance slice, and an exact local freshness-binding slice."
)
replace_once(
    TRACKER,
    "The contract remains non-normative. Before any schema or reference-runtime promotion, remaining evidence includes provider/model input economics, end-to-end latency, task adherence, production-grade external-adapter package provenance, authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch/exact-action authenticity and replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, revision freshness and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks/plugins/loaders and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane.",
    "The contract remains non-normative. Before any schema or reference-runtime promotion, remaining evidence includes provider/model input economics, end-to-end latency, task adherence, production-grade external-adapter package provenance, authority-controlled loading, dependency/transitive-code identity, revocation/update and downgrade semantics, distributed host/TEO authority synchronization, production resource-target canonicalization and containment, credential/account/tenant scope binding, production-grade remote or distributed dispatch/exact-action authenticity and replay beyond the brokered conformant process-lifetime path, result/effect receipt authenticity, restart-durable and distributed retry-budget coordination, production compatibility-catalog provenance/governance, remote freshness authenticity, downgrade resistance, expiry semantics, distributed/restart-durable freshness coordination, portfolio/task-admission authority separation, dynamic authority-surface discovery for executable hooks/plugins/loaders and constructed paths, restart-durable and distributed recursion state, production scheduler recursion/recovery containment, and independent review against a parallel routing or authority plane."
)
replace_once(
    TRACKER,
    "The next bounded provider-independent Host Integration gate should be selected from the remaining roadmap evidence, now narrowed to those genuinely open production, distributed, economic, freshness, dynamic-authority-surface, effect-evidence, and recursion/recovery requirements.",
    "The next bounded provider-independent Host Integration gate should be selected from the remaining roadmap evidence, now narrowed to those genuinely open production, distributed, economic, production-freshness, dynamic-authority-surface, effect-evidence, and recursion/recovery requirements."
)

# Host Integration summary canary: require the new local freshness evidence and reject stale summary text.
replace_once(HOST_TEST, '"nine provider-independent adversarial slices",', '"ten provider-independent adversarial slices",')
replace_once(HOST_TEST, '"Reference Implementation CI #658",', '"Reference Implementation CI #678",')
replace_once(HOST_TEST, '"863 automated tests",', '"891 automated tests",')
replace_once(HOST_TEST, '"528 tracked-file layout checks",', '"532 tracked-file layout checks",')
replace_once(
    HOST_TEST,
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "process-lifetime recursion resistance",',
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "host-integration-freshness-binding-2026-08-14.md",\n        "process-lifetime recursion resistance",\n        "exact local freshness binding",\n        "red-canary CI #676",'
)
replace_once(
    HOST_TEST,
    '    assert "eight provider-independent adversarial slices" not in text\n    assert "seven provider-independent adversarial slices" not in text',
    '    assert "nine provider-independent adversarial slices" not in text\n    assert "eight provider-independent adversarial slices" not in text\n    assert "seven provider-independent adversarial slices" not in text'
)
replace_once(
    HOST_TEST,
    '        "CI #658",\n        "host-integration-verifier-artifact-binding-2026-08-12.md",',
    '        "CI #658",\n        "Freshness binding",\n        "Exact local classification slice satisfied",\n        "CI #678",\n        "host-integration-verifier-artifact-binding-2026-08-12.md",'
)
replace_once(
    HOST_TEST,
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "dynamic executable hooks/plugins/transitive code remain open",',
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "host-integration-freshness-binding-2026-08-14.md",\n        "dynamic executable hooks/plugins/transitive code remain open",'
)
replace_once(
    HOST_TEST,
    '    assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text',
    '    assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text\n    assert "Registry freshness:** prove stale or mismatched TEO release, policy, registry, overlay, or executable-composition bindings are detected. **Open.**" not in text\n    assert "Integration freshness state:** distinguish current, compatible, update-available, unsupported, and mismatched TEO pins/vendorized copies. **Open.**" not in text'
)

# Documentation-control truth: point Host Integration evidence to #678 while leaving current-scale baseline for later clean reconciliation.
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_CI_RUN = 658", "EXPECTED_HOST_INTEGRATION_CI_RUN = 678")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TESTS = 863", "EXPECTED_HOST_INTEGRATION_TESTS = 891")
replace_once(DOC_TEST, "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 528", "EXPECTED_HOST_INTEGRATION_TRACKED_FILES = 532")
replace_once(
    DOC_TEST,
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "final execution provenance",',
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "host-integration-freshness-binding-2026-08-14.md",\n        "exact local freshness binding",\n        "red-canary CI #676",\n        "final execution provenance",'
)
replace_once(
    DOC_TEST,
    '        "process-lifetime recursion-resistance",\n        "Dynamic executable-hook discovery",',
    '        "process-lifetime recursion-resistance",\n        "exact local freshness-binding",\n        "Dynamic executable-hook discovery",'
)
replace_once(
    DOC_TEST,
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |",',
    '        "host-integration-recursion-resistance-2026-08-14.md",\n        "host-integration-freshness-binding-2026-08-14.md",\n        "| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |",'
)
replace_once(
    DOC_TEST,
    '        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",\n        "production-grade remote or distributed dispatch/exact-action authenticity and replay",',
    '        "Reference Implementation CI #658 passed **863 tests**, **528 tracked-file layout checks**",\n        "red-canary CI #676",\n        "Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",\n        "production-grade remote or distributed dispatch/exact-action authenticity and replay",'
)
