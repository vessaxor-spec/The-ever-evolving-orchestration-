<a id="readme-top"></a>

<p align="center">
  <img src="assets/banner/teo-banner-hd-optimized.png" alt="The Ever-Evolving Orchestration banner" width="100%">
</p>

<div align="center">

# The Ever-Evolving Orchestration

### Models evolve. Responsibilities endure.

A vendor-neutral orchestration specification and runnable reference control plane for deciding **which intelligence should do the work, under what authority, with which fallback, and with what verification**.

[![Reference Implementation CI](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/actions/workflows/reference-ci.yml/badge.svg)](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/actions/workflows/reference-ci.yml)
[![Release](https://img.shields.io/github/v/release/vessaxor-spec/The-ever-evolving-orchestration-?label=release)](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/releases/tag/v1.0.0)

[**Public overview**](https://vessaxor-spec.github.io/teo/) ·
[**Explore the specification**](docs/specification/lexicon.md) ·
[**Run the reference router**](reference/implementations/python/README.md) ·
[**See current progress**](docs/stewardship/progress-tracker.md) ·
[**View the roadmap**](docs/stewardship/roadmap.md)

**Stable:** `v1.0.0` · **State:** `reference_operational` · **Development:** `teo-reference-router==1.0.1.dev0`

</div>

---

<details>
<summary><strong>Table of contents</strong></summary>

- [About TEO](#about-teo)
- [How TEO works](#how-teo-works)
- [What TEO owns](#what-teo-owns)
- [Current state](#current-state)
- [Quick start](#quick-start)
- [Repository map](#repository-map)
- [Governance and evidence](#governance-and-evidence)
- [Roadmap](#roadmap)
- [Community stewardship](#community-stewardship)
- [License](#license)

</details>

## About TEO

AI models change quickly. Responsibility, authority, risk boundaries, and the need for accountable verification change much more slowly.

TEO is built around one enduring premise:

> **The model is not the architecture.**

TEO separates **what a task requires** from **which model happens to implement it today**. It resolves responsibility, effective risk, required capability, implementation eligibility, fallback, and independent verification before a result can become an evidence-bearing outcome.

That makes the system resilient to provider changes, model releases, new access mechanisms, and future implementations without repeatedly redesigning how work is understood and governed.

### Why this exists

TEO is designed to prevent several common orchestration failures:

- choosing a model before resolving responsibility and capability;
- treating model competence as execution authority;
- allowing fallback to silently weaken risk or verification requirements;
- coupling routing to API keys, subscriptions, OAuth state, or billing;
- letting one provider plan, execute, review, and verify consequential work without independence;
- presenting simulated, staged, or research evidence as live operational proof;
- embedding temporary provider assumptions into permanent architecture.

## How TEO works

TEO resolves the control path in this order:

```text
Task
  -> Effective risk
  -> Mission Control
  -> Team
  -> Worker
  -> Optional Specialist
  -> Required capabilities
  -> Eligible implementation
  -> Provider-aware recovery route
  -> Independent verifier
  -> Evidence-bearing outcome
```

The active control plane is **team-first, capability-first, evidence-first, and failure-aware**.

### Core routing principles

1. **Responsibility before implementation.** Resolve the accountable Team and Worker before selecting a model.
2. **Capability before provider.** Determine what the task requires before considering an implementation.
3. **Risk is a floor.** Convenience, fallback, or caller preference cannot lower effective risk.
4. **Connection is not fitness.** Authentication and subscription state do not become model-selection signals.
5. **Fallback preserves authority.** Recovery must remain capability-valid and cannot widen permissions or weaken verification.
6. **Verification is independent.** Consequential work must have route-appropriate independent verification and fail closed when none remains eligible.

The canonical routing source is [`policy/routing/core/routing.yaml`](policy/routing/core/routing.yaml). Model-sensitive changes are governed by [`policy/governance/model-freshness.yaml`](policy/governance/model-freshness.yaml). README prose summarizes those controls and does not outrank them.

## What TEO owns

| TEO owns | TEO deliberately does not own |
|---|---|
| responsibility resolution | the user's provider account |
| effective-risk interpretation | API keys, OAuth sessions, subscriptions, or billing |
| Team, Worker, and optional Specialist assignment | host identity or host-native permissions |
| required capabilities | an arbitrary sandbox, container, or deployment runtime |
| eligible implementation and reasoning route | permission to widen execution scope |
| provider-aware fallback and escalation | a permanent universal model ranking |
| independent verifier assignment | provider credentials or credential brokering |
| evidence-aware finalization | production distributed scheduling by implication |

Provider access is intentionally separated from routing. An integrating runtime may use any legitimate provider-supported access mechanism without changing TEO's responsibility, capability, risk, fallback, or verifier decisions. See [`docs/specification/provider-access-boundary.md`](docs/specification/provider-access-boundary.md) and [`policy/governance/provider-access-separation.yaml`](policy/governance/provider-access-separation.yaml).

## Current state

TEO has crossed the functional-v1 boundary and is now in post-v1 stewardship and controlled evolution.

| Surface | Current state |
|---|---|
| Stable release | [`v1.0.0`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/releases/tag/v1.0.0), `reference_operational` |
| Development line | `teo-reference-router==1.0.1.dev0` |
| Repository architecture | R1 through R5 complete and CI-governed |
| Guarded live execution | bounded `high_volume_simple` canary at low or medium effective risk |
| Staged live-scope candidate | `documentation`, evaluation only, not authorized for live execution |
| Regulated specialist evidence | six-card pilot stability-qualified; seven-day authority monitoring remains active; expansion requires explicit next risk-tier batch approval |
| High and critical live execution | not authorized |
| Current operational priority | evidence-governed live execution expansion |
| Canonical current status | [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md) |

The current reference system includes deterministic routing, risk controls, specialist bindings, capability checks, provider-diverse recovery, fresh-verifier rotation, guarded provider execution, content-free runtime telemetry, evidence-aware finalization, and qualified-human authority where policy requires it.

The bounded regulated-specialist evidence pilot has completed **2 of 2 formal refresh cycles** and the executable **stability qualification**. The qualification performed **five complete clean authority-resolution replays**, **three independent repeatability runs**, **15 of 15 governed fail-closed mutations**, a controlled authority-move path, and an external-network observation that resolved all seven declared authorities. The seven-day source-resolution cadence remains continuous drift monitoring, not an elapsed-time waiting gate. Qualification does not auto-authorize expansion; an explicit next risk-tier batch approval and separate reviewed change are still required.

### Host Integration research

The **Host Integration Contract** remains non-normative research. Empirical Fresh-AI trial 001 supports fresh-session, no-reminder **routing continuity**, but it did **not** establish full selected-executor/verifier end-to-end assimilation. TEO preserves that negative result rather than promoting it into a stronger claim.

See:

- [`research/roadmaps/host-integration-contract.md`](research/roadmaps/host-integration-contract.md)
- [`research/roadmaps/host-integration-assimilation-protocol.md`](research/roadmaps/host-integration-assimilation-protocol.md)
- [`research/roadmaps/host-integration-fresh-session-trial.md`](research/roadmaps/host-integration-fresh-session-trial.md)
- [`research/runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md`](research/runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md)

The repository's current validation counts, evidence milestones, and exact research boundaries belong in the canonical progress tracker and research records. The compact snapshot below is retained because TEO CI explicitly protects these README truth claims.

<details>
<summary><strong>Current evidence snapshot (CI-protected)</strong></summary>

TEO currently has **ten active organizational teams**, **84 workers**, **82 preserved specialist role cards**, and dedicated Mission Control workers for orchestration, operations, project delivery, and incident response. The Mission Control worker identities are `orchestration`, `operations`, `project_delivery`, and `incident_response`. The active specialist topology includes [`community/specialists/workforce-expansion-active.yaml`](community/specialists/workforce-expansion-active.yaml). Route-Outcome Evidence, the Benchmark and Outcome Lab, Source-backed Cost Attribution, **Shadow Route Evaluation**, and the **Qualified-human approval lifecycle** have completed their current declared milestones.

The accepted substantive runtime-control baseline remains **Reference Implementation CI #514** with **657 automated tests**, **477 tracked-file layout checks**, regulated specialist evidence validation, **40 JSON Schema** parses, valid linked configuration, and the provider-diverse end-to-end reference lifecycle. The documentation reconciliation baseline is **CI #602** with **802 automated tests** and **515 tracked-file layout checks**. The latest Host Integration research baseline remains **Reference Implementation CI #739** with **964 automated tests** and **543 tracked-file layout checks**. The regulated-evidence stability qualification was accepted with **967 automated tests**, **551 tracked-file layout checks**, **41 JSON Schemas**, valid linked configuration, regulated-specialist evidence validation, and the provider-diverse artifact-bound reference lifecycle. These baselines prove their declared checks, not broader provider-backed production claims.

The regulated pilot itself is now **stability-qualified**. Its current evidence consists of **five complete clean authority-resolution replays**, **three independent repeatability runs**, **15 of 15 governed fail-closed mutations**, a controlled authority move, and a GitHub-hosted external-network observation that resolved **7 of 7 declared authorities**. Continuous resolution remains on a **seven-day source-resolution cadence**, and any expansion still requires **explicit next risk-tier batch approval**.

Host Integration has accumulated **eleven provider-independent adversarial slices** plus integrated Fresh-AI assimilation/conformance. Those slices include **verifier-context independence**, **exact artifact/change-set stale-PASS resistance**, **brokered conformant process-lifetime cross-process authority/replay**, **static runtime-wired authority-surface reconciliation**, **process-lifetime recursion resistance**, **exact local freshness binding**, and **portfolio/task-admission separation**. The assimilation work operationalizes the rule **Assimilation is not installation** and requires **two distinct post-assimilation task IDs** rather than treating one successful demo as durable continuity.

Key research records include:

- [`host-integration-verifier-artifact-binding-2026-08-12.md`](research/runtime/host-integration-verifier-artifact-binding-2026-08-12.md)
- [`host-integration-cross-process-authority-2026-08-13.md`](research/runtime/host-integration-cross-process-authority-2026-08-13.md)
- [`host-integration-authority-surface-reconciliation-2026-08-14.md`](research/runtime/host-integration-authority-surface-reconciliation-2026-08-14.md)
- [`host-integration-recursion-resistance-2026-08-14.md`](research/runtime/host-integration-recursion-resistance-2026-08-14.md)
- [`host-integration-freshness-binding-2026-08-14.md`](research/runtime/host-integration-freshness-binding-2026-08-14.md)
- [`host-integration-portfolio-authority-separation-2026-08-15.md`](research/runtime/host-integration-portfolio-authority-separation-2026-08-15.md)
- [`host-integration-assimilation-protocol.md`](research/roadmaps/host-integration-assimilation-protocol.md)
- [`host-integration-fresh-session-trial.md`](research/roadmaps/host-integration-fresh-session-trial.md)
- [`host-integration-integrated-conformance-assimilation-2026-08-15.md`](research/runtime/host-integration-integrated-conformance-assimilation-2026-08-15.md)
- [`2026-08-15-local-fresh-ai-cross-session-trial-001.md`](research/runtime/2026-08-15-local-fresh-ai-cross-session-trial-001.md)

Empirical trial 001 supports fresh-session, no-reminder **routing continuity** but not full end-to-end assimilation. The hardened validator therefore limits research simulation to `routing_continuity_only` unless authenticated selected-versus-observed executor and verifier identity plus digest binding are proven. The earlier **red-canary CI #676** is preserved as evidence from the exact local freshness binding slice rather than hidden as a clean-history rewrite.

The current canonical workstream is **evidence-governed live execution expansion**, **now at 65%**. **`documentation` is the first staged candidate**; its provider-diverse topology and **staged replay harness are validated**, but **provider-backed replay evidence is still pending** and it has **no live-execution authority**. **The next gate is provider-backed controlled documentation replay evidence**. The low or medium risk `high_volume_simple` canary remains the only accepted live execution scope.

The targeted **control-integrity audit** closed a qualified-human **temporal-causality** gap and added recovery-authority regression coverage. **Control Integrity remains intentionally scored at 90%** because mutation depth remains an ongoing discipline. **Issue #100** repository branch-retention cleanup **is complete** and is not a runtime or routing blocker.

Current compatible extensions include **final execution provenance**. Accepted non-normative future research includes **Task Intent & Action Authority** and **Execution Environment & Recovery**. None of these research directions silently widen current live authority.

</details>

## Quick start

### Prerequisites

- Python **3.11+**
- Git

### Install the reference implementation

```bash
git clone https://github.com/vessaxor-spec/The-ever-evolving-orchestration-.git
cd The-ever-evolving-orchestration-
python -m pip install -e '.[test]'
```

The package is defined at the repository root and exposes the `teo` CLI.

### Validate linked configuration

```bash
teo --repo-root . validate
```

### Create a dispatch

```bash
teo --repo-root . plan \
  reference/examples/phase5-task.yaml \
  --output /tmp/teo-dispatch.json \
  --audit-log /tmp/teo-audit.jsonl
```

### Finalize an executed and independently verified result

```bash
teo --repo-root . finalize \
  /tmp/teo-dispatch.json \
  execution-result.json \
  verification-result.json \
  --audit-log /tmp/teo-audit.jsonl
```

### Run the demonstration and tests

```bash
python reference/examples/run_example.py
pytest
```

For provider adapters, retry/fallback behavior, guarded live execution, telemetry, live verification, and Route-Outcome Evidence integration, see the [`Python reference router guide`](reference/implementations/python/README.md).

## Repository map

```text
.
├── README.md                     # public entry point
├── CONSTITUTION.md               # enduring governance principles
├── AI_INSTRUCTIONS.md            # machine-facing repository operating rules
├── CHANGELOG.md                  # accepted change history
├── policy/                       # normative governance, routing, and runtime policy
├── registry/                     # teams, workers, specialists, models, and capabilities
├── community/                    # human-readable teams, specialists, capsules, stewardship
├── reference/                    # runnable reference implementation and examples
├── research/                     # non-normative experiments, evidence, and future directions
├── docs/                         # specification, architecture, methodology, releases, history
├── tests/                        # executable conformance and regression evidence
├── ci/                           # repository validation support
└── assets/                       # public visual assets
```

Repository placement is governed by [`policy/governance/repository-layout.yaml`](policy/governance/repository-layout.yaml) and explained in [`docs/stewardship/repository-layout.md`](docs/stewardship/repository-layout.md).

### Documentation map

| If you want to understand... | Start here |
|---|---|
| enduring principles | [`CONSTITUTION.md`](CONSTITUTION.md) |
| project philosophy | [`docs/philosophy/manifesto.md`](docs/philosophy/manifesto.md) |
| terminology | [`docs/specification/lexicon.md`](docs/specification/lexicon.md) |
| functional-v1 boundary | [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md) and [`docs/releases/v1-readiness.md`](docs/releases/v1-readiness.md) |
| current operational state | [`docs/stewardship/progress-tracker.md`](docs/stewardship/progress-tracker.md) |
| strategic direction | [`docs/stewardship/roadmap.md`](docs/stewardship/roadmap.md) |
| canonical routing | [`policy/routing/core/routing.yaml`](policy/routing/core/routing.yaml) |
| regulated specialist evidence | [`policy/specialists/evidence-pilot.yaml`](policy/specialists/evidence-pilot.yaml), [`policy/specialists/evidence-stability-qualification.yaml`](policy/specialists/evidence-stability-qualification.yaml), and [`docs/history/validation/regulated-specialist-evidence-stability-qualification-2026-08-16.md`](docs/history/validation/regulated-specialist-evidence-stability-qualification-2026-08-16.md) |
| provider-access separation | [`docs/specification/provider-access-boundary.md`](docs/specification/provider-access-boundary.md) |
| runnable implementation | [`reference/implementations/python/README.md`](reference/implementations/python/README.md) |
| historical audits | [`docs/history/audits/`](docs/history/audits/) |
| non-normative research | [`research/`](research/) |

## Governance and evidence

TEO distinguishes **Directive -> Interpretation -> Diagnosis -> Evidence -> Decision -> Approval -> Execution -> Verification -> Documentation -> Learning**.

Implementation is not completion. Consequential claims require evidence appropriate to the claim, and staged or simulated success is not represented as live operational proof.

### Authority hierarchy

When sources disagree, use the more authoritative and current source:

1. applicable machine-readable policy, registry, schema, and activation state;
2. immutable release contracts for the release being discussed;
3. canonical stewardship records for current progress;
4. research and evidence records for bounded claims;
5. README summaries and explanatory prose.

The README is deliberately an entry point, not a parallel source of truth.

### Evidence discipline

TEO's CI validates repository layout, Python sources, automated tests, regulated-specialist evidence, JSON schemas, linked configuration, and the provider-diverse reference lifecycle. A green CI run proves the checks it actually executed. It does not convert staged, simulated, or unexecuted provider evidence into a stronger empirical claim.

The stable release contract is [`docs/releases/v1.0.0.md`](docs/releases/v1.0.0.md). Current development state is tracked separately so post-v1 work cannot silently rewrite the historical release boundary.

## Roadmap

The original foundation milestones are complete:

- repository credibility and governance;
- organizational Team and Worker architecture;
- deterministic routing validation;
- registry and evidence structure;
- runnable reference control plane;
- functional `v1.0.0` release.

Post-v1 work is focused on **control integrity, evidence quality, governed live-scope expansion, calibration, regulated evidence freshness, and future distributed-runtime hardening**.

The current `NOW / NEXT / LATER` sequencing and completion estimates are maintained in the [`Progress Tracker`](docs/stewardship/progress-tracker.md). Strategic direction is maintained in the [`Roadmap`](docs/stewardship/roadmap.md).

Newer models trigger evaluation, not automatic promotion. New architecture directions enter through evidence and review, not README claims.

## Community stewardship

TEO is intended for public technical review and long-term stewardship.

Useful review includes:

- routing and capability gaps;
- stale provider/model evidence;
- verification-independence weaknesses;
- authority or recovery bypasses;
- specialist evidence freshness;
- reproducibility and CI weaknesses;
- documentation drift between policy, runtime, and prose.

Use [GitHub Discussions](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/discussions) for questions, early proposals, research, and technical exploration. Use [GitHub Issues](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/issues) for reproducible defects and accepted, scoped work. Participation is governed by [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

Accepted historical states are preserved as immutable **Capsules** rather than rewritten after the fact. See [`community/capsules/README.md`](community/capsules/README.md).

Because no permanent reuse license or contribution terms have been selected yet, external code contributions should wait until that boundary is resolved. Public review and evidence-backed discussion are still welcome.

## License

**No open-source license has been selected yet.**

The repository is publicly viewable, but no permission is currently granted to copy, modify, distribute, sublicense, or use its contents except where applicable law permits. See [`LICENSE`](LICENSE) for the current legal boundary.

---

<div align="center">

**Models evolve. Responsibilities endure.**

[Back to top](#readme-top)

</div>