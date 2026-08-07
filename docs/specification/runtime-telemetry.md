# Persistent Runtime Telemetry

## Status

This specification defines the persistent operational telemetry layer for guarded TEO live provider execution.

Telemetry version: `1`

The scope remains explicit `high_volume_simple` work at low or medium effective risk.

## Purpose

Runtime telemetry provides evidence about what TEO actually executed.

It is not a routing policy, retry policy, fallback policy, provider-health policy, verification mechanism, approval mechanism, quality score, or cost calculator.

## Event granularity

TEO records one telemetry event for every actual provider attempt.

An attempt is the single provider invocation already defined by the provider-adapter contract. Telemetry is emitted immediately after the provider attempt returns and before any later retry delay or fallback decision.

## Recorded fields

A `provider_attempt` event records:

- telemetry version
- recorded timestamp
- internal dispatch ID
- task type
- effective risk level
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

The event does **not** persist the caller-controlled task ID. Correlation uses the internally generated dispatch ID.

The JSON Schema is:

- `reference/schemas/runtime-telemetry-event.schema.json`

## Content and identifier exclusion

The default telemetry record must not contain:

- caller-controlled task identifiers
- user identifiers
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

Content-bearing tracing requires a separate explicit policy, access controls, retention rules, and privacy analysis. It is not enabled by telemetry version 1.

## Normalized usage

`ProviderUsage` may contain:

- `input_tokens`
- `output_tokens`
- `cached_input_tokens`
- `cache_creation_input_tokens`
- `reasoning_output_tokens`
- `tool_tokens`
- `total_tokens`

Fields are optional because providers differ in what they expose and some failures do not include usage. Unknown usage fields fail closed when parsing the normalized contract.

### Anthropic

TEO normalizes total Anthropic input as the sum of ordinary input tokens, cache-creation input tokens, and cache-read input tokens. Cache reads and cache creation remain separately visible.

### OpenAI

TEO normalizes Responses usage including input, output, cached input, reasoning output, and total tokens when reported.

### Google Gemini

TEO normalizes Interactions usage including input, output, cached input, thought tokens, tool-use tokens, and total tokens when reported.

Provider-specific payload structure remains inside the adapter.

## Latency

`duration_ms` is wall duration around one provider invocation. It does not include retry sleep or later fallback execution.

Telemetry version 1 does not claim to measure time to first token, inter-token latency, complete user-visible latency, verification latency, or total workflow duration.

## Retry relationship

A retry remains the same dispatch. If one authorized retry occurs, both provider-attempt events retain the same dispatch ID, provider, model, reasoning effort, and assigned verifier while the attempt number increments.

The telemetry sink does not authorize retry.

## Fallback relationship

Fallback remains a new canonical redispatch. A failed primary attempt is retained under its original dispatch and a fallback attempt is recorded under the fresh fallback dispatch with `role: fallback`.

## Circuit-breaker relationship

Telemetry and provider circuits are separate observers of execution. Circuit state may use normalized service-health evidence to protect later tasks. Telemetry must not open, close, or probe a circuit.

## Verification relationship

Telemetry records the verifier assigned to the active dispatch so execution evidence can later be joined to verification evidence. Telemetry does not run the verifier and does not assign quality.

## Cost boundary

Telemetry version 1 does not calculate monetary cost. It persists normalized usage counts required for later source-backed and effective-dated cost attribution.

## Persistence and failure behavior

The reference runtime provides:

- `InMemoryRuntimeTelemetrySink` for deterministic tests
- `JsonlRuntimeTelemetrySink` for append-only local persistence

The default guarded runtime writes:

- `.teo/runtime/artifacts/runtime-telemetry.jsonl`

The repository ignores `.teo/` so local runtime artifacts are not accidentally committed.

Each line is one strict telemetry object. Malformed JSONL fails closed when read. Required telemetry persistence also fails closed: a provider attempt must not silently lose the operational evidence the active policy requires.

## Distributed-runtime boundary

The JSONL sink is a single-process reference implementation, not a production distributed telemetry system. Multi-process or distributed deployments need a sink that provides suitable concurrency, retention, access control, integrity, and export behavior.

## Conformance

The reference tests prove that:

- prompt and task content are absent from serialized telemetry
- caller-controlled task IDs and user identifiers are absent
- model output and artifact references are absent
- provider-native evidence IDs are absent
- every actual provider attempt is recorded
- retries retain one dispatch and increment attempt number
- fallback uses a new dispatch and `fallback` role
- latency is measured at attempt granularity
- usage is normalized for active providers
- JSONL survives separate sink instances
- malformed or unknown telemetry fields fail closed
- negative token usage fails closed
- telemetry persistence failure fails closed

The primary conformance suite is `tests/test_runtime_telemetry.py`.

## Non-goals

Telemetry version 1 does not implement:

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
