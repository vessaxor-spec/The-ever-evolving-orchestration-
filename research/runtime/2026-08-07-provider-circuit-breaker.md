# Provider Circuit Breaker Research

Date: 2026-08-07
Status: implementation evidence
Scope: TEO guarded live runtime

## Research question

How should TEO represent provider health across separate executions without confusing provider outages with user-specific authentication, billing, quota, connection, model, or request failures?

## Evidence hierarchy

The implementation decision uses the following evidence order:

1. Current provider documentation and API error contracts
2. Established distributed-systems resilience guidance from AWS, Microsoft Azure, and Google Cloud
3. TEO's existing retry, fallback, verifier-independence, and connection-neutrality contracts
4. Practitioner reports as directional evidence only

Community reports are not treated as normative API contracts.

## Provider evidence

### OpenAI

OpenAI currently recommends exponential backoff for rate-limit failures and notes that rate limits apply to organizations and usage tiers. This makes a 429 insufficient evidence that OpenAI as a provider family is globally unhealthy.

Sources:

- https://help.openai.com/en/articles/6891753
- https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors
- https://developers.openai.com/api/docs/guides/latest-model

TEO implication:

- organization or usage-tier rate exhaustion must not open a provider-family circuit
- repeated server-side service failures may contribute to provider health
- hidden SDK retry remains disallowed because TEO owns retry budgets explicitly

### Anthropic

Anthropic documents distinct error classes. Authentication, billing, permission, and rate-limit errors are materially different from `api_error`, `timeout_error`, and `overloaded_error`. Anthropic also documents `retry-after` for 429 responses and states that SDKs automatically retry transient failures twice by default.

Sources:

- https://platform.claude.com/docs/en/api/errors
- https://platform.claude.com/docs/en/api/rate-limits
- https://platform.claude.com/docs/en/manage-claude/rate-limits-api

TEO implication:

- `rate_limit_error`, authentication, billing, and permission failures are tenant or connection concerns, not global provider-health evidence
- `overloaded_error`, repeated `api_error`, and provider timeouts are valid service-health signals after the active retry policy has completed
- TEO must continue disabling or avoiding hidden SDK retries when the control plane already owns the retry budget

### Google Gemini

Google's current Gemini API documentation distinguishes permission and quota errors from service availability failures. `rate_limit_exceeded` and `quota_exceeded` are 429 conditions tied to request/token or daily quota. `service_unavailable` is a 503 condition indicating overload or downtime. Google recommends exponential backoff with jitter and documents automatic retries in its SDKs.

Sources:

- https://ai.google.dev/gemini-api/docs/api-errors
- https://ai.google.dev/gemini-api/docs/troubleshooting
- https://ai.google.dev/gemini-api/docs/generate-content/api-errors

TEO implication:

- `RESOURCE_EXHAUSTED`, project quota, and permission failures must not poison provider-family health
- `UNAVAILABLE`, `INTERNAL`, and `DEADLINE_EXCEEDED` may contribute to service-health state after bounded retry

## Distributed-systems evidence

AWS describes circuit breaking as a mechanism that prevents repeated calls to a dependency that is likely to fail, while retry with backoff is intended for transient faults. AWS also recommends service-agnostic circuit-breaker implementation rather than duplicating the logic inside every dependency client.

Sources:

- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/circuit-breaker.html
- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html

Microsoft Azure describes the canonical `Closed`, `Open`, and `Half-Open` states. It recommends fast rejection while open, controlled recovery probes, configurable thresholds, and potentially increasing open timeouts when failures recur. Azure separately warns about retry storms and recommends honoring provider retry timing when available.

Sources:

- https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/

Google Cloud recommends truncated exponential backoff with jitter for retryable network/API failures, reinforcing the separation between bounded retry and circuit state.

Source:

- https://docs.cloud.google.com/iam/docs/retry-strategy

## Practitioner evidence

Practitioner reports show that sustained provider overload and quota behavior can be operationally noisy and may not always align cleanly with public status pages or user expectations. These reports support local observed-health state, but they do not determine TEO error semantics.

Directional sources:

- Anthropic overload reports: https://www.reddit.com/r/Anthropic/comments/1m1ddax/impossibly_too_many_api_error_529_overloaded_error/
- Google 429/503 guidance and discussion: https://discuss.ai.google.dev/t/handling-429-503-errors-from-the-gemini-api/124640
- Google platform-level 503 discussion: https://discuss.ai.google.dev/t/tier-3-project-persistent-503-429-errors-in-production-no-communication-need-eta/143670/9
- Retry-storm operational discussion: https://news.ycombinator.com/item?id=46866428

## Architecture findings

### 1. Circuit state belongs above provider adapters

Provider adapters remain single-attempt translators. They should never persist health state or choose alternate routes.

### 2. Circuit state must persist across executions

A retry budget is local to one dispatch. A circuit breaker exists specifically to remember repeated dependency failure across separate requests. The reference runtime therefore needs persistent state.

### 3. Global circuits must use service-health evidence only

TEO must not interpret the following as global provider outages:

- authentication failure
- permission failure
- billing failure
- organization/project/account quota exhaustion
- model-not-found
- bad request
- local connection failure

Those conditions may require local remediation or task-level fallback, but they are not sufficient to mark Anthropic, OpenAI, or Google globally unhealthy.

### 4. Open circuits should influence routing before execution

If a provider-family circuit is open, the runtime should add that provider to a copied task's blocked-provider constraints before canonical dispatch. The router then selects the alternate implementation and verifier. The circuit layer does not directly choose a model.

### 5. Recovery should be probed, not assumed

After cooldown, an open circuit becomes half-open. The guarded reference allows one probe dispatch at a time and requires two successful probes before closing. This avoids reopening full traffic after one lucky request.

### 6. Repeated trips should lengthen cooldown

The guarded policy starts at 60 seconds, doubles on repeated trips, and caps the cooldown at 300 seconds. This implements Azure's guidance that repeated failures may justify increasing the open interval while keeping the behavior bounded.

### 7. Corrupt health state must fail closed

Silently resetting a corrupt provider-health file could suddenly send traffic to a dependency that TEO previously isolated. The reference JSON store therefore rejects malformed state.

### 8. Reference persistence is not production distributed state

The JSON store proves persistence across separate executions in one runtime. Multi-process or distributed deployments require a transactional shared store with concurrency-safe probe claims. Redis, a database, or another durable coordination service belongs in a later runtime deployment layer.

## Guarded policy selected for TEO

The implementation uses:

- provider-family scope only
- three service-health failures within 120 seconds to trip
- 60-second initial open cooldown
- 2x cooldown multiplier on repeated trips
- 300-second cooldown cap
- one half-open probe dispatch at a time
- two successful half-open probes to close
- persistent JSON state for the reference implementation

These are guarded canary defaults, not universal production constants. They remain policy data so later operational evidence can change them without rewriting provider adapters.

## Important follow-up finding

All three providers document retry timing or backoff behavior, and Anthropic explicitly exposes `retry-after`. TEO's current normalized provider response does not yet preserve provider-directed retry timing. The bounded retry controller therefore uses its own policy delays only.

That is a real runtime gap, but it should be corrected in a separate change so circuit-state implementation is not mixed with a provider-response contract revision.

## Decision

Implement provider-family circuit breaking now, with service-health-only trip signals and persistent state above the adapter/retry layer.

Do not implement connection-scoped circuits, distributed state, external status-page ingestion, adaptive thresholds, or retry-header propagation in the same change.
