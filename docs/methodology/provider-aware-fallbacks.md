# Provider-Aware Fallback Methodology

## Decision

TEO prefers a capable implementation from a different provider family for its preselected routine fallback. Provider diversity is a resilience preference, not an absolute prohibition on using two models from the same provider.

The correct response depends on the scope of the failure. A model-specific limit or endpoint problem can leave another model from the same provider usable. An organization, project, account, authentication, billing, quota, regional, or provider-service failure can make every model behind that provider unavailable.

## Evidence

### OpenAI

OpenAI projects can configure model access and rate limits per model. OpenAI rate-limit errors can identify a specific model and organization, while project and organization controls can also create a broader shared boundary.

- https://help.openai.com/en/articles/9186755-managing-your-work-in-the-api-platform-with-projects
- https://help.openai.com/en/articles/5955604-how-can-i-solve-429-too-many-requests-errors
- https://help.openai.com/en/articles/6891753-what-are-the-best-practices-for-managing-my-rate-limits-in-the-api

### Anthropic

Anthropic applies service-configured limits at the organization level, but Messages API rate limits are measured for each model class and different models can have separate rate-limit pools. Organization-wide spend caps and service failures remain shared boundaries.

- https://platform.claude.com/docs/en/api/rate-limits

### Google Gemini

Gemini API rate limits are applied per project and vary by model and usage tier. Exceeding a model limit, project quota, or spend-based limit can all return resource-exhausted errors, so the error scope must be classified rather than inferred from the provider name alone.

- https://ai.google.dev/gemini-api/docs/rate-limits
- https://ai.google.dev/gemini-api/docs/api-errors
- https://ai.google.dev/gemini-api/docs/troubleshooting

### Resilience patterns

Transient failures should use bounded retries with exponential backoff and jitter. Persistent dependency failures should open a circuit breaker rather than create a retry storm. A circuit breaker must be scoped to the actual failing resource so one impaired model or endpoint does not unnecessarily block independent resources.

- https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- https://learn.microsoft.com/en-us/azure/architecture/best-practices/transient-faults
- https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker
- https://learn.microsoft.com/en-us/azure/architecture/antipatterns/retry-storm/

## Failure taxonomy

### Request-scoped failure

Examples:

- invalid input
- unsupported parameter
- malformed tool schema
- permission denied for the requested resource

Action:

- do not blindly retry or switch providers
- correct the request, permissions, or capability mismatch
- record the validation failure

### Transient model or endpoint failure

Examples:

- timeout
- temporary overload
- isolated 5xx response
- short-lived model-specific rate limit

Action:

- retry the same model with bounded exponential backoff and jitter
- honor `retry-after`
- stop when the retry budget is exhausted
- then use the preselected cross-provider fallback

### Model-scoped failure

Examples:

- model unavailable or deprecated
- model-specific quota exhausted
- model-specific context or tool limitation

Action:

- block the failed implementation
- prefer a capable model from another provider
- allow a same-provider model only when the failure is demonstrably model-scoped and no capable cross-provider candidate exists

### Provider-scoped failure

Examples:

- provider or project quota exhausted
- authentication or billing failure
- provider service outage
- regional provider impairment
- organization or account spend cap reached

Action:

- block the provider family for the redispatch
- open a provider-scoped circuit breaker
- select a fallback from a different provider
- do not attempt another model using the same affected credentials or quota boundary

### Capability-scoped failure

Examples:

- required tool unavailable
- missing multimodal support
- execution environment unavailable
- context requirement exceeds model capability

Action:

- reroute by capability fit
- provider diversity remains preferred, but capability correctness takes precedence

## TEO rules

1. **Cross-provider by default.** The routine fallback recorded in a dispatch must use a different provider family from the selected implementation.
2. **Failure scope before failover.** The orchestrator must classify the failure as request-, model-, provider-, or capability-scoped.
3. **Provider blocks are explicit.** Provider-scoped failures are represented through `blocked_providers` on redispatch.
4. **Model blocks are narrow.** Model-specific failures use `blocked_implementations` without unnecessarily blocking the provider.
5. **No automatic local models.** Local implementations can remain registered for future explicit use, but they are excluded from automatic fallback chains.
6. **Opus is not routine fallback.** `claude-opus-5` is reserved for the intentional `security_review` primary and evidence-based conditional escalation.
7. **Fallback is a new dispatch.** When a fallback becomes the executor, TEO must select a new independent verifier appropriate to that implementation and provider.
8. **Retries are bounded.** Use retry budgets, exponential backoff, jitter, and circuit breakers to prevent cascading failures.
9. **Capability remains authoritative.** Provider diversity never justifies selecting a model that cannot satisfy the task, tools, context, safety, or verification requirements.
10. **No universal model ranking.** Route choices remain evidence-driven and replaceable; this methodology defines resilience behavior, not permanent model superiority.
