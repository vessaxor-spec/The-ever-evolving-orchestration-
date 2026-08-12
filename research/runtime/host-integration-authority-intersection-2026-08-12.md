# Host Integration Restrictive Authority Intersection Audit

**Date:** 2026-08-12  
**Authority:** non-normative research  
**Base revision:** `6ee0da686a4e189977221caac27751cfa8bd2c7f`

## Question

Can an external host execute a TEO-dispatched action when either TEO or the host denies the concrete action, or can execution be bound to the restrictive intersection of both authority planes so that deny wins and the more restrictive control always wins?

## Mission Control lenses

- authority architecture
- zero-trust security
- risk controls
- independent adversarial verification

## Repository diagnosis

The Host Integration research roadmap already assigns different authority to TEO and to the host. TEO owns Team, Worker, Specialist, capability and model routing for an admitted task. The host retains native permissions, environment restrictions, and concrete host-tool execution permission. The roadmap explicitly requires tool/action execution to resolve through the restrictive intersection of TEO authorization and host authorization.

The current normative live-execution policy authorizes only `high_volume_simple` at low or medium effective risk. `documentation` remains a staged candidate with `activation_authorized: false`. This gives the research gate a real repository authority boundary to exercise instead of an invented permissive fixture.

The previous Host Integration slices separately established process-local dispatch provenance and process-local third-party adapter non-self-authorization. This audit does not merge or replace those controls. It assumes an already-routed dispatch and tests the next boundary: whether one concrete host-native action remains inside both TEO and host authority.

## Candidate research boundary

The research harness introduces a process-local `RestrictiveAuthorityGate`.

TEO authority is represented by:

- the exact already-routed `DispatchRecord`;
- the dispatch-authorized capability set;
- the current `active_scope.task_types` and `active_scope.risk_levels` loaded from `policy/runtime/live-execution-expansion.yaml`.

Host authority is represented by an explicit host execution scope containing:

- allowed and denied task types;
- allowed and denied risk levels;
- allowed and denied capabilities;
- allowed and denied provider families;
- allowed and denied concrete operations;
- an active/inactive state and scope identifier.

A concrete action authorization binds:

1. the complete dispatch snapshot;
2. the single capability being invoked;
3. the concrete host operation;
4. the current TEO execution-scope snapshot;
5. the current host execution-scope snapshot.

The action callback is invoked only after both authority planes permit the exact action and the bound snapshots still match.

## Restrictive semantics

The candidate boundary applies these rules:

- TEO denial blocks execution even when the host would allow it;
- host denial blocks execution even when TEO would allow it;
- explicit host deny wins over a host allow declaration;
- a host capability not present in the TEO dispatch cannot widen TEO authority;
- TEO active live scope cannot be widened by a host permission;
- host task, risk, provider, capability, or operation restrictions can narrow a TEO-authorized dispatch;
- an inactive host scope blocks execution;
- a token issued for one dispatch, capability, operation, or authority-scope snapshot cannot authorize another.

## Adversarial cases

The executable suite challenges the boundary with:

1. exact positive-control execution when both sides authorize;
2. host task-type denial against a TEO-authorized task;
3. TEO task-type denial against a host-authorized staged task;
4. host risk restriction against a TEO-authorized risk;
5. TEO high-risk denial against a permissive host;
6. explicit host capability deny overlapping a host allow;
7. missing host capability permission;
8. attempted host capability widening beyond the dispatch;
9. host provider-family restriction;
10. host operation restriction;
11. inactive host scope;
12. a self-issued action token;
13. cross-dispatch token reuse;
14. post-authorization capability substitution;
15. post-authorization operation substitution;
16. exact dispatch-snapshot mutations covering task identity, worker, selected model, verifier model, and routing explanation;
17. host-scope replacement after authorization;
18. TEO-scope replacement after authorization.

Every denied or altered case is required to stop before the concrete action callback. The exact positive control must execute once.

## Trust boundary

This experiment is intentionally process-local. It does not claim portable authorization, distributed revocation, cryptographic host identity, cross-process replay protection, or production host-policy synchronization.

It also does not treat the process-local `DispatchRecord` itself as portable proof of TEO provenance. That remains the concern of the separate dispatch-authorization research slice. Likewise, this gate does not establish third-party adapter package provenance or isolation.

The TEO side of this experiment uses the repository's current active live-execution scope only to test restrictive intersection semantics. It does not promote the Host Integration Contract into live runtime authority and does not change that policy.

## Verification record

Reference Implementation CI **#565** passed the first complete branch validation:

- **742 tests**;
- **503 tracked-file repository-layout checks**;
- regulated specialist evidence structural validation;
- **41 parsed JSON Schemas**;
- linked TEO configuration with zero issues;
- the provider-diverse end-to-end example.

The suite proves that the current repository active scope is read as `high_volume_simple` only at low/medium risk, that host and TEO denials both stop action execution, that explicit host deny wins over host allow, that host permissions cannot add a capability absent from the TEO dispatch, and that authorization cannot be reused across altered dispatch, capability, operation, host-scope, or TEO-scope snapshots.

## Decision

**Process-local restrictive host/TEO authority intersection: supported.** The tested boundary enforces deny-wins and more-restrictive-control-wins semantics before invoking a concrete host-native action.

**Process-local host execution-scope binding: supported.** The authorization is bound to the exact dispatch snapshot, selected capability, concrete operation, current TEO active scope, and current host scope.

**Distributed authority synchronization remains open.** This audit does not prove portable authorization, cryptographic host identity, distributed revocation, cross-process replay resistance, or production synchronization of host and TEO authority state.

This result does not make the Host Integration Contract normative, authorize `documentation`, widen live execution, change provider/model routing, or alter qualified-human authority.
