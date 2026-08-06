# Community Conversations and Sponsorship

This document defines how The Ever-Evolving Orchestration should use GitHub community features without confusing open conversation, accepted work, and financial support.

## GitHub Discussions

GitHub Discussions should be enabled for this repository.

TEO is an evolving architecture and benefits from a public space for questions, proposals, interpretation, design exploration, and community feedback before work becomes an accepted implementation commitment.

Use Discussions for:

- architectural ideas that are not yet scoped work
- questions about teams, workers, specialists, routing, fallbacks, verification, and governance
- requests for interpretation or clarification
- broad design tradeoffs and alternatives
- community examples and implementation experiences
- announcements and project-state conversations

Use Issues for:

- reproducible defects
- accepted and bounded feature work
- documentation corrections with a clear outcome
- implementation tasks that need an owner and completion criteria
- tracked remediation and follow-up

Use Pull Requests for:

- concrete proposed changes to repository content
- executable implementation changes
- reviewed governance or policy changes
- accepted specialist, worker, route, registry, test, and documentation updates

A useful progression is:

```text
Discussion
  -> decision or accepted direction
  -> issue when tracked work is required
  -> pull request
  -> validation and merge
```

Discussion does not create architectural authority by itself. Accepted changes still follow TEO stewardship, preservation, verification, and branch-protection requirements.

## Initial discussion categories

The recommended initial categories are:

- **Announcements** — maintainer-created project updates
- **Q&A** — questions with an answer-marking workflow
- **Ideas** — open proposals and architectural exploration
- **General** — community conversation that does not fit a narrower category
- **Show and tell** — public examples of TEO-compatible implementations

Structured forms are stored under `.github/DISCUSSION_TEMPLATE/` for the `ideas` and `q-a` category slugs.

## Public-scope boundary

Discussions must not contain:

- credentials or secrets
- proprietary workflows
- employer-specific processes
- private prompts
- confidential benchmarks
- personal infrastructure details that create security exposure
- identifying operational data

Questions or examples that depend on protected material should be generalized before publication.

## Sponsorship

Repository sponsorship should remain disabled until all of the following are true:

1. an open-source license and contribution terms have been selected
2. the intended recipient and use of funds are clearly stated
3. the recipient has an approved GitHub Sponsors profile or another valid funding destination
4. tax, payout, and account requirements are complete
5. sponsorship does not imply governance authority, routing preference, endorsement, or control over accepted contributions

A sponsor button is configured through `.github/FUNDING.yml`. Do not add that file with an unverified account name, placeholder URL, or funding destination that has not been approved by the repository owner.

When sponsorship becomes appropriate, publish a short funding statement explaining that support sustains public maintenance and infrastructure but does not purchase architectural influence or preferential acceptance.

## Governance separation

Community participation, contribution acceptance, and sponsorship are separate relationships:

- a participant may contribute ideas without funding the project
- a sponsor receives no automatic maintainer or decision authority
- a contributor is evaluated through evidence, compatibility, and review rather than financial support
- project decisions remain governed by TEO's public stewardship and verification rules
