# Benchmark and Outcome Lab

## Status

This specification defines the completed current milestone for TEO's Benchmark and Outcome Lab.

Benchmark Lab version: `1`

The Lab turns controlled fixtures and canonical route-outcome evidence into reproducible comparative evidence. It includes offline evaluation, controlled live replay, diagnostic multi-verifier disagreement measurement, and an independent-verification handoff for consequential evaluation conclusions.

The Lab does not acquire routing, model-selection, runtime-verification, approval, retry, fallback, provider-access, or policy-write authority.

## Purpose

The Benchmark and Outcome Lab addresses seven control problems:

1. keep tasks and evaluation conditions fixed enough that route comparisons are interpretable;
2. preserve nondeterminism through repeated trials rather than treating one run as ground truth;
3. reject incomparable cohorts instead of forcing a score;
4. keep fallback, retry, verification failure, missingness, uncertainty, and version context visible;
5. execute controlled replay through normal TEO routing without a forced-model bypass;
6. measure independent verifier disagreement without converting panel voting into truth or routing authority;
7. prevent consequential evaluation conclusions from advancing to Mission Control or maintainer review without an explicit independent challenge.

## Evidence basis

The design is consistent with primary-source evaluation guidance already adopted by this workstream:

- Anthropic's agent-evaluation guidance distinguishes tasks, trials, graders, traces, capability evals, and regression evals and recommends repeated trials for nondeterministic systems: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- OpenAI's evaluation guidance emphasizes that the harness, tools, scoring, budget, and environment are part of the tested system and should remain explicit in controlled comparisons: https://openai.com/index/trustworthy-third-party-evaluations-foundations/
- Google Vertex AI agent evaluation treats the evaluation dataset, agent configuration, metrics, and evaluation run as separate declared artifacts: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/evaluate

TEO does not depend on those frameworks. The sources inform evaluation controls only.

## Canonical artifacts

Core evaluation:

- evaluator: `reference/implementations/python/src/teo_reference/benchmark_lab.py`
- fixture schema: `reference/schemas/benchmark-fixture.schema.json`
- experiment schema: `reference/schemas/benchmark-experiment.schema.json`
- report schema: `reference/schemas/benchmark-report.schema.json`
- controlled fixtures: `reference/datasets/benchmark-lab/benchmark-fixtures-v1.jsonl`
- reference trial outcomes: `reference/datasets/benchmark-lab/route-outcomes-v1.jsonl`
- reference experiment manifest: `reference/datasets/benchmark-lab/benchmark-experiment-v1.json`
- conformance tests: `tests/test_benchmark_lab.py`

Controlled live replay:

- replay runner: `reference/implementations/python/src/teo_reference/benchmark_replay.py`
- replay-plan schema: `reference/schemas/benchmark-replay-plan.schema.json`
- conformance tests: `tests/test_benchmark_replay.py`

Multi-verifier disagreement:

- verifier-panel implementation: `reference/implementations/python/src/teo_reference/benchmark_verification.py`
- panel-plan schema: `reference/schemas/benchmark-verifier-panel-plan.schema.json`
- observation schema: `reference/schemas/benchmark-verifier-observation.schema.json`
- conformance tests: `tests/test_benchmark_verification.py`

Consequential conclusion handoff:

- conclusion implementation: `reference/implementations/python/src/teo_reference/benchmark_conclusion.py`
- conclusion schema: `reference/schemas/benchmark-conclusion.schema.json`
- independent-verification schema: `reference/schemas/benchmark-conclusion-verification.schema.json`
- review-handoff schema: `reference/schemas/benchmark-conclusion-handoff.schema.json`
- conformance tests: `tests/test_benchmark_conclusion.py`

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
```

Controlled live replay extends the same evidence path:

```text
fixed controlled fixture
  -> declared replay plan
  -> additive route-isolation constraints
  -> no-network normal-routing preflight
  -> exact candidate and assigned-verifier match
  -> guarded canary execution
  -> assigned live independent verifier
  -> canonical route-outcome evidence
  -> standard replay experiment manifest
  -> comparability gate
  -> integrity-protected benchmark report
```

Diagnostic disagreement extends a completed report without changing its runtime disposition:

```text
benchmark report
  + declared verifier-panel plan
  + exact fixture/candidate/trial/output binding
  -> blinded independent verifier observations
  -> observation completeness and integrity gate
  -> disagreement measurement
  -> benchmark report with diagnostic disagreement evidence
```

A consequential evaluation conclusion follows:

```text
sufficient benchmark report
  -> bounded conclusion record
  -> independent challenge and verification
  -> review handoff
  -> Mission Control or maintainer review
```

The final arrow is a review handoff, not policy execution. Any later routing change remains governed outside Benchmark Lab.

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

Controlled live replay version 1 is intentionally limited to `system_to_system` claims. Additive isolation changes evaluated route context, so live replay refuses `executor_only` claims rather than overstating model-only causality. Offline controlled experiments may still use `executor_only` when their stricter non-executor comparability conditions are satisfied.

## Controlled live replay

A replay plan is separately schema-validated before provider execution.

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

The replay experiment ID is `replay-<plan_sha256>`, binding generated evidence to the complete declared replay plan.

### Replay preflight

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

The execution phase uses the existing guarded canary. The replay layer does not own a separate provider adapter, retry mechanism, fallback engine, verifier, or routing path.

Each trial receives:

- a fresh in-memory circuit-state store;
- the active bounded retry policy;
- a fresh content-free runtime telemetry sink;
- the normal guarded canary runtime;
- the verifier assigned by the canonical dispatch;
- canonical Route-Outcome Evidence construction;
- an isolated artifact path.

The replay harness attempt budget must equal the active canary retry policy. Version 1 does not claim a wall-time deadline because the current reference runtime does not implement preemptive cancellation.

### Current live scope

Controlled live replay does not widen runtime authority.

It is restricted to the same currently authorized live canary scope:

- task type: `high_volume_simple`;
- effective risk: low or medium;
- existing provider adapters only;
- existing eligibility, capability, preview, retry, fallback, circuit, and verification controls;
- provider-diverse independent runtime verification.

High and critical live replay remain unauthorized.

## Repeated trials

Version 1 requires at least two trials per fixture for a declared experiment.

This does not create a universal statistical sufficiency threshold. It prevents the foundation from treating one stochastic run as a stable system property.

The report exposes both:

- `pass_any_trial_fixture_rate`: at least one verified completion among repeated trials;
- `pass_all_trials_fixture_rate`: every repeated trial verified complete.

These answer different reliability questions and must not be collapsed into one headline score.

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
- assigned runtime verifier matches the declared candidate;
- runtime version matches;
- routing-policy revision matches;
- registry revision matches;
- declared tool versions match.

For offline `executor_only` claims, all non-executor comparison fields must remain fixed across candidates, including verifier, runtime, routing policy, registry, and declared tool versions.

For controlled live replay, every candidate must resolve the same full canonical capability context for each source fixture. Source fixture integrity remains unchanged and is preserved in final report provenance.

A failed comparability gate returns `evidence_sufficiency: insufficient` and no candidate scorecard.

## Primary, retry, and fallback separation

The Lab consumes canonical route-outcome semantics.

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

A route rescued by fallback is not represented as equivalent to a primary-route success.

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

Monetary cost is intentionally not calculated in this workstream. Source-backed Cost Attribution is separately governed by the Progress Tracker.

## Regression signals

Regression experiments declare a baseline candidate.

Version 1 emits `descriptive_drop` when a candidate's controlled verified-completion rate or primary verified-completion rate is lower than the declared baseline.

A descriptive drop is an investigation signal, not automatic rollback or routing authority.

## Multi-verifier disagreement

Multi-verifier evidence is a separate diagnostic layer. It does not replace the canonical runtime verifier used to finalize Route-Outcome Evidence.

### Panel plan

A verifier-panel plan is versioned and bound to one benchmark experiment.

For every candidate it declares at least two independent observer identities spanning at least two provider families. Each observer declares:

- observer identity;
- provider family;
- concrete model;
- reasoning effort.

The panel policy is fixed to:

```text
minimum observers per trial: 2
minimum provider families: 2
decision use: diagnostic_only
canonical runtime verifier override: false
```

A panel may include an observer from the same provider family as the executor when it is a different model, but the panel as a whole must remain provider-diverse. No observer may reuse the active executor model.

### Observation binding

Each verifier observation is integrity-protected and binds:

- experiment identity;
- candidate, fixture, and trial identity;
- canonical route-outcome ID;
- panel-plan digest;
- observer identity, provider, model, and reasoning effort;
- active executor identity;
- canonical runtime-verifier identity;
- SHA-256 digest of the exact output reviewed;
- structured verifier decision;
- provider evidence where available.

Observers receive a blinded task and candidate output. The executor identity is not included in the verifier prompt.

The active canonical dispatch ID is used only as the verifier request correlation identity. Benchmark Lab does not require Route-Outcome Evidence to duplicate a separate task ID.

### Completeness and disagreement

The disagreement attachment requires the exact declared observation matrix for every trial with a successful active execution.

It fails to `status: insufficient` when evidence is missing or inconsistent, including:

- missing or duplicate observations;
- unexpected observer identity;
- plan or experiment mismatch;
- outcome mismatch;
- observer model, provider, or effort mismatch;
- executor-context mismatch;
- executor-model reuse;
- different output hashes across observers reviewing the same trial.

When complete, it records:

- observation count;
- verifiable trial count;
- unanimous trials;
- disagreement trials and rate;
- status disagreement;
- criterion disagreement;
- human-reason disagreement;
- the same metrics per candidate.

Disagreement is measured, not adjudicated by vote.

A majority vote, panel pass rate, or observer preference may not:

- change the canonical runtime verifier disposition;
- rewrite a Route-Outcome record;
- alter candidate completion metrics;
- select a routing winner;
- promote or demote a model;
- create policy-write authority.

## Consequential evaluation conclusions

A benchmark report is evidence. A conclusion drawn from it is a separate object with its own provenance and lifecycle.

### Conclusion record

A conclusion declares:

- source experiment and report integrity digest;
- conclusion kind;
- consequence level;
- bounded statement;
- evidence references;
- originator identity;
- whether independent verification is required;
- `policy_write_authority: false`.

Supported conclusion kinds are:

- `descriptive_summary`;
- `comparative_claim`;
- `regression_finding`;
- `evidence_insufficiency`.

Consequential comparative or regression conclusions require:

- passed benchmark comparability;
- benchmark evidence that is not `insufficient`;
- measured multi-verifier disagreement;
- an independent verification before review handoff.

A regression conclusion also requires an actual regression signal in the source report.

### Independent verification

An independent conclusion verification binds the exact conclusion digest and source report digest.

It checks:

- evidence support;
- preservation of uncertainty;
- preservation of authority boundaries;
- absence of unsupported causality.

The verification result is one of:

- `verified`;
- `rejected`;
- `needs_human`.

The verifier must be independent from the conclusion originator. When the originator is model-backed, the verifier must use a different provider family and may not reuse the originator model.

This is independent evaluation verification, not qualified-human approval.

### Review handoff

A consequential conclusion cannot produce a review handoff without the independent verification record.

A handoff may be:

- `ready_for_review` after successful independent verification;
- `rejected` when the independent challenge rejects the conclusion;
- `needs_human` when the verification evidence remains uncertain.

The only destination in this milestone is:

`mission_control_or_maintainer_review`

Every handoff explicitly preserves:

- `policy_write_authority: false`;
- `qualified_human_approval_satisfied: false`.

The handoff therefore cannot change routing, approve a regulated or safety-critical action, or satisfy another policy's qualified-human requirement.

## Integrity and reproducibility

Benchmark fixtures, reports, verifier observations, conclusions, conclusion verifications, and conclusion handoffs use SHA-256 over canonical JSON content.

Reports preserve:

- experiment manifest digest;
- source fixture integrity digests;
- ordered source route-outcome IDs;
- experiment and suite identity;
- harness and candidate identity through the source manifest.

Controlled replay additionally binds generated experiment identity to the replay-plan digest.

Reports enriched with disagreement evidence additionally preserve:

- verifier-panel plan digest;
- source verifier-observation IDs.

Persisted report and observation records are schema and integrity validated when written and read.

## Authority boundary

The Benchmark Lab may produce controlled comparative and diagnostic evidence.

It may not:

- select a winner as routing policy;
- force a model around normal TEO eligibility;
- promote or demote a model;
- weaken capability eligibility;
- lower effective risk;
- alter fallback rules;
- weaken canonical independent runtime verification;
- use verifier-panel voting to override a runtime verifier;
- remove provider-diversity requirements;
- satisfy qualified-human approval;
- treat provider authentication or connection mechanism as a routing signal;
- calculate unsupported cost claims;
- hide failures, disagreement, or missing trials;
- use one candidate's favorable harness while representing the result as an executor-only comparison;
- convert a conclusion handoff directly into a routing or policy mutation.

## Relationship to specialist #82

`orchestration-evaluation-analyst` remains the post-run specialist that interprets controlled evidence, tests evidence sufficiency, and produces bounded recommendation states.

Benchmark Lab does not itself produce `SHADOW_CHANGE_CANDIDATE` or any other routing recommendation. That remains governed by the separate Shadow Route Evaluation workstream.

A model-backed conclusion originated through specialist #82 is still subject to the independent verification boundary defined above when the conclusion is consequential.

## Milestone completion

The current Benchmark and Outcome Lab milestone is complete when all of the following are executable and validated:

- fixed benchmark fixtures and declared experiment conditions;
- repeated trials;
- strict comparability and missingness gates;
- route/model/reasoning/verifier/version binding;
- primary, retry, and fallback separation;
- uncertainty and regression evidence;
- controlled live replay through normal routing;
- diagnostic multi-verifier disagreement with explicit insufficiency behavior;
- independent-verification handoff for consequential evaluation conclusions;
- preservation of recommendation-only and policy-write boundaries.

Reference Implementation CI #429 validated the completed executable contract with 574 passing tests, 437 tracked-file layout checks, regulated specialist evidence validation, 28 parsed JSON Schemas, valid linked configuration, and the provider-diverse end-to-end example.

The workstream may continue receiving compatible maintenance, larger fixture banks, additional observational evidence, and later integration into Shadow Route Evaluation without reopening this completed current milestone.
