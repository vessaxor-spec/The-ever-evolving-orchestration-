# Bounded Transient Retry

## Status

This specification defines the runtime retry control for the guarded TEO canary.

Retry is intentionally separate from fallback and circuit state.

A retry means the routing decision is still valid and the same authorized dispatch is attempted again because the failure is temporary. A fallback means the routing decision must be reconsidered and TEO creates a new dispatch. A circuit breaker remembers repeated service-health failure across separate executions and can block a provider before a future dispatch.

## Scope

The active retry policy is:

- task type: `high_volume_simple`
- risk: low or medium
- eligible failure scope: `transient` only
- maximum provider attempts per dispatch: 2
- initial local delay: 0.5 seconds
- local backoff multiplier: 2.0
- maximum local backoff delay: 2.0 seconds
- local jitter: plus or minus 20 percent
- honor normalized provider retry timing: true
- maximum provider-directed wait budget: 60 seconds
- provider hint above wait budget: stop rather than retry early
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

Provider-directed timing cannot create another attempt. It can only change the wait before an attempt that TEO has already authorized.

This limit applies independently to the primary dispatch and to the single fallback dispatch. The existence of a retry budget does not authorize another fallback dispatch or a third provider chain.

## Delay, jitter, and provider minimums

The retry controller applies bounded exponential backoff with jitter and can also honor normalized provider-directed retry timing.

For an eligible retry:

1. calculate TEO's local jittered backoff
2. read `ProviderExecutionResponse.retry_after_seconds`, if present
3. if the provider value is at or below the 60-second guarded wait budget, use the greater of the local delay and provider delay
4. if the provider value is above 60 seconds, stop rather than retry before the requested minimum has elapsed

The local 2-second backoff cap applies only to TEO-generated backoff. It does not authorize TEO to shorten a provider-requested minimum wait.

Jitter exists to reduce synchronized retries against a recovering provider. Tests inject deterministic randomness and a no-op sleeper so conformance does not depend on wall-clock timing.

The provider timing contract is documented in:

- `docs/specification/provider-directed-retry-timing.md`

## Failure transitions

A retry sequence can end in four ways:

1. success, which keeps the original dispatch active
2. exhausted or timing-budget-stopped transient failure, which returns execution failure without direct fallback
3. model failure, which leaves retry and may enter guarded model fallback
4. provider failure, which leaves retry and may enter guarded provider fallback

Request and capability failures terminate immediately and do not consume another retry attempt.

An exhausted transient failure is not relabeled as a provider failure.

A retry timing hint never changes failure scope. A provider-scoped rate-limit failure can carry retry timing while remaining non-retryable under the current guarded taxonomy.

## Circuit-breaker interaction

Provider circuit observation happens after the retry sequence finishes.

This means a single retryable provider error does not by itself become cross-execution health evidence. If the retry succeeds, the circuit observes success. If the retry sequence ends in a declared service-health failure, that final response contributes one health observation to the provider-family circuit.

If enough service-health observations trip the circuit, future tasks may route around that provider before execution. The active exhausted transient task is not retroactively converted into fallback authority merely because the circuit opened.

The circuit specification is:

- `docs/specification/provider-circuit-breaker.md`

## Adapter boundary

Provider adapters remain single-attempt implementations.

Adapters may normalize provider-native timing metadata into `retry_after_seconds`, but they do not sleep or retry. Retry is owned by the runtime coordinator above the adapters. This prevents provider SDK behavior from creating hidden attempts and keeps the attempt budget observable across OpenAI, Anthropic, Google, local runtimes, and future providers.

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
- provider timing is honored as a minimum wait
- provider timing cannot create an extra attempt
- an over-budget provider wait stops rather than causes an early retry
- retry does not mutate routing authority
- a transient retry that later returns provider failure can enter guarded redispatch
- fallback dispatches receive their own independent retry budget
- failed fallback retries do not create a third provider chain
- policy cannot silently enable fallback after transient exhaustion
- policy cannot exceed two attempts in the guarded canary
- circuit observation occurs only after the retry sequence returns its final response

The conformance suites are:

- `tests/test_bounded_transient_retry.py`
- `tests/test_provider_retry_timing.py`
- `tests/test_guarded_canary_fallback.py`
- `tests/test_provider_circuit_breaker.py`

## Non-goals

This retry layer does not implement:

- circuit-state persistence itself
- provider health classification itself
- adaptive retry budgets
- HTTP-date Retry-After parsing
- cost-aware retry decisions
- telemetry persistence
- high or critical risk retries
- verifier execution
- human approval integration

Provider circuit state is implemented separately by `docs/specification/provider-circuit-breaker.md`.
