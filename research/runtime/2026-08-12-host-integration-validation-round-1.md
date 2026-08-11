# Host Integration Validation Round 1

**Date:** 2026-08-12  
**Status:** research evidence  
**Authority:** non-normative  
**Scope:** first implementation feedback from an external host integrating the candidate TEO Host Integration Contract

## Purpose

This document records the first implementation-backed validation round for the Host Integration Contract research. The external host is intentionally treated as an implementation specimen rather than a TEO dependency or product-specific target.

The host implemented three major corrections after the original premortem:

1. restored canonical specialist cards after an earlier host-specific identity injection;
2. separated host identity from selected TEO specialist context through an execution-envelope concept;
3. introduced a capability-adapter manifest and programmatic router that translates abstract TEO capability requests into host-native execution tools.

The host then exercised the adapter on a real implementation task and later added shell-safe invocation, fail-closed unknown-capability handling, and dispatch logging.

This was sufficient to validate the architectural direction. It was not sufficient to prove full TEO conformance or a hardened execution boundary.

## What the validation proved

### 1. Identity separation works better than specialist rewriting

The host successfully removed host-specific mandate text from copied specialist role cards and instead carried host invariants separately from the selected specialist context.

This supports the existing Host Integration Contract principle:

```text
host identity and native invariants
  -> TEO orchestration decision
  -> selected specialist context
  -> host-native execution
```

The host can remain itself while using a TEO specialist as a bounded decision lens. No specialist-card mutation is required.

### 2. Capability adapters are a viable execution boundary

The host demonstrated the pattern:

```text
TEO capability request
  -> host capability adapter
  -> concrete installed host tool
  -> execution result
```

This validates the architectural separation between capability intent and host implementation. It also demonstrates why host-specific tool names should remain outside canonical specialist cards.

### 3. Fail-closed routing and shell-safe execution materially improve the adapter

A later hardening iteration replaced shell-interpolated execution with argument-vector execution, rejected unknown capabilities, resolved execution from a fixed host root, and wrote dispatch audit records.

These changes are evidence that the adapter boundary can enforce meaningful controls rather than acting as a prompt-only convention.

## Gaps exposed by the implementation

### 1. Exact TEO routing structure must remain intact

The host's demonstration collapsed TEO responsibility layers by presenting a specialist category as a Team and the specialist itself as a Worker.

A conformant host must preserve the explicit chain:

```text
Mission Control
  -> Team
  -> Worker
  -> optional Specialist
  -> Capability
  -> Implementation
  -> Verification
```

Host-local labels may supplement this chain but must not replace or collapse TEO responsibility fields while claiming a TEO dispatch record.

**Contract implication:** conformance must validate structural routing fields, not merely the presence of a specialist name.

### 2. Effective risk cannot be lowered by host classification

The demonstration classified an implementation task as low risk while the selected specialist allocation carried a higher risk profile.

This does not prove the task had to inherit the specialist risk unchanged, but it does prove that an external host needs an explicit effective-risk reconciliation rule. A host-local classification must not silently lower a TEO risk floor or bypass controls attached to the selected route.

**Contract implication:** effective risk must be evidence-bound and non-lowerable across integration layers.

### 3. Adapter authority data must not be self-modifiable by the active executor

In the first prototype, the same execution flow that consumed the capability-adapter manifest also edited that manifest before invoking it again.

That creates a potential self-authorization path:

```text
executor requests capability
  -> executor changes capability binding
  -> executor consumes changed binding
```

The safer boundary is:

```text
executor requests authorized capability
  -> governed read-only adapter binding
  -> host permission check
  -> concrete implementation
```

Changes to capability bindings should be separate governed changes with review, integrity/version evidence, and appropriate verification.

**Contract implication:** capability-adapter manifests are authority surfaces and should be immutable to the active dispatch unless a separately authorized governance change is being executed.

### 4. A successful smoke test is not independent verification

The adapter successfully translated and executed a diagnostic capability. That proves basic functional routing. It does not prove independent model verification, policy conformance, authorization correctness, rollback, command containment, or manifest integrity.

**Contract implication:** execution evidence and independent verification evidence must remain distinct.

### 5. Host authority and TEO authority need explicit restrictive intersection semantics

The host already had native approval and governance rules that could be stricter than the TEO route. The implementation showed that a prompt-level TEO dispatch can otherwise proceed without proving the host's own stricter gate was satisfied.

The general rule should be:

```text
effective action authority
  = TEO authorization intersected with host authorization
```

Where the two differ, the more restrictive control wins. A TEO authorization must never weaken a stricter host safety, permission, approval, environment, or operator boundary. A host preference must likewise never weaken TEO risk, verification, or qualified-human requirements.

**Contract implication:** deny wins and more-restrictive-control wins should be explicit, not inferred.

### 6. Deployment and synchronization claims must be evidence-bound

The first implementation was reported as committed to the host's main branch before the corresponding remote commit was observable. A later synchronization made the commits observable and resolved the discrepancy.

This is not an architectural failure, but it demonstrates an evidence rule:

- local commit is not remote synchronization;
- remote synchronization is not deployment;
- deployment is not successful execution;
- successful execution is not independent verification.

**Contract implication:** host conformance and completion claims should state the exact evidence level reached.

### 7. Native host capabilities need classification before adapter enforcement

The host initially described all native skills as execution muscles that must run only after Mission Control and specialist authorization. That is too broad.

A mature host may contain several capability classes:

| Class | Typical purpose | Relationship to TEO |
|---|---|---|
| Pre-routing safety controls | intake sanitization, untrusted-content screening, isolation prechecks | may run before Mission Control |
| TEO-dispatched execution capabilities | code mutation, research, data processing, controlled actions | invoked through authorized TEO capability bindings |
| Host runtime infrastructure | continuity, queueing, telemetry, lifecycle state | operates beneath or beside TEO |
| Host authority infrastructure | credentials, native approval gates, environment restrictions | cannot be bypassed by TEO |
| Verification capabilities | tests, scanners, independent verifier routes | invoked under the verification contract |
| Host maintenance capabilities | health checks, hygiene, local upkeep | may be system-triggered under host governance |

Forcing every native operation through a specialist dispatch would recreate the orchestration paralysis identified in the premortem and could incorrectly place pre-routing safety behind the system it is supposed to protect.

**Contract implication:** classify host capabilities before deciding which ones are TEO-dispatched.

### 8. A policy execution lock is not a programmatic execution lock

The host added a strong policy statement that ordinary task execution must originate from Mission Control. The initial capability router, however, only proved that a requested capability existed in the adapter manifest before executing the mapped tool.

A stronger governed execution path would additionally bind execution to evidence such as:

- dispatch identifier;
- resolved Team and Worker;
- optional selected Specialist and source;
- effective risk decision;
- authorized capability set;
- host approval/permission result;
- verification requirement;
- version/integrity binding;
- expiry or replay boundary where appropriate.

**Contract implication:** hosts should distinguish policy-enforced routing from dispatch-bound executable authorization.

### 9. Copied TEO authority can silently fork

The host copied TEO Mission Control and specialist registry material into its own repository. The copied Mission Control implementation preferences and version labels did not remain synchronized with current TEO repository truth.

This validates the original registry-drift concern at a broader level: copying canonical TEO files is not sufficient version binding.

**Contract implication:** an embedded host should bind to a TEO release and executable configuration identity, detect stale or mismatched copies, and avoid treating locally copied policy text as independent canonical authority.

### 10. Specialist counts are not registry identity

The host correctly carried the current active count but described that count as coming from the base specialist registry. Current TEO executable composition is instead built from the base registry plus active extension/override registries.

A correct host binding therefore needs the executable composition or equivalent integrity identity, not only a count.

**Contract implication:** bind the complete executable registry composition, including active overlays and policy versions, rather than `active_specialist_count` alone.

## Contract refinements supported by round 1

The following candidate requirements now have implementation evidence behind them:

1. **Host capability classification** before deciding which capabilities are TEO-dispatched.
2. **Exact routing-structure preservation** for Team, Worker, Specialist, Capability, Implementation, and Verification fields.
3. **Non-lowerable effective-risk reconciliation** across host and TEO layers.
4. **Restrictive authority intersection**, with deny-wins and more-restrictive-control-wins semantics.
5. **Dispatch-bound executable authorization** for governed capability routers where enforcement is claimed.
6. **Adapter-manifest immutability** to the active executor, except through a separately authorized governance change.
7. **Evidence-level completion claims** distinguishing local change, synchronization, deployment, execution, and verification.
8. **Executable TEO composition binding** rather than file counts or a single base registry.
9. **Anti-fork freshness checks** for copied TEO policy, routing, registry, and specialist artifacts.
10. **Per-dispatch bounded specialist context**, while still allowing Mission Control to create multiple bounded specialist dispatches when a genuinely cross-disciplinary task requires them.

## What remains unproven

Round 1 does not yet prove:

- conformance against a second structurally different host;
- context-economics improvement versus naive corpus loading;
- hardened dispatch-token or dispatch-record enforcement;
- adapter-manifest integrity protection;
- provider-diverse independent verification inside the host;
- correct behavior when host and TEO authority disagree;
- mutation resistance for risk lowering, authorization bypass, stale registry binding, and recursive orchestration;
- recovery and rollback behavior across failed host-native capability execution.

## Disposition

This round strengthens the case for a Host Integration Contract but does not justify normative promotion yet.

The next research gate remains:

1. incorporate the round-1 requirements into the candidate contract;
2. validate the same concepts against at least one structurally different host;
3. mutation-test authority, registry, adapter, recursion, and verification failure paths;
4. only then evaluate a normative schema or reference implementation.

No current TEO runtime, routing, specialist, verification, approval, release, or Progress Tracker authority is changed by this evidence.
