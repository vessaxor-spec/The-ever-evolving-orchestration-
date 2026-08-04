<p align="center">
  <img src="assets/banner/teo-banner.svg" alt="The Ever-Evolving Orchestration banner" width="100%">
</p>

<div align="center">

# The Ever-Evolving Orchestration

### Models evolve. Responsibilities endure.

An open, vendor-neutral orchestration framework and reference specification for coordinating intelligent systems through teams, workers, capabilities, implementations, and verification.

**Navigate by principles. Adapt by evidence.**

</div>

---

Every few months, the AI landscape changes.

New models appear. Existing models improve. Providers add capabilities, change limits, and alter the economics of execution.

Most orchestration systems respond by adding another model-specific rule.

TEO starts from a different premise:

> **The model is not the architecture.**

Responsibilities change slowly. Capabilities evolve gradually. Implementations change constantly.

The Ever-Evolving Orchestration separates those layers so a system can adopt better models without repeatedly redesigning how work is understood, assigned, executed, and verified.

## What is TEO?

TEO is a public framework for answering one durable question:

> **How should intelligent systems decide which intelligence to use?**

It does not attempt to declare a permanent best model. It provides a structured way to:

- interpret a task
- identify the responsible team
- select the appropriate worker
- resolve required capabilities
- choose the best available implementation
- verify the result according to risk
- improve future routing through evidence

TEO combines a human-readable architecture with machine-readable routing policies and model registries. It is intended to be useful to engineers, AI agents, researchers, and organizations building multi-model systems.

## Core architecture

<p align="center">
  <img src="assets/diagrams/core-architecture.svg" alt="Task to Mission Control to Team to Worker to Capability to Implementation to Verification" width="100%">
</p>

```text
Task
  |
  v
Mission Control
  |
  v
Team
  |
  v
Worker
  |
  v
Capability
  |
  v
Implementation
  |
  v
Verification
```

A task is never routed directly to a model unless the system has already resolved the responsibility, capability, and risk requirements behind that choice.

This hierarchy is designed to remain stable even when model names, providers, prices, context limits, or tool capabilities change.

## Core principles

### Team-first

Route work to a responsibility before selecting an implementation.

### Capability-first

Select the capabilities required by the task before selecting a provider or model.

### Evidence-first

Improve routing through validation, measured outcomes, and documented tradeoffs rather than preference.

## Team-first orchestration

TEO treats orchestration as an organizational problem before treating it as a model-selection problem.

### Mission Control

Mission Control receives the task, interprets intent, identifies constraints, assesses risk, selects the responsible team, coordinates execution, and determines the required verification path.

Mission Control does not own specialist work. It owns dispatch, coordination, and completion.

### Planning Team

The Planning Team handles architecture, decomposition, dependency analysis, sequencing, and tradeoff evaluation.

Current preferred implementations include Claude Sonnet, Codex Sol, and Gemini Pro, depending on the need for general reasoning, executable repository awareness, or external research.

### Engineering Team

The Engineering Team handles implementation, debugging, testing, refactoring, migrations, and tool execution.

Codex Terra is the default execution profile. Codex Sol supports difficult engineering reasoning. Gemini Pro and local coding models provide fallback paths when needed.

### Research Team

The Research Team handles external research, technical documentation, standards, source comparison, repository mapping, and large-context analysis.

Gemini Pro is the default deep research implementation. Gemini Flash supports fast collection, extraction, mapping, and multimodal triage.

### Review Team

The Review Team challenges assumptions, reviews architecture and code, checks requirements alignment, identifies hidden risks, and escalates consequential decisions.

Claude Sonnet, Codex Sol, and Claude Opus currently serve distinct review roles.

### Verification Team

The Verification Team confirms that execution satisfied the original requirements.

Verification may include tests, static analysis, runtime checks, source grounding, independent review, rollback planning, or human approval, depending on risk.

## Capability roles and current implementations

TEO defines responsibilities independently from providers. Terra, Sol, and Luna are internal capability roles, not OpenAI endorsements and not a complete representation of the ecosystem.

| Capability role | Purpose | Current implementation families |
|---|---|---|
| **Engineering execution** | inspect, implement, edit, test, debug, verify | Codex Terra, local coding models, Gemini Pro as fallback |
| **Engineering reasoning** | plan complex changes, reason across repositories, connect architecture to execution | Codex Sol, Claude Sonnet, Gemini Pro |
| **General reasoning and review** | architecture, requirements, critique, tradeoff analysis, semantic review | Claude Sonnet, Claude Opus, Codex Sol, Gemini Pro |
| **Research and long context** | source discovery, grounded comparison, large-context synthesis | Gemini Pro, Gemini Flash, Claude Sonnet |
| **Multimodal and high-volume processing** | classify, extract, transform, map, summarize, triage | Gemini Flash, Claude Haiku, local models |
| **Independent verification** | test claims, challenge assumptions, validate execution | Codex Terra, Claude Sonnet, Gemini Pro, human review when required |

## Current routing baseline

The current policy uses the following implementation split:

| Work type | Primary direction |
|---|---|
| Architecture and general planning | Claude Sonnet, supported by Codex Sol and Gemini Pro |
| Engineering architecture with repository constraints | Codex Sol |
| Daily coding and implementation | Codex Terra |
| Deep debugging | Codex Terra with Codex Sol and Claude review |
| Deep research and large-context analysis | Gemini Pro |
| Repository mapping and multimodal triage | Gemini Flash |
| Semantic and adversarial review | Claude Sonnet |
| High-consequence reasoning | Claude Opus |
| High-volume simple work | Claude Haiku, Gemini Flash, Luna, or local models |

The complete machine-readable policy is available in [`policy/routing/routing.yaml`](policy/routing/routing.yaml).

Team dispatch rules are available in [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml).

## Example workflow

Consider a request to diagnose and repair a failing service across a large repository.

```text
Mission Control
  |
  +--> classifies the task as deep debugging
  +--> assigns the Engineering Team
  +--> selects the relevant backend, database, or infrastructure worker
  |
  v
Codex Terra
  |
  +--> reproduces the failure
  +--> inspects the repository
  +--> implements and tests the fix
  |
  v
Codex Sol and Claude Sonnet
  |
  +--> challenge the root-cause hypothesis
  +--> review cross-system implications
  |
  v
Verification Team
  |
  +--> reruns targeted and regression tests
  +--> confirms the original failure is resolved
  +--> records the routing outcome
```

The models can change. The responsibility chain remains understandable.

## Getting started

### For humans

1. Read this README.
2. Read [`CONSTITUTION.md`](CONSTITUTION.md), [`MANIFESTO.md`](MANIFESTO.md), and [`LEXICON.md`](LEXICON.md).
3. Review the canonical routing policy in [`policy/routing/routing.yaml`](policy/routing/routing.yaml).
4. Review the team architecture in [`community/teams/`](community/teams/).
5. Review specialist workers in [`community/workers/workers.yaml`](community/workers/workers.yaml).
6. Compare the current model aliases in [`models.yaml`](models.yaml).

### For AI agents

Use this repository as a source of truth for orchestration.

Read in this order:

1. [`AI_INSTRUCTIONS.md`](AI_INSTRUCTIONS.md)
2. [`policy/routing/team-routing.yaml`](policy/routing/team-routing.yaml)
3. [`community/teams/`](community/teams/)
4. [`community/workers/workers.yaml`](community/workers/workers.yaml)
5. [`policy/routing/routing.yaml`](policy/routing/routing.yaml)
6. [`models.yaml`](models.yaml)

Then resolve:

```text
Task
  -> Team
  -> Worker
  -> Capability
  -> Implementation
  -> Verification
```

For consequential work, do not allow the same implementation to be the sole planner, executor, and verifier.

## Repository structure

```text
.
├── README.md
├── MANIFESTO.md
├── CONSTITUTION.md
├── LEXICON.md
├── AI_INSTRUCTIONS.md
├── CODE_OF_CONDUCT.md
├── STEWARDSHIP.md
├── ROADMAP.md
├── CHANGELOG.md
├── models.yaml
│
├── docs/
│   ├── philosophy/
│   ├── specification/
│   ├── architecture/
│   ├── methodology/
│   ├── examples/
│   └── history/
│
├── registry/
│   ├── providers/
│   ├── models/
│   ├── capabilities/
│   └── benchmarks/
│
├── policy/
│   ├── routing/
│   ├── escalation/
│   ├── verification/
│   └── governance/
│
├── reference/
│   ├── configs/
│   ├── implementations/
│   └── datasets/
│
├── assets/
│   ├── logo/
│   ├── diagrams/
│   └── banner/
│
└── community/
    ├── teams/
    ├── workers/
    ├── capsules/
    ├── discussions/
    └── proposals/
```

Not every directory is complete. The structure establishes where each type of artifact belongs as the framework develops.

## Documentation

The foundation documents define the boundaries and language of the project:

- [`MANIFESTO.md`](MANIFESTO.md) explains why TEO exists.
- [`CONSTITUTION.md`](CONSTITUTION.md) defines the enduring principles that constrain the project.
- [`LEXICON.md`](LEXICON.md) defines stable orchestration terminology.
- [`STEWARDSHIP.md`](STEWARDSHIP.md) defines how the project is maintained.
- [`ROADMAP.md`](ROADMAP.md) defines the approved build sequence.

Normative guidance belongs under `docs/specification/` and `policy/`.

Provider, model, capability, and benchmark information belongs under `registry/`.

Reference configurations and implementations belong under `reference/`.

## Public scope

This repository is intended only for public use.

It must not contain:

- private prompts
- proprietary workflows
- credentials or secrets
- employer-specific processes
- personal infrastructure
- confidential benchmarks
- identifying operational data

All examples, policies, registries, and discussions should be safe for public review and reuse once a license is selected.

## Roadmap

TEO is being built under a strict phase sequence.

### Phase 1: Repository credibility

- complete the flagship README
- align the visible structure with the documented architecture
- add diagrams and visual identity

### Phase 2: Core team completion

- complete Mission Control
- complete Planning, Engineering, Research, Review, and Verification teams
- standardize team inputs, outputs, escalation, and success criteria

### Phase 3: Routing validation

- test the approved routing against real task classes
- record failures, disagreements, and verification outcomes
- change routing only when evidence exposes a weakness

### Phase 4: Registry population

- document providers
- document models
- document capabilities
- document benchmark evidence

### Phase 5: Reference implementation

- implement a readable reference router
- connect team and worker selection to the policy files
- add validation and conformance examples

The approved scope is tracked in [`ROADMAP.md`](ROADMAP.md).

## Community

TEO is intended to evolve through public collaboration.

Contributions should improve one of the following:

- routing quality
- verification quality
- capability definitions
- registry accuracy
- reference implementations
- documentation clarity

Model updates should include evidence, limitations, and the routing role affected. A newer model should not replace an existing default solely because it is newer or stronger on one benchmark.

The repository owner is `vessaxor-spec`. The project was originally initiated by Sylvester Roxas in 2026 and is intended to grow through community stewardship.

## Capsules

Capsules preserve the state of TEO and the wider AI ecosystem at specific moments in time.

Unlike ordinary documentation, an accepted Capsule is not rewritten. Future stewards add a new Capsule rather than revising the historical record.

Capsules may record:

- the date and project version
- the state of the model ecosystem
- the routing assumptions in use
- important unknowns
- a message to future stewards

The first Capsule belongs in [`community/capsules/`](community/capsules/).

> If this repository still exists years from now, it belongs to every steward who chose to improve it rather than restart it.

## License

No open-source license has been selected yet.

Until a license is added, the repository is publicly viewable but is not yet offered for reuse, modification, or redistribution. External code contributions should wait until the licensing and contribution terms are finalized.

---

<div align="center">

**The best orchestration framework is not the one that predicts the future. It is the one that remains useful when the future arrives.**

</div>
