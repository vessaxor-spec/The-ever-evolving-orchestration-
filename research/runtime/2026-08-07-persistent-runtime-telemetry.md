# Runtime research: persistent provider-neutral telemetry

Date: 2026-08-07

Status: implementation evidence

## Question

What runtime evidence should TEO persist for live provider execution so that later reliability, cost, and route-quality decisions can be based on measured outcomes without coupling TEO to one provider or storing sensitive model content by default?

## Conclusion

TEO should persist one provider-neutral telemetry event for every actual provider attempt.

The first telemetry contract should record execution identity, routing identity, latency, normalized token usage, normalized failure state, retry timing, and verifier identity. It should not persist prompts, model outputs, provider-native payloads, credentials, authorization material, or connection type by default.

Cost calculation and quality scoring should remain separate evidence layers.

This separation is supported by current OpenTelemetry GenAI conventions, the usage objects exposed by Anthropic, OpenAI, and Google, and practitioner experience with multi-provider production systems.

## OpenTelemetry findings

### Current semantic-convention baseline

OpenTelemetry Semantic Conventions 1.43.0 define a common vocabulary for telemetry across systems and explicitly include Generative AI conventions.

Sources:

- https://opentelemetry.io/docs/specs/semconv/
- https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/

Relevant concepts include provider identity, request/response model identity, and input/output token usage. The conventions are intentionally designed to make telemetry consumable across libraries and platforms.

### Content is a different risk class

OpenTelemetry explicitly warns that GenAI input and output message attributes are likely to contain sensitive information, including user or PII data.

This supports a conservative TEO default:

- persist operational metadata automatically
- do not persist prompt or response content automatically
- treat content tracing as a separate, explicitly authorized policy decision

This also avoids turning runtime telemetry into an uncontrolled copy of user data.

## Anthropic findings

Sources:

- https://platform.claude.com/docs/en/api/typescript/messages/create
- https://platform.claude.com/docs/en/api/go/messages

Anthropic Message responses expose a `usage` object.

Current documented usage includes:

- `input_tokens`
- `cache_creation_input_tokens`
- `cache_read_input_tokens`
- `output_tokens`
- output-token details including thinking tokens on supported paths

Anthropic explicitly states that total input tokens are the sum of uncached input tokens, cache-creation input tokens, and cache-read input tokens.

TEO therefore normalizes:

- total Anthropic input into `input_tokens`
- cache reads into `cached_input_tokens`
- cache writes into `cache_creation_input_tokens`
- output into `output_tokens`
- thinking-token details into `reasoning_output_tokens` when present

TEO does not preserve the provider-native usage object.

## OpenAI findings

Sources:

- https://platform.openai.com/docs/api-reference/responses-streaming/response/refusal/delta?lang=curl
- https://developers.openai.com/api/docs/guides/latest-model

Current OpenAI Responses usage exposes:

- `input_tokens`
- `input_tokens_details.cached_tokens`
- `output_tokens`
- `output_tokens_details.reasoning_tokens`
- `total_tokens`

Current GPT-5.6 guidance also recommends tracking cache behavior, total tokens, latency, and cost when comparing configurations.

TEO therefore normalizes those usage counts without deriving price inside the provider adapter or telemetry sink.

The provider usage response is evidence. Pricing is a separate time-sensitive registry concern.

## Google Gemini findings

Source:

- https://ai.google.dev/api/interactions-api-v1

The current Gemini Interactions API exposes usage fields including:

- `total_input_tokens`
- `total_output_tokens`
- `total_cached_tokens`
- `total_thought_tokens`
- `total_tool_use_tokens`
- `total_tokens`

Google documents thought tokens separately from ordinary generated output tokens. TEO therefore retains a separate `reasoning_output_tokens` field rather than imposing a provider-independent arithmetic relationship between thought and output tokens.

## Why cost is not part of telemetry v1

Provider pricing changes independently from execution records. Prices may also vary by model, service tier, batch mode, prompt length, cache behavior, or future commercial terms.

If an attempt event stores a calculated cost as though it were an immutable provider fact, later price corrections can make historical interpretation ambiguous.

TEO v1 therefore stores the raw normalized usage evidence needed for later cost attribution and leaves pricing to a dated, source-backed calculation layer.

A later cost record should identify:

- pricing source and effective date
- model and service tier
- input, cached input, cache creation, output, reasoning, and tool-use treatment where applicable
- currency
- calculation version

## Why quality is not part of telemetry v1

The model that produced an answer should not be allowed to define the quality score for its own answer.

Quality evidence should come from independent verification, executable tests, human approval where required, or outcome measurements.

Runtime telemetry can later be joined to those evidence records through task and dispatch identifiers.

This preserves TEO's independent-verification principle.

## Latency semantics

The first telemetry layer records provider-attempt wall duration measured around the single provider invocation.

It does not yet claim to measure:

- time to first token
- inter-token latency
- queue delay exposed by provider internals
- end-to-end user latency
- verification latency
- total task completion latency

Those are separate useful measures once streaming and full workflow telemetry exist.

## Attempt-level rather than outcome-only logging

Retries and fallback can materially change latency, usage, and later cost.

If telemetry records only the final successful provider call, it hides the resources and failures that occurred before success.

TEO therefore records every provider attempt immediately after it completes and before any later retry sleep, fallback redispatch, or final outcome.

This means a task that experiences:

1. primary failure
2. primary retry
3. fallback redispatch
4. fallback success

produces four provider-attempt events if all four provider attempts actually occur.

## Practitioner evidence

Practitioner sources are directional evidence only. They do not define TEO policy.

Recent discussions consistently emphasize:

- latency by model/provider
- token usage
- error rates
- privacy-safe logging
- visibility across fallback paths
- cost per completed task rather than only cost per provider call

Examples reviewed:

- https://www.reddit.com/r/Observability/comments/1u8hw4g/what_do_you_actually_monitor_for_llm_apps_in/
- https://www.reddit.com/r/LangChain/comments/1v4b9cw/failover_between_llm_providers_saved_our_uptime/
- https://www.reddit.com/r/mlops/comments/1ujw4ko/how_we_finally_got_real_observability_into_our/
- https://www.reddit.com/r/LLMDevs/comments/1vf0hgy/which_inference_provider_are_you_using_in/

A particularly relevant failure pattern is hidden cost and latency amplification when fallback chains replay work. TEO already limits fallback depth; attempt-level telemetry makes that amplification measurable.

## Telemetry v1 record

One provider-attempt event records:

- telemetry version
- event type
- timestamp
- task ID
- dispatch ID
- task type
- risk level
- primary or fallback role
- attempt number within the dispatch
- provider family
- model
- selected reasoning effort
- assigned verifier provider/model
- provider-attempt duration
- success or failure
- normalized failure scope/code
- normalized provider retry hint
- normalized token usage

It deliberately excludes:

- task text
- system prompts
- conversation content
- model output
- output artifact reference
- provider-native payload
- request/response headers
- credential material
- authorization data
- connection mechanism
- user identifiers
- calculated price
- model-generated quality score

## Persistence choice

The reference implementation uses append-only JSONL.

Advantages for the reference runtime:

- transparent and inspectable
- one immutable line per observed attempt
- easy to replay into later analysis
- does not require a telemetry backend to validate the contract

Limitations:

- it is a single-process reference sink
- it is not a distributed transaction log
- it has no retention, rotation, encryption-at-rest, or centralized access-control layer
- concurrent multi-process writers require a stronger sink

A future OpenTelemetry exporter or shared telemetry backend can implement the same `RuntimeTelemetrySink` boundary without changing routing semantics.

## Architectural decision

Telemetry observes execution. It does not control execution.

The telemetry sink must not:

- select a provider or model
- change reasoning effort
- authorize retry
- trigger fallback
- open or close provider circuits
- select a verifier
- satisfy human approval
- change specialist or worker routing

This keeps evidence collection separate from authority.
