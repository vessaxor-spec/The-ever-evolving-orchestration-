# Bounded Transient Retry

## Status

This specification defines the first runtime retry control for the guarded TEO canary.

Retry is intentionally separate from fallback.

A retry means the routing decision is still valid and the same authorized dispatch is attempted again because the failure is temporary. A fallback means the routing decision must be reconsidered and TEO creates a new dispatch.

## Scope

The active policy is:

- task type: `high_volume_simple`
- risk: low or medium
- eligible failure scope: `transient` only
- maximum provider attempts per dispatch: 2
- initial delay: 0.5 seconds
- backoff multiplier: 2.0
- maximum delay: 2.0 seconds
- jitter: plus or minus 20 percent
- fallback after transient exhaustion: false

The machine-readable policy is:

- `policy/runtime/canary-retry.yaml`

## Same-dispatch invariant

A transient retry must preserve:

- dispatch ID
- task ID
- provider family
- model
- reasoning effort
- verifier assignment
- risk level
- specialist and worker route
- human-approval requirements

Retry must not add blocked models or providers and must not run the router again.

If any of those routing properties need to change, the operation is a redispatch or fallback rather than a retry.

## Attempt budget

The canary permits at most two provider attempts for one dispatch.

The first attempt consumes one attempt. A transient failure may schedule exactly one additional attempt. A success or any non-transient failure terminates the retry sequence immediately.

This limit applies independently to the primary dispatch and to the single fallback dispatch. The existence of a retry budget does not authorize another fallback dispatch or a third provider chain.

## Delay and jitter

The retry controller applies bounded exponential backoff with jitter.

For the current two-attempt canary, only the first retry delay is normally exercised. The formula and maximum delay remain explicit so later retry-budget changes cannot silently introduce unbounded waits.

Jitter exists to reduce synchronized retries against a recovering provider. Tests inject deterministic randomness and a no-op sleeper so conformance does not depend on wall-clock timing.

## Failure transitions

A retry sequence can end in four ways:

1. success, which keeps the original dispatch active
2. exhausted transient failure, which returns execution failure without fallback
3. model failure, which leaves retry and may enter guarded model fallback
4. provider failure, which leaves retry and may enter guarded provider fallback

Request and capability failures terminate immediately and do not consume another retry attempt.

An exhausted transient failure is not relabeled as a provider failure. That distinction is preserved for future circuit-breaker and outage policy.

## Adapter boundary

Provider adapters remain single-attempt implementations.

Retry is owned by the runtime coordinator above the adapters. This prevents provider SDK behavior from creating hidden attempts and keeps the attempt budget observable across OpenAI, Anthropic, Google, local runtimes, and future providers.

## Verification boundary

Retry never executes or changes the verifier.

Because a retry preserves the same dispatch, the verifier assignment also remains unchanged. If execution later enters a fallback redispatch, the fallback rules require a fresh independent verifier.

A successful retry remains subject to normal independent verification and any qualified human approval requirements.

## Conformance

The reference tests prove that:

- transient then success uses two attempts on the same dispatch
- transient exhaustion stops after two attempts
- request, model, and provider failures are not retried
- jitter remains inside the configured bound
- retry does not mutate routing authority
- a transient retry that later returns provider failure can enter guarded redispatch
- fallback dispatches receive their own independent retry budget
- failed fallback retries do not create a third provider chain
- policy cannot silently enable fallback after transient exhaustion
- policy cannot exceed two attempts in the guarded canary

The conformance suites are:

- `tests/test_bounded_transient_retry.py`
- `tests/test_guarded_canary_fallback.py`

## Non-goals

This slice does not implement:

- circuit breakers
- provider health aggregation
- adaptive retry budgets
- Retry-After header interpretation
- cost-aware retry decisions
- telemetry persistence
- high or critical risk retries
- verifier execution
- human approval integration
