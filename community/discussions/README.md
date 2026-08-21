# Discussions

TEO uses GitHub Discussions for public exploration before work becomes a scoped repository change.

## Boundary

- **Discussions**: questions, early proposals, research, alternatives, demonstrations, and unresolved design topics.
- **Issues**: reproducible defects, accepted and scoped work, or concrete implementation/documentation tasks.
- **Pull requests**: reviewable repository changes with evidence appropriate to the change.
- **`research/`**: retained research artifacts once findings need a durable canonical repository record.

A discussion does not create routing, runtime, governance, provider/model, specialist, live-execution, or approval authority. Evidence and review still govern material changes.

## Category configuration

The repository Discussion settings should use the following categories. The slug matters because GitHub binds a discussion form to a category by matching the form filename under `.github/DISCUSSION_TEMPLATE/` to that category slug.

| Category | Format | Slug | Purpose | Structured form |
|---|---|---|---|---|
| 📣 Announcements | Announcement | `announcements` | Releases, milestones, major project or governance updates from maintainers | No |
| 💡 Ideas | Open-ended | `ideas` | Early proposals and possible improvements before scope is accepted | `ideas.yml` |
| 🙏 Q&A | Question and answer | `q-a` | Questions about architecture, routing, governance, specialists, implementation, or contribution workflow | `q-a.yml` |
| 🔬 Research & Exploration | Open-ended | `research-exploration` | External research, projects, standards, benchmarks, model/provider evidence, and experiments that may inform TEO | `research-exploration.yml` |
| 🙌 Show and tell | Open-ended | `show-and-tell` | Implementations, integrations, experiments, or demonstrations related to TEO | No |
| 💬 General | Open-ended | `general` | Relevant conversation that does not fit a more precise category | No |

Polls are intentionally not part of the initial TEO discussion structure. Add them only when community participation makes voting materially useful.

## Community progress steward

Discussion #191 is the standing public conversation for what people are working on with orchestration. TEO should participate in that conversation by stating its own current work before asking others to share theirs.

`.github/workflows/community-progress-steward.yml` provides that project-status participation. It is deliberately deterministic rather than an autonomous conversational bot:

- it runs only after `docs/stewardship/progress-tracker.md` changes on `main`, when the steward workflow itself changes, or when a maintainer explicitly dispatches it;
- it reads the canonical `## NOW` section and posts the current focus and next evidence gate to Discussion #191;
- every update links to the exact Progress Tracker revision and source commit;
- it hashes the full `## NOW` section and records that digest in a hidden comment marker so the same canonical state is not posted twice;
- it asks for concrete feedback, contrary evidence, failure cases, and challenges to TEO assumptions;
- it does not generate replies to community comments and does not create routing, runtime, governance, model/provider, specialist, live-execution, approval, issue, or implementation authority.

Incoming community comments remain subject to maintainer or Mission Control review before any substantive response or repository action. Automation should surface genuine project state, not manufacture activity.

## Discussion lifecycle

1. Start in the narrowest relevant Discussion category.
2. Separate observed evidence from inference, preference, or proposal.
3. Resolve questions in Q&A or record the material conclusion in the thread.
4. When a proposal becomes accepted and sufficiently scoped, create or link the corresponding Issue.
5. When research needs durable repository preservation, move the accepted evidence into the appropriate canonical `research/` location through normal review.
6. Implement changes through a Pull Request and verify them independently where consequence or policy requires it.

Do not use Discussions as a parallel issue tracker or as a second source of truth for current TEO state.

## Public-scope rules

Discussion content must not contain credentials, private prompts, proprietary processes, confidential benchmarks, employer-specific material, or identifying operational data. Prefer primary and current sources for time-sensitive technical claims, state uncertainty explicitly, and preserve contrary evidence when it changes the conclusion.

Participation is governed by [`CODE_OF_CONDUCT.md`](../../CODE_OF_CONDUCT.md). The repository's licensing and contribution boundary remains authoritative; public discussion does not grant reuse rights or permission to contribute code outside the current terms.
