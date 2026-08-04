# The Ever-Evolving Orchestration

A community-maintained framework for routing work across AI models and agent profiles based on capability, cost, latency, risk, and evidence.

The purpose of this repository is not to declare a permanent “best model.” Model capabilities change quickly. Instead, this project provides a transparent and updateable routing framework that can evolve as new releases from OpenAI, Anthropic, Google, local-model projects, and other providers become available.

## Core principle

Select the capability profile first, then select the best available model.

- **Terra** — engineering execution: inspect, modify, test, debug, and verify
- **Sol** — synthesis and high-reasoning work: architecture, trade-offs, planning, and challenge
- **Luna** — high-throughput work: extraction, classification, transformation, and routing

Provider models are implementations of these profiles, not permanent owners of them.

## Default routing philosophy

| Work type | Primary lane | Supporting lane | Typical escalation |
|---|---|---|---|
| Daily coding | Codex / Terra | Claude for ambiguous design | Gemini Pro coding fallback |
| Deep debugging | Codex / Terra | Claude hypothesis review | Opus or Gemini Pro |
| Repository-wide refactor | Gemini mapping → Claude planning → Codex execution | Codex verification | Opus for high-risk decisions |
| Architecture | Claude Sonnet / Sol | Gemini research and context | Claude Opus |
| Deep research | Gemini Pro | Claude synthesis and challenge | Independent source verification |
| Code review | Codex executable review | Claude semantic/adversarial review | Opus for security-critical code |
| Multimodal analysis | Gemini Flash or Pro | Claude synthesis | Domain specialist review |
| High-volume simple work | Haiku, Flash, or Luna | Local model | Stronger model only when confidence is low |

See [`config/routing.yaml`](config/routing.yaml) for the machine-readable version.

## Design rules

1. Separate planner, executor, and verifier for consequential work.
2. Route by risk and uncertainty, not only task labels.
3. Escalate after evidence of failure, disagreement, or scope growth.
4. Measure effective cost, including retries and human correction.
5. Treat provider benchmarks and model claims as time-bound evidence.
6. Keep model identifiers configurable rather than embedded in orchestration logic.

## Repository structure

```text
config/
  routing.yaml       Default routing policy
  models.yaml        Model registry and capability profiles
docs/
  methodology.md     Evaluation and decision methodology
CONTRIBUTING.md      How to propose model and routing updates
LICENSE              Project license
```

## Updating the framework

New model releases should be proposed through a pull request that includes:

- official model identifier and release date
- provider documentation or primary-source evidence
- capability changes relevant to existing lanes
- cost, context, latency, and tool-use implications where available
- proposed routing changes
- limitations and uncertainty

A new model should not replace an existing default solely because it is newer or scores higher on a single benchmark.

## Status

This is an early framework. The initial mappings are informed recommendations, not universal facts. Results depend on tooling, prompts, repository access, inference settings, and workload characteristics.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).