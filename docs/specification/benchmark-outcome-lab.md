# Benchmark and Outcome Lab

## Status

This specification defines the current executable foundation for TEO's Benchmark and Outcome Lab, including controlled live replay.

Benchmark Lab version: `1`

This layer evaluates controlled route-outcome evidence. It does not acquire routing, model-selection, verification, approval, retry, fallback, provider-access, or policy-write authority.

## Purpose

The Benchmark and Outcome Lab turns fixed controlled fixtures and canonical route-outcome records into reproducible comparative evidence.

The current implementation focuses on five problems:

1. keep the task and evaluation setup fixed enough that route comparisons are interpretable;
2. preserve nondeterminism through repeated trials rather than treating one run as ground truth;
3. reject incomparable cohorts instead of forcing a score;
4. keep fallback, retry, verification failure, missingness, uncertainty, and version context visible;
5. execute controlled replay through normal TEO routing without giving the evaluation layer a forced-model bypass.

## Evidence basis

The design is consistent with current primary-source evaluation guidance:

- Anthropic's agent-evaluation guidance distinguishes tasks, trials, graders, traces, capability evals, and regression evals, and recommends repeated trials for nondeterministic systems: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- OpenAI's evaluation guidance emphasizes that the harness, tools, scoring, budget, and environment are part of the tested system and should remain explicit in controlled comparisons: https://openai.com/index/trustworthy-third-party-evaluations-foundations/
- Google Vertex AI agent evaluation treats the evaluation dataset, agent configuration, metrics, and evaluation run as separate declared artifacts: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/evaluate

TEO does not depend on those frameworks. The sources inform evaluation controls only.

## Canonical artifacts

- evaluator: `reference/implementations/python/src/teo_reference/benchmark_lab.py`
- controlled replay runner: `reference/implementations/python/src/teo_reference/benchmark_replay.py`
- fixture schema: `reference/schemas/benchmark-fixture.schema.json`
- experiment schema: `reference/schemas/benchmark-experiment.schema.json`
- report schema: `reference/schemas/benchmark-report.schema.json`
- replay-plan schema: `reference/schemas/benchmark-replay-plan.schema.json`
- controlled fixtures: `reference/datasets/benchmark-lab/benchmark-fixtures-v1.jsonl`
- reference trial outcomes: `reference/datasets/benchmark-lab/route-outcomes-v1.jsonl`
- reference experiment manifest: `reference/datasets/benchmark-lab/benchmark-experiment-v1.json`
- benchmark conformance tests: `tests/test_benchmark_lab.py`
- controlled replay conformance tests: `tests/test_benchmark_replay.py`

## Evaluation sequence

Offline evaluation follows:

```text
controlled fixture bank
  -> declared experiment manifest
  -> candidate and harness identity
  -> fixed repeated trial bindings
  -> canonical route-outcome records
  -> comparability gate
  -> descriptive metrics and uncertainty
  -> integrity-protected benchmark report
  -> independent evaluation / specialist #82
  -> shadow recommendation later
```

Controlled live replay extends the same evidence path:

```text
fixed controlled fixture
  -> declared replay plan
  -> additive route-isolation constraints
  -> no-network normal-routing preflight
  -> exact candidate and verifier match
  -> guarded canary execution
  -> assigned live independent verifier
  -> canonical route-outcome evidence
  -> standard replay experiment manifest
  -> comparability gate
  -> integrity-protected benchmark report
```

The report is evidence. It cannot edit routing policy.

## Fixture contract

A benchmark fixture declares:

- fixture and suite identity;
- suite version;
- capability or regression intent;
- task type;
- effective risk;
- required capabilities;
- controlled synthetic or otherwise authorized benchmark input;
- explicit success criteria;
- tags;
- integrity hash.

Benchmark fixtures are distinct from production telemetry. Controlled fixture content may be retained when it is synthetic, public, or otherwise authorized for evaluation. Production route-outcome evidence remains content-minimized.

For offline evaluation, fixture capabilities remain exact comparison context.

For controlled live replay, fixture capabilities are minimum task requirements. Normal TEO routing may add worker or routing capabilities. The replay evaluator requires every candidate and trial for a fixture to resolve the same full canonical capability context before comparison. It does not rewrite the source fixture. Final report provenance preserves the original fixture integrity hashes.

## Experiment manifest

Every experiment declares before evaluation:

- experiment identity;
- study type: `benchmark`, `replay`, or `regression`;
- claim scope: `system_to_system` or `executor_only`;
- benchmark suite and version;
- trials per fixture;
- primary metric;
- fixed stopping rule;
- harness identity and version;
- tool-access profile;
- attempt and wall-time budget where applicable;
- candidate system configurations;
- exact fixture/candidate/trial to route-outcome bindings;
- regression baseline when the study type is regression.

Version and harness identity are evidence, not incidental metadata.

Controlled live replay v1 is intentionally limited to `system_to_system` claims. Additive isolation changes the evaluated route context, so the live runner refuses `executor_only` claims rather than overstating model-only causality. Offline controlled experiments may still use `executor_only` when their stricter non-executor comparability conditions are satisfied.

## Controlled live replay plan

A replay plan is separately schema-validated before any provider execution.

It declares:

- replay identity;
- suite and version;
- repeated-trial count;
- fixed stopping rule and primary metric;
- harness identity and version;
- active attempt budget;
- tool-access profile;
- candidate provider, model, reasoning effort, verifier, runtime, repository, policy, registry, and tool-version context;
- additive implementation or provider blocks used to isolate a canonical route.

The replay plan may restrict eligibility. It may not directly select or unblock a model, lower risk, remove required capabilities, change the assigned verifier, accept a preview model, alter provider access, or satisfy qualified-human approval.

The replay experiment ID is `replay-<plan_sha256>`, binding the generated evidence to the complete declared replay plan.

## Replay preflight and execution authority

Before any provider call, the replay runner sends the fixed task through the normal TEO routing engine with only the replay plan's additive isolation constraints.

The preflight must prove that the resulting canonical dispatch matches the declared candidate for:

- task type;
- effective risk;
- minimum fixture-required capabilities;
- provider family;
- concrete model;
- reasoning effort;
- assigned verifier provider and model;
- independent-verification requirement;
- absence of a qualified-human requirement within the currently authorized live scope.

A mismatch fails closed before network execution.

The execution phase then uses the existing guarded canary. The replay layer does not own a separate provider adapter, retry mechanism, fallback engine, verifier, or routing path.

Each trial receives:

- a fresh in-memory circuit-state store;
- the active bounded retry policy;
- a fresh content-free runtime telemetry sink;
- the normal guarded canary runtime;
- the verifier assigned by the canonical dispatch;
- canonical Route-Outcome Evidence construction;
- an isolated artifact path.

The replay harness attempt budget must equal the active canary retry policy. Version 1 does not claim a wall-time deadline because the current reference runtime does not implement preemptive cancellation.

## Current live scope

Controlled live replay does not widen runtime authority.

It is restricted to the same currently authorized live canary scope:

- task type: `high_volume_simple`;
- effective risk: low or medium;
- existing provider adapters only;
- existing eligibility, capability, preview, retry, fallback, circuit, and verification controls;
- provider-diverse independent verification.

High and critical live replay remain unauthorized.

## Repeated trials

Version 1 requires at least two trials per fixture for a declared experiment.

This does not create a universal statistical sufficiency threshold. It prevents the foundation from treating one stochastic run as a stable system property.

The report exposes both:

- `pass_any_trial_fixture_rate`: at least one verified completion among repeated trials;
- `pass_all_trials_fixture_rate`: every repeated trial verified complete.

These correspond to different reliability questions and must not be collapsed into one headline score.

## Comparability gate

The evaluator fails the comparison before computing candidate metrics when the experiment contains material identity drift.

It checks:

- every candidate sees the same fixture and trial matrix;
- no trial is silently missing or extra;
- one route-outcome record cannot be reused across multiple trials;
- route-outcome task type matches the fixture;
- effective risk matches the fixture;
- required capability context is comparable;
- primary provider, model, and reasoning effort match the declared candidate;
- assigned verifier matches the declared candidate;
- runtime version matches;
- routing-policy revision matches;
- registry revision matches;
- declared tool versions match.

For offline `executor_only` claims, all non-executor comparison fields must remain fixed across candidates, including verifier, runtime, routing policy, registry, and declared tool versions.

For controlled live replay, every candidate must resolve the same full canonical capability context for each source fixture. Source fixture integrity remains unchanged and is preserved in final report provenance.

A failed comparability gate returns `evidence_sufficiency: insufficient` and no candidate scorecard.

## Primary, retry, and fallback separation

The Lab consumes the canonical route-outcome contract and preserves its semantics.

For each candidate it reports separately:

- verified completed trials;
- primary-route verified completions;
- fallback-assisted verified completions;
- retry-assisted verified completions;
- verification failures;
- awaiting-human outcomes;
- verification-missing outcomes;
- execution failures;
- abandoned outcomes.

A route rescued by fallback is therefore not represented as equivalent to a primary-route success.

## Uncertainty

Version 1 reports 95 percent Wilson intervals for verified completion rate and primary verified completion rate.

The interval is descriptive evidence. It is not a policy threshold and does not establish causal superiority.

No universal significance level, minimum sample size, or promotion threshold is encoded.

## Latency and usage

The evaluator reports total observed route duration across primary and fallback attempts.

Normalized token usage is reported only when present in canonical route outcomes. Usage completeness is classified as:

- `complete`;
- `partial`;
- `unknown`.

Missing token usage is not converted to zero.

Monetary cost is intentionally not calculated in this workstream. Source-backed cost attribution remains separately governed by the Progress Tracker.

## Regression signals

Regression experiments declare a baseline candidate.

Version 1 emits `descriptive_drop` when a candidate's controlled verified-completion rate or primary verified-completion rate is lower than the declared baseline.

A descriptive drop is an investigation signal, not automatic rollback or routing authority.

## Integrity and reproducibility

Benchmark fixtures and reports use SHA-256 over canonical JSON content.

Reports preserve:

- experiment manifest digest;
- source fixture integrity digests;
- ordered source route-outcome IDs;
- experiment and suite identity;
- harness and candidate identity through the source manifest.

Controlled replay additionally binds the generated experiment identity to the complete replay-plan digest.

Persisted reports are schema and integrity validated when written and read.

## Authority boundary

The Benchmark Lab may produce controlled comparative evidence.

It may not:

- select a winner as routing policy;
- force a model around normal TEO eligibility;
- promote or demote a model;
- weaken capability eligibility;
- lower effective risk;
- alter fallback rules;
- weaken independent verification;
- remove provider-diversity requirements;
- satisfy qualified-human approval;
- treat provider authentication or connection mechanism as a routing signal;
- calculate unsupported cost claims;
- hide failures or missing trials;
- use one candidate's favorable harness while representing the result as an executor-only comparison.

## Remaining incomplete gates

Controlled live replay is implemented and validated, but the current Benchmark and Outcome Lab milestone remains incomplete.

Two material gates remain:

1. **Multi-verifier disagreement measurement.** The report preserves the canonical runtime verifier disposition but does not yet execute or join multiple independent benchmark-verifier observations.
2. **Consequential-conclusion independent-verification handoff.** Benchmark evidence cannot yet express and enforce the explicit independent challenge required before a consequential evaluation conclusion advances to Mission Control or maintainer review.

These gaps keep the workstream in progress.

## Relationship to specialist #82

`orchestration-evaluation-analyst` remains the post-run specialist that interprets controlled evidence, tests evidence sufficiency, and produces bounded recommendation states.

Benchmark Lab itself does not produce `SHADOW_CHANGE_CANDIDATE` or any other policy recommendation. That remains a later governed handoff under the Shadow Route Evaluation workstream.

## Relationship to the Progress Tracker

Controlled live replay advances, but does not close, the current `NOW` Benchmark and Outcome Lab workstream.

After Reference Implementation CI #423 validated the replay implementation, the workstream is tracked at 75 percent. The remaining gates are multi-verifier disagreement measurement and consequential-conclusion independent verification while preserving the same fixture, comparability, provenance, routing, and authority boundaries.
