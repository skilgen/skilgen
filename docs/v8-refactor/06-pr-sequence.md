# PR-0 PR Sequence

This sequence fixes the Phase A risks by turning them into reviewable, bounded PRs. No application code changes are included in PR-0.

## PR-1: IA shell and feature flag

Branch: `v8/01-ia-shell`  
Depends on: PR-0 approval

Scope:

- Establish the v8 API path convention as `apps/api/api/v8/<surface>/`.
- Add `IA_V8_DEFAULT` env default and per-tenant override at `orgs.settings.feature_flags.IA_V8`.
- Add `SidebarLegacy` and `SidebarV8`.
- Add placeholder v8 routes for Activity, Policy, Audit, Skills, Insights, Settings.
- Create `docs/v8-refactor/conventions.md` with:
  - v8 API path convention: `apps/api/api/v8/<surface>/`
  - v8 dashboard route convention: `apps/dashboard/app/(v8)/<surface>/`
  - `IA_V8` flag-helper signatures, server and client
  - Sidebar component contract
  - Tab-as-sub-route rule, no query-param tabs
  - Branch naming: `v8/0X-<surface>`
  - Commit message convention: Conventional Commits, scope `v8`

Files touched:

- `apps/dashboard/app/dashboard/layout.tsx`
- `apps/dashboard/components/SidebarLegacy.tsx`
- `apps/dashboard/components/SidebarV8.tsx`
- `apps/dashboard/app/(v8)/activity/page.tsx`
- `apps/dashboard/app/(v8)/policy/page.tsx`
- `apps/dashboard/app/(v8)/audit/page.tsx`
- `apps/dashboard/app/(v8)/skills/page.tsx`
- `apps/dashboard/app/(v8)/insights/page.tsx`
- `apps/dashboard/app/(v8)/settings/page.tsx`
- `apps/dashboard/lib/flags.ts`
- `apps/api/api/v8/flags.py`
- `apps/api/alembic/versions/...add_ia_v8_tenant_override.py`
- `docs/v8-refactor/conventions.md`
- Playwright smoke test path TBD

Success criteria reference:

- AGENTS section 10 plus PR-1-specific flag-on/flag-off sidebar tests.

## PR-2: Activity

Branch: `v8/02-activity`  
Depends on: PR-1 merge

Scope:

- Build Activity tabs: Live feed, Sessions, Replay, Heatmap.
- Reuse `GET /orgs/{id}/feed/stream`.
- Reuse existing sessions and replay records.
- Add heatmap view only if needed.

Files touched:

- `apps/dashboard/app/(v8)/activity/**`
- `apps/api/api/v8/activity/**`
- Existing reusable components from `apps/dashboard/app/dashboard/analytics/LiveFeed.tsx`, `sessions`, `heatmap`
- Optional Alembic migration for activity heatmap view
- Tests under `apps/api/tests` and dashboard E2E

Success criteria reference:

- PRD 4.1 and AGENTS section 10.

## PR-3: Policy

Branch: `v8/03-policy`  
Depends on: PR-1 merge

Scope:

- Build Policy tabs: Rules, Violations, Approvals, Quarantine.
- Reuse org policies, red flags, review, and autopilot logic.
- Add YAML DSL parser and starter packs only as PRD 4.2 requires.
- Extend policy decision verbs from existing `block/warn/log` to PRD 4.2.1 `allow/deny/require_approval/log_only/redact/route_to_dlp`; map existing rows `block→deny`, `warn→require_approval`, `log→log_only`, and deprecate the old names.

Files touched:

- `apps/dashboard/app/(v8)/policy/**`
- `apps/dashboard/e2e/policy-v8.spec.ts`
- `apps/dashboard/e2e/ia-v8.spec.ts`
- `apps/dashboard/lib/data.ts`
- `apps/api/api/index.py`
- `apps/api/api/v8/policy/**`
- `apps/api/api/v8/policy/dsl/**`
- `apps/api/api/v8/policy/starter_packs/**`
- `packages/db/models/org_policy.py`
- `apps/api/alembic/versions/20260505_0005_policy_verbs_dsl.py`
- `apps/api/tests/test_v8_policy.py`

Implementation notes:

- Existing policy services remain intact; v8 Policy wraps them and does not change `red_flags`.
- Migration creates `policy_violations_v8` as a query view over flagged policy decisions (`deny`, `require_approval`, `log_only`) with SLA timestamps.
- Settings RBAC middleware is not present on `v8/integration` yet, so Policy exposes a dependency interface that delegates to `apps.api.api.v8.settings.rbac.require_permission` when available and returns 501 for approval mutations until Settings lands.
- Quarantine uses `skill_registry_entries` disposition state (`tags`, `is_deprecated`, `deprecation_message`) and exposes only promote/retire decisions.

Success criteria reference:

- PRD 4.2 and AGENTS section 10.

## PR-4: Audit

Branch: `v8/04-audit`  
Depends on: PR-1 merge

Scope:

- Build Audit tabs: Event log, Reports, Exports, Evidence packages.
- Add hash-chain implementation in isolated module.
- Reuse existing audit events, manifests, and export endpoints.
- Evidence package export must use existing async infrastructure.

Files touched:

- `apps/dashboard/app/(v8)/audit/**`
- `apps/api/api/v8/audit/**`
- `apps/api/api/v8/audit/chain.py`
- Existing audit/manifest services
- Optional Alembic migration for hash chain/evidence package jobs
- Tests including property-based or equivalent chain invariants

Success criteria reference:

- PRD 4.3 and AGENTS section 10.

## PR-5: Skills

Branch: `v8/05-skills`  
Depends on: PR-1 merge

Scope:

- Build Skills tabs: Registry, Score, Drift, Provenance, SkillQL, Repos.
- Reuse Registry, Score/Gaps/Debt, Half-life, Dependency Graph, SkillQL, Repos, Sources.
- No algorithm changes.

Files touched:

- `apps/dashboard/app/(v8)/skills/**`
- `apps/api/api/v8/skills/**`
- Existing dashboard components from registry, debt, eval/gaps, half-life, skillql, repos, sources
- Existing API wrappers for skills, registry, repos, orgs skill endpoints
- Tests under `apps/api/tests` and dashboard E2E
- Actual PR-5 additions: `apps/api/api/v8/skills/router.py`, `apps/api/api/v8/skills/__init__.py`, `apps/dashboard/app/(v8)/skills/{layout,page}.tsx`, `apps/dashboard/app/(v8)/skills/{registry,score,drift,provenance,skillql,repos}/page.tsx`, `apps/api/alembic/versions/20260505_0001_add_repo_sensitivity_tier.py`, `docs/v8-refactor/skills/score-rubric.md`, `apps/api/tests/test_v8_skills.py`, `apps/dashboard/e2e/ia-v8.spec.ts`.
- Actual PR-5 updates: `packages/db/models/repo.py`, `apps/api/api/index.py`, `apps/dashboard/lib/data.ts`.

Success criteria reference:

- PRD 4.4 and AGENTS sections 10 and 11.

## PR-6: Insights

Branch: `v8/06-insights`  
Depends on: PR-1 merge

Scope:

- Build Insights tabs: Fleet KPIs, Risky agents, Risky repos, Coverage SLA.
- Compose existing analytics, agent scorecard, knowledge risk, runtime breakdown, SLA endpoints.
- Add risky-agent/repo views only if existing queries are insufficient.

Files touched:

- `apps/dashboard/app/(v8)/insights/**`
- `apps/api/api/v8/insights/**`
- Existing dashboard components from analytics, agent-scorecard, knowledge-risk, sla
- Optional Alembic migration for risky-agent/repo SQL views
- Tests under `apps/api/tests` and dashboard E2E

Success criteria reference:

- PRD 4.5 and AGENTS section 10.

## PR-7: Settings

Branch: `v8/07-settings`  
Depends on: PR-1 merge

Scope:

- Build Settings tabs: Teams, RBAC, SSO, Connectors, Admin action audit, Billing.
- Reuse Settings, Teams, Connect Agent, Sources, Billing, Slack/email/LLM config.
- Add RBAC tables only if no existing roles model supports the PRD.

Files touched:

- `apps/dashboard/app/(v8)/settings/**`
- `apps/api/api/v8/settings/**`
- Existing dashboard components from settings, teams, connect, sources, billing
- Optional Alembic migration for roles/role_bindings
- Tests under `apps/api/tests` and dashboard E2E

Success criteria reference:

- PRD 4.6 and AGENTS section 10.

## PR-8: v7 deprecation

Branch: `v8/08-deprecate-v7`  
Depends on: PR-2 through PR-7 merged and explicit user approval

Scope:

- Replace v7 sidebar with v8 sidebar unconditionally.
- Add 301 redirects from `01-route-map.md`.
- Add deprecation headers to v7-only endpoints.
- Add deprecation banner for tenants still off, if any.
- Rename v7-only cut tables with `_deprecated_v7_` prefix only; no deletion.

Files touched:

- Dashboard redirect/middleware paths TBD
- API deprecation header helpers and router decorators TBD
- Alembic migration for approved `_deprecated_v7_` table renames only
- `docs/v8-refactor/01-route-map.md` updates if implementation drift occurs

Success criteria reference:

- PRD 3.3, AGENTS sections 9 and 10.

## Risk controls across all PRs

- No changes to root `skilgen/` OSS CLI except stable hook references explicitly approved by user.
- No auth, billing, or old migration edits unless a PR explicitly scopes and asks.
- Every old route remains 200 while `IA_V8=false`.
- Every v8 route is gated by `IA_V8`.
- Any data migration with non-zero row counts requires staging/sanitized-clone verification before merge.
