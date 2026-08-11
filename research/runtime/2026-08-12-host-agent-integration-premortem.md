# Host-Agent Integration Premortem

**Date:** 2026-08-12  
**Status:** research  
**Authority:** non-normative  
**Scope:** embedding TEO Mission Control into an existing autonomous AI agent  
**Reconciled against:** `main` at commit `3a3f7cf8c9b0f467b6c9fc6218fb8752542640b2`

## Purpose

This research records lessons from a premortem produced while integrating TEO Mission Control into an external AI agent. The host agent predicted catastrophic failure if TEO were treated as an absolute in-prompt replacement for the host's identity, context management, tool system, autonomy model, and verification topology.

The premortem is useful evidence even where it misreads current TEO semantics. Its strongest contribution is not a defect in TEO's internal control plane. It exposes an under-specified **host integration boundary**: TEO has mature internal routing, capability, risk, authority, and verification contracts, but it does not yet define how an independent host agent should embed those contracts without losing its own identity, native tools, context discipline, or execution model.

This document does not authorize runtime, routing, specialist, verification, or approval changes.

## Repository truth at review time

The current executable TEO roster is:

- 10 organizational teams;
- 84 workers;
- 82 active specialists;
- 4 Mission Control workers.

The host premortem referred to 87 Specialist Cards. That count does not match current executable `ConfigBundle` truth. External integrations must therefore bind to versioned executable registry state rather than count Markdown files or rely on copied/stale inventories.

Relevant current architecture:

- Mission Control owns task intake, responsibility resolution, capability and implementation selection, proportional verification assignment, and final assembly.
- Specialist routing follows `Task -> Mission Control -> Team -> Worker -> Specialist -> Capability -> Implementation -> Independent Verification`.
- Canonical specialist specifications are preservation-protected and must not be rewritten to fit a host agent.
- Tool access is distinct from capability and implementation eligibility.
- Qualified-human approval is activated only when routing already requires it; it is not implied by task complexity or multi-step execution.
- Live independent verification requires model and provider-family independence from the executor for the guarded reference path.

## Premortem findings

### 1. Context-bloat collapse

**Premortem claim:** loading Mission Control plus the complete specialist corpus for every task exhausts context, increases cost, and causes user constraints to be displaced.

**Assessment:** valid failure mode, incorrect integration method.

TEO's responsibility-first structure does not require all specialist cards to be injected into every prompt. An external host should resolve the smallest relevant Team and Worker first, narrow the candidate specialist set from governed metadata, then load only the selected canonical specialist specification and the task-relevant execution envelope.

Recommended routing order:

```text
Task
  -> deterministic task/risk classification
  -> Team
  -> Worker
  -> candidate specialist metadata
  -> exact specialist selection
  -> selected specialist context only
```

Semantic or vector retrieval may support ambiguous discovery, but embedding similarity should not become routing authority when deterministic registry relationships already exist.

**Lesson for TEO:** bounded context projection should become an explicit host-integration requirement. The existing `Specialist Execution Envelope` research is now supported by a concrete external-host failure scenario.

### 2. Identity dilution

**Premortem claim:** the host agent loses its original identity and quality bar when it assumes generalized TEO specialist personas.

**Assessment:** valid and architecturally important.

A host agent should not become the selected specialist. The host identity and the TEO specialist identity are separate layers:

```text
Host identity and mandate
  -> TEO control plane
  -> selected Team / Worker / Specialist lens
  -> host-native execution capabilities
```

The host's identity, safety baseline, quality standard, operating philosophy, and product-specific constraints should remain invariant unless the host itself intentionally changes them. TEO specialist cards remain canonical domain capability definitions and should not be rewritten to inherit host-specific branding or mandates.

When host invariants and specialist instructions conflict materially, the integration should surface an explicit compatibility conflict rather than silently overriding either side.

**Lesson for TEO:** specialist preservation is strong, but host-identity preservation is not yet explicitly specified. A host integration contract should define both.

### 3. Approval paralysis

**Premortem claim:** every complex or multi-step action stalls behind repeated verification and operator approval.

**Assessment:** mostly a misinterpretation of current TEO, but a valid integration-documentation risk.

Current TEO does not equate complexity with human approval. Qualified-human approval only begins after routing has already marked a dispatch `human_approval_required`. Mission Control requires review and verification appropriate to risk and consequence rather than universal operator interruption.

External hosts nevertheless need an explicit autonomy profile so that "Mission Control is required" cannot be interpreted as "ask permission at every orchestration boundary."

A useful conceptual distinction is:

```text
AUTONOMOUS
  routine or reversible execution

VERIFIED_AUTONOMOUS
  autonomous execution plus required independent verification

ESCALATED
  unresolved ambiguity, elevated consequence, or failed controls

HUMAN_GATED
  only where policy explicitly requires qualified-human authority
```

**Lesson for TEO:** host integration should expose autonomy and authority semantics directly rather than leave them to prompt interpretation.

### 4. Skill-to-specialist mismatch

**Premortem claim:** TEO specialists do not know the host's custom tool ecosystem, leading to hypothetical or invalid tool use.

**Assessment:** valid failure mode.

Canonical specialists should request capabilities, not host-specific commands. An external host needs a capability-adapter manifest that maps governed TEO capability requirements onto concrete host tools and records whether those tools are currently available and authorized.

Conceptual binding:

```text
TEO capability
  -> host capability binding
  -> concrete installed tool or action
```

A host capability binding should be able to declare at least:

- capability identifier;
- concrete tool/action identifier;
- availability;
- permissions and scope;
- read/write or side-effect class;
- sandbox or isolation boundary;
- prerequisites;
- output contract;
- rollback or compensating action where applicable;
- fallback capability binding where one exists.

**Lesson for TEO:** this mapping belongs in a host integration layer, not in canonical specialist cards, preserving provider and runtime neutrality.

### 5. Verification schism

**Premortem claim:** a single-agent host cannot honestly perform independent verification and instead simulates a second persona inside the same session.

**Assessment:** valid problem; proposed same-session/subagent simulation is insufficient.

A distinct subagent invocation is not automatically independent. Where TEO requires provider-diverse independent model verification, the host must use a genuinely eligible verifier or explicitly record that the required verification path is unavailable.

Deterministic evidence such as tests, static analysis, sandbox execution, schema checks, and security scanners can materially strengthen a result, but must not be mislabeled as provider-diverse model verification.

**Lesson for TEO:** external integrations need explicit verification capability declarations and truthful degradation/refusal semantics when required independence cannot be achieved.

## Additional failure modes exposed by the review

### 6. Registry drift

The host premortem's 87-card count conflicts with current executable truth of 82 active specialists. An integration that enumerates files, copies registries, or caches an unversioned specialist list can silently route against stale authority.

A host integration should bind at least:

- TEO release/runtime version;
- routing-policy version;
- specialist-registry version;
- capability-registry version;
- host integration-contract version.

The active executable configuration remains the roster authority.

### 7. Recursive orchestration

An existing autonomous host may already contain planners, orchestrators, subagents, or collective execution. Embedding TEO without recursion boundaries can create nested loops such as:

```text
Host orchestrator
  -> TEO Mission Control
  -> orchestration specialist
  -> host orchestrator
  -> TEO Mission Control
  -> ...
```

External-host execution therefore needs bounded delegation depth, specialist-spawn limits, retry limits, and explicit termination criteria. These limits may restrict execution but must never lower effective risk or weaken required verification.

### 8. Control-plane capture

"TEO is non-negotiable" can be misread as "TEO owns the host agent." TEO should govern orchestration decisions inside its declared authority boundary, not erase the host's native safety controls, identity, product constraints, permissions, or execution environment.

A host integration contract should specify authority precedence and conflict handling rather than rely on prompt hierarchy alone.

### 9. Big-bang enforcement

Replacing a mature host's native orchestration with mandatory TEO enforcement in one step conflicts with TEO's own evidence-governed expansion philosophy.

A safer integration sequence is:

```text
native host baseline
  -> TEO shadow routing
  -> compare route/output/tool decisions
  -> measure quality, latency, normalized usage, failures, and verification availability
  -> bounded governed activation
  -> wider activation only from evidence
```

### 10. Missing integration conformance profile

External hosts currently lack a concise way to state which TEO semantics they genuinely implement. Without this, partial implementations can incorrectly claim full TEO behavior.

A future conformance profile should make support explicit for surfaces such as:

- Mission Control responsibility resolution;
- active-registry binding;
- specialist routing;
- capability binding;
- non-lowerable risk;
- autonomy/authority semantics;
- independent verification;
- route-outcome evidence;
- recovery/fallback semantics;
- qualified-human authority where applicable.

Unsupported semantics should be declared, not simulated.

## Disposition of the premortem's proposed mitigations

| Proposed mitigation | Disposition | Reason |
|---|---|---|
| Vector/RAG retrieval for specialists | Modify | Use deterministic Team/Worker/registry narrowing first; semantic retrieval is fallback support, not routing authority. |
| Inject host mandate into specialist cards | Reject as stated | Preserve host mandate separately and keep canonical specialist identity intact. |
| Map host tools to TEO domains | Accept with architectural change | Implement as a host capability-adapter manifest rather than specialist-card modification. |
| Distinct subagent verification | Reject as sufficient | A subagent does not by itself satisfy required model/provider independence. |
| Shadow integration before enforcement | Add | Compare native and TEO-governed behavior before widening authority. |

## Architectural conclusion

The premortem does not justify weakening Mission Control, specialist preservation, risk, verification, or human-authority boundaries.

It does justify a new integration-layer research direction:

> **TEO needs an explicit Host Integration Contract that preserves host identity, projects bounded context, binds host-native capabilities, declares autonomy and authority semantics, prevents recursive orchestration, binds versioned registry truth, and reports verification/conformance capability honestly.**

This contract should sit between an external host agent and TEO Mission Control. It should adapt the host to TEO semantics without rewriting either the host's identity or TEO's canonical specialist definitions.

## Next research gate

Before any normative schema or runtime implementation is proposed:

1. define a non-normative Host Integration Contract candidate;
2. validate it against the external-host premortem that triggered this research;
3. test the same contract against at least one structurally different host architecture;
4. identify which fields are truly universal versus host-specific;
5. prove the contract does not create a second routing authority, weaken existing TEO controls, or require full specialist-corpus prompt loading;
6. only then decide whether a normative specification/schema is justified.

No current Progress Tracker workstream is promoted or reordered by this research.