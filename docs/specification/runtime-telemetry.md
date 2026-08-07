# Persistent Runtime Telemetry

## Status

This specification defines the first persistent operational telemetry layer for TEO live provider execution.

Telemetry version: `1`

The scope remains the guarded `high_volume_simple` runtime at low or medium risk.

## Purpose

Runtime telemetry provides evidence about what TEO actually executed.

It is not a routing policy, retry policy, fallback policy, provider-health policy, verification mechanism, or approval mechanism.

The first version exists so later reliability, cost, latency, and route-outcome analysis can use measured provider-attempt evidence rather than assumptions.

## Event granularity

TEO records one telemetry event for every provider attempt.

An attempt is the single provider invocation already defined by the provider-adapter contract.

Telemetry is emitted immediately after the provider attempt returns and before any later retry delay or fallback decision.

This preserves failed attempts that would otherwise disappear behind a successful retry or fallback.

## Recorded fields

A `provider_attempt` event records:

- telemetry version
- recorded timestamp
- task ID
- dispatch ID
- task type
- risk level
- execution role: `primary` or `fallback`
- attempt number within the dispatch
- provider family
- model
- selected reasoning effort
- assigned verifier provider family
- assigned verifier model
- provider-attempt duration in milliseconds
- provider execution status
- normalized failure scope and code when failed
- normalized provider retry timing when present
- normalized token usage when the provider reports it

The JSON Schema is:

- `reference/schemas/runtime-telemetry-event.schema.json`

## Content-exclusion rule

The default telemetry record must not contain:

- task text
- prompts
- conversation messages
- provider request body
- model output
- output artifact reference
- provider-native response payload
- provider-native headers
- credentials
- authorization headers
- passwords or tokens
- connection mechanism
- user identifiers

This is deliberate. Current OpenTelemetry GenAI guidance warns that model input/output message fields may contain sensitive or PII data.

Content-bearing tracing may be useful in some deployments, but it requires a separate explicit policy, access controls, retention rules, and privacy analysis. It is not enabled by telemetry v1.

## Normalized usage

`ProviderUsage` may contain:

- `input_tokens`
- `output_tokens`
- `cached_input_tokens`
- `cache_creation_input_tokens`
- `reasoning_output_tokens`
- `tool_tokens`
- `total_tokens`

Fields are optional because providers differ in what they expose and some failures do not include usage.

Unknown usage fields fail closed when parsing the normalized contract.

### Anthropic

TEO normalizes total Anthropic input as the sum of:

- ordinary input tokens
- cache-creation input tokens
- cache-read input tokens

Cache reads and cache creation remain separately visible as additional fields.

### OpenAI

TEO normalizes current Responses usage including input, output, cached input, reasoning output, and total tokens when reported.

### Google Gemini

TEO normalizes current Interactions usage including input, output, cached input, thought tokens, tool-use tokens, and total tokens.

Provider-specific payload structure remains inside the adapter.

## Latency

`duration_ms` is wall duration around one provider invocation.

It does not include retry sleep or later fallback execution.

This first version does not claim to measure time to first token, inter-token latency, complete user-visible latency, verification latency, or total workflow duration.

## Retry relationship

A retry remains the same dispatch.

If the first provider attempt fails transiently and TEO performs its one authorized retry, telemetry records:

- primary attempt 1
- primary attempt 2

Both events share the same dispatch ID, provider, model, reasoning effort, and verifier.

The telemetry sink does not authorize the retry.

## Fallback relationship

Fallback remains a new canonical redispatch.

If a provider or model failure triggers fallback, telemetry records the failed primary attempt under its original dispatch and records fallback attempts under the new dispatch with `role: fallback`.

This preserves the distinction between repeated execution of one route and a routing decision change.

## Circuit-breaker relationship

Telemetry and provider circuits are separate observers of execution.

Circuit state may use normalized failure evidence to protect later tasks. Telemetry persists execution evidence for analysis.

The telemetry sink must not open, close, or probe a circuit.

## Verification relationship

Telemetry records the verifier assigned to the active dispatch so later execution evidence can be joined to verification evidence.

Telemetry does not run the verifier and does not assign a quality score.

A future route-quality dataset should join provider attempts to independent verification and final outcome records rather than allowing the execution model to grade itself.

## Cost boundary

Telemetry v1 does not calculate monetary cost.

It persists the normalized usage counts required for later price calculation.

Pricing is time-sensitive and may depend on model, cache mode, service tier, batch mode, input size, or future commercial terms. Cost attribution therefore requires a separate dated pricing source and calculation version.

## Persistence

The reference runtime provides:

- `InMemoryRuntimeTelemetrySink` for deterministic tests
- `JsonlRuntimeTelemetrySink` for append-only local persistence

The default guarded runtime writes:

- `.teo/runtime/artifacts/runtime-telemetry.jsonl`

when the default artifact root is used.

Each line is one strict telemetry object.

Malformed JSONL fails closed when read by the reference sink.

## Distributed-runtime boundary

The JSONL sink is not a production distributed telemetry system.

Multi-process or distributed deployments need a sink that provides appropriate concurrency, retention, access control, integrity, and export behavior.

A future OpenTelemetry exporter can implement `RuntimeTelemetrySink` without changing provider routing or adapter contracts.

## Conformance

The reference tests prove that:

- prompt/task content is absent from serialized telemetry
- model output and artifact references are absent
- provider-native evidence IDs are absent
- every actual provider attempt is recorded
- retries retain one dispatch and increment attempt number
- fallback uses a new dispatch and `fallback` role
- latency is measured at attempt granularity
- usage is normalized for the active providers
- JSONL survives separate sink instances
- unknown telemetry fields fail closed
- negative token usage fails closed
- existing retry, fallback, circuit, routing, verification, and evidence controls remain unchanged

The primary conformance suite is:

- `tests/test_runtime_telemetry.py`

## Non-goals

Telemetry v1 does not implement:

- prompt or response tracing
- monetary cost attribution
- quality scoring
- route optimization
- provider selection based on telemetry
- adaptive retry budgets
- adaptive circuit thresholds
- streaming latency metrics
- distributed telemetry storage
- OpenTelemetry export
- verifier execution
- human approval integration
