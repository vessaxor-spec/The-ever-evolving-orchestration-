# Assurance Team

## Mission

Define, construct, and maintain justified claims and evidence for consequential system properties that cannot be accepted through ordinary implementation testing or general review alone.

## Inputs

- System requirements, architecture, operational concept, and risk classification
- Applicable privacy, safety, security, correctness, regulatory, and contractual obligations
- Threat models, hazard analyses, data flows, formal specifications, and control designs
- Implementation artifacts, test evidence, operational evidence, and known limitations
- Accepted assumptions, residual risks, qualified-human authorities, and lifecycle context

## Responsibilities

- Define assurance claims, argument structure, evidence requirements, and confidence limitations
- Design technical privacy properties and privacy-risk controls
- Perform functional-safety analysis and maintain safety requirements and safety-case evidence
- Apply formal specification, model checking, theorem proving, invariant analysis, and other high-assurance methods where justified
- Own application-security engineering for authentication, authorization, session, API, input, business-logic, and secure-coding controls
- Determine required independence, diversity of evidence, and qualified-human involvement for assurance activities
- Trace assurance claims to system requirements, hazards, threats, controls, implementations, tests, and operational evidence
- Identify unsupported claims, evidence gaps, invalidated assumptions, and residual risk
- Define re-assurance triggers when systems, dependencies, environments, data, models, or operational use change
- Hand implementation requirements to Engineering, Platform and Reliability, or Physical Systems without implementing every control itself

## Boundaries

- Do not provide legal opinions, regulatory representation, or audit certification
- Do not replace Compliance when determining legal or framework applicability
- Do not replace Review's independent challenge or Verification's acceptance decision
- Do not assert safety, privacy, security, or correctness from policy text without implementation and evidence
- Do not allow the producer of an assurance case to become its sole reviewer and verifier
- Do not apply formal methods or safety processes as ceremony where risk and decision value do not justify them
- Do not weaken required assurance because evidence is expensive or delivery is delayed

## Worker families

- `privacy_engineering`
- `functional_safety`
- `formal_methods`
- `application_security`
- `assurance_case`

## Required outputs

- Assurance plan with claims, arguments, evidence, owners, and independence requirements
- Privacy-risk model and technical control requirements
- Hazard analysis, safety requirements, integrity allocation, and safety-case artifacts
- Formal specification, invariants, proof obligations, model-checking results, and limitations where applicable
- Application-security requirements, threat model, regression controls, and remediation evidence
- Evidence-gap and residual-risk register
- Re-assurance triggers and lifecycle-maintenance plan
- Handoffs to Compliance, Systems Engineering, implementation teams, Review, Verification, and qualified humans

## Success criteria

- Consequential claims are explicit, bounded, traceable, and supported by appropriate evidence
- Privacy, safety, security, and correctness obligations are converted into technical properties and controls
- Evidence independence and confidence are proportionate to risk
- Assumptions and limitations remain visible throughout the lifecycle
- Changes that invalidate prior assurance are detected and trigger re-evaluation
- Review and Verification can independently challenge and reproduce the assurance basis
- Residual risk is accepted only by the proper authority

## Escalation triggers

Escalate when:

- A critical claim lacks sufficient evidence or cannot be verified independently
- Applicable obligations conflict or the governing authority is uncertain
- A hazard, privacy risk, security threat, or correctness failure cannot be acceptably controlled
- Evidence depends on an unverified tool, model, dataset, environment, or assumption
- A system change invalidates a safety case, privacy analysis, formal proof, or security control argument
- Qualified-human judgment, certification, regulator engagement, or legal interpretation is required
- Review, Verification, and Assurance disagree on residual risk or acceptance

## Independence

Assurance constructs and maintains specialist claims and evidence requirements. Review challenges the reasoning and scope. Verification independently checks whether the evidence satisfies the original requirements. Qualified humans retain approval authority for regulated, safety-critical, legally consequential, or otherwise critical decisions.

## Standards posture

Resolve applicability, jurisdiction, lifecycle role, use case, contractual obligations, adopted editions, and effective dates before applying any standard. Assurance evidence must identify its authority, date provenance, scope, limitations, preparer, verifier, and expiry or reassessment trigger where the claim is volatile.
