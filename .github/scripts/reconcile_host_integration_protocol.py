from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"guard failed for {path}: expected 1 occurrence, got {count}: {old[:100]!r}"
        )
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


module = "reference/implementations/python/src/teo_reference/host_integration_protocol.py"
replace_once(
    module,
    '''    def __init__(self, dispatch: DispatchRecord, *, max_attempts_per_route: int = 1):
        if isinstance(max_attempts_per_route, bool) or max_attempts_per_route < 1:
            raise HostIntegrationProtocolError("max_attempts_per_route must be positive")
''',
    '''    def __init__(self, dispatch: DispatchRecord, *, max_attempts_per_route: int = 1):
        if (
            isinstance(max_attempts_per_route, bool)
            or not isinstance(max_attempts_per_route, int)
            or max_attempts_per_route < 1
        ):
            raise HostIntegrationProtocolError(
                "max_attempts_per_route must be a positive integer"
            )
''',
)
replace_once(
    module,
    '''    def issue_execution(self, *, route_role: RouteRole = "primary", attempt: int = 1) -> HostExecutionInstruction:
''',
    '''    def _has_unresolved_execution(self) -> bool:
        return any(key not in self._accepted_execution for key in self._issued_attempts)

    def _has_successful_execution(self) -> bool:
        return any(
            receipt.status == "succeeded"
            for receipt in self._accepted_execution.values()
        )

    def _fallback_was_issued(self) -> bool:
        return any(role == "fallback" for role, _ in self._issued_attempts)

    def issue_execution(self, *, route_role: RouteRole = "primary", attempt: int = 1) -> HostExecutionInstruction:
''',
)
replace_once(
    module,
    '''        key = (route_role, attempt)
        if key in self._issued_attempts:
            raise HostIntegrationProtocolError("execution attempt was already issued")

        if route_role == "fallback":
''',
    '''        key = (route_role, attempt)
        if key in self._issued_attempts:
            raise HostIntegrationProtocolError("execution attempt was already issued")
        if self._issued_verification or self._verification_receipt is not None:
            raise HostIntegrationProtocolError(
                "execution phase is closed after verification has started"
            )
        if self._has_successful_execution():
            raise HostIntegrationProtocolError(
                "execution phase is closed after a successful execution receipt"
            )
        if route_role == "primary" and self._fallback_was_issued():
            raise HostIntegrationProtocolError(
                "primary route is closed after fallback issuance"
            )
        if self._has_unresolved_execution():
            raise HostIntegrationProtocolError(
                "previous execution instruction remains unresolved"
            )

        if route_role == "fallback":
''',
)
replace_once(
    module,
    '''        if instruction is None:
            raise HostIntegrationProtocolError("execution receipt references an unknown instruction")
        instruction.validate_integrity()
''',
    '''        if instruction is None:
            raise HostIntegrationProtocolError("execution receipt references an unknown instruction")
        if isinstance(receipt.attempt, bool) or not isinstance(receipt.attempt, int):
            raise HostIntegrationProtocolError("execution receipt attempt must be an integer")
        instruction.validate_integrity()
''',
)

tests = Path("tests/test_host_integration_protocol.py")
test_text = tests.read_text(encoding="utf-8")
test_text += '''


def test_retry_budget_requires_positive_integer():
    for budget in (True, 0, -1, 1.5, "2", None):
        with pytest.raises(HostIntegrationProtocolError, match="positive integer"):
            HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=budget)


def test_execution_receipt_boolean_attempt_is_rejected():
    session = HostIntegrationProtocolSession(_dispatch())
    instruction = session.issue_execution()
    receipt = replace(_receipt(instruction), attempt=True)
    with pytest.raises(HostIntegrationProtocolError, match="attempt must be an integer"):
        session.accept_execution(receipt)


def test_outstanding_primary_retry_blocks_fallback_issue():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    first = session.issue_execution()
    session.accept_execution(_receipt(first, status="failed"))
    session.issue_execution(attempt=2)
    with pytest.raises(HostIntegrationProtocolError, match="remains unresolved"):
        session.issue_execution(route_role="fallback")


def test_fallback_transition_closes_primary_route_after_fallback_failure():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary, status="failed"))
    fallback = session.issue_execution(route_role="fallback")
    session.accept_execution(_receipt(fallback, status="failed"))
    with pytest.raises(HostIntegrationProtocolError, match="primary route is closed"):
        session.issue_execution(route_role="primary", attempt=2)


def test_success_terminates_execution_phase_across_routes():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary, status="failed"))
    fallback = session.issue_execution(route_role="fallback")
    session.accept_execution(
        _receipt(
            fallback,
            output_ref="artifact://fallback",
            output_sha256=FALLBACK_SHA,
        )
    )
    with pytest.raises(HostIntegrationProtocolError, match="successful execution"):
        session.issue_execution(route_role="primary", attempt=2)


def test_verification_start_closes_execution_phase():
    session = HostIntegrationProtocolSession(_dispatch(), max_attempts_per_route=2)
    primary = session.issue_execution()
    session.accept_execution(_receipt(primary))
    session.issue_verification()
    with pytest.raises(HostIntegrationProtocolError, match="verification has started"):
        session.issue_execution(route_role="fallback")
'''
tests.write_text(test_text, encoding="utf-8")

spec = "docs/specification/host-integration-protocol-candidate.md"
replace_once(
    spec,
    '''For this candidate:

- attempt `n + 1` may be issued only after accepted attempt `n` for the same route failed;
- attempts cannot exceed the TEO-side session ceiling;
- fallback can be issued only after the latest accepted primary attempt failed;
- fallback identity comes only from `DispatchRecord.fallback_implementation`;
- a host cannot introduce an undeclared fallback provider/model through a receipt.
''',
    '''For this candidate:

- the session retry ceiling must be a positive integer;
- only one execution instruction may remain unresolved at a time;
- attempt `n + 1` may be issued only after accepted attempt `n` for the same route failed;
- attempts cannot exceed the TEO-side session ceiling;
- fallback can be issued only after the latest accepted primary attempt failed;
- once any fallback instruction is issued, the primary route cannot reopen within that session;
- once any execution receipt succeeds, the execution phase is terminal;
- once verification begins, no further execution instruction may be issued;
- fallback identity comes only from `DispatchRecord.fallback_implementation`;
- a host cannot introduce an undeclared fallback provider/model through a receipt.
''',
)
replace_once(
    spec,
    '''- TEO-controlled fallback after primary failure;
- sequential bounded retry;
- independent verifier binding;
''',
    '''- TEO-controlled fallback after primary failure;
- sequential bounded retry with a positive-integer budget;
- one unresolved execution instruction at a time;
- monotonic primary-to-fallback progression without route reopening;
- terminal execution after success or verification start;
- independent verifier binding;
''',
)

replace_once(
    "docs/specification/README.md",
    '''## Cross-boundary evidence

- [`final-execution-provenance.md`](final-execution-provenance.md) defines the optional read-only projection from validated Route-Outcome Evidence into a host-consumable `FinalOutcome` without creating routing or execution authority.

## Specification documents
''',
    '''## Cross-boundary evidence

- [`final-execution-provenance.md`](final-execution-provenance.md) defines the optional read-only projection from validated Route-Outcome Evidence into a host-consumable `FinalOutcome` without creating routing or execution authority.

## Host integration reference candidate

- [`host-integration-protocol-candidate.md`](host-integration-protocol-candidate.md) defines the non-normative, non-production `teo-host-integration/0.1` message boundary for TEO-directed host-native execution and independent verification. It does not widen routing, live-execution, provider-access, specialist, or production authority.

## Specification documents
''',
)
replace_once(
    "reference/implementations/README.md",
    '''[`python/README.md`](python/README.md) documents the runnable Python router, provider-adapter boundary, retry/fallback behavior, live verification, finalization, controlled documentation replay, and executable regulated-evidence stability qualification.
''',
    '''[`python/README.md`](python/README.md) documents the runnable Python router, provider-adapter boundary, retry/fallback behavior, live verification, finalization, controlled documentation replay, executable regulated-evidence stability qualification, and the non-production Host Integration Protocol 0.1 reference candidate.
''',
)
replace_once(
    "reference/implementations/python/README.md",
    '''## Staged documentation replay
''',
    '''## Host Integration Protocol 0.1 reference candidate

The package includes `teo_reference.host_integration_protocol`, a non-normative, non-production coordinator for a TEO-directed host-native execution boundary. The candidate binds provider/model execution and independent verification to a defensive `DispatchRecord` snapshot while leaving provider authentication and transport with the embedding host.

The candidate is deliberately sequential and fail-closed: retry budgets must be positive integers, only one execution instruction may be unresolved at a time, fallback is a monotonic transition that cannot reopen the primary route, a successful execution closes the execution phase, and verification start prevents any later execution issuance. Host receipts remain evidence presented to TEO rather than final acceptance authority.

This reference candidate does not provide hostile-transport authenticity, authenticated host/account/tenant identity, restart-persistent replay state, production retry-policy snapshot binding, credential-scope binding, distributed coordination, or production containment. It does not widen the current `high_volume_simple` live scope or authorize `documentation`.

The wire contract is `reference/schemas/host-integration-protocol.schema.json`, and the human-readable boundary is `docs/specification/host-integration-protocol-candidate.md`.

## Staged documentation replay
''',
)

research_path = "research/roadmaps/host-integration-contract.md"
replace_once(research_path, "**Last reconciled:** 2026-08-16", "**Last reconciled:** 2026-08-17")
replace_once(
    research_path,
    '''- [`../runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md`](../runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md), the first empirical localhost two-session run, which supports fresh-session/no-reminder standing-hook and routing continuity but records a full end-to-end FAIL after executor and verifier substitution were independently falsified.

This document does not change current routing, runtime, specialist, verification, approval, Task Request, Dispatch Record, live-execution, or release authority.
''',
    '''- [`../runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md`](../runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md), the first empirical localhost two-session run, which supports fresh-session/no-reminder standing-hook and routing continuity but records a full end-to-end FAIL after executor and verifier substitution were independently falsified.
- [`../../docs/specification/host-integration-protocol-candidate.md`](../../docs/specification/host-integration-protocol-candidate.md), the `teo-host-integration/0.1` non-production reference candidate for TEO-issued execution/verification instructions and host receipts, reconstructed on current `main` with monotonic route progression, single-outstanding-instruction sequencing, terminal success, and strict integer retry-budget enforcement.
- [`../runtime/host-integration-protocol-0-1-2026-08-17.md`](../runtime/host-integration-protocol-0-1-2026-08-17.md), the dated reconciliation and verification record for the candidate.

This document does not change current routing, runtime, specialist, verification, approval, Task Request, Dispatch Record, live-execution, or release authority. The protocol candidate is an implementation-backed research artifact, not a production Host Integration promotion or a second authority plane.
''',
)

roadmap = "docs/stewardship/roadmap.md"
replace_once(
    roadmap,
    '''Additional provider-independent research has also satisfied the static bounded-context payload slice, process-local dispatch-provenance and bundled-adapter self-expansion slice, process-local third-party adapter non-self-authorization slice, restrictive host/TEO authority-intersection and execution-scope slice, exact process-local execution-envelope integrity slice, verifier-context independence, and exact artifact/change-set stale-PASS resistance. Those are research findings, not normative host certification.

Remaining pre-normative evidence is narrower and materially different:''',
    '''Additional provider-independent research has also satisfied the static bounded-context payload slice, process-local dispatch-provenance and bundled-adapter self-expansion slice, process-local third-party adapter non-self-authorization slice, restrictive host/TEO authority-intersection and execution-scope slice, exact process-local execution-envelope integrity slice, verifier-context independence, and exact artifact/change-set stale-PASS resistance. Those are research findings, not normative host certification.

The `teo-host-integration/0.1` reference candidate now makes one bounded host-native execution/verification message path executable without promoting the broader contract. It preserves TEO ownership of route, retry/fallback authorization, verifier selection, and evidence acceptance; enforces one unresolved execution instruction at a time, monotonic primary-to-fallback progression, terminal success, and no execution after verification begins; and leaves provider authentication/transport with the host. It remains explicitly non-normative and non-production.

Remaining pre-normative evidence is narrower and materially different:''',
)

tracker = "docs/stewardship/progress-tracker.md"
replace_once(
    tracker,
    '''and process-local integrated Fresh-AI assimilation/conformance plus premortem replay research slices satisfied and a Fresh-AI cross-session trial framework/validator implemented, with empirical trial 001 supporting fresh-session/no-reminder routing continuity; contract remains non-normative''',
    '''and process-local integrated Fresh-AI assimilation/conformance plus premortem replay research slices satisfied, a Fresh-AI cross-session trial framework/validator implemented, and the non-production `teo-host-integration/0.1` execution/verification reference candidate implemented with monotonic route progression and terminal execution sequencing, with empirical trial 001 supporting fresh-session/no-reminder routing continuity; contract remains non-normative''',
)
replace_once(
    tracker,
    '''or integrated process-local Fresh-AI assimilation/conformance and premortem-replay research slices, or implementing the Fresh-AI cross-session trial framework, does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage.''',
    '''or integrated process-local Fresh-AI assimilation/conformance and premortem-replay research slices, implementing the Fresh-AI cross-session trial framework, or accepting the non-production `teo-host-integration/0.1` reference candidate, does not promote it ahead of the current live-execution milestone or imply an arbitrary completion percentage.''',
)

replace_once(
    "CHANGELOG.md",
    '''- provider-independent Host Integration Contract research covering two-host architecture diversity, bounded context projection, dispatch provenance, bundled-adapter self-expansion resistance, third-party adapter trust, restrictive host/TEO authority intersection, exact execution-envelope integrity, verifier-context independence, and exact artifact/change-set stale-PASS resistance
''',
    '''- provider-independent Host Integration Contract research covering two-host architecture diversity, bounded context projection, dispatch provenance, bundled-adapter self-expansion resistance, third-party adapter trust, restrictive host/TEO authority intersection, exact execution-envelope integrity, verifier-context independence, and exact artifact/change-set stale-PASS resistance
- non-normative `teo-host-integration/0.1` reference candidate for TEO-issued host execution and independent-verification instructions, host receipts, sequential retry/fallback control, terminal success, and evidence projection without provider-credential transport or live-authority promotion
''',
)

truth = "tests/test_documentation_control_plane_truth.py"
replace_once(
    truth,
    '''        "process-local integrated Fresh-AI assimilation/conformance",
        "assimilation is not installation",
''',
    '''        "process-local integrated Fresh-AI assimilation/conformance",
        "`teo-host-integration/0.1`",
        "monotonic route progression",
        "terminal execution sequencing",
        "assimilation is not installation",
''',
)
replace_once(
    truth,
    '''    assert "CI conformance with deterministic fake transports does not count as empirical provider-backed evidence" in text
    assert "remains the only accepted live execution scope" in text
''',
    '''    assert "CI conformance with deterministic fake transports does not count as empirical provider-backed evidence" in text
    assert "`teo-host-integration/0.1` reference candidate" in text
    assert "explicitly non-normative and non-production" in text
    assert "remains the only accepted live execution scope" in text
''',
)

evidence = Path("research/runtime/host-integration-protocol-0-1-2026-08-17.md")
evidence.write_text(
    '''# Host Integration Protocol 0.1 Reconciliation

**Date:** 2026-08-17  
**Status:** verification pending  
**Authority:** non-normative research evidence  
**Canonical base:** `95ec0d35e49c8b4e7b96d0105ca95b4a968f59ce`  
**Source candidate:** PR #179 head `70adc79c8f190c281868f001cdc472987016673d`

## Diagnosis

PR #179 preserved a useful `teo-host-integration/0.1` reference candidate but its branch had diverged from current repository truth. The candidate head was 14 commits behind current `main` and three commits ahead from merge base `4b4f07fc448b48c9b551e5ae759dd02cf1bb8d24`. Its earlier synthetic merge against documentation-reconciled `main` passed CI #797 with 987 tests, 556 tracked-file layout checks, 42 JSON Schemas, valid regulated evidence, valid linked configuration, and the provider-diverse end-to-end reference lifecycle.

The branch was therefore treated as evidence to harvest, not as a continuation to merge or rebase-and-trust.

## Control defects found during recalibration

The reconstruction corrects five fail-closed sequencing/type gaps that the original suite did not falsify:

1. fractional/non-integer `max_attempts_per_route` values were accepted by the constructor;
2. a boolean receipt attempt could compare equal to integer attempt 1;
3. fallback could be issued while a newer primary retry instruction remained unresolved;
4. after fallback issuance, a later primary retry could reopen the primary route;
5. after a successful fallback, later execution issuance remained possible, including after verification began.

## Decision

Retain the protocol as a bounded non-production reference candidate, reconstructed from current `main`. Preserve TEO ownership of routing, retry/fallback authorization, verifier selection, and acceptance. Preserve host ownership of provider authentication and transport. Do not widen live scope, provider access, specialist authority, Task Request/Dispatch authority, or production Host Integration status.

The corrected session enforces:

- positive-integer retry ceilings;
- exact integer receipt attempts;
- one unresolved execution instruction at a time;
- monotonic primary-to-fallback progression;
- terminal execution after any success;
- no execution issuance once verification starts.

## Verification

Pending on this reconstructed branch:

- full Reference Implementation CI on the current base;
- targeted mutation campaign for the corrected controls;
- final exact-head CI after evidence and stewardship reconciliation.

The eventual PASS, if achieved, qualifies only the non-production reference candidate. Production transport authenticity, host/account/tenant identity, restart-persistent replay state, policy-snapshot retry binding, credential scope, containment, distributed coordination, effect authenticity, and full selected-executor/verifier live-provider assimilation remain open.
''',
    encoding="utf-8",
)
