---
capsule_id: TEO-CAPSULE-0010
status: accepted
captured_at: 2026-08-17T21:58:55+02:00
snapshot_commit: f7ade2c1d2de6a8a4546f81c49b9268648d6ac7d
project: The Ever-Evolving Orchestration
steward: Sylvester Roxas
references:
  - TEO-CAPSULE-0009
immutability: accepted capsules are never rewritten
---

# Capsule 0010: Evidence Qualification and Post-v1 Stewardship

This capsule records TEO after a post-v1 stewardship transition: the regulated specialist evidence program moved from calendar-based waiting to executable qualification without weakening continuous monitoring, fail-closed evidence rules, independent verification requirements, or explicit expansion authority.

It preserves the repository at commit `f7ade2c1d2de6a8a4546f81c49b9268648d6ac7d`, captured on **17 August 2026**. It extends [TEO-CAPSULE-0009](0009-2026-08-11-evidence-becomes-authority.md). Earlier accepted capsules remain immutable.

## Why this moment was preserved

Capsule 0009 preserved the point where evidence became part of a governed authority chain across evaluation, cost attribution, shadow recommendation, qualified-human authority, staged activation, and recovery.

The next question was whether TEO could maintain evidence-backed freshness without allowing governance process to become a substitute for empirical proof.

The regulated specialist evidence pilot had already established source authority, expiry, independent ownership, fail-closed validation, refresh history, and scheduled source resolution. Its next expansion gate originally included a 30-day elapsed-time requirement.

That requirement was later challenged against repository truth.

The active pilot policy required a seven-day source-resolution cadence. The roadmap required demonstrated reliable behavior. Neither required that 30 calendar days themselves become evidence. The fixed waiting period existed only as a stewardship criterion.

TEO therefore replaced the elapsed-time blocker with a bounded executable stability qualification.

The important transition is:

```text
Calendar time as a proxy
  -> repeated clean execution
  -> independent repeatability
  -> fail-closed mutation resistance
  -> controlled authority-move handling
  -> external-network observation
  -> continuous scheduled drift monitoring
  -> explicit human-approved expansion decision
```

Time remains useful for detecting future drift.

Time no longer substitutes for qualification evidence.

This capsule preserves the point where TEO made that distinction executable.

## Current project state

TEO remains beyond the functional-v1 boundary.

Current identity at this snapshot:

- stable release: `v1.0.0`
- stable state: `reference_operational`
- development package: `teo-reference-router==1.0.1.dev0`
- 10 active organizational teams
- 84 workers
- 82 active preserved specialist role cards
- 4 dedicated Mission Control workers
- repository information architecture R1 through R5 complete
- regulated specialist evidence pilot complete against its current declared milestone
- evidence-governed live execution expansion remains the canonical `NOW` workstream

The current Progress Tracker was reconciled on 17 August 2026 and remains the canonical current-state record.

## The regulated evidence pilot is now stability-qualified

The bounded pilot remains six specialists:

- Legal Operations
- Tax Strategist
- Loan Officer Assistant
- Compliance Auditor
- Civil Engineer
- Embedded Engineer

The pilot completed two formal evidence-refresh cycles.

Refresh Cycle 2 also proved that authority maintenance must handle changes in source infrastructure rather than treating a previously valid URL as permanently authoritative.

The embedded-engineering ISO source had been machine-resolvable when originally recorded, but GitHub-hosted `urllib` requests to the original `www.iso.org` page later returned HTTP 403. The resolver failed closed as designed.

TEO did not respond by weakening the resolver, accepting 403 as success, spoofing browser behavior, or bypassing the authority check.

Instead, the evidence review found an official machine-resolvable ISO endpoint under `committee.iso.org` for the same ISO/IEC 9899:2024 standard. The expected host and source URL changed while the claim statement, standard identity, verification ownership, and fail-closed resolver semantics remained intact.

That controlled authority move became evidence that the maintenance system could adapt without rewriting the underlying specialist capability.

## The 30-day gate was retired

The earlier refresh records correctly preserve a 30-day scheduled authority-resolution stability prerequisite because that was the stewardship rule in force when those records were created.

Those historical records were not rewritten.

Current policy now distinguishes qualification from monitoring:

- `calendar_wait_required: false`
- five complete clean authority-resolution replays
- three independently executed repeatability runs
- all governed mutation classes must fail closed
- a controlled authority-move path must succeed without weakening the claim
- external-network resolution evidence is required
- the seven-day source-resolution cadence remains continuous monitoring
- qualification cannot automatically authorize registry expansion
- the next risk-tier batch requires explicit approval and a separate reviewed change

This is evidence density instead of calendar delay.

It is not less governance.

It is governance tied more directly to observable behavior.

## Practical qualification, not theoretical qualification

The stability gate was exercised as runnable behavior rather than documented only as a policy concept.

The qualification demonstrated:

- 7 declared consequential claims exercised
- 5 of 5 complete clean authority-resolution replays passed
- 3 independently executed repeatability runs produced the same normalized result
- 15 of 15 governed fail-closed mutation classes were killed
- controlled authority-move handling passed
- external-network observation resolved 7 of 7 declared authorities
- qualification remained unable to auto-authorize expansion

The mutation program covered the classes that could otherwise create false confidence in the evidence layer, including authority identity, expected host, source availability, expiry, malformed or missing evidence, ownership and independence requirements, scope integrity, refresh-history integrity, registry binding, and forged expansion state.

A weakness was found during implementation review: an early repository implementation calculated repeatability by hashing one normalized replay object three times instead of independently executing the resolution path three times.

That was rejected as insufficient evidence.

The implementation was corrected so repeatability performs three separate executions. A targeted mutation then injected a failure only into the second repeatability run and qualification was required to fail.

This matters because a green test is useful only when the test can detect the failure mode it claims to govern.

## Codex placeholder topology was explicitly bounded

The practical sandbox exercise needed multiple reasoning roles even though all intended provider lanes were not available in the execution environment.

For the purpose of qualification testing only, Codex profiles were used as placeholders:

- GPT-5.6 Terra at medium reasoning for primary qualification execution
- GPT-5.6 Luna at medium reasoning for replay and mutation execution
- GPT-5.6 Sol at xhigh reasoning for the strongest review lane

This substitution exercised orchestration shape and reasoning-role separation.

It did **not** prove provider diversity.

It did **not** change production routing.

It did **not** satisfy a provider-diverse verification requirement merely because different Codex profiles were used.

TEO now states this boundary explicitly in current-facing documentation: test-only one-provider or Codex placeholder lanes must never be described as provider-diverse verification.

The distinction is important because model-role diversity and provider independence are different properties.

## Continuous monitoring remains mandatory

Retiring the 30-day waiting period did not retire longitudinal monitoring.

The evidence pilot still requires scheduled authority resolution on a seven-day cadence.

That schedule exists to detect future drift such as:

- source disappearance
- authority relocation
- unexpected host changes
- stale evidence
- expiry
- applicability drift
- conflicting authoritative guidance
- broken ownership or verification bindings

A real failed observation still fails closed and must be remediated.

The policy change only removed the idea that 30 uneventful calendar days, by themselves, were stronger evidence than repeatable execution and adversarial qualification.

## Qualification is not expansion authority

The current six-card pilot is complete against its declared maintainability milestone.

That does not mean the entire regulated-specialist registry is approved.

The qualification contract deliberately separates:

```text
Can this pilot be maintained reliably?
```

from:

```text
Should another risk-tier batch be admitted?
```

The first question is now answered with executable evidence.

The second remains a governance decision.

No next batch is automatically approved.

No new specialist is automatically admitted.

No live execution scope is widened.

No effective-risk requirement is lowered.

A later expansion requires explicit approval and a separate bounded reviewed change.

## Host Integration research remains non-normative

Since Capsule 0009, TEO also accumulated deeper Host Integration research and adversarial validation.

The research now covers multiple provider-independent slices including bounded specialist projection, dispatch provenance, adapter self-expansion resistance, third-party adapter trust, restrictive host and TEO authority intersection, execution-envelope integrity, verifier-context independence, artifact/change-set stale-PASS resistance, process-lifetime cross-process authority/replay resistance, runtime-wired authority-surface reconciliation, recursion resistance, exact local freshness binding, portfolio/task-admission separation, and integrated Fresh-AI assimilation/conformance research.

That research remains non-normative.

It does not create live execution authority.

It does not become part of routing merely because a research harness passes.

The Fresh-AI trial is especially important because TEO preserved a negative result rather than promoting partial success into a stronger claim.

Fresh-session, no-reminder routing continuity was observed.

Full end-to-end assimilation was not proven because the observed executor and verifier identities did not match the implementations selected by TEO. The validator was hardened so research simulation can report only `routing_continuity_only` unless selected-versus-observed executor and verifier identity plus digest binding are authenticated.

The lesson is consistent with the evidence qualification program:

> A system should claim only the property its evidence actually demonstrates.

## Live execution authority did not widen

The accepted live runtime boundary remains intentionally narrow.

Current accepted live scope:

- task class: `high_volume_simple`
- effective risk: low or medium only
- guarded provider execution
- provider-diverse fallback
- fresh-verifier rotation
- bounded transient retry
- circuit-state protection
- content-free telemetry
- evidence-bearing finalization

The `documentation` task class remains a staged candidate only.

Its replay harness and operator path are implemented and validated, but empirical provider-backed controlled replay evidence remains pending because the required provider access has not been supplied to that evidence path.

That blocker remains an execution-boundary condition.

It does not justify changing the selected route.

It does not convert credentials into a model-fitness signal.

High and critical live execution remain unauthorized.

## Current validation state

At this snapshot, the canonical Progress Tracker records the current validated scale as:

- 967 automated tests passed
- 551 tracked-file layout checks passed
- 41 JSON Schemas parsed
- regulated specialist evidence validation passed
- linked configuration valid with zero issues
- provider-diverse artifact-bound end-to-end reference lifecycle passed
- current validation baseline established by CI #784

The documentation-reconciliation change that produced this snapshot also passed final exact-head PR CI #787 before merge.

The merge commit preserved by this capsule is `f7ade2c1d2de6a8a4546f81c49b9268648d6ac7d`.

## Documentation truth was reconciled with policy truth

After the qualification implementation merged, current-facing documentation was swept for stale references to the former elapsed-time gate and pre-qualification status.

The reconciliation updated:

- the root README
- AI instructions
- changelog
- specialist roster README
- regulated-evidence methodology
- specialist-freshness guidance
- validation-history index
- release readiness documentation
- stewardship index and roadmap
- canonical Progress Tracker
- reference implementation READMEs
- documentation-truth regression coverage

Dated historical records were intentionally excluded from rewriting.

The immutable `v1.0.0` release contract was also left untouched.

This preserves a core repository rule:

> Current truth should be current. Historical truth should remain historical.

## What did not change

The transition preserved the architecture and governance principles established by earlier capsules.

The following remain true:

- the model is not the architecture
- responsibility resolves before implementation
- Team -> Worker -> optional Specialist -> Capability -> Implementation remains the durable ordering
- Mission Control remains the top-level orchestration and governance layer
- effective risk cannot be lowered for convenience
- provider access remains outside model-fitness routing
- fallback and verification remain separate responsibilities
- provider diversity cannot be simulated by renaming lanes within one provider
- preview models require explicit acceptance
- stale or unavailable consequential evidence fails closed
- authoritative conflicts escalate rather than being averaged away
- evidence may inform a decision but cannot self-write authority
- qualification does not create expansion authority
- human gates cannot be satisfied by a model pretending to be human authority
- recovery cannot silently widen task authority
- research results do not become normative architecture without a reviewed promotion step
- a successful execution call is not automatically a completed evidence-bearing outcome

## Current stewardship posture

TEO is no longer primarily proving that its architecture can exist.

It is proving that the architecture can be maintained, challenged, recalibrated, and extended without losing its boundaries.

Several workstreams are therefore intentionally not scored at 100%:

- Control Integrity remains at 90% because mutation depth and newly discovered failure modes remain an ongoing adversarial discipline.
- Verifier calibration evidence remains at 70% because additional repeatability, disagreement, adversarial, and route-specific evidence is still valuable.
- Live execution expansion remains at 65% because the staged `documentation` candidate still lacks empirical provider-backed controlled replay evidence.
- Distributed runtime hardening remains a future workstream.
- Licensing and contribution terms remain unresolved.

These percentages represent current declared milestones, not architectural incompleteness claims.

## Known remaining horizons

The following remain open after this snapshot:

- maintain the seven-day regulated-authority resolution schedule
- respond fail closed to any future source-resolution drift
- approve a specific next regulated risk-tier batch only when intentionally chosen
- provider-backed controlled `documentation` replay
- downstream evaluation and independent review before any documentation activation decision
- continued verifier-calibration evidence accumulation
- deeper control-integrity mutation testing
- authenticated full selected-executor/verifier Fresh-AI assimilation evidence if pursued
- distributed circuit and telemetry coordination
- execution-environment and recovery hardening where future evidence justifies promotion
- licensing and contribution terms

Optional independent-human calibration remains available as research, but it is not a release, routing, architecture, or evidence-maintenance blocker.

## Message to future stewards

Governance should make evidence harder to fake, not merely slower to obtain.

A calendar can tell you how long nothing visible happened.

It cannot prove that a control rejects a forged host, notices an expired claim, catches a broken history chain, survives an authority move, or fails when the second independent replay diverges.

Those properties must be exercised.

This milestone is therefore not about moving faster for its own sake.

It is about replacing a weak proxy with stronger evidence while preserving the monitoring that time uniquely provides.

Keep the distinction clear:

- qualification proves bounded behavior now
- scheduled monitoring looks for future drift
- approval decides whether authority should expand

Do not merge those three responsibilities into one shortcut.

TEO should evolve quickly when evidence is strong enough, and stop immediately when evidence fails.

That balance is the point.

> **Models evolve. Evidence must be exercised. Monitoring detects drift. Authority remains governed.**

The signal persists.

---

**Recorded under the stewardship of Sylvester Roxas.**
