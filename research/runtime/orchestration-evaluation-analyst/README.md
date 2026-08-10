# Orchestration Evaluation Analyst Research Package

**Status:** Proposed, inactive research candidate  
**Recorded:** 2026-08-10  
**Authority:** Non-normative research only  
**Activation authorized:** No

## Purpose

This package evaluates whether TEO has a real unowned responsibility for post-run route-outcome analysis and, if so, defines the candidate specialist without changing the live specialist registry, worker topology, routing policy, model policy, risk policy, or runtime authority.

The candidate is intentionally separated from live authority until its duplication, evidence, privacy, and authority boundaries are reviewed.

## Candidate

`orchestration-evaluation-analyst`

Proposed responsibility:

> Analyze populations of completed TEO dispatches to determine whether routing configurations show reproducible differences in verified outcome quality, cost, latency, fallback dependence, retry behavior, verifier disagreement, and failure patterns, then produce bounded shadow recommendations for Mission Control.

The candidate does not own live routing and cannot apply its own recommendations.

## Package contents

- [`role-card.md`](role-card.md) defines the complete candidate specialist identity, methods, outputs, and safety boundaries.
- [`proposed-allocation.yaml`](proposed-allocation.yaml) defines a non-active future allocation proposal using the existing Mission Control `orchestration` worker.
- [`conformance.yaml`](conformance.yaml) defines future activation tests and negative controls.
- [`authority-review.md`](authority-review.md) records the duplication and authority-leakage analysis.

## Relationship to current TEO architecture

The package is a direct implementation research artifact for the existing post-v1 route-outcome evidence direction. It does not create a new roadmap objective.

The intended separation is:

```text
agents-orchestrator
  -> designs and operates governed pipelines

orchestration-evaluation-analyst
  -> evaluates completed routing decisions across cohorts
  -> produces evidence and shadow recommendations
  -> cannot modify routing

Mission Control / maintainers
  -> decide whether evidence justifies a reviewed policy change
```

## Activation rule

Nothing in this directory is loaded by the reference router.

Activation requires a separate reviewed change that intentionally updates all applicable active surfaces, including specialist identity, allocation, model policy, routing/conformance coverage, documentation truth, repository-layout governance where required, and tests.

A future activation must preserve the candidate's non-sovereign boundary. Evidence may inform routing. It may not silently become routing authority.
