# Guarded Canary Fallback

## Status

This specification defines the automatic live fallback path in the TEO reference runtime.

The scope is intentionally narrow. It applies only to explicit `high_volume_simple` tasks at low or medium risk and allows at most one fallback redispatch.

## Core rule

Fallback is a new TEO dispatch, not an adapter chain.

When an eligible execution fails, the runtime returns the failure to orchestration. TEO creates a new dispatch after applying the appropriate execution block. The new dispatch receives its own dispatch ID, selected implementation, routine fallback state, and independent verifier assignment before execution resumes.

An adapter never invokes another adapter directly.

## Eligible failure scopes

Automatic fallback is currently permitted only for:

- `model`
- `provider`

A model-scoped failure blocks the failed implementation model before redispatch.

A provider-scoped failure blocks the failed provider family before redispatch. The replacement execution must therefore use another provider family.

The following scopes do not directly trigger automatic fallback:

- `request`
- `transient`
- `capability`

Request failures require correction or rejection. Transient failures may use the separate bounded same-dispatch retry policy. Exhausted transient retries remain transient and do not automatically become fallback authority. Capability failures return to capability resolution rather than silently substituting a model.

If a transient retry later returns a `model` or `provider` failure, that new normalized failure may enter the guarded fallback path.

## Redispatch requirements

An eligible fallback must satisfy all of the following:

1. create a new dispatch ID
2. preserve the original task ID and authorized task intent
3. preserve canonical team, worker, specialist, risk, and human-approval rules
4. apply the failed model or provider block before routing
5. apply any currently open provider-family circuit blocks before routing
6. select an implementation different from the failed implementation
7. leave the failed provider family when the failure is provider-scoped
8. assign an independent verifier different from the fallback execution model
9. assign a fresh verifier implementation rather than reusing the primary dispatch verifier
10. execute through the provider adapter and connection boundaries
11. create at most one fallback dispatch

A failed fallback does not chain automatically to a third provider.

The primary and fallback dispatches may each consume the separately governed transient retry budget without changing these redispatch limits.

## Circuit-breaker interaction

Provider circuit state is applied before both the primary dispatch and any fallback redispatch.

An already-open provider is added to copied blocked-provider constraints so the canonical router does not select it. The circuit layer never chooses the replacement model itself.

A failure in the active execution is observed by the provider circuit only after that dispatch's bounded retry sequence finishes. Circuit classification is intentionally narrower than the broad fallback `provider` scope. Authentication, billing, permission, quota/rate-limit, and local connection failures may still trigger current-task fallback according to routing policy, but they do not establish global provider unhealthiness.

The circuit specification is:

- `docs/specification/provider-circuit-breaker.md`

## Verification boundary

`execute_guarded_canary` is an execution coordinator, not a completion gate.

A successful primary or fallback provider response is not a completed TEO outcome. The verifier assigned by the active dispatch still has to execute independently, and any required human approval remains outstanding.

The fallback runtime must not:

- perform verification itself
- mark human approval complete
- waive critical-risk controls
- reuse a verifier solely because it was assigned to the failed primary dispatch

## Connection boundary

Fallback routing remains independent from connection mechanics.

The runtime receives provider connections after TEO has selected the active dispatch. API keys, OAuth, delegated identity, service accounts, connector sessions, SDK-backed credentials, credential brokers, local runtimes, and future connection methods remain implementation plumbing.

A missing connection for the newly selected provider fails closed. It does not authorize a hidden route change.

## Retry boundary

Transient retry is governed separately by:

- `policy/runtime/canary-retry.yaml`
- `docs/specification/bounded-transient-retry.md`

A retry preserves the existing dispatch, provider, model, reasoning effort, and verifier. A fallback changes the routing context and therefore requires a new dispatch.

This separation prevents retry attempts from being confused with policy fallback and makes both attempt budgets observable.

## Conformance

The reference tests verify that:

- provider-scoped failure creates a new cross-provider dispatch
- model-scoped failure blocks the failed model before redispatch
- fallback uses the policy-selected implementation
- fallback receives a fresh independent verifier
- open provider circuits are honored before redispatch
- request failures do not fallback
- exhausted transient retries do not fallback directly
- a retry that later produces model or provider failure may redispatch
- fallback failure does not chain to a third provider
- original task constraints are not mutated
- automatic fallback requires an explicit `high_volume_simple` task type

The conformance suites are:

- `tests/test_guarded_canary_fallback.py`
- `tests/test_bounded_transient_retry.py`
- `tests/test_provider_circuit_breaker.py`

## Non-goals

This fallback layer does not implement:

- provider circuit state itself
- automatic fallback for high or critical risk
- capability-driven rerouting after execution failure
- verifier execution
- human approval integration
- cost, latency, reliability, or quality telemetry
- more than one fallback redispatch

Provider circuit state is implemented separately by `docs/specification/provider-circuit-breaker.md`.
