# Guarded Canary Fallback

## Status

This specification defines the first automatic live fallback path in the TEO reference runtime.

The scope is intentionally narrow. It applies only to explicit `high_volume_simple` tasks at low or medium risk and allows at most one fallback execution attempt.

## Core rule

Fallback is a new TEO dispatch, not an adapter chain.

When an eligible primary execution fails, the runtime returns the failure to orchestration. TEO creates a new dispatch after applying the appropriate execution block. The new dispatch receives its own dispatch ID, selected implementation, routine fallback state, and independent verifier assignment before execution resumes.

An adapter never invokes another adapter directly.

## Eligible failure scopes

Automatic fallback is currently permitted only for:

- `model`
- `provider`

A model-scoped failure blocks the failed implementation model before redispatch.

A provider-scoped failure blocks the failed provider family before redispatch. The replacement execution must therefore use another provider family.

The following scopes do not trigger automatic fallback in this version:

- `request`
- `transient`
- `capability`

Request failures require correction or rejection. Transient failures are reserved for the future bounded retry policy. Capability failures return to capability resolution rather than silently substituting a model.

## Redispatch requirements

An eligible fallback must satisfy all of the following:

1. create a new dispatch ID
2. preserve the original task ID and authorized task intent
3. preserve canonical team, worker, specialist, risk, and human-approval rules
4. apply the failed model or provider block before routing
5. select an implementation different from the failed implementation
6. leave the failed provider family when the failure is provider-scoped
7. assign an independent verifier different from the fallback execution model
8. assign a fresh verifier implementation rather than reusing the primary dispatch verifier
9. execute through the provider adapter and connection boundaries
10. perform at most one fallback execution attempt

A failed fallback does not chain automatically to a third provider.

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

This version intentionally does not retry transient failures.

Retry budgets, delay, backoff, jitter, and circuit breakers are a separate runtime control. Keeping them separate prevents a transient retry from being confused with a policy fallback or from consuming an undeclared number of attempts.

## Conformance

The reference tests verify that:

- provider-scoped failure creates a new cross-provider dispatch
- model-scoped failure blocks the failed model before redispatch
- fallback uses the policy-selected implementation
- fallback receives a fresh independent verifier
- request failures do not fallback
- transient failures do not fallback
- fallback failure does not chain to a third provider
- original task constraints are not mutated
- automatic fallback requires an explicit `high_volume_simple` task type

The conformance suite is:

- `tests/test_guarded_canary_fallback.py`

## Non-goals

This slice does not implement:

- transient retry budgets
- exponential backoff or jitter
- circuit breakers
- automatic fallback for high or critical risk
- capability-driven rerouting after execution failure
- verifier execution
- human approval integration
- cost, latency, reliability, or quality telemetry
- more than one fallback attempt
