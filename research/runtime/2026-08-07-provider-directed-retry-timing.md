# Provider-Directed Retry Timing Research

Date: 2026-08-07
Status: implementation evidence
Scope: TEO guarded live runtime

## Research question

When a provider indicates how long a client should wait before retrying, how should TEO preserve and use that signal without allowing provider-native headers, SDK behavior, or rate-limit policy to acquire orchestration authority?

## Evidence hierarchy

1. Current provider documentation and API error contracts
2. Established cloud retry guidance
3. TEO's existing single-attempt adapter, bounded retry, fallback, circuit, and connection-neutral contracts
4. Practitioner evidence only where useful for operational context

## Anthropic

Anthropic's current API error documentation states that official SDKs automatically retry transient failures twice by default and honor the `retry-after` header when present. Anthropic's rate-limit documentation explicitly defines `retry-after` as the number of seconds to wait and warns that earlier retries will fail.

Sources:

- https://platform.claude.com/docs/en/api/errors
- https://platform.claude.com/docs/en/api/rate-limits
- https://platform.claude.com/docs/en/build-with-claude/fast-mode

TEO implication:

- a numeric Anthropic `retry-after` is authoritative timing evidence for the failed provider response
- TEO should normalize the duration rather than persist the provider-native header
- the hint does not decide whether TEO is allowed to retry
- hidden SDK retries remain incompatible with TEO-owned attempt budgets unless explicitly disabled or accounted for

## Google Gemini

The current Gemini Interactions API error page recommends waiting and retrying with exponential backoff for rate-limit and service-unavailable failures. The current Interactions error schema documents `code` and `message` but does not promise a `RetryInfo` detail on every error.

Google's common API error model defines `google.rpc.RetryInfo` with a `retry_delay` recommendation and instructs clients to wait at least that duration before retrying, then combine it with exponential backoff on repeated failure.

Sources:

- https://ai.google.dev/gemini-api/docs/api-errors
- https://ai.google.dev/gemini-api/docs/troubleshooting
- https://docs.cloud.google.com/php/docs/reference/common-protos/latest/Rpc.RetryInfo
- https://docs.cloud.google.com/iam/docs/retry-strategy

TEO implication:

- local exponential backoff remains valid when Gemini provides no explicit timing hint
- if a standard `google.rpc.RetryInfo` detail appears, TEO can normalize its duration without making that field mandatory for the Interactions API
- a generic numeric `Retry-After` response header may also be normalized when present

## OpenAI

OpenAI's current API and help guidance emphasizes explicit retry limits and exponential backoff for rate-limit or transient failures. Current public documentation used in this review does not establish a universal `Retry-After` response-header guarantee across the Responses API.

Sources:

- https://developers.openai.com/api/docs/guides/latest-model
- https://help.openai.com/en/articles/6891753
- https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors

TEO implication:

- TEO must not require a retry header from OpenAI
- TEO may normalize a standards-compatible numeric `Retry-After` header if one is actually returned by the runtime connection
- in the absence of an explicit provider hint, TEO uses its own bounded exponential backoff with jitter

## Cloud resilience guidance

AWS, Azure, and Google Cloud guidance consistently separate retry eligibility from retry delay. Exponential backoff and jitter reduce synchronized retry pressure; provider-directed retry timing should be honored when available; retry counts still need explicit limits to prevent retry storms.

Sources:

- https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html
- https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/
- https://docs.cloud.google.com/iam/docs/retry-strategy

## Architecture findings

### 1. Retry timing belongs in the normalized provider response

The adapter is the only layer that can see provider-native response headers or structured provider error details. It should extract a duration and expose only normalized `retry_after_seconds`.

The raw header or provider-specific error structure must not cross the adapter boundary.

### 2. A timing hint is not retry authority

`retry_after_seconds` answers only: if another attempt is already permitted, what is the minimum wait?

It must not:

- change failure scope
- create another attempt
- cause redispatch
- select fallback
- change provider or model
- bypass circuit state

### 3. TEO should wait for the greater of local backoff and provider minimum

When a retryable transient response includes a hint inside the guarded wait budget:

`effective delay = max(local jittered backoff, provider retry_after_seconds)`

This prevents TEO from retrying earlier than the provider requested while retaining its own backoff floor.

### 4. Excessive provider waits should stop the canary rather than retry early

The guarded canary sets a 60-second maximum provider-directed wait budget. If a provider asks for more than 60 seconds, TEO returns the current failure instead of sleeping indefinitely or violating the provider's requested minimum.

This 60-second value is a TEO canary policy choice, not a universal provider constant. It remains machine-readable policy so operational evidence can revise it.

### 5. Provider hints cannot expand the attempt budget

The guarded runtime still allows at most two provider attempts per dispatch. A hint can only affect timing between already-authorized attempts.

### 6. Non-transient failures remain non-retryable in the current canary

A rate-limit failure may carry `retry-after`, especially on Anthropic, but the current TEO canary classifies tenant/account rate-limit conditions as provider-scoped task recovery rather than transient same-dispatch retry.

The timing hint is still preserved for observability and future policy work, but it does not override the current failure taxonomy.

### 7. Circuit behavior remains unchanged

Provider circuit observation occurs after the retry controller returns its final response. A longer provider-directed wait does not create additional health observations.

## Guarded policy selected

`policy/runtime/canary-retry.yaml` now requires:

- transient-only retry
- maximum two attempts per dispatch
- local exponential backoff with jitter
- provider retry hints honored as minimum waits
- 60-second maximum provider-directed wait budget
- stop if a provider hint exceeds that budget
- no fallback solely because transient retry is exhausted

## Decision

Normalize provider-directed retry timing in adapter responses and let the bounded retry controller honor it without changing retry eligibility or attempt count.

Do not introduce hidden SDK retry, rate-limit-specific redispatch changes, adaptive wait budgets, distributed schedulers, or provider-native header persistence in this change.
