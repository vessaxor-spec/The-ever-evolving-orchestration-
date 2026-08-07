# Provider-Directed Retry Timing

## Status

This specification defines how the guarded TEO runtime uses provider-requested retry timing without allowing a provider or adapter to expand the retry budget.

It applies to the low/medium-risk `high_volume_simple` live canary.

## Core rule

A provider timing hint is a minimum wait, not permission to retry.

The provider adapter may normalize a retry duration from provider-native response metadata into:

`retry_after_seconds`

The retry controller remains the only layer that decides whether another attempt is authorized.

## Normalized field

`ProviderExecutionResponse.retry_after_seconds`:

- is optional
- is expressed in seconds
- must be finite and non-negative
- is valid only on failed responses
- does not expose the raw provider header or provider-native error object

Current adapter extraction:

- Anthropic: numeric `retry-after` header
- OpenAI: numeric `Retry-After` header if actually present
- Google: numeric `Retry-After` header if present, otherwise standard `google.rpc.RetryInfo.retryDelay` if present

Absence of a provider hint is normal. TEO then uses its local retry backoff policy.

## Retry authority

A timing hint must not:

- make a non-transient failure retryable
- add another provider attempt
- change the selected provider or model
- change reasoning effort
- change the verifier
- create a fallback dispatch
- change provider circuit state directly
- bypass risk or human-approval controls

For the current canary, only `transient` failures are retry-eligible.

A rate-limit response may carry retry timing while remaining provider-scoped under current TEO failure policy. The timing is preserved but does not override retry eligibility.

## Delay calculation

When a transient failure is eligible for another attempt:

1. compute TEO's local exponential-backoff delay with jitter
2. read normalized `retry_after_seconds`, if present
3. if the provider hint is within the guarded provider-wait budget, use the greater of the local delay and the provider hint
4. if the provider hint exceeds the guarded provider-wait budget, stop the retry sequence rather than retrying earlier than requested

The current machine-readable policy is:

- `policy/runtime/canary-retry.yaml`

Current limits:

- maximum two provider attempts per dispatch
- 0.5-second local initial delay
- 2x local backoff multiplier
- 2-second local backoff cap
- plus or minus 20 percent local jitter
- provider-directed wait budget: 60 seconds
- provider hint over 60 seconds: stop

The 60-second provider-wait budget is a guarded TEO canary policy choice, not a provider guarantee or universal production value.

## Why provider timing may exceed local backoff

The local `max_delay_seconds` controls TEO-generated exponential backoff. It does not authorize TEO to violate a longer provider minimum.

For example, if local backoff computes 0.5 seconds and a provider says wait 5 seconds, the effective delay is 5 seconds.

If the provider asks for 90 seconds, the canary does not clamp that request to 2 or 60 seconds and retry early. It stops after the current failed attempt.

## Interaction with fallback

Provider timing does not alter fallback rules.

- transient failure with an in-budget hint may retry under the same dispatch
- exhausted transient failure remains transient and does not directly fallback
- model/provider failure may enter the guarded redispatch path regardless of whether retry timing metadata was present

Fallback remains a new TEO dispatch with a fresh independent verifier.

## Interaction with circuit breaking

Circuit observation still occurs after the retry sequence returns its final response.

A provider-directed delay does not create extra circuit observations. If a retry succeeds, the circuit observes success. If the retry sequence ends in a declared service-health failure, that final response contributes one health observation.

## Connection neutrality

Retry timing is derived from provider response metadata, not from how the runtime authenticated or connected.

API keys, OAuth, delegated identity, service accounts, connector sessions, SDK-backed credentials, credential brokers, and future connection methods do not change the retry timing contract.

## Evidence basis

The supporting research record is:

- `research/runtime/2026-08-07-provider-directed-retry-timing.md`

It reviews current Anthropic, Google Gemini, OpenAI, AWS, Azure, and Google Cloud guidance.

## Conformance

The tests prove that:

- numeric Retry-After headers are normalized without leaking headers
- invalid or negative header values are ignored
- successful responses cannot carry retry timing
- negative normalized retry timing fails closed
- provider timing is used as a minimum wait
- a provider hint over the guarded wait budget stops rather than retries early
- provider timing never creates an additional attempt
- non-transient failures remain non-retryable even when timing metadata is present
- Anthropic retry-after is normalized
- OpenAI retry-after is normalized when present without assuming it is guaranteed
- standard Google RetryInfo is normalized when present

The conformance suite is:

- `tests/test_provider_retry_timing.py`

## Non-goals

This slice does not implement:

- HTTP-date Retry-After parsing
- adaptive wait budgets
- rate-limit-specific same-dispatch retry policy changes
- hidden provider SDK retries
- distributed delayed-job scheduling
- streaming retry semantics
- telemetry persistence
- high or critical risk live execution
