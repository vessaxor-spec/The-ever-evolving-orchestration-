from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def write(path: str, text: str) -> None:
    Path(path).write_text(text, encoding="utf-8")


# README
path = Path("README.md")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "The latest Host Integration executable research validation is Reference Implementation CI #678: **891 automated tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the corrected exact local freshness-binding slice after red-canary CI #676 exposed a typed YAML date scalar that the first fingerprint encoder could not canonicalize. The correction preserves date-versus-string type identity rather than flattening values to text. It remains non-normative evidence and does not close production compatibility-catalog provenance, remote freshness authenticity, downgrade resistance, distributed freshness coordination, dynamic executable-hook discovery, transitive-code identity, or production authenticity boundaries.",
    "The latest Host Integration executable research validation is Reference Implementation CI #703: **915 automated tests**, **535 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end reference lifecycle. That run validated the corrected conformant process-local portfolio/task-admission authority-separation slice. Security and Authority Boundaries review found that the first candidate did not bind revalidation to the exact host-issued TEO session identity; the accepted design stores and revalidates that identity, while host queue, priority, admission, cancellation, and revocation authority remain outside the TEO-facing gateway. It remains non-normative evidence and does not close remote/distributed admission authenticity, restart durability, production scheduler integration, tenant/account binding, compromised-host bypass, or distributed duplicate-work prevention.",
    "README latest Host Integration validation",
)
text = replace_once(
    text,
    "Since those validation rounds, ten provider-independent adversarial slices have converted several previously open integration questions into executable evidence:",
    "Since those validation rounds, eleven provider-independent adversarial slices have converted several previously open integration questions into executable evidence:",
    "README adversarial slice count",
)
text = replace_once(
    text,
    "- exact local freshness binding derives release/runtime/revision plus authority-surface and effective routing, registry, model, evidence, and executable-composition fingerprints; it rejects tested unknown, mixed, malformed, stale, and host-mislabeled snapshots while production compatibility-catalog provenance, remote authenticity, downgrade resistance, and distributed freshness remain open.",
    "- exact local freshness binding derives release/runtime/revision plus authority-surface and effective routing, registry, model, evidence, and executable-composition fingerprints; it rejects tested unknown, mixed, malformed, stale, and host-mislabeled snapshots while production compatibility-catalog provenance, remote authenticity, downgrade resistance, and distributed freshness remain open;\n- conformant process-local portfolio/task-admission separation keeps queue, prioritization, admission, cancellation, and revocation state host-owned; TEO can only claim and revalidate one exact host-issued admission bound to portfolio, task payload, admission revision, authorization token, and exact issued session identity, while remote/distributed authenticity, durable admission state, production scheduler integration, tenant binding, and compromised-host bypass remain open.",
    "README portfolio bullet",
)
fresh_para = "The exact local freshness-binding slice first produced red-canary CI #676: repository layout and compilation passed, but pytest ended with **863 passed and 26 errors** because a YAML date scalar loaded as a typed Python date and falsified the first encoder's assumption that effective configuration was directly JSON serializable. The correction uses deterministic typed canonicalization, so a YAML date remains distinct from an ordinary string with the same visible text and unsupported value types fail closed. Corrected Reference Implementation CI #678 passed **891 automated tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. This supports exact local current, compatible, update-available, stale-unsupported, and mismatched classification only; a production compatibility catalog and its provenance remain unproven."
portfolio_para = "The portfolio/task-admission authority-separation slice preserved two distinct negative findings before acceptance. Reference Implementation CI #696 completed with **913 passed and 1 failed** because the sibling-admission test expected a later task-ID mismatch even though the gate correctly failed earlier on admission-ID mismatch. Separately, Security and Authority Boundaries review found that the first candidate did not bind session revalidation to the exact host-issued TEO session identity. The correction stored and revalidated that identity, added a fabricated-session counterexample, and kept the TEO-facing gateway limited to exact admission claim and revalidation. Clean corrected Reference Implementation CI #703 passed **915 automated tests**, **535 tracked-file layout checks**, regulated specialist evidence validation, **41 JSON Schema** parses, valid linked configuration, and the provider-diverse artifact-bound end-to-end lifecycle. This supports conformant process-local separation only; remote/distributed host-admission authenticity, restart durability, production scheduler integration, tenant/account binding, compromised-host bypass, and distributed duplicate-work prevention remain open."
text = replace_once(text, fresh_para, fresh_para + "\n\n" + portfolio_para, "README portfolio evidence paragraph")
text = replace_once(
    text,
    "distributed/restart-durable freshness coordination and expiry semantics, portfolio/task-admission authority separation, dynamic authority-surface discovery",
    "distributed/restart-durable freshness coordination and expiry semantics, production-grade portfolio/task-admission authenticity, durable revocation/admission state, scheduler integration, tenant/account binding, dynamic authority-surface discovery",
    "README remaining portfolio evidence",
)
text = replace_once(
    text,
    "[`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md), and [`research/runtime/host-integration-freshness-binding-2026-08-14.md`](research/runtime/host-integration-freshness-binding-2026-08-14.md).",
    "[`research/runtime/host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md), [`research/runtime/host-integration-freshness-binding-2026-08-14.md`](research/runtime/host-integration-freshness-binding-2026-08-14.md), and [`research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md`](research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md).",
    "README research link",
)
write(str(path), text)


# Host Integration roadmap
path = Path("research/roadmaps/host-integration-contract.md")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "| Freshness binding | **Exact local classification slice satisfied** | current/compatible/update-available/stale-unsupported/mismatched classification from exact authority-owned bindings; typed configuration canonicalization and tested mixed/unknown/host-mislabeled rejection; production catalog provenance, remote authenticity, downgrade, expiry, and distributed coordination remain open |",
    "| Freshness binding | **Exact local classification slice satisfied** | current/compatible/update-available/stale-unsupported/mismatched classification from exact authority-owned bindings; typed configuration canonicalization and tested mixed/unknown/host-mislabeled rejection; production catalog provenance, remote authenticity, downgrade, expiry, and distributed coordination remain open |\n| Portfolio/task-admission authority separation | **Conformant process-local slice satisfied** | host-owned queue, priority, admission, cancellation, and revocation state; exact task/admission/session binding and tested forgery, replay, sibling substitution, cancellation/revocation, widening-field, and duplicate-claim resistance through the TEO-facing gateway; remote/distributed authenticity, restart durability, scheduler integration, tenant binding, and compromised-host bypass remain open |",
    "roadmap evidence row",
)
text = replace_once(
    text,
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, #658, and corrected freshness validation CI #678. Red-canary CI #676 is retained as evidence that the first freshness encoder failed on a typed YAML date before typed canonicalization was introduced. CI evidence proves the tested repository research boundary only; it does not promote the contract into normative runtime authority.",
    "Validation milestones include CI #546, #552, #555, #560, #565, #570/#573, #577/#580, #626, #644, #658, corrected freshness validation CI #678, and corrected portfolio/task-admission validation CI #703. Red-canary CI #676 is retained as evidence that the first freshness encoder failed on a typed YAML date before typed canonicalization was introduced. CI #696 is retained as a portfolio-slice test-assumption canary: 913 tests passed while one sibling-admission assertion expected a later mismatch than the fail-closed gate emitted. Security and Authority Boundaries review separately found and corrected missing exact session-identity binding before acceptance. CI evidence proves the tested repository research boundary only; it does not promote the contract into normative runtime authority.",
    "roadmap validation milestones",
)
text = replace_once(
    text,
    "15. **Portfolio-authority separation:** prove TEO routing cannot silently seize host backlog, product-priority, or task-admission authority unless explicitly delegated. **Research principle established; executable promotion evidence remains open.**",
    "15. **Portfolio-authority separation:** prove TEO routing cannot silently seize host backlog, product-priority, or task-admission authority unless explicitly delegated. **Conformant process-local task-admission separation slice satisfied by the 2026-08-15 research harness and corrected CI #703; remote/distributed admission authenticity, durable revocation/admission state, production scheduler integration, tenant/account binding, distributed duplicate-work prevention, and compromised-host bypass remain open.**",
    "roadmap gate 15",
)
text = replace_once(
    text,
    "- **Specialist Execution Envelope:** host embedding now has concrete process-local and brokered process-lifetime evidence for scoped context, dispatch authorization, exact action binding, replay resistance on the conformant path, verifier-context separation, static runtime-wired authority-surface reconciliation, and exact local freshness binding.",
    "- **Specialist Execution Envelope:** host embedding now has concrete process-local and brokered process-lifetime evidence for scoped context, dispatch authorization, exact action binding, replay resistance on the conformant path, verifier-context separation, static runtime-wired authority-surface reconciliation, exact local freshness binding, and host-owned portfolio/task-admission separation through a bounded TEO-facing gateway.",
    "roadmap relationship portfolio",
)
write(str(path), text)


# Progress Tracker
path = Path("docs/stewardship/progress-tracker.md")
text = path.read_text(encoding="utf-8")
text = replace_once(
    text,
    "| Host-integration research validation | CI #678: 891 tests, 532 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected executable exact local freshness-binding research head |",
    "| Host-integration research validation | CI #703: 915 tests, 535 tracked-file layout checks, 41 schemas, valid linked configuration, regulated-specialist evidence pass, provider-diverse artifact-bound end-to-end pass on the corrected conformant process-local portfolio/task-admission authority-separation research head |",
    "tracker Host Integration validation",
)
text = replace_once(
    text,
    "process-lifetime recursion resistance, and exact local freshness-binding research slices satisfied;",
    "process-lifetime recursion resistance, exact local freshness-binding, and conformant process-local portfolio/task-admission authority-separation research slices satisfied;",
    "tracker Host Integration snapshot",
)
text = replace_once(
    text,
    "process-lifetime recursion resistance, or exact local freshness-binding research slices does not promote it ahead",
    "process-lifetime recursion resistance, exact local freshness-binding, or conformant process-local portfolio/task-admission authority-separation research slices does not promote it ahead",
    "tracker non-scored research paragraph",
)
fresh_tracker = "The following provider-independent Host Integration slice made exact local integration freshness classification executable. The TEO-side research binding combines release, runtime version, exact revision, runtime-derived authority-surface identity, and effective Team, implementation, Worker, Specialist, Capability, model, model-evidence, and executable-composition fingerprints. Red-canary CI #676 preserved a real research assumption failure: repository layout and compilation passed, but pytest ended with **863 passed and 26 errors** because a typed YAML date scalar could not be encoded by the first naïve JSON fingerprint path. The correction uses deterministic typed canonicalization so dates and same-text strings remain distinct, unsupported value types fail closed, and malformed historical catalog bindings are rejected explicitly. Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. Exact local `PINNED_CURRENT`, `PINNED_COMPATIBLE`, `UPDATE_AVAILABLE`, `STALE_UNSUPPORTED`, and `MISMATCHED` semantics are now supported by research evidence, while production compatibility-catalog provenance, remote authenticity, downgrade resistance, expiry, distributed freshness coordination, and automatic update authority remain open. See [`../../research/runtime/host-integration-freshness-binding-2026-08-14.md`](../../research/runtime/host-integration-freshness-binding-2026-08-14.md)."
portfolio_tracker = "The next provider-independent Host Integration slice made portfolio/task-admission authority separation executable on a conformant process-local path. The host research authority retains queue, priority, admission, cancellation, and revocation state and exposes to TEO only exact admission claim and session revalidation. Initial CI #696 preserved a test-assumption canary with **913 passed and 1 failed** because the sibling-admission case expected a task-ID mismatch after the gate had already rejected the admission-ID mismatch. Security and Authority Boundaries review separately found that the first candidate did not bind revalidation to the exact host-issued TEO session identity. The corrected design stores and revalidates that identity and adds an explicit fabricated-session counterexample. Clean corrected Reference Implementation CI #703 passed **915 tests**, **535 tracked-file layout checks**, regulated specialist evidence validation, **41 parsed JSON Schemas**, valid linked configuration with zero issues, and the provider-diverse artifact-bound end-to-end lifecycle. This supports conformant process-local separation only; remote/distributed host-admission authenticity, restart-durable admission/revocation state, production scheduler integration, tenant/account binding, distributed duplicate-work prevention, and compromised-host bypass remain open. See [`../../research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md`](../../research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md)."
text = replace_once(text, fresh_tracker, fresh_tracker + "\n\n" + portfolio_tracker, "tracker portfolio history")
text = replace_once(
    text,
    "a process-lifetime recursion-resistance slice, and an exact local freshness-binding slice.",
    "a process-lifetime recursion-resistance slice, an exact local freshness-binding slice, and a conformant process-local portfolio/task-admission authority-separation slice.",
    "tracker LATER slice list",
)
text = replace_once(
    text,
    "distributed/restart-durable freshness coordination, portfolio/task-admission authority separation, dynamic authority-surface discovery",
    "distributed/restart-durable freshness coordination, production-grade portfolio/task-admission authenticity, durable admission/revocation state, scheduler integration, tenant/account binding, distributed duplicate-work prevention, dynamic authority-surface discovery",
    "tracker LATER remaining evidence",
)
write(str(path), text)


# Host Integration summary truth test
path = Path("tests/test_host_integration_summary_truth.py")
text = path.read_text(encoding="utf-8")
text = replace_once(text, '"ten provider-independent adversarial slices",', '"eleven provider-independent adversarial slices",', "summary truth slice count")
text = replace_once(text, '"Reference Implementation CI #678",\n        "891 automated tests",\n        "532 tracked-file layout checks",', '"Reference Implementation CI #703",\n        "915 automated tests",\n        "535 tracked-file layout checks",', "summary truth latest validation")
text = replace_once(text, '"host-integration-freshness-binding-2026-08-14.md",\n        "exact local freshness binding",', '"host-integration-freshness-binding-2026-08-14.md",\n        "host-integration-portfolio-authority-separation-2026-08-15.md",\n        "exact local freshness binding",\n        "portfolio/task-admission separation",', "summary truth portfolio phrases")
text = replace_once(text, 'assert "nine provider-independent adversarial slices" not in text', 'assert "ten provider-independent adversarial slices" not in text\n    assert "nine provider-independent adversarial slices" not in text', "summary stale ten count")
text = replace_once(text, '"CI #678",\n        "host-integration-verifier-artifact-binding-2026-08-12.md",', '"CI #678",\n        "Portfolio-authority separation",\n        "Conformant process-local task-admission separation slice satisfied",\n        "CI #703",\n        "host-integration-portfolio-authority-separation-2026-08-15.md",\n        "host-integration-verifier-artifact-binding-2026-08-12.md",', "roadmap truth portfolio phrases")
text = replace_once(
    text,
    'assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text',
    'assert "Recursion resistance:** mutation-test delegation-depth, spawn-budget, and recovery/re-entry boundaries. **Open.**" not in text\n    assert "Portfolio-authority separation:** prove TEO routing cannot silently seize host backlog, product-priority, or task-admission authority unless explicitly delegated. **Research principle established; executable promotion evidence remains open.**" not in text',
    "roadmap stale portfolio assertion",
)
write(str(path), text)


# Canonical documentation/control-plane truth test
path = Path("tests/test_documentation_control_plane_truth.py")
text = path.read_text(encoding="utf-8")
text = replace_once(text, "EXPECTED_HOST_INTEGRATION_CI_RUN = 678\nEXPECTED_HOST_INTEGRATION_TESTS = 891\nEXPECTED_HOST_INTEGRATION_TRACKED_FILES = 532", "EXPECTED_HOST_INTEGRATION_CI_RUN = 703\nEXPECTED_HOST_INTEGRATION_TESTS = 915\nEXPECTED_HOST_INTEGRATION_TRACKED_FILES = 535", "control-plane Host Integration constants")
text = replace_once(text, '"host-integration-freshness-binding-2026-08-14.md",\n        "exact local freshness binding",', '"host-integration-freshness-binding-2026-08-14.md",\n        "host-integration-portfolio-authority-separation-2026-08-15.md",\n        "exact local freshness binding",\n        "portfolio/task-admission separation",', "README truth portfolio phrases")
text = replace_once(text, '"process-lifetime recursion-resistance",\n        "exact local freshness-binding",', '"process-lifetime recursion-resistance",\n        "exact local freshness-binding",\n        "portfolio/task-admission authority-separation",', "tracker truth portfolio summary")
text = replace_once(text, '"host-integration-freshness-binding-2026-08-14.md",\n        "| Staged live-scope candidate', '"host-integration-freshness-binding-2026-08-14.md",\n        "host-integration-portfolio-authority-separation-2026-08-15.md",\n        "| Staged live-scope candidate', "tracker truth portfolio link")
text = replace_once(text, '"Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",\n        "production-grade remote', '"Corrected Reference Implementation CI #678 passed **891 tests**, **532 tracked-file layout checks**",\n        "Initial CI #696 preserved a test-assumption canary with **913 passed and 1 failed**",\n        "Clean corrected Reference Implementation CI #703 passed **915 tests**, **535 tracked-file layout checks**",\n        "production-grade remote', "tracker truth CI #703")
write(str(path), text)
