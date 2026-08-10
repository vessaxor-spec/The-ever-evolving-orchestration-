# Branch Cleanup Audit — 2026-08-10

## Scope

Issue #100 identified retained `agent/*` working branches as repository-hygiene debt after the post-v1 hard audit.

A fresh inventory on 2026-08-10 found **104** retained `agent/*` refs, up from the 102 recorded by the earlier audit. There were **no open pull requests** in the repository at review time.

The 104 refs reconcile as:

- **85** branches associated with merged pull-request history,
- **12** branches associated only with closed, superseded, or intentionally unmerged pull requests, and
- **7** historical intermediate branches without their own pull-request record.

The reviewed cleanup snapshot is fixed in `.github/workflows/branch-retention.yml`. The workflow must preserve any branch that unexpectedly backs an open pull request when the cleanup executes.

## Merged pull-request heads

| Branch | Accounted history |
|---|---|
| `agent/activate-principal-specialists` | PR #49 merged |
| `agent/add-analytics-worker` | PR #12 merged |
| `agent/add-assurance-specialists` | PR #45 merged |
| `agent/add-compliance-worker` | PR #33 merged |
| `agent/add-final-specialist-tranche` | PR #47 merged |
| `agent/add-first-time-capsule` | PR #14 merged |
| `agent/add-incident-response-route` | PR #8 merged |
| `agent/add-market-research-worker` | PR #10 merged |
| `agent/add-mission-control-routes` | PR #7 merged |
| `agent/add-mission-control-workers` | PR #6 merged |
| `agent/add-physical-systems-specialists` | PR #44 merged |
| `agent/add-platform-reliability-core` | PR #42 merged |
| `agent/add-platform-reliability-operations` | PR #43 merged |
| `agent/add-reference-ci` | PR #3 merged |
| `agent/add-research-worker` | PR #9 merged |
| `agent/add-routing-conformance` | PR #4 merged |
| `agent/add-specialist-freshness-capsule` | PR #30 merged |
| `agent/add-systems-engineering-specialist` | PR #41 merged |
| `agent/add-user-research-worker` | PR #31 merged |
| `agent/ai-mediated-discovery-final` | PR #25 merged |
| `agent/align-reference-version-v1` | PR #85 merged |
| `agent/anthropic-live-canary` | PR #53 merged |
| `agent/bounded-transient-retry` | PR #57 merged |
| `agent/capsule-0006-runtime-evidence` | PR #64 merged |
| `agent/capsule-0008-final` | PR #84 merged |
| `agent/centralize-roadmap-research` | PR #93 merged |
| `agent/control-integrity-hardening` | PR #73 merged |
| `agent/decouple-routing-from-provider-access-final` | PR #78 merged |
| `agent/define-v1-release-contract` | PR #86 merged |
| `agent/document-compliance-milestone` | PR #34 merged |
| `agent/document-main-protection` | PR #36 merged |
| `agent/document-principal-engineering-final` | PR #51 merged |
| `agent/document-user-research-milestone` | PR #32 merged |
| `agent/documentation-lifecycle-separation` | PR #96 merged |
| `agent/empirical-verifier-calibration` | PR #67 merged |
| `agent/enable-readme-reconciliation` | PR #50 merged |
| `agent/ensure-v1-release-publication` | PR #89 merged |
| `agent/fix-specialist-roster-audit` | PR #15 merged |
| `agent/guarded-canary-fallback` | PR #56 merged |
| `agent/live-independent-verification` | PR #62 merged |
| `agent/mission-control-routing-recalibration` | PR #82 merged |
| `agent/model-routing-audit-2026-08-07` | PR #54 merged |
| `agent/multi-provider-canary-parity` | PR #55 merged |
| `agent/native-operations-final` | PR #27 merged |
| `agent/persistent-runtime-telemetry` | PR #61 merged |
| `agent/phase-5-reference-router` | PR #2 merged |
| `agent/policy-topology` | PR #97 merged |
| `agent/post-v1-status-integrity-audit` | PR #99 merged |
| `agent/prepare-community-governance` | PR #37 merged |
| `agent/prepare-main-protection` | PR #35 merged |
| `agent/principal-engineering-teams` | PR #40 merged |
| `agent/principal-expansion-completeness-lock` | PR #48 merged |
| `agent/provider-adapter-contract` | PR #52 merged |
| `agent/provider-aware-fallbacks` | PR #11 merged |
| `agent/provider-directed-retry-timing` | PR #60 merged |
| `agent/provisional-evidence-workflow` | PR #77 merged |
| `agent/provisional-machine-panel-calibration` | PR #69 merged |
| `agent/publish-v1-release` | PR #87 merged |
| `agent/readme-capsule-0007` | PR #79 merged |
| `agent/readme-control-plane-truth` | PR #72 merged |
| `agent/readme-post-routing-recalibration` | PR #83 merged |
| `agent/readme-post-v1-audit-alignment` | PR #101 merged |
| `agent/reconcile-live-runtime-readme` | PR #59 merged |
| `agent/reconcile-model-freshness-governance` | PR #74 merged |
| `agent/reconcile-verification-runtime-readme` | PR #63 merged |
| `agent/refine-implementation-directions` | PR #80 merged; later PR #81 closed and superseded by PR #82 |
| `agent/regulated-evidence-pilot` | PR #39 merged |
| `agent/regulated-refresh-verified` | PR #23 merged |
| `agent/remove-v1-release-workflow` | PR #90 merged |
| `agent/repository-layout-constitution` | PR #94 merged |
| `agent/repository-wide-specialist-remediation` | PR #65 merged |
| `agent/research-analytics-security-final` | PR #29 merged |
| `agent/resolve-code-review-worker` | PR #5 merged |
| `agent/roadmap-intelligence-control-plane` | PR #92 merged |
| `agent/root-research-normalization` | PR #95 merged |
| `agent/specialist-freshness-foundation-final` | PR #20 merged |
| `agent/stateful-provider-circuit-breaker` | PR #58 merged |
| `agent/update-readme-current-state` | PR #13 merged |
| `agent/update-readme-machine-panel-evidence` | PR #70 merged |
| `agent/update-readme-operational-evidence` | PR #68 merged |
| `agent/update-readme-v1-release` | PR #91 merged |
| `agent/v1-operational-readiness` | PR #76 merged |
| `agent/verifier-calibration-evidence` | PR #66 merged |
| `agent/verify-v1-release-publication` | PR #88 merged |
| `agent/worker-implementation-topology` | PR #98 merged |

## Closed or superseded pull-request heads

| Branch | Accounted history |
|---|---|
| `agent/add-final-principal-specialists` | PR #46 closed; superseded by PR #47 |
| `agent/deepen-research-analytics-security` | PR #28 closed; superseded by PR #29 |
| `agent/model-freshness-governance` | PR #71 closed; superseded by PR #74 |
| `agent/refresh-ai-mediated-discovery` | PR #24 closed; superseded by PR #25 |
| `agent/refresh-native-operations` | PR #26 closed; superseded by PR #27 |
| `agent/refresh-regulated-specialists` | PR #21 closed; superseded by PR #23 |
| `agent/regulated-refresh-final` | PR #22 closed; superseded by PR #23 |
| `agent/specialist-freshness-foundation` | PR #16 closed; superseded by PR #20 |
| `agent/specialist-freshness-foundation-v2` | PR #17 closed; superseded by PR #20 |
| `agent/specialist-freshness-foundation-v3` | PR #18 closed; superseded by PR #20 |
| `agent/specialist-freshness-foundation-v4` | PR #19 closed; superseded by PR #20 |
| `agent/verify-main-ruleset` | PR #38 closed intentionally after successful ruleset-enforcement verification; none of its files needed to enter `main` |

## Historical intermediate refs without a dedicated pull request

| Branch | Verification and disposition |
|---|---|
| `agent/activate-systems-engineering-route` | GitHub comparison: 0 commits ahead of `main`, 51 behind. Fully contained in accepted history. |
| `agent/capsule-0008` | GitHub comparison: 0 ahead, 18 behind. Intermediate state superseded by final Capsule PR #84. |
| `agent/decouple-routing-from-provider-access` | GitHub comparison: 0 ahead, 23 behind. Intermediate provider-access work preceding final PR #78. |
| `agent/decouple-routing-from-provider-access-v2` | GitHub comparison: 0 ahead, 23 behind. Intermediate provider-access work preceding final PR #78. |
| `agent/decouple-routing-from-provider-access-v3` | GitHub comparison: 0 ahead, 23 behind. Intermediate provider-access work preceding final PR #78. |
| `agent/document-principal-engineering-activation` | Temporary reconciliation branch. It diverges from current `main`, but final accepted documentation and Capsule state were merged through PR #51, which explicitly removed the temporary migration workflow and script. No open PR remains. |
| `agent/specialist-constitutional-integration` | GitHub comparison: 0 ahead, 59 behind. Fully contained in accepted history. |

## Deletion decision

All 104 reviewed legacy refs are eligible for cleanup subject to one final runtime safety check: if any ref backs an open pull request when the workflow executes, that ref is preserved.

The deletion removes branch refs only. It does not alter protected `main`, release tags, GitHub Releases, accepted Capsules, merged pull-request records, or historical documents.

## Prevention

The permanent retention rule is documented in `docs/stewardship/branch-retention.md`.

After this cleanup, merged same-repository `agent/*` pull-request heads are deleted automatically by `.github/workflows/branch-retention.yml`. Closed but unmerged branches remain a deliberate maintainer decision because abandonment, supersession, recovery, and forensic retention cannot safely be inferred from merge state alone.

## Completion criterion

Issue #100 is complete only after:

1. this reviewed cleanup change passes required CI,
2. the pull request is merged,
3. the branch-retention workflow completes successfully,
4. a fresh GitHub branch inventory confirms that the 104 legacy refs and the cleanup branch itself are absent, and
5. `main`, release tags, Capsules, and accepted history remain unchanged except for the reviewed hygiene policy, workflow, tests, and audit record.
