# Host Integration Context Economics: Static Payload Slice

**Date:** 2026-08-12  
**Authority:** non-normative research  
**Base revision:** `9d3b5855aff8f445eea06bf6712349df49f4321a`

## Question

Does the candidate Host Integration Contract's bounded one-specialist projection materially reduce the specialist-card context component compared with naively loading every active specialist card?

## Mission Control lenses

- orchestration evaluation
- performance engineering
- repository integrity
- independent verification

## Method

The executable harness at `research/runtime/host_integration_context_economics.py` loads the active roster through the same `ConfigBundle` composition used by the reference implementation. It does not infer the active roster from directory contents.

For each runtime-resolved specialist it follows the configured `role_card`, verifies that the path remains inside `community/specialists/`, and measures the raw UTF-8 file payload in bytes.

The comparison is intentionally narrow:

- **naive:** load all active specialist role cards;
- **bounded:** load exactly one active specialist role card for a dispatch;
- common task, team, worker, capability, policy, and host context is excluded from both sides;
- provider tokenization, inference latency, and task adherence are not inferred from byte counts.

A 95% worst-case reduction is used only as an adversarial research threshold for this static payload slice. It is not a normative runtime budget.

## Result

At the base revision, `ConfigBundle` resolves **82 active specialists**.

| Measure | Result |
|---|---:|
| All active role cards | 1,157,957 bytes |
| Mean one-card payload | 14,121.43 bytes |
| Median one-card payload | 13,648 bytes |
| Smallest one-card payload | 6,700 bytes |
| Largest one-card payload | 27,449 bytes |
| Mean bounded share of naive payload | 1.2195% |
| Worst-case bounded share of naive payload | 2.3705% |
| Mean payload reduction | 98.7805% |
| Worst-case payload reduction | 97.6295% |

The candidate one-card projection therefore clears the 95% static specialist-payload reduction threshold even for the largest active role card.

## Drift correction

The external premortem/host-integration discussion used an **87-card** assumption. Current repository truth is **82 runtime-resolved active specialists**. This measurement rejects the stale count rather than carrying it into the evidence record.

This is a snapshot, not a permanent roster target. Future runs derive the count from `ConfigBundle`.

## Reproduction

From the repository root:

```bash
python research/runtime/host_integration_context_economics.py \
  --require-min-reduction-percent 95
```

The harness exits non-zero if the worst-case reduction falls below the supplied research threshold.

## Decision

**Static prompt-size slice: supported.**

The evidence is sufficient to reject the specific failure mechanism in which every specialist card must be loaded for each dispatch. Under the candidate contract, bounded one-card projection reduces the specialist-card payload by more than 97% even in the current worst case.

**Full context-economics gate: still open.**

The following evidence remains required before the Host Integration Contract can claim the complete context-economics gate:

1. normalized provider/model input usage from real host executions;
2. end-to-end latency comparison under matched tasks and routes;
3. task-adherence comparison showing that projection does not discard required task context;
4. architecture-diverse replay so the result is not specific to one host implementation.

No runtime authority, routing policy, specialist identity, provider access, or live-execution scope changes as a result of this research slice.
