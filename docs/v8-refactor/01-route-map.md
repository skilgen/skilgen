# PR-0 Route Map

Source inputs: `docs/PRD-v8.docx` sections 3.2, 3.3, and 4.1-4.6; `docs/v8-refactor/00-discovery.md`; current dashboard App Router files under `apps/dashboard/app/dashboard/`.

Disposition vocabulary:

- `kept`: route stays valid and keeps its purpose.
- `redirected-to-X`: route remains valid but should 301 to the v8 route once v7 is deprecated.
- `removed-with-redirect-to-X`: v7 surface is cut, but bookmarked URLs still redirect to the best v8 destination.
- `new`: v8 route to add behind `IA_V8`.

## v8 routes to add

| Route | Disposition | PRD citation | Notes |
| --- | --- | --- | --- |
| `/dashboard/activity` | new | PRD 3.2, 4.1 | v8 homepage; tabs are sub-routes. |
| `/dashboard/activity/live-feed` | new | PRD 4.1.1 | Default Activity tab; may redirect from `/dashboard/activity`. |
| `/dashboard/activity/sessions` | new | PRD 4.1.2 | Reuses session records. |
| `/dashboard/activity/replay` | new | PRD 4.1.3 | Session replay entry; detail pages can be added as needed. |
| `/dashboard/activity/heatmap` | new | PRD 4.1.4 | Reuses heatmap surface; future materialized view. |
| `/dashboard/policy` | new | PRD 3.2, 4.2 | Rules default tab. |
| `/dashboard/policy/rules` | new | PRD 4.2.1 | YAML policy rule library and CRUD. |
| `/dashboard/policy/violations` | new | PRD 4.2.2 | Red Flags move here. |
| `/dashboard/policy/approvals` | new | PRD 4.2.3 | Review/quarantine/approval queue. |
| `/dashboard/policy/quarantine` | new | PRD 4.2.4 | Skill quarantine workflow. |
| `/dashboard/audit` | kept | PRD 3.3, 4.3 | Promote v7 Audit to top-level v8 Audit. |
| `/dashboard/audit/event-log` | new | PRD 4.3.1 | Event log tab. |
| `/dashboard/audit/reports` | new | PRD 4.3.2 | Prebuilt compliance reports. |
| `/dashboard/audit/exports` | new | PRD 4.3.3 | CSV/JSON/SIEM/raw export management. |
| `/dashboard/audit/evidence-packages` | new | PRD 4.3.4 | Evidence bundle generation. |
| `/dashboard/skills` | kept | PRD 3.2, 3.3, 4.4 | Existing route becomes v8 Skills top-level. |
| `/dashboard/skills/registry` | new | PRD 4.4 | Registry tab. |
| `/dashboard/skills/score` | new | PRD 4.4 | Score tab for gaps/debt filters. |
| `/dashboard/skills/drift` | new | PRD 4.4 | Half-life/drift tab. |
| `/dashboard/skills/provenance` | new | PRD 4.4 | Dependency graph/provenance tab. |
| `/dashboard/skills/skillql` | new | PRD 4.4 | Power-user search tab. |
| `/dashboard/skills/repos` | new | PRD 4.4 | Repos and sources tab. |
| `/dashboard/insights` | new | PRD 3.2, 4.5 | Fleet KPIs default tab. |
| `/dashboard/insights/fleet-kpis` | new | PRD 4.5 | Analytics composition. |
| `/dashboard/insights/risky-agents` | new | PRD 4.5 | Agent scorecard/performance composition. |
| `/dashboard/insights/risky-repos` | new | PRD 4.5 | Knowledge risk composition. |
| `/dashboard/insights/coverage-sla` | new | PRD 4.5 | Coverage SLA tab. |
| `/dashboard/settings` | kept | PRD 3.2, 4.6 | Existing Settings remains top-level. |
| `/dashboard/settings/notifications` | new | PRD 3.3, 4.6 | Digest becomes a notification setting. |
| `/dashboard/settings/teams` | new | PRD 4.6 | Teams tab. |
| `/dashboard/settings/rbac` | new | PRD 4.6 | RBAC tab. |
| `/dashboard/settings/sso` | new | PRD 4.6 | SSO tab. |
| `/dashboard/settings/connectors` | new | PRD 4.6 | Connect Agent and sources move here. |
| `/dashboard/settings/admin-audit` | new | PRD 4.6 | Admin action audit tab. |
| `/dashboard/settings/billing` | kept | PRD 4.6 | Existing billing route remains valid. |

## Existing sidebar routes

| Existing route | v7 item (PRD §3.3 row) | Current renderer | v8 disposition | Target route | PRD citation |
| --- | --- | --- | --- | --- | --- |
| `/dashboard` | Overview | `apps/dashboard/app/dashboard/page.tsx` | redirected-to-X | `/dashboard/activity` when `IA_V8=true`; keep legacy when off | 3.2, 3.3, 4.1 |
| `/dashboard/repos` | Repos | `apps/dashboard/app/dashboard/repos/page.tsx` | redirected-to-X | `/dashboard/skills/repos` | 3.3, 4.4 |
| `/dashboard/skills` | Skills | `apps/dashboard/app/dashboard/skills/page.tsx` | kept | `/dashboard/skills` | 3.2, 3.3, 4.4 |
| `/dashboard/agent-prs` | PR Inbox | `apps/dashboard/app/dashboard/agent-prs/page.tsx` | redirected-to-X | `/dashboard/activity/live-feed` | 3.3, 4.1 |
| `/dashboard/review` | Review | `apps/dashboard/app/dashboard/review/page.tsx` | redirected-to-X | `/dashboard/policy/approvals` | 3.3, 4.2 |
| `/dashboard/agent-scorecard` | Agent Scorecard | `apps/dashboard/app/dashboard/agent-scorecard/page.tsx` | redirected-to-X | `/dashboard/insights/risky-agents` | 3.3, 4.5 |
| `/dashboard/ai-readiness` | AI Readiness | `apps/dashboard/app/dashboard/ai-readiness/page.tsx` | removed-with-redirect-to-X | `/dashboard/activity` | 3.3 |
| `/dashboard/connect` | Connect Agent | `apps/dashboard/app/dashboard/connect/page.tsx` | redirected-to-X | `/dashboard/settings/connectors` | 3.3, 4.6 |
| `/dashboard/settings` | Settings (not in PRD §3.3) | `apps/dashboard/app/dashboard/settings/page.tsx` | kept | `/dashboard/settings` | 3.2, 4.6 |
| `/dashboard/my-code-today` | My Code Today | `apps/dashboard/app/dashboard/my-code-today/page.tsx` | removed-with-redirect-to-X | `/dashboard/activity` | 3.3 |
| `/dashboard/leaderboard` | Leaderboard | `apps/dashboard/app/dashboard/leaderboard/page.tsx` | removed-with-redirect-to-X | `/dashboard/insights/risky-agents` | 3.3 |
| `/dashboard/analytics` | Analytics | `apps/dashboard/app/dashboard/analytics/page.tsx` | redirected-to-X | `/dashboard/insights/fleet-kpis` | 3.3, 4.5 |
| `/dashboard/eval` | Agent Performance | `apps/dashboard/app/dashboard/eval/page.tsx` | redirected-to-X | `/dashboard/insights/risky-agents` | 3.3, 4.5 |
| `/dashboard/heatmap` | Heatmap | `apps/dashboard/app/dashboard/heatmap/page.tsx` | redirected-to-X | `/dashboard/activity/heatmap` | 3.3, 4.1 |
| `/dashboard/intelligence` | Intelligence | `apps/dashboard/app/dashboard/intelligence/page.tsx` | removed-with-redirect-to-X | `/dashboard/insights/fleet-kpis` | 3.3 |
| `/dashboard/skillql` | SkillQL | `apps/dashboard/app/dashboard/skillql/page.tsx` | redirected-to-X | `/dashboard/skills/skillql` | 3.3, 4.4 |
| `/dashboard/eval/gaps` | Skill Gaps | `apps/dashboard/app/dashboard/eval/gaps/page.tsx` | redirected-to-X | `/dashboard/skills/score` | 3.3, 4.4 |
| `/dashboard/debt` | Skill Debt | `apps/dashboard/app/dashboard/debt/page.tsx` | redirected-to-X | `/dashboard/skills/score` | 3.3, 4.4 |
| `/dashboard/knowledge-risk` | Knowledge Risk | `apps/dashboard/app/dashboard/knowledge-risk/page.tsx` | redirected-to-X | `/dashboard/insights/risky-repos` | 3.3, 4.5 |
| `/dashboard/red-flags` | Red Flags | `apps/dashboard/app/dashboard/red-flags/page.tsx` | redirected-to-X | `/dashboard/policy/violations` | 3.3, 4.2 |
| `/dashboard/eval/ab-tests` | A/B Tests | `apps/dashboard/app/dashboard/eval/ab-tests/page.tsx` | removed-with-redirect-to-X | `/dashboard/insights/risky-agents` | 3.3 |
| `/dashboard/registry` | Registry | `apps/dashboard/app/dashboard/registry/page.tsx` | redirected-to-X | `/dashboard/skills/registry` | 3.3, 4.4 |
| `/dashboard/sessions` | Sessions | `apps/dashboard/app/dashboard/sessions/page.tsx` | redirected-to-X | `/dashboard/activity/sessions` | 3.3, 4.1 |
| `/dashboard/digest` | Digest | `apps/dashboard/app/dashboard/digest/page.tsx` | removed-with-redirect-to-X | `/dashboard/settings/notifications` | 3.3, 4.6 |
| `/dashboard/autopilot` | Autopilot | `apps/dashboard/app/dashboard/autopilot/page.tsx` | redirected-to-X | `/dashboard/policy/rules` | 3.3, 4.2 |
| `/dashboard/sources` | Sources | `apps/dashboard/app/dashboard/sources/page.tsx` | redirected-to-X | `/dashboard/skills/repos` | 3.3, 4.4 |
| `/dashboard/sla` | Coverage SLA | `apps/dashboard/app/dashboard/sla/page.tsx` | redirected-to-X | `/dashboard/insights/coverage-sla` | 3.3, 4.5 |
| `/dashboard/half-life` | Half-life | `apps/dashboard/app/dashboard/half-life/page.tsx` | redirected-to-X | `/dashboard/skills/drift` | 3.3, 4.4 |
| `/dashboard/registry/dependency-graph` | Dependency Graph | `apps/dashboard/app/dashboard/registry/dependency-graph/page.tsx` | redirected-to-X | `/dashboard/skills/provenance` | 3.3, 4.4 |
| `/dashboard/teams` | Teams | `apps/dashboard/app/dashboard/teams/page.tsx` | redirected-to-X | `/dashboard/settings/teams` | 3.3, 4.6 |
| `/dashboard/audit` | Audit | `apps/dashboard/app/dashboard/audit/page.tsx` | kept | `/dashboard/audit` | 3.3, 4.3 |
| `/dashboard/admin` | Admin (not in PRD §3.3) | `apps/dashboard/app/dashboard/admin/page.tsx` | kept outside primary IA until answered | `/dashboard/settings/admin-audit` or `/dashboard/audit` TBD | Open question |

## Existing non-sidebar dashboard routes

| Existing route | v7 item (PRD §3.3 row) | Current renderer | v8 disposition | Target route | PRD citation |
| --- | --- | --- | --- | --- | --- |
| `/dashboard/admin/logins` | Admin (not in PRD §3.3) | `apps/dashboard/app/dashboard/admin/logins/page.tsx` | kept outside primary IA until answered | TBD | Open question |
| `/dashboard/admin/orgs` | Admin (not in PRD §3.3) | `apps/dashboard/app/dashboard/admin/orgs/page.tsx` | kept outside primary IA until answered | TBD | Open question |
| `/dashboard/admin/orgs/{orgId}` | Admin (not in PRD §3.3) | `apps/dashboard/app/dashboard/admin/orgs/[orgId]/page.tsx` | kept outside primary IA until answered | TBD | Open question |
| `/dashboard/admin/users` | Admin (not in PRD §3.3) | `apps/dashboard/app/dashboard/admin/users/page.tsx` | kept outside primary IA until answered | TBD | Open question |
| `/dashboard/connect/agent-run-spec` | Connect Agent | `apps/dashboard/app/dashboard/connect/agent-run-spec/page.tsx` | redirected-to-X | `/dashboard/settings/connectors/agent-run-spec` | 3.3, 4.6 |
| `/dashboard/memory` | AI Readiness | `apps/dashboard/app/dashboard/memory/page.tsx` | removed-with-redirect-to-X | `/dashboard/activity` | 3.3 |
| `/dashboard/onboarding` | Connect Agent | `apps/dashboard/app/dashboard/onboarding/page.tsx` | redirected-to-X | `/dashboard/settings/connectors` | 3.3, 4.6 |
| `/dashboard/registry/{registryId}` | Registry | `apps/dashboard/app/dashboard/registry/[registryId]/page.tsx` | redirected-to-X | `/dashboard/skills/registry/{registryId}` | 3.3, 4.4 |
| `/dashboard/repos/{repoId}` | Repos | `apps/dashboard/app/dashboard/repos/[repoId]/page.tsx` | redirected-to-X | `/dashboard/skills/repos/{repoId}` | 3.3, 4.4 |
| `/dashboard/repos/{repoId}/time-machine` | Dependency Graph | `apps/dashboard/app/dashboard/repos/[repoId]/time-machine/page.tsx` | redirected-to-X | `/dashboard/skills/provenance` | 3.3, 4.4 |
| `/dashboard/repos/{repoId}/skills/{skillId}` | Registry | `apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/page.tsx` | redirected-to-X | `/dashboard/skills/registry/{skillId}` | 3.3, 4.4 |
| `/dashboard/repos/{repoId}/skills/{skillId}/time-machine` | Dependency Graph | `apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/time-machine/page.tsx` | redirected-to-X | `/dashboard/skills/provenance` | 3.3, 4.4 |
| `/dashboard/repos/{repoId}/skills/{skillId}/versions/{versionId}` | Registry | `apps/dashboard/app/dashboard/repos/[repoId]/skills/[skillId]/versions/[versionId]/page.tsx` | redirected-to-X | `/dashboard/skills/registry/{skillId}/versions/{versionId}` | 3.3, 4.4 |
| `/dashboard/sessions/{id}` | Sessions | `apps/dashboard/app/dashboard/sessions/[id]/page.tsx` | redirected-to-X | `/dashboard/activity/sessions/{id}` | 3.3, 4.1 |
| `/dashboard/settings/billing` | Settings (not in PRD §3.3) | `apps/dashboard/app/dashboard/settings/billing/page.tsx` | kept | `/dashboard/settings/billing` | 3.2, 4.6 |
| `/dashboard/skills/guide` | Skills | `apps/dashboard/app/dashboard/skills/guide/page.tsx` | redirected-to-X | `/dashboard/skills/registry` | 3.3, 4.4 |
| `/dashboard/upgrade` | Settings (not in PRD §3.3) | `apps/dashboard/app/dashboard/upgrade/page.tsx` | kept | `/dashboard/upgrade` | 3.2, 4.6 |

## Redirect rule

Before PR-8, old routes must remain 200 when `IA_V8=false`. Once PR-8 is approved, add 301 redirects for all `redirected-to-X` and `removed-with-redirect-to-X` rows. Do not return 404 for any route listed above.
