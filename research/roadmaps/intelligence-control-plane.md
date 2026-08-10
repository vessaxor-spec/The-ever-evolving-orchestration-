# TEO Roadmap Research

**Status:** Post-v1 strategic research direction  
**Recorded:** 2026-08-10  
**Authority:** Non-normative research guidance  
**Scope:** Future trajectory of The Ever-Evolving Orchestration after the `v1.0.0` functional reference boundary

## Purpose

This document records a strategic research direction for TEO. It is intentionally separate from the normative v1 contract.

Its purpose is to guide future stewardship toward a durable competitive position without turning every promising idea into an immediate implementation commitment.

The central trajectory is:

> **TEO should become the vendor-neutral intelligence control plane that can sit above any orchestration runtime and continuously determine the safest, highest-quality, most efficient way to accomplish a task.**

TEO should not attempt to win by reproducing every graph, workflow, persistence, hosting, streaming, or deployment feature already developed by execution-focused orchestration frameworks.

Instead, TEO should specialize in the layer that decides:

- who is responsible for the work
- what risk and authority constraints apply
- which capabilities are actually required
- which implementation is eligible
- which reasoning effort is justified
- which fallback remains valid
- which verifier is independent and qualified
- whether human authority is required
- whether the resulting evidence is sufficient
- what observed outcome should inform future routing

## Competitive observation

Contemporary orchestration systems are increasingly capable at execution.

Examples include:

- LangGraph: stateful graph execution, persistence, checkpoints, human-in-the-loop, recovery, and fault tolerance
- Microsoft Agent Framework: typed workflows, executors and edges, sequential and concurrent orchestration, handoffs, group chat, manager-style orchestration, checkpointing, streaming, and human-in-the-loop
- OpenAI Agents SDK: agents, tools, runners, handoffs, guardrails, sessions, and tracing
- CrewAI: role-based agents and crews, deterministic and event-driven flows, memory, persistence, guardrails, observability, and deployment tooling

These capabilities are useful execution substrates. They should not define TEO's competitive battlefield.

TEO's stronger architectural position is one layer above them:

```text
                 TEO
       +-----------------------+
       | Intelligence policy   |
       | Risk and authority    |
       | Capability matching   |
       | Model selection       |
       | Economic allocation   |
       | Verification          |
       | Outcome learning      |
       +-----------+-----------+
                   |
       +-----------+-------------+-------------+
       |                         |             |
   LangGraph              Agent Framework    CrewAI
       |                         |             |
       +-------------------------+-------------+
                   |
       OpenAI / Anthropic / Google / local / future
```

TEO may integrate with these or other runtimes rather than requiring them to be replaced.

## Strategic optimization objective

Future TEO research should optimize toward:

> **Maximum verified outcome quality per unit of cost and latency, subject to risk, capability, evidence, and authority constraints.**

This is deliberately different from maximizing:

- number of agents
- number of integrations
- model size
- newest-model usage
- workflow complexity
- autonomous behavior
- raw benchmark score

Those are possible inputs. They are not the objective.

The desired loop is:

```text
Task
  -> Governed intelligence configuration
  -> Execution
  -> Independent verification
  -> Measured outcome
  -> Evidence update
  -> Better future routing
```

## Potential durable advantages

### 1. Outcome-learning routing

TEO should eventually learn which combinations of Team, Worker, Specialist, implementation, reasoning effort, tools, fallback, and verification actually perform best for a task class.

This must not begin as uncontrolled self-modifying routing. The first objective is trustworthy evidence collection and comparative evaluation.

### 2. Runtime neutrality

TEO should be able to govern work executed through multiple orchestration substrates, including:

- LangGraph
- Microsoft Agent Framework
- OpenAI Agents SDK
- CrewAI
- direct provider APIs or SDKs
- local runtimes
- custom enterprise orchestrators
- future execution systems

Runtime selection should remain an execution concern unless a runtime capability is itself required by the task.

### 3. Risk-aware intelligence allocation

Routing should consider more than subject classification.

Relevant signals may include:

- effective risk
- uncertainty
- reversibility
- consequence of error
- authority requirements
- specialist risk profile
- evidence requirements
- verification requirements

A low-consequence reversible task and a high-consequence specialist task should not receive identical intelligence budgets simply because they share a topic.

### 4. Verification orchestration

Verification should remain an independent orchestration responsibility.

TEO should continue to distinguish:

- executor
- fallback executor
- verifier
- escalation implementation
- qualified human authority

A fallback redispatch must not silently inherit a verifier that is no longer independent or capability-valid.

### 5. Evidence-bearing decisions

For consequential routing, TEO should be able to explain why a route was selected.

A future dispatch record should be able to show evidence for decisions such as:

- Team and Worker assignment
- Specialist activation
- effective-risk determination
- required capabilities
- implementation eligibility
- reasoning-effort choice
- fallback eligibility
- verifier independence
- escalation requirements

The goal is accountable routing, not opaque model preference.

### 6. Continuous model-market intelligence

Models should be treated as replaceable implementations rather than architecture.

TEO should continuously refresh authoritative evidence about:

- currently available models
- documented capabilities
- limitations
- preview or stability status
- context and modality support
- tool support
- reasoning controls
- provider availability
- observed TEO benchmark performance

A model can be promoted, demoted, constrained, or removed without redefining Team, Worker, Specialist, risk, or authority structure.

### 7. Economic optimization

TEO should eventually reason explicitly about the marginal value of a stronger route.

Conceptually, it should be able to distinguish cases such as:

```text
Configuration X
Verified acceptance: 94%
Estimated cost: EUR 0.18
Latency: 11 s

Configuration Y
Verified acceptance: 96%
Estimated cost: EUR 0.74
Latency: 31 s
```

If the additional quality does not justify the increased cost and latency for the applicable risk tier, TEO should prefer the efficient configuration.

For consequential work, the same optimization may correctly select the more expensive route because the risk constraint dominates cost.

Cost must never be allowed to lower the effective-risk floor, capability requirement, verification requirement, or human-authority requirement.

### 8. TEO conformance standard

A longer-term opportunity is to define a conformance contract through which external runtimes, providers, or enterprise systems can become TEO-compatible without adopting the TEO reference implementation.

Potential conformance surfaces include:

- task contract
- capability declaration
- dispatch contract
- evidence contract
- verifier contract
- fallback contract
- telemetry contract
- outcome contract

This would allow TEO to evolve as a specification and control plane rather than becoming locked to one execution engine.

## Highest-priority research program: TEO Benchmark and Outcome Lab

Outcome-learning routing should not be implemented before the measurement substrate is trustworthy.

The first major post-v1 research program should therefore be a canonical evaluation harness.

### Minimum dispatch record

For controlled benchmark and operational evidence, record at least:

```text
Task class
Effective risk
Team
Worker
Specialist
Required capabilities
Executor implementation
Reasoning effort
Tools and runtime capabilities used
Fallback events
Verifier implementation
Verification result
Qualified-human result where applicable
Latency
Token or compute consumption where observable
Cost where source-backed
Failure mode
Final acceptance state
Evidence provenance
```

### Research objective

The initial comparison should be:

> **TEO versus TEO.**

Different valid configurations should be tested against the same controlled workload so that TEO can learn which routing policies actually improve outcomes.

Only after that evidence is credible should broader claims compare:

> **TEO-governed execution versus conventional orchestration baselines.**

The benchmark program must avoid designing tests merely to prove TEO superior. Baselines, tasks, scoring rules, verifier criteria, and exclusions should be declared before comparison wherever practical.

## Proposed research sequence

### R0. Measurement substrate

Build the Benchmark and Outcome Lab.

Required properties:

- canonical task fixtures
- reproducible dispatch records
- source-backed cost and latency where available
- failure classification
- independent verification records
- evidence provenance
- blinded human review support for claims that require human ground truth
- deterministic replay where runtime permits

**Exit condition:** measurement quality is sufficient to distinguish a routing improvement from measurement noise.

### R1. Comparative routing experiments

Run controlled TEO-versus-TEO comparisons across:

- task classes
- risk tiers
- specialists
- implementations
- reasoning efforts
- verifier assignments
- fallback strategies
- runtime substrates where relevant

**Exit condition:** repeated evidence demonstrates stable performance differences for defined task classes.

### R2. Shadow recommendations

Introduce a non-authoritative recommendation layer that predicts a preferred route but does not control live dispatch.

Compare recommended routes with the governed production decision and eventual outcomes.

**Exit condition:** the recommendation layer demonstrates useful predictive value without violating policy constraints.

### R3. Policy-constrained adaptive routing

Allow outcome evidence to influence routing only inside explicit policy boundaries.

Hard constraints remain authoritative. Learning may optimize only among eligible routes.

Examples of non-negotiable constraints:

- effective risk cannot be lowered
- required capabilities cannot be bypassed
- preview authorization remains explicit
- provider-diversity rules remain enforceable
- human authority cannot be substituted by model confidence
- verification independence cannot be traded away for cost

**Exit condition:** adaptive routing improves verified outcomes or efficiency while all safety and governance invariants remain mutation-tested.

### R4. Runtime adapter and conformance layer

Define stable adapter contracts for external execution runtimes.

The adapter should translate a governed TEO dispatch into runtime-specific execution without allowing the runtime to rewrite the governing decision silently.

**Exit condition:** the same TEO dispatch semantics can execute through at least two materially different runtime substrates with equivalent policy observability.

### R5. External comparative evidence

Publish controlled comparisons between TEO-governed execution and representative conventional orchestration baselines.

Claims should be scoped narrowly to what the evidence actually supports.

**Exit condition:** results are reproducible enough for independent challenge and do not depend on privileged or hidden benchmark assumptions.

## Guardrails for outcome learning

Outcome learning can create a stronger control plane, but it can also create subtle failure modes. The following constraints should guide design research:

### Learning never outranks governance

Historical performance cannot override a hard policy constraint.

### Correlation is not qualification

A model that performs well historically is not automatically eligible for a task whose required capabilities it does not satisfy.

### Verification quality must itself be measured

A high verifier pass rate is meaningless if the verifier is weak, correlated with the executor, or systematically permissive.

### Cost data must be source-backed

Do not fabricate precision where provider or infrastructure cost is unknown.

### Failure data should be retained, not optimized away

A system that records only successful routes will learn the wrong lesson.

### Model updates can invalidate historical evidence

Outcome evidence should be versioned against the actual implementation used. Evidence for one model generation must not silently transfer to another.

### Human ground truth remains a separate evidence tier

Machine-panel agreement is useful operational evidence but should not be represented as human-ground-truth calibration.

### Adaptive behavior must remain auditable

A future observer should be able to reconstruct why the router's preference changed.

## Non-goals

This roadmap does not commit TEO to:

- replacing existing orchestration runtimes
- becoming a universal distributed workflow engine
- building every provider integration directly
- maximizing autonomous execution
- allowing models to rewrite governance policy
- using model confidence as a substitute for qualified human authority
- routing to the newest model merely because it is new
- claiming superiority before controlled evidence exists

## Strategic test

Future post-v1 proposals should be challenged with the following question:

> **Does this make TEO materially better at governing and allocating intelligence, or are we merely reproducing functionality that belongs more naturally to the execution substrate?**

If the latter, prefer interoperability over duplication unless TEO requires the capability to preserve a governance invariant.

## Long-term target behavior

A mature TEO should eventually be able to reason along these lines:

```text
For this task class, specialist, risk tier, capability set, and budget:

Configuration X has the strongest verified quality-to-cost profile under current evidence.
Configuration Y has marginally higher quality but materially higher cost and latency.
The current risk tier does not justify the marginal expenditure.
Select X and retain independent verification.
```

And for a consequential task:

```text
Historical evidence shows that the economical route has an unacceptable failure rate at this effective-risk tier.
Select the higher-capability implementation.
Require independent provider-diverse verification.
Require qualified-human approval where policy mandates it.
```

That is the intended destination:

> **TEO should not merely orchestrate agents. It should govern the allocation of intelligence.**

## Relationship to v1.0.0

This roadmap does not alter the `v1.0.0` release contract or its immutable historical tag.

The existing v1 control plane already provides important prerequisites for this trajectory, including risk floors, capability-aware eligibility, reasoning-effort routing, provider-diverse fallback, independent verification, failure-aware recovery, telemetry, calibration instrumentation, model-freshness governance, and evidence/freshness controls.

Route-outcome learning and broader runtime integration remain post-v1 evolution areas. They should advance only when their evidence and governance foundations are strong enough to preserve existing invariants.

## Research sources reviewed

The competitive framing recorded here was checked against current first-party documentation on 2026-08-10:

1. LangChain, LangGraph persistence and human-in-the-loop documentation: https://docs.langchain.com/oss/python/langgraph/persistence and https://docs.langchain.com/oss/python/langchain/human-in-the-loop
2. Microsoft, Agent Framework workflows and orchestration documentation: https://learn.microsoft.com/en-us/agent-framework/workflows/ and https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/
3. OpenAI, Agents SDK agent, handoff, and guardrail documentation: https://openai.github.io/openai-agents-python/agents/ , https://openai.github.io/openai-agents-python/handoffs/ , and https://openai.github.io/openai-agents-python/guardrails/
4. CrewAI documentation for agents, crews, flows, state, memory, guardrails, observability, and deployment: https://docs.crewai.com/

These references establish the comparative execution capabilities observed at the time of research. They do not create permanent claims about competitors. Future comparative work should refresh them before relying on this document for current-state assertions.
