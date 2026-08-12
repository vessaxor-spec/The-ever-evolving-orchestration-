# Host Integration execution-envelope integrity research

Date: 2026-08-12  
Status: non-normative research  
Scope: provider-independent, process-local Host Integration evidence

## Question

After TEO has routed a task and authorized a host capability, can the host change the concrete action that will execute by lowering risk, changing the target or parameters, widening resource or side-effect scope, bypassing prerequisites, or multiplying retries beyond TEO's own retry budget?

The prior restrictive authority-intersection slice bound the exact dispatch, capability, operation, TEO live scope, and host execution scope. It intentionally did not claim that the dispatch schema itself carries an exact host resource target, concrete invocation parameters, prerequisite evidence, or an execution-attempt budget.

This experiment tests the next boundary: once TEO authorizes one exact host action, can the execution layer remain bound to that action through host authorization and retry?

## Mission Control lenses

- Host Integration and Authority Architecture
- Runtime Security and Least Authority
- Risk and Retry Controls
- Independent Adversarial Verification

## Recalibration

Current repository truth at the start of this experiment:

- stable release remains `v1.0.0`;
- development line remains `1.0.1.dev0`;
- active roster remains 10 teams, 84 workers, 82 active specialists, and 4 Mission Control workers;
- guarded live execution remains `high_volume_simple` at low or medium effective risk;
- `documentation` remains staged with `activation_authorized: false`;
- the active canary retry policy allows at most two attempts per dispatch, preserves the same dispatch during retry, forbids redispatch during retry, and does not authorize fallback after transient exhaustion;
- provider-backed documentation replay remains deferred and is not bypassed by this research;
- no open PR or issue owned this Host Integration gate.

A separate external-host integration exercise supplied the motivating implementation experience. Private host identifiers, repository paths, and host-specific code are intentionally not copied into this public research record. The reusable lesson is narrower: capability-level authorization can still be too broad if concrete arguments, targets, side effects, prerequisites, and local retry loops are not part of the authority-bound execution envelope.

## Diagnosis

A capability name is not a complete action authorization.

For example, an authorization such as `code_mutation` or `tool_execution` does not by itself answer:

- which resource may be changed;
- which exact target is permitted;
- which parameters may be supplied;
- which side-effect class is allowed;
- which prerequisites must already be true;
- how many attempts may execute;
- whether a host-local retry loop can multiply a TEO retry budget.

The existing `DispatchRecord` remains authoritative for routed task, effective risk, team, worker, specialist, capability requirement, provider/model choice, fallback, and verifier assignment. This research does not change that schema. Instead it models a separate authority-owned exact-action snapshot that a future Host Integration contract could bind to the routed dispatch.

## Candidate boundary

The research harness introduces a two-stage process-local authority.

### Stage 1: TEO exact-action issuance

`ExecutionEnvelopeAuthority.issue_teo_action()` first validates the routed dispatch against current TEO active live scope and retry policy, then issues an opaque process-local action token bound to:

- the complete `DispatchRecord` snapshot;
- exact capability;
- exact operation;
- exact dispatch effective risk;
- resource kind;
- exact target identifier;
- canonical JSON parameters;
- side-effect class;
- TEO-required prerequisites;
- TEO-authorized maximum attempts;
- the current TEO live-scope snapshot;
- the current TEO retry-policy snapshot.

A host-created action object without the authority-issued token is not accepted as TEO authorization.

### Stage 2: restrictive host execution authorization

The host may only narrow the issued action. `authorize_host_execution()` additionally checks:

- host execution scope is active;
- resource kind is allowed;
- exact action target lies within a host-allowed target prefix;
- side-effect class is allowed;
- the union of TEO-required and host-required prerequisites is satisfied;
- the attempt number is within the effective retry budget;
- attempts proceed sequentially and only one attempt is pending for an action at a time.

The effective attempt budget is:

```text
min(
  TEO action authorization,
  current TEO retry policy,
  host retry limit
)
```

A broader host retry setting therefore cannot widen TEO, while a narrower host setting can restrict execution further.

The resulting host execution token binds the exact TEO action, both current authority-scope snapshots, host scope, prerequisite evidence, and exact attempt number. The token is single-use.

## Adversarial cases

The test suite covers the following classes:

1. positive exact-action execution;
2. host self-issued TEO action token;
3. effective-risk lowering;
4. capability addition absent from the dispatch;
5. TEO action retry budget wider than active TEO retry policy;
6. disallowed host resource kind;
7. target outside host resource prefix;
8. disallowed side-effect class;
9. missing TEO action prerequisite;
10. missing host prerequisite;
11. host retry budget broader than TEO;
12. host retry budget narrower than TEO;
13. target mutation after TEO action issuance;
14. parameter mutation after TEO action issuance;
15. side-effect mutation after TEO action issuance;
16. dispatch mutation after TEO action issuance;
17. target mutation after host execution authorization;
18. prerequisite-evidence mutation after host execution authorization;
19. attempt-number mutation after host execution authorization;
20. host-scope replacement after execution authorization;
21. TEO retry-policy snapshot replacement after action issuance;
22. TEO live-scope snapshot replacement after action issuance;
23. execution-token replay and second-attempt sequencing;
24. cross-dispatch TEO action-token reuse.

All unauthorized cases are required to fail before the supplied action callback executes.

## Important limits

This is intentionally process-local evidence. It does not yet prove:

- cross-process or distributed authenticity of action or execution tokens;
- a normative TEO exact-action schema;
- production filesystem path canonicalization, symlink, mount, or namespace containment;
- DNS, redirect, IP-resolution, or network-destination equivalence for network targets;
- credential, account, tenant, or secret-scope binding;
- operating-system sandbox or least-privilege enforcement;
- package or transitive-code provenance;
- distributed retry coordination after process restart;
- provider/model input economics, latency, or task adherence;
- provider-backed `documentation` replay.

The process-local action authority is an architectural research abstraction. Production use would require an authority-controlled source for the exact action snapshot and a transport/authenticity mechanism appropriate to the deployment architecture. An untrusted host must not be allowed to mint both the action and the proof that TEO authorized it.

## Verification

Pending Reference Implementation CI on the research branch.

## Decision

Pending adversarial verification. No normative Host Integration schema, runtime authority, routing policy, live-execution scope, provider policy, specialist allocation, or qualified-human authority is changed by this experiment.
