# Local Fresh-AI Cross-Session Trial 001

**Date:** 2026-08-15
**Status:** empirical research evidence — FAIL for end-to-end assimilation; routing continuity supported
**Authority:** non-normative
**TEO revision:** `a141d38db6812469c9b1803798e805c915f86f4f`
**Issue:** #168

## Scoped claim

Test whether a genuinely fresh AI session, after a prior assimilation session has ended, inherits a durable host TEO integration and handles an ordinary no-reminder task through the complete TEO-selected execution and verification path.

The test distinguishes three questions:

1. Did the later AI process lack the assimilation conversation and receive no ad hoc TEO reminder?
2. Did the durable host hook still route the admitted task through TEO before task execution?
3. Did the executor and verifier that actually ran match the implementation and verifier identities selected by TEO?

The run supports questions 1 and 2. It fails question 3.

## Pre-assimilation environment

A dedicated localhost chroot was created at `/mnt/data/teo-fresh-session-sandbox` with a neutral host bootstrap and no TEO project material in the initial host work/home context.

Evidence at preparation time:

- host identity: `Local Fresh Session Sandbox`;
- neutral bootstrap SHA-256: `15867a8d82f735118268c67b847ad0c3f9f2545c267c63b3c59e00ceff20aed6`;
- normal environment reduced to neutral host/session values;
- Linux `unshare` namespaces unavailable (`Operation not permitted`), so isolation used `chroot` plus an empty environment;
- exact TEO source revision later supplied for setup: `a141d38db6812469c9b1803798e805c915f86f4f`.

A local inference runtime was provisioned without injecting TEO content:

- llama.cpp release `b10441`, Ubuntu x64 CPU archive SHA-256 `360a5bfab5b8fe562c52e060a998a052f5fc7d98a0448b035c2eedbb6acfbd94`;
- official `Qwen/Qwen3-1.7B-GGUF`, `Qwen3-1.7B-Q8_0.gguf`, SHA-256 `061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a`.

A disposable pre-assimilation model process answered that it had no prior project-specific knowledge of The Ever Evolving Orchestration. That process ended before the assimilation session.

## Assimilation setup result

The exact TEO source tree was exported from the pinned revision and made available to the setup environment. Executable integration truth derived from that source included:

- stable release `v1.0.0`;
- development runtime `1.0.1.dev0`;
- 10 teams, 84 workers, 82 active specialists;
- active live task type `high_volume_simple`;
- staged task type `documentation`;
- Host Integration binding ID `e9406db17eec9cd189fbf362a228b9887ea8dd9bf15d68a7494508ad274425d4`.

### Self-declared readiness counterexample

The first genuine setup-model declaration stated `ready_for_shadow`, but canonical `AssimilationAuthority` rejected it. The AI had semantically approximated required values, collapsed structured fields, and omitted required unsupported-surface disclosures.

This is empirical evidence that **AI self-declared integration readiness is not sufficient**. The setup required a machine feedback/correction loop. Only the later strict declaration was accepted by the canonical authority.

Accepted assimilation-declaration file SHA-256:

`55f2527130367df7db1ce6898f416f94a4de38aee66cd88c4416a91cbb0b1966`

Canonical declaration digest:

`07b2c4e7c089d4acafac416dee3fff232518e21c9e1161175ab43cfa7081c1d8`

## Persistent host hook and setup conformance

The host installed its standing TEO hook only after:

1. the strict assimilation declaration passed;
2. the sandbox Python/TEO import gate passed.

Standing-hook configuration SHA-256:

`dd6f87002655f6b21dc52bdd1c1002792818ac55d5ccaa5e510d26a273dbae52`

Before any fresh-session challenge existed, the host passed the process-local integrated conformance harness:

- one shadow dispatch;
- two distinct governed setup tasks;
- all six negative controls;
- all ten premortem checks.

This established process-local readiness only.

## Frozen setup commitment

`setup-commitment.json` was frozen before challenge generation.

- trial ID: `local-fresh-ai-trial-001`;
- setup session: `fresh-local-assimilation-setup-001`;
- setup ended: `2026-08-15T13:02:19Z`;
- standing hook: `local-standing-hook-e9406db1`;
- commitment digest: `c881a23775ce0a6d523854e3f8d0cc06e2774c404bf464483e61796738e7d5bb`;
- setup-commitment file SHA-256: `25d3f5e4785bb81beecd22669b98a54a966a2308c85a055ebd8d8cd7825be5a0`.

## Fresh session and no-reminder challenge

A distinct local model process started as `fresh-local-challenge-001` after setup ended. It received only the unchanged neutral host bootstrap and no setup transcript or session-specific TEO/Mission Control instruction.

- fresh session start: `2026-08-15T13:03:03Z`;
- bootstrap locked: `2026-08-15T13:03:37Z`;
- clean replacement challenge issued: `2026-08-15T13:04:07.824900Z`.

An earlier challenge-generation attempt was aborted before disclosure because shell quoting consumed literal status text. The aborted record was retained rather than silently rewritten.

The disclosed neutral challenge was:

> Classify this status as healthy or unhealthy and give one short reason: service alpha, errors 0, retries 0.

Challenge digest:

`15443cf5ad0f21831882808f15ac1c57f178bdd29cce4c181dddf9930b19f1ae`

## TEO routing before task disclosure

The standing host hook invoked TEO before the task was sent to the fresh model process.

TEO dispatch:

`dispatch-348cbd3f2f8c`

TEO selected:

- executor: `google/gemini-3.5-flash-lite`;
- fallback: `anthropic/claude-haiku-4-5`;
- independent verifier: `anthropic/claude-sonnet-5`.

Host admission, TEO dispatch, authority intersection, and exact execution-envelope authorization were established before challenge disclosure to the fresh AI.

This is positive evidence for cross-session standing-hook and routing continuity.

## Fresh AI response and artifact

The fresh local Qwen model answered:

> Healthy — No errors or retries reported, indicating the service is functioning correctly.

Response/artifact SHA-256:

`b8171e1f46a2aefc0d8fd0d754309407a0ded1e15fc242e4b6ae04eb7a639c39`

The later finalized artifact was byte-identical to the Qwen response.

## Structural validator false positive

The original `host_integration_fresh_session_trial.py` validator returned `passed: true` because the packet contained:

- distinct session chronology;
- unchanged bootstrap/hook fingerprints;
- no reminder contamination;
- a TEO dispatch ID;
- `passed` verification status;
- completed finalization/outcome status;
- all required stage names.

Independent falsification then proved that the stronger claim was false.

### Executor substitution

TEO selected `google/gemini-3.5-flash-lite`, but the artifact was generated by local `Qwen3-1.7B-Q8_0`.

The host therefore silently replaced TEO's selected implementation after routing.

### Verifier substitution

TEO selected `anthropic/claude-sonnet-5`, but no live Claude verifier executed. The research path produced a verification fixture carrying the assigned verifier identity.

A fixture may support research simulation, but it cannot authenticate that the selected verifier actually ran.

## Independent verdict

**FAIL** for end-to-end Fresh-AI assimilation.

Failure code:

`executor_and_verifier_authenticity_not_preserved`

Supported narrower result:

**routing continuity supported** — a genuinely distinct no-reminder fresh session inherited the committed host hook and the task entered TEO admission/routing/authority/envelope controls before the AI saw the task.

Unsupported result:

**end-to-end TEO-selected execution/verification** — the actual executor and verifier identities were not preserved.

## Remediation requirement

The fresh-session validator must distinguish routing-continuity evidence from full end-to-end evidence.

A full PASS now requires, at minimum:

- `live_provider` execution mode;
- exact match between TEO-selected and independently observed executor provider/model;
- authenticated executor identity;
- observed executor-output digest equal to the finalized artifact digest;
- exact match between TEO-selected and independently observed verifier provider/model;
- authenticated verifier identity;
- observed verifier-record digest equal to the canonical verification-record digest;
- complete verification/finalization/outcome and downstream evidence stages.

A `research_simulation` may prove routing continuity but must return `passed: false` with a bounded `routing_continuity_only` disposition.

## Authority disposition

This trial did not widen live scope, provider access, routing policy, qualified-human authority, or production Host Integration authority. It remains non-normative research evidence.
