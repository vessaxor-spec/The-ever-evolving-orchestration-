# Benchmark Evidence Methodology

TEO uses benchmark evidence to improve routing, not to produce a permanent model leaderboard.

## Evidence grades

### Grade A: TEO-observed

A reproducible result generated through a documented TEO method with:

- exact task or dataset
- exact implementation identifier
- prompt, tools, and configuration
- execution environment
- raw or reviewable artifacts
- failures and missing runs
- limitations

### Grade B: Independent benchmark

A reproducible external result from an independent source whose task, harness, and scoring method are relevant to the TEO route being evaluated.

### Grade C: Provider claim

A current statement from official provider documentation. Grade C evidence may establish identifiers, availability, limits, supported features, or a provider-described use case. It does not establish TEO task superiority.

### Grade D: Unverified

An anecdote, unsourced assertion, marketing summary without a primary source, or comparison that cannot be reproduced.

Grade D evidence must not change a default route.

## Comparison rules

Results may be compared directly only when they use materially equivalent:

- tasks or datasets
- acceptance criteria
- model snapshots
- prompts and system instructions
- tools and tool permissions
- reasoning or sampling configuration
- context supplied
- execution environment
- number of attempts
- scoring method

A benchmark score from one harness must not be treated as interchangeable with a score from another harness.

## Routing relevance

Every evidence entry must state which routing decision it informs, such as:

- primary implementation selection
- fallback order
- preview eligibility
- verification depth
- escalation threshold
- cost or latency constraint
- local deployment suitability

Evidence that does not affect a routing decision belongs in general research, not the benchmark registry.

## Failure recording

The registry must include:

- failed tasks
- tool failures
- unavailable models
- rate-limit failures
- invalid outputs
- inconclusive reviews
- cases excluded from scoring and the reason

Selective reporting invalidates the result.

## Refresh rules

Refresh evidence when:

- a routing default changes
- the concrete model identifier changes
- a provider changes availability or version status
- the evaluation harness changes materially
- a new failure case exposes a routing weakness
- the evidence is too old for the decision it supports

## Initial scope

Phase 4 records the completed Phase 3 routing-policy conformance run as Grade A evidence and current provider model documentation as Grade C evidence.

Live cross-model task quality, cost, and latency comparisons remain unrecorded until a controlled harness and reproducible runs exist.
