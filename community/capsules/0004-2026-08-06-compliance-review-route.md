---
capsule_id: TEO-CAPSULE-0004
status: accepted
captured_at: 2026-08-06T07:07:00+02:00
snapshot_commit: 09e46863d481b673790f646099087133e06d1e9d
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0003
immutability: accepted capsules are never rewritten
---

# Capsule 0004: Compliance Becomes a Human-Gated Review Responsibility

This capsule records the state of **The Ever-Evolving Orchestration** after the dedicated `compliance` worker became part of the reference control plane.

It preserves the repository at commit [`09e46863d481b673790f646099087133e06d1e9d`](https://github.com/vessaxor-spec/The-ever-evolving-orchestration-/commit/09e46863d481b673790f646099087133e06d1e9d), captured on **6 August 2026 at 07:07 CEST**.

It references [TEO-CAPSULE-0003](0003-2026-08-06-user-research-route.md). Earlier capsules remain untouched.

## Why this moment was preserved

The specialist corpus already contained a critical-risk `compliance-auditor` role with deep protocols for:

- SOC 2 and ISO management systems
- privacy and regulated-data governance
- PCI DSS and HIPAA controls
- GDPR and CCPA applicability
- AI-system and agentic trust governance
- evidence, audit impact, remediation, and third-party risk

The reference control plane did not yet have a core worker matching that responsibility.

Without a dedicated worker, a compliance task could be mistaken for:

- security engineering
- broad research
- legal analysis
- documentation
- technical implementation
- ordinary semantic review

Those are related responsibilities, but none is equivalent to compliance assurance.

TEO therefore added a distinct Review Team route that determines what applies, what evidence exists, what is missing, what risk remains, and which accountable human must approve the outcome.

## Authoritative specialist preserved

The authoritative role remains:

```text
community/specialists/compliance-auditor.md
```

The role card was not shortened, generalized, or rewritten.

Its identity, methodologies, protocols, tools, safety boundaries, collaboration rules, outputs, examples, risk profile, and creator attribution remain authoritative.

The additive worker is:

```text
community/workers/compliance-worker.yaml
```

## Worker responsibility

The `compliance` worker owns:

- applicability and scope determination
- framework and control mapping
- design and operating-effectiveness review
- evidence inventory and gap analysis
- privacy and data-flow assessment
- AI and agentic-system governance review
- third-party risk review
- automation governance review
- audit-impact and risk triage
- remediation ownership and deadline definition
- privacy-artifact grounding
- board and audit-committee briefing

It does not implement controls or issue legal or certification opinions.

## Authority boundary

The worker explicitly prohibits:

- legal opinions or regulator representation
- certification or audit-opinion issuance
- technical control implementation
- approval without defined scope and evidence
- privacy artifacts that misrepresent actual data practices
- treating a framework label as proof of compliance
- asserting volatile obligations without current authority
- self-approval or self-verification
- sharing findings outside authorized channels
- regulated or high-consequence decisions without a qualified human owner

The worker can classify, challenge, map, and recommend. The accountable human retains authority.

## First-class route

The reference control plane now includes:

```text
compliance_review
```

The team route resolves to:

```text
Review Team -> compliance worker -> optional compliance-auditor specialist
```

The route is separate from `security_review`, `deep_research`, `documentation`, and future `legal` responsibility.

Representative deterministic triggers include:

- compliance audit or review
- SOC 2
- ISO 27001 or ISO 27701
- PCI DSS
- GDPR, CCPA, or HIPAA compliance
- privacy or data-protection impact assessment
- control mapping
- operating effectiveness
- audit evidence
- AI Act compliance
- agentic trust
- privacy policies grounded in data flows

## Provider-diverse implementation

The active route at this moment is:

| Responsibility | Implementation | Provider |
|---|---|---|
| Primary compliance reasoning | `claude-sonnet-5` | Anthropic |
| Routine fallback | `gpt-5.6-sol` | OpenAI |
| Independent verifier | `gemini-3.1-pro-preview` | Google |
| Executable technical verification | `gpt-5.6-terra` | OpenAI |
| Conditional escalation | `claude-opus-5` | Anthropic |

The primary, routine fallback, and default verifier use three provider families.

Opus is not an ordinary fallback. It is reserved for evidence-based escalation such as active regulatory violation, prohibited or high-risk AI use, critical control failure, material data exposure, or unresolved conflict between governing authorities.

## Critical-risk verification

Activating the `compliance-auditor` specialist elevates the task to `critical` risk.

The resulting verification contract requires:

- independent multi-agent review
- executable verification where evidence allows
- qualified human approval
- an audit trace
- rollback or remediation planning

The route cannot produce an accepted consequential compliance outcome through one model acting as planner, analyst, reviewer, and approver.

## Evidence doctrine

The worker requires traceability across:

- jurisdiction, entity, legal role, system, and use case
- current law, regulator guidance, standard, or contract
- framework and version
- control objective and implementation
- design evidence versus operating evidence
- exceptions, contradictions, and compensating controls
- finding severity and audit impact
- residual risk
- owner, deadline, and approval path

The latest publication is not automatically the governing requirement. Applicability remains jurisdiction-, role-, contract-, use-case-, transition-, and effective-date dependent.

## Conformance state

The repository gained:

- `policy/routing/review-routing.yaml`
- `reference/datasets/compliance-worker-conformance.yaml`
- `tests/test_compliance_worker.py`
- provider-fallback coverage for `compliance_review`
- deterministic classification coverage
- exact authority-boundary assertions
- critical-risk and human-approval assertions

The exact warning baseline removed only `compliance`. Every other unresolved binding remained visible.

The merge candidate passed:

- Python compilation
- the complete automated test suite
- JSON-schema parsing
- linked configuration validation
- the end-to-end reference-router example

## Known limitations

At this moment:

- the control plane selects and records compliance responsibility but does not access live audit systems or regulator portals
- provider adapters and evidence-collection integrations remain future work
- legal interpretation and formal certification remain outside the worker's authority
- current regulatory obligations still require live primary-authority verification
- executable verification depends on available repositories, configurations, logs, and evidence
- qualified human approval remains external to the reference runtime
- other critical specialist bindings, including legal, tax, lending, finance, and security advisory roles, remain unresolved

## Next horizon

The next worker should continue to be selected from the exact warning baseline by responsibility uniqueness, routing value, risk, and verification need.

The strongest future candidates include other high-consequence responsibilities that should not be silently absorbed by generic review or planning workers.

The runtime horizon remains provider adapters, live evidence retrieval, retry and circuit-breaking behavior, telemetry, qualified-human approval integration, and audit-grade execution records.

## Message to future stewards

Compliance is not a list of framework names.

It is a chain of applicability, control intent, implementation evidence, operating history, exceptions, residual risk, ownership, and approval.

Do not confuse:

- a policy with a functioning control
- a certification with universal compliance
- a security test with regulatory assurance
- a privacy notice with accurate data practice
- a model's confident answer with a legal obligation

Preserve the evidence chain and the human authority at its end.

---

**Compliance becomes trustworthy when every conclusion can show what applies, what proves it, what remains unresolved, and who is accountable for the decision.**
