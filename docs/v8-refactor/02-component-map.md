# PR-0 Component Map

Source inputs: `docs/PRD-v8.docx` sections 3.2, 3.3, and 4.1-4.6; current top-level dashboard page components under `apps/dashboard/app/dashboard/`.

Disposition vocabulary:

- `reused`: component logic can be reused directly in a v8 route or tab.
- `renamed`: component should move/rename to match v8 naming but keep behavior.
- `decomposed`: large page should be split into tab-level or shared components before reuse.
- `replaced`: v7 page is cut or its product framing is no longer valid.

## Shell and navigation

| Component/file | Disposition | v8 destination | Notes |
| --- | --- | --- | --- |
| `apps/dashboard/app/dashboard/layout.tsx` | decomposed | `SidebarLegacy`, `SidebarV8`, shared dashboard shell | Sidebar arrays are inline today. PR-1 should extract without changing v7 behavior. |
| `apps/dashboard/src/components/dashboard-nav-link.tsx` | reused | shared legacy/v8 nav link | Active matching supports `/dashboard` and exact eval routes; may need tab route matching. |
| `apps/dashboard/app/dashboard/error.tsx` | reused | shared dashboard route error | No IA logic. |

## Existing top-level page components

| Existing page | Disposition | v8 location | PRD citation |
| --- | --- | --- | --- |
| `dashboard/page.tsx` | decomposed | Activity homepage plus Insights KPI cards | 3.3, 4.1, 4.5 |
| `dashboard/repos/page.tsx` | reused/renamed | Skills -> Repos tab | 3.3, 4.4 |
| `dashboard/skills/page.tsx` | decomposed | Skills top-level; Registry/Score/SkillQL entry points | 3.2, 4.4 |
| `dashboard/agent-prs/page.tsx` | reused/decomposed | Activity live feed PR filter | 3.3, 4.1 |
| `dashboard/review/page.tsx` | reused/decomposed | Policy -> Approvals | 3.3, 4.2 |
| `dashboard/agent-scorecard/page.tsx` | reused/renamed | Insights -> Risky agents | 3.3, 4.5 |
| `dashboard/ai-readiness/page.tsx` | replaced | None; redirect to Activity | 3.3 |
| `dashboard/connect/page.tsx` | reused/renamed | Settings -> Connectors | 3.3, 4.6 |
| `dashboard/settings/page.tsx` | decomposed | Settings tabs | 3.2, 4.6 |
| `dashboard/my-code-today/page.tsx` | replaced | None; selected pieces may inform Activity | 3.3 |
| `dashboard/leaderboard/page.tsx` | replaced | None; risk-agent summaries may reuse internals only if enterprise-safe | 3.3 |
| `dashboard/analytics/page.tsx` | decomposed | Insights -> Fleet KPIs | 3.3, 4.5 |
| `dashboard/eval/page.tsx` | decomposed | Insights -> Risky agents | 3.3, 4.5 |
| `dashboard/heatmap/page.tsx` | reused/renamed | Activity -> Heatmap | 3.3, 4.1 |
| `dashboard/intelligence/page.tsx` | replaced | None; any useful metrics move into Insights | 3.3 |
| `dashboard/skillql/page.tsx` | reused/renamed | Skills -> SkillQL | 3.3, 4.4 |
| `dashboard/eval/gaps/page.tsx` | reused/decomposed | Skills -> Score filter coverage | 3.3, 4.4 |
| `dashboard/debt/page.tsx` | reused/decomposed | Skills -> Score filters structure/freshness | 3.3, 4.4 |
| `dashboard/knowledge-risk/page.tsx` | reused/renamed | Insights -> Risky repos | 3.3, 4.5 |
| `dashboard/red-flags/page.tsx` | reused/renamed | Policy -> Violations | 3.3, 4.2 |
| `dashboard/eval/ab-tests/page.tsx` | replaced | None; keep legacy until PR-8 redirect | 3.3 |
| `dashboard/registry/page.tsx` | reused/renamed | Skills -> Registry | 3.3, 4.4 |
| `dashboard/sessions/page.tsx` | reused/renamed | Activity -> Sessions | 3.3, 4.1 |
| `dashboard/digest/page.tsx` | replaced | Settings notification controls | 3.3, 4.6 |
| `dashboard/autopilot/page.tsx` | reused/decomposed | Policy -> Rules auto-approval | 3.3, 4.2 |
| `dashboard/sources/page.tsx` | reused/decomposed | Skills -> Repos and Settings -> Connectors split | 3.3, 4.4, 4.6 |
| `dashboard/sla/page.tsx` | reused/renamed | Insights -> Coverage SLA | 3.3, 4.5 |
| `dashboard/half-life/page.tsx` | reused/renamed | Skills -> Drift | 3.3, 4.4 |
| `dashboard/registry/dependency-graph/page.tsx` | reused/renamed | Skills -> Provenance | 3.3, 4.4 |
| `dashboard/teams/page.tsx` | reused/renamed | Settings -> Teams | 3.3, 4.6 |
| `dashboard/audit/page.tsx` | reused/decomposed | Audit top-level and tabs | 3.3, 4.3 |
| `dashboard/admin/page.tsx` | reused outside six-item IA until answered | TBD | Not in PRD 3.3 |

## Existing nested page components

| Existing page | Disposition | v8 location |
| --- | --- | --- |
| `dashboard/admin/logins/page.tsx` | reused outside six-item IA until answered | TBD |
| `dashboard/admin/orgs/page.tsx` | reused outside six-item IA until answered | TBD |
| `dashboard/admin/orgs/[orgId]/page.tsx` | reused outside six-item IA until answered | TBD |
| `dashboard/admin/users/page.tsx` | reused outside six-item IA until answered | TBD |
| `dashboard/connect/agent-run-spec/page.tsx` | reused/renamed | Settings -> Connectors -> AgentRun spec |
| `dashboard/memory/page.tsx` | replaced | Already redirects to AI Readiness; v8 redirect should go to Activity |
| `dashboard/onboarding/page.tsx` | reused | Onboarding route outside primary IA |
| `dashboard/registry/[registryId]/page.tsx` | reused/renamed | Skills -> Registry detail |
| `dashboard/repos/[repoId]/page.tsx` | reused/decomposed | Skills -> Repos detail |
| `dashboard/repos/[repoId]/time-machine/page.tsx` | reused/renamed | Skills -> Provenance time-machine view |
| `dashboard/repos/[repoId]/skills/[skillId]/page.tsx` | reused/decomposed | Skills -> Registry/Score detail |
| `dashboard/repos/[repoId]/skills/[skillId]/time-machine/page.tsx` | reused/renamed | Skills -> Provenance time-machine view |
| `dashboard/repos/[repoId]/skills/[skillId]/versions/[versionId]/page.tsx` | reused/renamed | Skills -> Registry version detail |
| `dashboard/sessions/[id]/page.tsx` | reused/renamed | Activity -> Sessions detail |
| `dashboard/settings/billing/page.tsx` | reused | Settings -> Billing |
| `dashboard/skills/guide/page.tsx` | reused/renamed | Skills -> Registry guide |
| `dashboard/upgrade/page.tsx` | reused | Upgrade route outside primary IA |

## Component boundaries to establish in PR-1

- `apps/dashboard/components/SidebarLegacy.tsx`: created by extracting existing sidebar logic from `apps/dashboard/app/dashboard/layout.tsx` with no behavior change. This is an extraction, not a rewrite; the flag-off render tree must remain visually and functionally identical.
- `apps/dashboard/components/SidebarV8.tsx`: six top-level items only: Activity, Policy, Audit, Skills, Insights, Settings.
- `apps/dashboard/lib/flags.ts`: dashboard flag read helper and route helpers, backed by server-computed tenant flag state.
- `apps/dashboard/app/(v8)/...`: v8 route group, subject to final convention in PR-1.

No component should be deleted in PR-0 or PR-1.
