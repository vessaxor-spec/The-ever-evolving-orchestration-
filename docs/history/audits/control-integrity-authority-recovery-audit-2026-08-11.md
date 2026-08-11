# Control Integrity Authority and Recovery Audit - 2026-08-11

## Authority

This record documents a targeted TEO Mission Control audit of the finalization -> qualified-human authority -> runtime recovery junction on post-v1 `main`.

It is historical audit evidence. It does not replace current policy, schemas, registries, runtime code, or the canonical Progress Tracker.

## Active review lenses

- Control Integrity
- Assurance and Verification
- Runtime and Recovery
- Governance and Authority
- Principal Engineering

## Scope

The audit intentionally concentrated on composition boundaries rather than reopening controls already proven independently:

1. terminal/finalization evidence;
2. qualified-human authority lifecycle;
3. provider recovery, circuit preparation, and fallback redispatch;
4. preservation of effective risk and human-approval requirements across recovery.

Provider-backed execution was not required for this audit.

## Confirmed finding: qualified-human temporal causality gap

Two related chronology invariants were not enforced by the qualified-human approval lifecycle:

1. an initial approval disposition could carry an `effective_at` timestamp earlier than the approval request's `requested_at` timestamp;
2. human finalization could use the latest disposition even when `finalized_at` was earlier than that disposition's `effective_at` timestamp.

The existing lifecycle already enforced request expiry, grant validity, disposition lineage, revocation, approval expiry, exact dispatch and Route-Outcome Evidence binding, and integrity hashes. The missing checks were specifically cross-record temporal causality.

### Test-first reproduction

PR #132 first introduced two regression probes without a production fix.

Reference Implementation CI #510 produced the expected failure:

- 653 existing tests passed;
- both new temporal-causality probes failed because `ProviderAdapterContractError` was not raised;
- repository layout validation completed before the test failure;
- later CI stages were skipped because the intentional reproduction stopped the run.

This isolated the defect without relying on hypothetical code inspection alone.

## Remediation

The reference lifecycle now fails closed when:

- any disposition `effective_at` predates its bound approval request `requested_at`;
- finalization `finalized_at` predates the current disposition `effective_at` that finalization would rely on.

The checks are applied through the existing cross-record transition and finalization paths. They do not alter schemas, routing, model selection, provider access, risk classification, authority scope, or live-execution policy.

Reference Implementation CI #511 validated the temporal remediation with 655 passing tests, 475 tracked-file layout checks, regulated specialist evidence validation, 40 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

## Recovery and authority junction

No authority-bypass defect was found in the inspected recovery path.

The guarded fallback and provider-circuit paths preserve the existing task authority surface:

- fallback redispatch copies the active dispatch's effective risk rather than recomputing or lowering it;
- fallback redispatch preserves `require_human_approval` while adding only the failed implementation or provider to the appropriate block list;
- circuit preparation preserves task type, risk level, specialist selection, and `require_human_approval` while adding only active provider-health blocks;
- guarded automatic fallback remains restricted to explicit `high_volume_simple` tasks and refuses high or critical dispatches;
- Route-Outcome Evidence rejects `completed` when `human_approval_required` remains true.

Two regression tests were added so the recovery preparation layer fails CI if a future change lowers effective risk, removes a human-approval requirement, or mutates the caller's original recovery constraints while preparing redispatch.

Reference Implementation CI #513 validated the combined temporal-authority remediation, recovery-authority regression coverage, and specification update with:

- 657 tests passed;
- 476 tracked files passed repository-layout validation;
- regulated specialist evidence passed structural validation;
- 40 JSON Schemas parsed;
- linked configuration reported zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

## Disposition

- Confirmed temporal authority defects: remediated and regression-protected.
- Recovery-to-authority bypass: not found in the inspected bounded reference path.
- Effective-risk preservation across recovery: verified and regression-protected.
- Human-approval preservation across recovery: verified and regression-protected.
- Route-Outcome Evidence mutation: unchanged; human finalization remains separate evidence.
- Live execution scope: unchanged.
- `documentation` candidate authority: unchanged and still staged.
- High and critical live execution: unchanged and unauthorized.

## Progress impact

This audit strengthens the existing Control Integrity workstream but does not justify declaring it permanently complete. The canonical 90% score intentionally reserves ongoing capacity for future mutation depth, finalization-path resistance, authority-leakage checks, recovery gaps, and newly discovered failure modes.

The provider-backed controlled `documentation` replay remains a separate deferred open action item and was not bypassed or reclassified by this work.
