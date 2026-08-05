# Phase 5 Minimal Runnable Scope

## Decision

The first reference implementation is a deterministic, provider-neutral orchestration control plane.

It proves that TEO's documented responsibility chain can be loaded from the repository, resolved into a dispatch, passed through an independent verification gate, and closed with an auditable outcome. It does not attempt to prove live model quality or implement every provider adapter.

## In scope

1. **Task schema** — task, explicit or inferred task class, risk, domain, optional specialist, and execution constraints.
2. **Configuration loading** — canonical team routing, routing policy, worker registry, specialist registry, and model aliases.
3. **Task and risk classification** — deterministic rules with explicit overrides. Ambiguous tasks stop rather than receiving an invented route.
4. **Team and worker resolution** — canonical team routes with context-based worker overrides.
5. **Specialist resolution** — explicit or unambiguous specialist selection only after team and worker selection. Team and worker bindings are enforced.
6. **Capability resolution** — worker-required capabilities plus task-specific requirements.
7. **Implementation resolution** — policy route first, worker preferences second, then documented fallback order, while respecting blocked models and providers.
8. **Fallback and escalation** — a dispatch records the next eligible implementation and failed execution can close as escalated.
9. **Independent verification** — every dispatch receives a verifier implementation different from the execution implementation. Risk policy determines minimum checks and human approval requirements.
10. **Audit output** — dispatch and final outcome records can be appended as JSON Lines.
11. **CLI and example** — validate, plan, finalize, and one complete simulated lifecycle.
12. **Automated tests** — classification, routing, constraints, specialist binding, verification independence, and finalization.

## Explicitly out of scope

- provider SDK integrations and credentials
- live model invocation
- dynamic pricing or latency telemetry
- benchmark-based adaptive scoring
- distributed queues and concurrency
- persistence beyond append-only JSONL
- automatic human approval
- modification or compression of existing team, worker, or specialist definitions

## Safety and conformance behavior

- Explicit task type and risk are accepted when valid.
- Ambiguous classification fails closed.
- Missing workers or incompatible specialists fail closed.
- Existing registry inconsistencies are reported as warnings; the router does not silently rewrite canonical policy.
- Critical routes require human approval.
- An execution model cannot verify its own result.
- Failed verification prevents completion.

## Completion criteria

The Phase 5 skeleton is complete when a clean checkout can:

```text
load configuration
  -> validate linked registries
  -> read an example task
  -> emit a structured dispatch
  -> assign an independent verifier
  -> accept execution and verification evidence
  -> emit and audit a final outcome
  -> pass automated tests
```
