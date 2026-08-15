# Host Integration Fresh-AI Assimilation Protocol Research

**Date:** 2026-08-15
**Status:** research protocol
**Authority:** non-normative
**Parent authority:** [`host-integration-contract.md`](host-integration-contract.md)
**Scope:** the process a fresh AI or existing AI host must follow when asked to assimilate, adopt, embed, or integrate TEO

## Purpose

A fresh AI can misread TEO in several dangerous ways even when it has access to the complete repository. It may treat TEO as:

- a plugin to install and then ignore;
- a finished product that sits beside the host rather than governing admitted orchestration;
- a prompt persona or specialist library;
- a one-time migration task that is considered complete once files are copied;
- a set of advisory documents that can be bypassed by the host's existing router;
- a second orchestration stack that competes with the host instead of governing an explicit boundary.

Those interpretations are integration failures.

This protocol defines an evidence-bearing assimilation sequence intended to make a fresh AI **reconstitute TEO as an orchestration control plane, integrate it without erasing host identity, prove that the host actually uses it, and preserve that use after the integration task is over**.

It is a companion process to the Host Integration Contract. It does not create new production authority and does not make Host Integration normative.

## Core rule

> **Assimilation is not installation. Integration is not complete when TEO files, prompts, skills, packages, or configuration are present. Integration is complete only to the extent that the host can prove admitted work actually traverses the declared TEO control path and continues to do so after the setup task ends.**

TEO must not be represented as an optional plugin, SDK, library, persona pack, or finished application. It is an orchestration control plane whose authority applies only inside the integration boundary explicitly delegated to it.

The host remains the host. TEO remains TEO.

## Required assimilation lifecycle

The minimum research lifecycle is:

```text
0. Source and revision acquisition
1. Reconstitute TEO from repository truth
2. Reconstitute the host independently
3. Map the host/TEO authority boundary
4. Produce an assimilation declaration
5. Install a persistent control-plane hook
6. Run TEO in shadow mode
7. Perform bounded governed activation
8. Replay negative controls and the integration premortem
9. Prove continued use on a later task
10. Emit an evidence-bounded conformance statement
```

No phase may be replaced by a statement such as "TEO is installed", "TEO is integrated", "the plugin is enabled", or "all tests pass".

## Phase 0: acquire an exact TEO source identity

The integrating AI must identify the exact TEO source it is assimilating.

At minimum capture:

- repository or trusted source identity;
- exact revision or immutable release reference;
- stable release identity;
- runtime package version;
- freshness/compatibility state where available.

A copied folder with no provenance is not enough to claim current TEO identity. A remembered specialist count or copied Mission Control document is not executable composition truth.

If the source cannot be authenticated, the host may inspect it, but must not represent the source as an authenticated current TEO integration.

## Phase 1: reconstitute TEO before designing the integration

The fresh AI must first understand TEO as TEO, not through the host's existing architecture.

Follow the repository read order in `AI_INSTRUCTIONS.md`. The assimilation report must derive, from current repository truth:

- stable release and runtime version;
- exact revision and Host Integration binding/freshness identity;
- active Team, Worker, and Specialist counts;
- the responsibility chain:

```text
Mission Control
  -> Team
  -> Worker
  -> Optional Specialist
  -> Capability
  -> Implementation
  -> Independent Verification
  -> Evidence-bearing Outcome
```

- current active live task types;
- staged but unauthorized live candidates;
- current qualified-human authority behavior;
- provider/model routing versus provider connection separation;
- current Host Integration residual boundaries.

The AI must be able to explain the following distinctions without collapsing them:

- Team is not Worker.
- Worker is not Specialist.
- Specialist is not Capability.
- Capability is not tool implementation.
- Implementation/model is selected after responsibility and authority.
- Provider access is not model-routing authority.
- Verification is not executor self-review.
- Successful execution is not finalization.
- TEO orchestration authority is not host portfolio authority.

A fresh AI that cannot reconstruct those distinctions has not assimilated TEO.

## Phase 2: reconstitute the host separately

Before changing the host, identify its native architecture without renaming it into TEO terminology.

Capture:

- host identity and mission;
- native safety and privacy invariants;
- existing planner/router/orchestrator behavior;
- portfolio or task-admission authority;
- native tools and capabilities;
- execution environment;
- credential and tenant boundaries;
- approval surfaces;
- verifier/testing surfaces;
- recovery and retry behavior;
- persistence mechanism for standing instructions or middleware.

The host must not be rewritten to look like TEO. TEO must not be rewritten to look like the host.

## Phase 3: map the integration boundary

Build an explicit boundary map before implementation.

The minimum ownership model is:

| Surface | Default authority |
|---|---|
| Host identity, mission, product constraints | Host |
| Host backlog, priority, and task admission | Host |
| Routing of admitted TEO-governed work | TEO Mission Control |
| Team/Worker/Specialist resolution | TEO |
| Risk floor and TEO authority requirements | TEO, intersected restrictively with host constraints |
| Native tool implementation | Host capability adapter |
| Credentials/account/tenant access | Host/runtime boundary |
| Model/provider selection | TEO routing |
| Provider connection mechanism | Host/runtime after routing |
| Independent verification assignment | TEO verification contract |
| Final host action | Exact TEO authorization intersected with host authorization |

If the host already has a router, the integration must state what happens to that router for TEO-admitted tasks. It may perform pre-routing host safety/admission work, but it must not silently override TEO Team, Worker, Specialist, implementation, fallback, or verifier decisions after work enters the TEO-governed boundary.

## Phase 4: produce an assimilation declaration

Before activation, the fresh AI must produce an explicit declaration containing at least:

```yaml
host_id: <stable-host-identity>
integration_role: embedded_orchestration_control_plane
host_identity_preserved: true
portfolio_authority_owner: host
routing_authority_owner: teo_mission_control
connection_semantics: connection_after_routing
responsibility_chain:
  - mission_control
  - team
  - worker
  - optional_specialist
  - capability
  - implementation
  - independent_verification
  - evidence_bearing_outcome
specialist_context_mode: selected_only_bounded_projection
verification_mode: independent_provider_diverse_when_required
activation_sequence:
  - shadow
  - bounded_governed_activation
  - evidence_gated_expansion
stable_release: <derived>
runtime_version: <derived>
revision: <derived>
binding_id: <derived>
team_count: <derived>
worker_count: <derived>
specialist_count: <derived>
active_live_task_types: <derived>
staged_live_task_types: <derived>
unsupported_surfaces:
  - <explicitly-unproven-boundary>
```

The declaration is not proof by itself. It is a falsifiable statement that later phases must test.

The current process-local research harness rejects declarations that frame TEO as a plugin/product, collapse the responsibility chain, hide unsupported surfaces, misstate current roster/live-scope truth, use same-session verification roleplay, or skip shadow integration.

## Phase 5: install a persistent control-plane hook

A one-time conversation instruction is insufficient.

The host must create a durable integration mechanism appropriate to its architecture. Examples include:

- a project/system instruction inherited by new sessions;
- routing middleware;
- an admission gateway;
- a host lifecycle hook;
- a persistent orchestration policy;
- a code-level dispatch boundary;
- another reviewable mechanism that new sessions cannot silently omit.

The standing rule must be semantically equivalent to:

```text
For every task the host admits into the TEO-governed boundary,
TEO Mission Control must resolve the orchestration decision before governed execution.
The host may narrow or deny authority, but may not silently replace the TEO route.
```

The hook must be version/freshness bound and testable. Merely placing TEO files in a repository or installing the reference package does not satisfy this phase.

## Phase 6: shadow integration

Do not immediately replace mature host behavior.

Route representative admitted tasks through TEO while the existing host path remains behaviorally authoritative. Capture:

- host-native decision;
- TEO dispatch;
- Team/Worker/Specialist resolution;
- capability requirements;
- selected implementation/fallback;
- verifier assignment;
- effective risk/human authority;
- latency and failure observations where available;
- material disagreements.

Shadow mode must not mutate production behavior merely to prove integration.

No bounded activation is allowed in the research conformance harness until at least one real TEO shadow dispatch exists.

## Phase 7: bounded governed activation

Select only a task class already authorized by current TEO live policy and host authority.

The integrated path should compose, as applicable:

```text
Host task admission
  -> assimilation/freshness validation
  -> TEO Mission Control dispatch
  -> dispatch provenance
  -> recursion/resource budget
  -> restrictive TEO/host authority intersection
  -> exact execution envelope
  -> host-native capability execution
  -> exact artifact/result evidence
  -> independent verification
  -> finalization
```

A successful call to a model or tool is not enough. The evidence must show that the exact task actually traversed the TEO-governed path.

## Phase 8: replay negative controls and the premortem

At minimum, the integrated host must demonstrate the following fail-closed behaviors where applicable:

- a staged but unauthorized TEO task type remains blocked;
- revoked host admission blocks continued execution;
- post-verification artifact mutation blocks finalization;
- high-risk work is not automatically human-gated when policy does not require it;
- critical qualified-human authority remains blocking where policy requires it;
- recursive TEO re-entry beyond the declared budget is refused;
- stale/mismatched registry or integration truth is not treated as current;
- TEO cannot mutate host backlog/priority through the TEO-facing gateway;
- executor and verifier independence is not simulated by roleplay;
- the host cannot silently substitute its own route after TEO dispatch.

The complete process-local replay should map back to the original ten Host Integration premortem failure paths:

1. context-bloat collapse;
2. identity dilution;
3. approval paralysis;
4. skill-to-specialist mismatch;
5. verification schism;
6. registry drift;
7. recursive orchestration;
8. control-plane capture;
9. big-bang enforcement;
10. missing integration conformance profile.

Passing individual component tests is not the same as replaying those failure modes across the composed host path.

## Phase 9: prove continued use after the integration task

This phase exists specifically to prevent "integrate TEO" from becoming a one-time setup exercise.

After the first bounded activation succeeds:

1. end the setup/installation step;
2. present a second distinct admitted task;
3. do not give the host a special "use TEO now" reminder;
4. verify that the persistent host hook routes the later task through TEO again;
5. capture a second independent governed-use receipt.

A host that can demonstrate one integration demo but then returns to its native router has **not** assimilated TEO operationally. In this protocol, one successful integration demo is insufficient.

The research harness therefore requires at least two governed receipts with **distinct task IDs** before it will emit a process-local integrated conformance result. Replaying the same setup/demo task twice is not continuity evidence.

The process-local harness still cannot prove that the second task occurred in a genuinely fresh session, that no hidden reminder was supplied, or that a host persisted its hook across restart. Those remain explicit cross-session/production evidence requirements even after the process-local result passes.

## Phase 10: emit an evidence-bounded conformance statement

The final statement must distinguish:

- supported surfaces;
- partially supported surfaces;
- unsupported surfaces;
- exact TEO binding/revision;
- evidence runs;
- negative controls exercised;
- persistent integration mechanism;
- remaining production/distributed boundaries.

Never say simply "TEO integrated" or "full TEO support" unless a future normative conformance profile explicitly defines and proves that claim.

A valid research statement should look more like:

> This host demonstrated process-local integrated TEO conformance for the tested admitted-task path at binding `<id>`, including shadow routing, repeated governed execution, exact authority intersection, artifact-bound verification, and the declared negative controls. Remote/distributed authenticity, restart-durable state, and compromised-host bypass resistance remain unsupported.

## Required evidence packet

A fresh AI integration should leave behind an auditable packet containing:

1. exact TEO source/revision/freshness identity;
2. assimilation declaration;
3. host architecture and authority-boundary map;
4. capability-adapter map;
5. persistent control-plane hook or equivalent durable rule;
6. shadow comparison evidence;
7. first bounded activation receipt;
8. negative-control and premortem replay results;
9. later-task continued-use receipt;
10. explicit conformance/non-conformance statement;
11. residual boundaries and follow-up actions.

If an AI cannot point to these artifacts, it should describe the integration as incomplete rather than infer success from installed files.

## Fresh-AI bootstrap directive

The following is the recommended research bootstrap instruction when asking a fresh AI to assimilate TEO into an existing architecture:

```text
Assimilate The Ever-Evolving Orchestration (TEO) into this host architecture.

Do not treat TEO as a plugin, SDK, prompt persona, specialist pack, or finished product.
TEO is an orchestration control plane. Reconstitute TEO from current repository truth before changing the host.

First:
1. Read and follow TEO's AI_INSTRUCTIONS.md and Host Integration Contract research.
2. Derive the current TEO release/runtime/revision, active Team/Worker/Specialist composition, responsibility chain, live-scope boundary, model-routing versus provider-connection semantics, verification requirements, and remaining Host Integration gaps.
3. Reconstruct this host's identity, native safety rules, portfolio/task-admission authority, tools, permissions, execution environment, verification, recovery, and persistence separately. Do not rename the host into TEO terminology and do not rewrite TEO specialists to match the host.
4. Produce an explicit host/TEO authority-boundary map and assimilation declaration. TEO Mission Control must own routing for work explicitly admitted into the TEO-governed boundary. Host restrictions may narrow or deny authority but may not silently replace the TEO route.
5. Install a durable host mechanism so future sessions/tasks continue to invoke TEO for admitted work. A one-time prompt, copied files, package installation, or successful setup test is not completion.
6. Start in shadow mode. Compare native and TEO decisions before bounded activation.
7. Activate only a currently authorized bounded scope and prove the complete path through admission, TEO dispatch, authority intersection, exact execution envelope, verification, finalization, and evidence.
8. Run negative controls, including staged-scope refusal, revoked admission, artifact mutation, human-authority preservation, recursion refusal, and stale/mismatched integration truth.
9. After setup is complete, run a second distinct admitted task without a special reminder and prove the persistent integration still routes it through TEO.
10. Report only evidence-backed conformance. Explicitly list unsupported surfaces. Do not claim 'TEO integrated' merely because files, prompts, skills, or packages are present.

Repository truth overrides memory. Preserve TEO architecture and the host's native identity. Do not widen live authority as part of integration.
```

## Integration failure conditions

Treat the integration as failed or incomplete if any of the following is true:

- the AI reports success immediately after copying or installing TEO;
- TEO is called a plugin and can be bypassed by ordinary admitted tasks;
- the host keeps making Team/Worker/Specialist/model decisions after TEO is supposedly authoritative for that task;
- a fresh session does not inherit the TEO integration boundary;
- only the setup task ever traversed TEO;
- the host cannot state which TEO revision/composition it is using;
- all specialist cards are loaded into every prompt;
- host identity is replaced by specialist personas;
- the host invents capabilities or generic tools from specialist prose;
- same-session roleplay is called independent verification;
- unsupported surfaces are hidden behind a generic "full integration" claim;
- shadow evidence is skipped and the host jumps directly to broad enforcement;
- a successful sandbox run is used to widen production authority automatically.

## Ongoing assimilation maintenance

Assimilation is continuous, not a one-time migration.

A host should re-evaluate its integration when any of the following changes materially:

- TEO revision or compatible release;
- routing/model policy;
- active Team/Worker/Specialist composition;
- capabilities or adapter implementations;
- live-execution scope;
- verification/finalization contract;
- host identity or authority boundaries;
- host tools/credentials/tenant model;
- recovery or scheduler architecture;
- Host Integration conformance requirements.

Freshness detection does not itself authorize an update. The host should assess compatibility, rerun relevant shadow/negative controls, and preserve the last known-safe integration boundary until evidence supports the new state.

## Current research implementation

The process-local executable companion is:

- `research/runtime/host_integration_integrated_conformance.py`
- `tests/test_host_integration_integrated_conformance.py`

The harness intentionally requires:

- exact assimilation truth;
- control-plane rather than plugin/product framing;
- preserved host portfolio authority;
- exact responsibility-chain semantics;
- bounded specialist context;
- independent verification semantics;
- shadow-before-activation;
- a persistent standing host hook;
- repeated post-assimilation governed use;
- integrated negative controls;
- explicit residual boundaries.

A passing result is only **process-local integrated research evidence**. It is not a production host certification and does not resolve remote/distributed authenticity, restart-durable state, or compromised-host bypass resistance.
