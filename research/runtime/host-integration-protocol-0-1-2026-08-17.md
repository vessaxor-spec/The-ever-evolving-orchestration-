# Host Integration Protocol 0.1 Reconciliation

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
