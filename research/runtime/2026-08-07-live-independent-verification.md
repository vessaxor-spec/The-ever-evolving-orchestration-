# Live Independent Verification Research

Date: 2026-08-07
Status: implementation research record
Scope: guarded low and medium risk `high_volume_simple` runtime verification

## Research question

How should TEO execute the verifier already assigned by routing without turning a model judge into a new source of routing authority, hiding evaluator bias, or allowing an automated verifier to replace qualified human approval?

## Conclusion

For the current guarded runtime, the strongest defensible design is a narrow pointwise verification gate with these properties:

1. execute only the verifier already assigned by the active dispatch
2. require a different model and provider family from the active executor
3. blind the verifier to executor identity, retry history, fallback history, and runtime telemetry
4. use explicit criterion-level structured output instead of an unstructured overall score
5. expose an explicit `needs_human` state when evidence is insufficient or conflicting
6. perform one verifier attempt with no verifier retry or verifier fallback in this first slice
7. treat verifier infrastructure failure as failure to obtain verification evidence, not as a model judgment
8. never allow model verification to satisfy a qualified-human approval requirement

This design is deliberately narrower than a general LLM-as-a-judge framework. It verifies observable canary properties and refuses to invent semantic ground truth that is not present in the supplied task or output.

## Official-source findings

### OpenAI

OpenAI's GDPval work uses detailed rubrics to improve grading consistency and transparency. OpenAI also states that its automated grader is an experimental approximation of expert judgment and is not used as a replacement for expert graders.

Source:
- https://openai.com/index/gdpval/
- https://evals.openai.com/gdpval/grading

OpenAI's 2026 guidance for trustworthy third-party evaluation emphasizes that evaluation validity depends on the task environment and setup, not only the model being tested. This supports keeping the evaluator contract explicit and observable rather than treating a judge-model score as intrinsic truth.

Source:
- https://openai.com/index/trustworthy-third-party-evaluations-foundations/

OpenAI's current GPT-5.6 Luna documentation confirms Responses API support, reasoning-token support, and structured outputs. Luna is therefore technically capable of bounded structured verification when routing assigns it, while GPT-5.6 Sol remains available for more demanding verifier assignments.

Source:
- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://developers.openai.com/api/docs/guides/latest-model

### Anthropic

Anthropic's agent-evaluation guidance recommends matching evaluation methods to the complexity of the system and combining approaches rather than relying on one broad signal. This supports TEO's separation between executable checks, model verification, and human approval.

Source:
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents

Anthropic's structured-output documentation confirms JSON-schema-constrained output through `output_config.format` for current Claude models. Claude Sonnet 5 also supports the current effort controls required by TEO's verifier adapter.

Source:
- https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- https://platform.claude.com/docs/en/about-claude/models/whats-new-sonnet-5

### Google

Google's Gen AI evaluation documentation explicitly recommends evaluating judge models against human-rated ground truth. It provides balanced accuracy, F1, and confusion-matrix approaches for assessing judge quality. This is strong evidence that a model judge should itself be calibrated and evaluated rather than assumed correct.

Source:
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/evaluate-judge-model

Google also recommends rubric-driven evaluation and supports static/custom rubrics for instruction following, formatting, grounding, safety, and other measurable criteria.

Source:
- https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/determine-eval

Gemini 3.6 Flash currently supports structured outputs and thinking controls. Gemini 3.1 Pro Preview supports low, medium, and high thinking levels. The current Interactions API uses `response_format` for structured JSON output.

Sources:
- https://ai.google.dev/gemini-api/docs/models/gemini-3.6-flash
- https://ai.google.dev/gemini-api/docs/thinking
- https://ai.google.dev/gemini-api/docs/interactions-breaking-changes-may-2026

## Research evidence on judge bias

Recent research continues to show that LLM judges are not neutral measurement instruments.

A 2026 study across multiple provider families found substantial style-related bias and showed that mitigation effectiveness varies by judge model. This supports criterion decomposition and avoiding vague holistic scoring.

Source:
- https://arxiv.org/abs/2604.23178

A separate 2026 study across 20 mainstream models found measurable self-preference bias and reported that structured multidimensional evaluation reduced that bias. This supports TEO's provider/model separation and fixed criterion decomposition.

Source:
- https://arxiv.org/abs/2604.22891

Earlier work also documents self-preference effects in LLM judges, reinforcing the decision not to let the active executor verify itself.

Source:
- https://arxiv.org/abs/2506.02592

## Practitioner and forum signals

Community evidence is directional rather than authoritative, but several recurring patterns align with the official and research evidence.

A MachineLearning discussion on LLM evaluation emphasizes that judge prompts need tuning, reference-based scoring is stronger where ground truth exists, and human evaluation on a subset remains important for calibration.

Source:
- https://www.reddit.com/r/MachineLearning/comments/1h11lbt

A recent LocalLLM discussion describes deliberately using a different model family for RAG judging to reduce self-bias, while still finding large disagreement between correctness and faithfulness metrics. This is a useful reminder that cross-family judging reduces one risk but does not make judge outputs ground truth.

Source:
- https://www.reddit.com/r/LocalLLM/comments/1ukbnq1/how_do_you_validate_your_llm_judge_for_rag/

Recent practitioner discussions on Hacker News report that broad LLM-as-judge prompts can suffer from context overload and that decomposing evaluation into smaller rubric criteria improves debuggability and reliability.

Sources:
- https://news.ycombinator.com/item?id=44735843
- https://news.ycombinator.com/item?id=44737058

These signals reinforce, but do not independently authorize, TEO's design.

## Why pointwise rather than pairwise for the guarded canary

The live canary is deciding whether one execution satisfies its task sufficiently to pass a gate. It is not ranking two competing model outputs.

Pointwise evaluation avoids introducing candidate-order effects and makes the decision directly traceable to the active execution. The verifier is asked to judge four observable criteria:

- `output_present`
- `task_adherence`
- `format_consistency`
- `unsupported_claims_absent`

The verifier returns `pass`, `fail`, or `uncertain` for each criterion.

A global `passed` result requires every criterion to pass. A definitive `failed` result requires at least one failed criterion and no uncertainty. Uncertainty routes to `needs_human`.

## Why executor identity is blinded

The verifier does not need to know the executor provider, model, reasoning effort, retry count, fallback history, or circuit history to judge the observable candidate output against the task.

Suppressing those fields reduces several avoidable sources of evaluator bias and prevents operational history from becoming an implicit reason to reward or punish an otherwise identical output.

The verifier receives:

- original task text
- candidate output text
- declared verification methods
- fixed rubric and output schema

It does not receive:

- executor provider or model
- retry history
- fallback history
- runtime telemetry
- provider request IDs
- token usage or cost

## Provider-diverse verification after fallback

The original canary route executes Claude Haiku 4.5 and now explicitly assigns Gemini 3.6 Flash as its independent verifier.

Fallback creates an additional challenge. If execution moves to Gemini 3.6 Flash, the original verifier can no longer be considered provider-diverse. The routing layer therefore reselects an eligible verifier rather than letting the runtime invent one.

Current guarded behavior:

- Haiku primary execution -> Gemini 3.6 Flash verifier
- model-specific Haiku failure -> Gemini 3.6 Flash execution -> Claude Sonnet 5 verifier when Anthropic remains usable
- Anthropic provider failure -> Gemini 3.6 Flash execution -> GPT-5.6 Sol verifier because Anthropic is blocked

This keeps verifier choice within routing authority and preserves provider diversity where a live canary is allowed to proceed.

If no provider-diverse verifier remains eligible, routing fails closed instead of silently accepting same-provider verification.

## Why there is no verifier retry or verifier fallback yet

The first live verification slice permits one verifier attempt only.

Retrying or replacing a verifier introduces a new class of questions:

- whether verifier failure is transient, model-specific, provider-specific, or evidence-specific
- whether replacing the verifier changes the evaluation distribution
- whether repeated judging encourages selection of a favorable verdict
- how verifier retries should be represented in telemetry
- whether multiple judges require consensus or adjudication

Those concerns should be designed explicitly rather than inherited from execution retry/fallback behavior.

## Why infrastructure failure is not `failed`

A verifier HTTP failure, unavailable connection, malformed structured response, or unsupported assigned model means TEO failed to obtain valid verification evidence.

It does not prove that the candidate output failed the task.

The runtime therefore fails closed by raising a verification infrastructure error. It does not synthesize a `failed`, `passed`, or `needs_human` model judgment from an invocation failure.

A higher orchestration layer may later translate verification unavailability into an operator action, but it must preserve the distinction between "candidate failed verification" and "verification could not be performed."

## Human authority boundary

A model-based verifier can contribute evidence. It cannot satisfy qualified-human approval where TEO requires it.

The live verification scope remains low and medium risk only. High and critical risk execution is still outside the guarded live canary.

Even when future higher-risk execution is introduced, model verification must remain separate from required legal, safety, regulatory, financial, or operational human authority.

## Calibration requirement before expansion

Before live model verification expands beyond this canary, TEO should collect a human-rated calibration set for the fixed rubric and measure at minimum:

- per-criterion agreement
- false-pass rate
- false-fail rate
- `needs_human` rate
- confusion matrix
- provider/model-specific disagreement
- stability across repeated evaluation
- disagreement after executor-provider blinding

The judge should be evaluated as an implementation, not assumed to be an oracle.

## Implementation boundary

This research authorizes only the guarded first slice:

- explicit `high_volume_simple`
- low and medium risk
- local text output artifacts up to the guarded size limit
- one dispatch-assigned verifier attempt
- provider and model independence
- fixed structured rubric
- no verifier retry
- no verifier fallback
- no judge consensus panel
- no semantic ground truth invention
- no human approval substitution

Broader verification remains future work and must be justified by operational evidence.
