# Control Integrity Mutation Audit - Finalization, Authority, Recovery - 2026-08-11

## Authority

This record preserves the targeted TEO Mission Control mutation audit of the finalization -> qualified-human authority -> runtime recovery junction on post-v1 `main`.

It extends, but does not replace, the earlier 2026-08-11 control-integrity audit. It is historical audit evidence and does not create routing, execution, approval, provider-access, model-selection, or live-scope authority.

## Active review lenses

- Control Integrity
- Assurance and Verification
- Runtime and Recovery
- Governance and Authority
- Principal Engineering
- Independent Verification

## Scope

The audit targeted ten high-leverage invariants at composition boundaries:

1. disposition cannot predate its approval request;
2. finalization cannot predate the current disposition it relies on;
3. authority-grant scope must cover the effective risk;
4. finalization must revalidate the exact dispatch binding;
5. approval validity is exclusive at `approval_expires_at`;
6. request validity is exclusive at `expires_at`;
7. authority-grant validity is exclusive at `valid_until`;
8. fallback redispatch must preserve the active dispatch's effective risk;
9. fallback redispatch must preserve an explicit human-approval requirement;
10. circuit preparation must preserve an explicit human-approval requirement.

Provider-backed live execution was not required because the audit weakens deterministic reference-control invariants and uses CI as the execution oracle.

## Method

A targeted mutation harness copies the reference Python package into an isolated temporary path, weakens exactly one named invariant, and executes the smallest regression slice expected to detect that weakening. The production source tree is never rewritten by the mutant process.

A mutant is considered killed only when the corresponding regression slice fails. If the regression slice remains green, the mutant survives and proves that the current tests do not distinguish the intended invariant from the weakened behavior.

Independent verification tightened that oracle further: the harness accepts a kill only when pytest returns exit code `1` and reports a failed test. Collection, usage, missing-node, or internal runner errors therefore cannot masquerade as mutation resistance.

The harness itself is retained as regression protection so future changes continue to prove these specific authority and recovery invariants rather than merely exercising the surrounding code.

## Test-first evidence: CI #519

Reference Implementation CI #519 ran the initial ten-mutant matrix before remediation.

Result:

- 663 tests passed;
- four mutation probes failed because their weakened implementations survived the targeted tests;
- six mutants were killed by existing regression coverage;
- repository layout validation passed for 478 tracked files before the intentional mutation-test failure;
- later validation stages were skipped because the mutation audit intentionally stopped CI on surviving mutants.

The four surviving mutants were:

1. `finalized >= approval_expires_at` weakened to `finalized > approval_expires_at`;
2. `disposition_time >= request_expires_at` weakened to `disposition_time > request_expires_at`;
3. `disposition_time >= authority_grant.valid_until` weakened to `disposition_time > authority_grant.valid_until`;
4. fallback redispatch copying `dispatch.risk_level` weakened to copying `task.risk_level`.

## Finding classification

The four survivors proved **test-evidence gaps**, not production-control defects.

Inspection of the current reference implementation confirmed that production behavior already failed closed at all three exact expiry boundaries and already copied the active dispatch's effective risk during fallback redispatch. The weakness was that existing tests exercised only values after the expiry boundaries, and the recovery test used a caller-declared risk already equal to the dispatch risk.

No production source change was therefore justified.

## Remediation

Four focused regression cases were added:

- finalization exactly at `approval_expires_at` must be blocked as expired;
- a human disposition exactly at request `expires_at` must be rejected as expired;
- a human disposition exactly at authority-grant `valid_until` must be rejected because the grant is no longer valid;
- fallback redispatch must preserve a dispatch-elevated critical effective risk when the caller originally declared low risk.

The mutation matrix was rebound to those exact boundary/elevation probes. No routing, schema, model, provider-access, live-scope, risk policy, or approval-authority behavior was changed.

## Verification: CI #521

Reference Implementation CI #521 killed all ten targeted mutants and completed the full repository validation:

- 671 tests passed;
- 479 tracked files passed repository-layout validation;
- regulated specialist evidence passed structural validation;
- 40 JSON Schemas parsed;
- linked TEO configuration reported zero issues;
- the provider-diverse end-to-end reference lifecycle passed.

This establishes targeted mutation resistance for the ten audited invariants at the audited revision. It does not imply that Control Integrity is permanently complete or that untested mutants cannot exist elsewhere.

## Disposition

- Production defects proven by this mutation audit: none.
- Test-evidence gaps proven: four.
- Test-evidence gaps remediated: four.
- Targeted mutants killed after remediation: 10 of 10.
- Effective-risk preservation across fallback redispatch: mutation-protected for caller-risk versus dispatch-risk divergence.
- Human-approval preservation across fallback and circuit preparation: mutation-protected by the targeted matrix.
- Exact request, approval, and grant expiry boundaries: mutation-protected by explicit equality-boundary tests.
- Qualified-human temporal causality and exact dispatch binding: mutation-protected by the targeted matrix.
- Live-execution scope: unchanged.
- `documentation` candidate authority: unchanged and still staged.
- Provider-backed controlled `documentation` replay: unchanged and still a deferred open action item.
- High and critical live execution: unchanged and unauthorized.

## Progress impact

The audit materially strengthens the evidence behind the existing Control Integrity workstream but does not justify changing its intentionally non-terminal 90% score. Continuing mutation depth remains an adversarial maintenance discipline, and future audits should add mutants only where they test materially distinct authority, finalization, recovery, or integrity failure modes.

The canonical evidence-governed live execution expansion sequence remains unchanged.
