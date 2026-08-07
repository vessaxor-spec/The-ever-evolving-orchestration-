---
capsule_id: TEO-CAPSULE-0006
status: accepted
captured_at: 2026-08-07T12:56:00+02:00
snapshot_commit: 37e1d86b4a637834774b95bbe742795783063cf9
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0001
  - TEO-CAPSULE-0005
immutability: accepted capsules are never rewritten
---

# Capsule 0006: TEO Becomes an Evidence-Bearing Live Runtime

This capsule records the state of **The Ever-Evolving Orchestration** after the reference control plane crossed from dispatch planning into guarded live execution, recovery, persistent operational evidence, and executable independent verification.

It preserves the repository at commit [`37e1d86b4a637834774b95bbe742795783063cf9`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/commit/37e1d86b4a637834774b95bbe742795783063cf9), captured on **7 August 2026 at 12:56 CEST**.

It references [TEO-CAPSULE-0001](0001-2026-08-05-reference-control-plane.md), which preserved the first runnable control plane, and [TEO-CAPSULE-0005](0005-2026-08-06-principal-engineering-control-plane.md), which preserved the 10-team, 78-specialist principal-engineering activation. Earlier accepted capsules remain untouched.

## Why this moment was preserved

Capsule 0005 ended with an operational horizon rather than a live provider runtime.

At that point TEO could select teams, workers, specialists, implementations, fallbacks, verifiers, risk controls, and human-approval requirements, but execution still stopped at the dispatch boundary.

This snapshot preserves the moment when those control-plane decisions began to govern real provider execution without collapsing provider access, recovery, verification, or evidence collection into the adapters themselves.

The important change is not simply that TEO can call models.

The important change is that TEO can now execute a bounded route while retaining explicit control over:

- provider and model authority
- reasoning effort
- connection neutrality
- transient retry
- model and provider fallback
- provider-family health state
- retry timing
- persistent attempt evidence
- fresh verifier assignment after redispatch
- live independent verification
- finalization and human authority

The runtime therefore remains an orchestration system rather than becoming a collection of provider SDK wrappers.

## Runtime progression preserved by this capsule

The live runtime was built in deliberately separated slices.

### Provider-adapter contract

The first runtime boundary established a provider-neutral execution request and response contract.

Adapters may translate an already-authorized TEO dispatch into a provider operation and normalize the result. They may not choose another provider, change the selected model, retry themselves, invoke fallback, select a verifier, satisfy human approval, or mutate routing policy.

Failure scopes are normalized as:

- `request`
- `transient`
- `model`
- `provider`
- `capability`

The scope describes what happened. It does not itself decide recovery.

### Connection-neutral access

TEO does not treat API keys as the architecture.

Provider execution is separated from connection mechanics through `ProviderConnection`.

A route may therefore remain the same whether access is supplied through:

- API key
- OAuth
- delegated identity
- service account
- connector session
- SDK-managed identity
- credential broker
- local runtime connection
- another provider-supported mechanism

The connection method does not change the selected team, worker, specialist, provider family, model, reasoning effort, fallback, or verifier.

This applies across OpenAI and Codex, Anthropic and Claude, Google and Gemini or Antigravity, local runtimes, and future providers.

## Live provider canaries

The guarded runtime now contains live provider adapters for the bounded `high_volume_simple` path at low or medium risk:

- Anthropic Claude Haiku 4.5
- OpenAI GPT-5.6 Luna
- Google Gemini 3.6 Flash

The adapters remain single-attempt boundaries.

The first live route is intentionally narrow. It proves execution control without granting broad autonomous authority to the runtime.

High and critical risk live execution remain outside this canary.

## Effort-aware execution

The specialist-routing audit introduced model-specific reasoning effort as executable routing metadata rather than decorative YAML.

The runtime preserves the selected effort through the provider boundary where supported.

At this snapshot:

- OpenAI effort is mapped into the supported Responses API reasoning control
- Gemini thinking level is mapped into its supported provider control
- unsupported model effort controls fail closed rather than being invented

The broader specialist-routing layer covers all 78 active specialists with explicit primary, fallback, verifier, and reasoning templates.

Claude Opus 5 is no longer treated mainly as a security or generic escalation model. It is a deliberate primary for selected high-consequence specialists whose work requires deep systems, regulatory, safety, formal, physical, or cross-domain reasoning.

## Recovery is separated into distinct mechanisms

One of the most important runtime principles preserved here is that retry and fallback are not the same operation.

### Transient retry

A bounded transient retry:

- keeps the same dispatch ID
- keeps the same provider
- keeps the same model
- keeps the same reasoning effort
- keeps the same assigned verifier
- does not re-run routing

The guarded runtime allows at most two provider attempts per dispatch.

A retry does not gain authority to select a different implementation.

### Model or provider fallback

A model or provider fallback is a new orchestration decision.

The runtime therefore returns to canonical routing and creates a new dispatch.

The redispatch:

- blocks the failed model for a model-scoped failure, or the provider family for a provider-scoped failure
- selects the next eligible implementation under existing policy
- receives a new dispatch ID
- receives a fresh independent verifier

A failed fallback does not automatically chain into an unlimited third-provider cascade.

### Provider-directed retry timing

Provider timing hints are treated as timing evidence, not retry authority.

When another transient attempt is already allowed, TEO may honor a normalized provider-requested minimum wait.

The runtime uses the greater of its own bounded delay and an acceptable provider hint.

A provider hint cannot:

- create another attempt
- increase the retry budget
- change failure scope
- trigger fallback
- change the selected model
- mutate circuit state

If a provider requests a wait outside the guarded timing budget, TEO stops rather than retrying early.

## Stateful provider-family health

TEO now persists provider-family circuit state across separate executions.

The circuit breaker uses:

- Closed
- Open
- Half-Open

Repeated service-health failures can open a provider circuit. After cooldown, bounded recovery probes determine whether normal routing can resume.

The circuit layer does not directly select a replacement model. An open provider is represented as a blocked-provider constraint and canonical TEO routing chooses the eligible alternative.

A crucial distinction is preserved between service health and connection or entitlement problems.

The following do not by themselves poison global provider-family health:

- authentication failure
- billing failure
- permission failure
- account or project quota exhaustion
- ordinary rate-limit exhaustion
- model-not-found
- malformed request
- local connection failure

This prevents one user's credentials, quota, or account condition from incorrectly marking an entire provider as unhealthy.

## Persistent runtime telemetry

Every actual provider attempt can now produce persistent provider-neutral telemetry.

The default guarded reference sink is append-only JSONL.

Each provider-attempt event can preserve:

- task and dispatch identifiers
- task type and effective risk
- primary or fallback role
- provider family
- model
- reasoning effort
- attempt number
- attempt duration
- success or normalized failure state
- retry timing when present
- assigned verifier identity
- normalized provider-reported token usage

A failed first attempt remains visible even when a retry or fallback later succeeds.

### Privacy boundary

Telemetry v1 is content-free by default.

It does not persist:

- task text
- prompts
- model output
- output artifact contents
- provider-native request payloads
- provider-native response payloads
- provider headers
- credentials
- authorization material
- connection mechanism
- user identifiers

The runtime records operational evidence without turning observability into indiscriminate content collection.

### Usage is evidence, not cost

Provider token usage is normalized where stable equivalents exist.

The current neutral envelope can represent:

- input tokens
- output tokens
- cached input tokens
- cache-creation input tokens
- reasoning or thought tokens
- tool-use tokens
- total tokens

TEO does not calculate monetary cost inside telemetry v1.

Pricing is time-sensitive external evidence. Historical cost attribution must eventually combine immutable usage evidence with a dated, source-backed pricing record and a versioned calculation method.

The telemetry layer also does not invent a quality score. Quality must come from independent verification, tests, human evaluation, or measured outcomes.

## Live independent verification

This snapshot also preserves the first executable model-verification gate.

A successful provider call is not a completed TEO outcome.

The runtime can now execute the verifier already assigned by the active dispatch for the guarded low and medium risk canary.

### Verifier authority

The verification runtime does not choose its preferred judge.

It executes only the verifier selected by routing.

The live gate requires:

- a different verifier model from the executor
- a different verifier provider family from the executor
- one verifier attempt
- structured output
- no verifier retry
- no verifier fallback
- no model-verifier substitution for human approval

Verifier infrastructure failure is not converted into a fabricated `failed`, `passed`, or `needs_human` judgment. It means valid verification evidence was not obtained.

### Blinded pointwise rubric

The verifier sees:

- original task
- candidate output
- declared verification methods
- fixed evaluation criteria

It does not see:

- executor provider
- executor model
- retry history
- fallback history
- circuit history
- runtime telemetry
- usage
- cost

The current fixed criteria are:

- `output_present`
- `task_adherence`
- `format_consistency`
- `unsupported_claims_absent`

Each criterion returns:

- `pass`
- `fail`
- `uncertain`

The overall verifier status is:

- `passed`
- `failed`
- `needs_human`

Uncertainty must remain uncertainty. The verifier is not allowed to invent semantic ground truth that is absent from the supplied evidence.

## Provider-diverse canary verifier ladder

The live-verification review found that model independence alone was insufficient.

The previous bounded route could use one Anthropic model to execute and another Anthropic model to verify. That met model independence but not provider diversity.

The active canary now preserves the following verifier paths:

| Active execution | Assigned verifier |
|---|---|
| Claude Haiku 4.5 primary | Gemini 3.6 Flash |
| Gemini 3.6 Flash after a Haiku model-specific failure | Claude Sonnet 5 |
| Gemini 3.6 Flash after Anthropic provider failure | GPT-5.6 Sol |

The runtime does not hard-code these replacements. Routing re-evaluates verifier eligibility under the active constraints.

If no provider-diverse verifier remains eligible, the route fails closed.

## Existing finalization remains authoritative

Live verification feeds the existing `VerificationResult` contract.

The normal finalization gate still requires:

- matching dispatch identity
- the verifier model assigned by routing
- execution and verification independence
- successful execution
- acceptable verification state
- qualified human approval where policy requires it

A model verifier cannot approve its own authority expansion.

A model verifier cannot satisfy a critical human-approval requirement.

## Evidence-backed architecture principle

The runtime work preserved a deeper design rule:

> Operational mechanisms should produce evidence without acquiring unrelated authority.

Adapters execute but do not route.

Connections authenticate but do not choose models.

Retry controllers repeat bounded transient attempts but do not choose fallbacks.

Circuit breakers represent health state but do not choose replacements.

Telemetry observes but does not optimize routes by itself.

Verifiers judge the assigned evidence but do not select themselves or replace human authority.

This separation is the runtime expression of TEO's original principle:

> **The model is not the architecture.**

## Regulated evidence boundary remains unchanged

The six-card evidence-backed freshness pilot remains exactly:

- Legal Operations
- Tax Strategist
- Loan Officer Assistant
- Compliance Auditor
- Civil Engineer
- Embedded Engineer

None of the runtime execution work authorizes broader evidence-registry rollout.

The pilot still requires demonstrated maintainability, stable authority resolution, refresh cycles, mutation-test survival, ownership, and explicit approval before wider expansion.

## Known limitations

At this snapshot:

- live provider execution remains restricted to explicit `high_volume_simple` work at low or medium risk
- live model verification remains restricted to the same guarded canary
- high and critical risk live execution are not authorized
- qualified-human approval remains outside the automated reference runtime
- verifier retry, verifier fallback, verifier circuits, and multi-judge consensus are not implemented
- verifier quality has not yet been calibrated against a human-rated ground-truth set
- JSON circuit state and JSONL telemetry are single-process reference persistence, not distributed coordination infrastructure
- distributed circuit state and distributed telemetry export are not implemented
- telemetry does not yet calculate source-backed monetary cost
- telemetry does not yet calculate route quality
- streaming remains outside the guarded reference path
- controlled cross-model production outcome history remains limited
- the six-card freshness pilot has not yet completed the evidence required for wider rollout

## Next horizon

The next horizon is no longer simply "make providers callable."

The runtime can now execute, recover, observe, and independently verify a bounded route.

The next work should improve the quality of operational evidence and the external authority integrations around it:

- verifier calibration against independent or human-rated outcomes
- deterministic validators and gold-label checks where available
- qualified-human approval integration
- source-backed and effective-dated cost attribution
- route-outcome evaluation using execution and verification evidence
- distributed circuit-state coordination
- distributed telemetry export, access control, and retention policy
- streaming and richer latency evidence
- continued observation of the six-card regulated evidence pilot

Expansion to high or critical live execution should require evidence that these controls work reliably, not merely confidence that the models are capable.

## Message to future stewards

Do not confuse increased runtime capability with permission to erase boundaries.

The system became more useful at this moment because execution was added **without** making execution sovereign.

Preserve the distinctions that made this possible:

- routing authority is not provider access
- authentication is not model selection
- retry is not fallback
- failure scope is not recovery policy
- service health is not user quota
- telemetry is not unrestricted content logging
- token usage is not historical cost
- model judgment is not ground truth
- model verification is not human approval
- successful execution is not a completed outcome

The goal is not to automate every gate.

The goal is to make every gate explicit enough that future implementations can change without making responsibility, evidence, or authority unintelligible.

Models will evolve. Providers will evolve. Access methods will evolve. Evaluation methods will evolve.

The responsibility chain must remain inspectable when they do.

---

**A live orchestration system becomes trustworthy not when it can call more models, but when execution, recovery, evidence, verification, and human authority remain separate even after the calls become real.**
