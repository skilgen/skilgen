# AGENTS.md — Skillayer v8 Governance-Plane Refactor

> **This file is your mission brief.** Read it fully before any tool call. Re-read sections relevant to your current task before each major change.

*Version 8.0.1 — terminology aligned with prompt set; conventions doc pointer added in §7.*

---

## 1. Mission

Refactor the existing Skilgen / Skillayer codebase from the v7 information architecture (~30 sidebar items, "skill platform" framing) to the v8 information architecture (6 sidebar items, "coding-agent governance plane" framing) defined in `docs/PRD-v8.docx`.

The refactor must:

1. Preserve every piece of customer data, every existing API contract, and every URL that an authenticated customer might have bookmarked.
2. Ship the v8 surfaces (Activity, Policy, Audit, Skills, Insights, Settings) as **six parallel, independently-reviewable PRs** behind a single feature flag `IA_V8`.
3. Map every v7 sidebar item to its v8 disposition exactly as specified in PRD §3.3 — `cut`, `merge`, `move`, or `promote`. No items get invented or dropped beyond the PRD.
4. Leave the codebase in a state where flipping `IA_V8=true` for one tenant works, the legacy IA remains the default until PR-8 deprecation is approved by the user, and rolling back is a single env-var change.

## 2. Source of truth

- `docs/PRD-v8.docx` — the product requirements. **Read this first.** When this file disagrees with anything in the existing code, the PRD wins.
- `docs/PRD-v7.docx` (if present) — historical reference only. Do not implement from this.
- This `AGENTS.md` — operational rules.

If the PRD is missing or unreadable, **stop and report**. Do not proceed from memory.

## 3. Stack you will be working in

| Layer | Tech | Conventions |
|------|------|-------------|
| Dashboard | Next.js 15 App Router, TypeScript, Vercel | App Router routes under `apps/dashboard/app/`. Server components by default. Tailwind. |
| API | FastAPI, Python 3.12, Uvicorn | Service code under `apps/api/skillayer/`. SQLAlchemy 2.0 typed models. Alembic migrations. |
| DB | Neon Postgres (serverless) | Migrations only via Alembic. Never raw `ALTER` in code. |
| Auth | WorkOS (SSO/SAML) + org API keys (`sk-` prefix) | Auth middleware in `apps/api/skillayer/auth/`. Do not bypass. |
| Realtime | SSE + DB polling | Existing pattern at `GET /orgs/{id}/feed/stream`. Reuse it for Activity. |
| CLI | `skilgen` (Python, OSS) | Separate repo / package. **Do not modify** unless the PRD explicitly requires CLI changes. |
| Agent hook | `claude_code_hook.py` PostToolUse | Already in production. Treat as a stable ingest source. |

**If the actual stack on disk differs from this table, stop and report the discrepancy before proceeding.**

## 4. Operating principles (these are non-negotiable)

1. **Discover before you change.** Section 5 below is mandatory pre-flight. No file edits until pre-flight is complete.
2. **Plan before you code.** Section 6 is the migration-plan gate. The plan is its own commit and PR. The user reviews and approves before any surface PR opens.
3. **Feature-flag everything.** Every new route, component, and API endpoint added in this refactor must check `IA_V8`. Default off. Existing routes keep working when off.
4. **Redirect, don't delete.** When a v7 route is replaced, add a 301 redirect to the v8 equivalent. Never return 404 for a previously valid logged-in URL.
5. **Migrations are forward-only and reversible.** Every Alembic migration must have a tested `downgrade()`.
6. **No data loss, ever.** Renaming a table is a copy-then-cut migration across two releases, not a rename.
7. **One PR per surface.** Activity, Policy, Audit, Skills, Insights, Settings each get their own PR. Plus PR-0 (plan), PR-1 (IA shell + flag), PR-8 (deprecate v7 routes — opens last, after user approval).
8. **Scope your tooling.** When running tests or linters, scope to the package you changed (`pytest apps/api/skillayer/activity/`, not the full suite). Run the full suite only at PR finalization.
9. **Never modify auth, billing, or migration files outside the explicit scope of a PR.** If a change requires touching them, stop and ask.
10. **Never commit secrets, API keys, customer data, or `.env` files.** This is a hard ban regardless of how convenient it would be.

## 5. Pre-flight: discover the codebase

Run this before doing anything else. Output the findings into `docs/v8-refactor/00-discovery.md`. Do **not** edit application code in this phase.

1. Repository layout: produce a tree of the top three levels, annotated with what each folder contains.
2. Sidebar inventory: locate the current sidebar component (likely `apps/dashboard/components/Sidebar.tsx` or similar). List every item, the route it links to, and the file that renders that route.
3. v7→v8 mapping audit: for every item in PRD §3.3, confirm it exists in the codebase. Flag any item the PRD names that you cannot find, and any sidebar item that exists in code but is not named in the PRD.
4. API surface inventory: list every endpoint under `apps/api/skillayer/`, grouped by router. Identify which endpoints back which sidebar items.
5. DB schema inventory: list every table, with row counts where possible. Flag tables whose names match v7 concepts (e.g. `ai_readiness_*`, `leaderboard_*`) that the PRD says to cut — these need migration plans, not deletion.
6. Existing feature flags: list every flag in use today, the mechanism (env var, LaunchDarkly, internal table), and current values per environment.
7. Test coverage: report % coverage per package and identify packages below 60% — these need extra caution.
8. Open PRs and recent migrations: list the last 30 days of merged PRs and the last 10 Alembic migrations, so we don't conflict with in-flight work.

End the discovery doc with a "**Risks I flagged**" section listing anything you found that the PRD assumes but the code doesn't support, or anything that looks dangerous to refactor.

**Stop after pre-flight. Wait for user approval before opening PR-0.**

## 6. PR-0: migration plan (the gate)

Branch: `v8/00-migration-plan`. Adds `docs/v8-refactor/` only. No app code changes.

Produce these documents:

- `01-route-map.md` — every existing route → its v8 disposition (kept / redirected-to-X / removed-with-redirect-to-X / new). Cite the PRD section that justifies each.
- `02-component-map.md` — every existing top-level page component → its v8 disposition. Note which components are reused, renamed, decomposed, or replaced.
- `03-api-map.md` — every existing endpoint → its v8 disposition. New endpoints needed for v8 are listed with proposed signatures, not implementations.
- `04-data-map.md` — every table → its v8 disposition. Migrations needed are listed by name and direction; SQL is not yet written.
- `05-flag-rollout.md` — how `IA_V8` is read, where it is checked, the per-tenant override mechanism, the rollback plan.
- `06-pr-sequence.md` — the exact PR plan: PR-1 IA shell, PR-2 Activity, PR-3 Policy, PR-4 Audit, PR-5 Skills, PR-6 Insights, PR-7 Settings, PR-8 v7 deprecation. For each, list scope, dependencies, files touched (paths only, not diffs), and the success criteria from §10 below.
- `07-open-questions.md` — anything the PRD left ambiguous that you need answered before PR-2+ can land.

Open PR-0 with the description "v8 migration plan — review before any code changes" and **wait**.

## 7. PR-1: IA shell and feature flag

Branch: `v8/01-ia-shell`. Depends on PR-0 approval.

Scope:

- Add `IA_V8` flag plumbing (env var + per-tenant override row in `tenants` table — Alembic migration with downgrade).
- Add the new sidebar component (`SidebarV8.tsx`) with the six items: Activity, Policy, Audit, Skills, Insights, Settings. Each links to a placeholder page that renders "Coming soon — v8 surface".
- Wire the existing layout to render `SidebarV8` when `IA_V8=true` for the current tenant, otherwise the existing sidebar.
- No logic changes. No deletions. No redirects yet.
- Ship a Playwright smoke test: with flag on, every v8 nav item renders its placeholder page; with flag off, the v7 sidebar is unchanged.

This PR must be mergeable to main with the flag defaulted to off, and have zero observable effect for existing users.

**After this PR merges:** the conventions established here (route group naming, flag-helper signatures, sidebar component contract, file paths under `apps/api/skillayer/v8/` and `apps/dashboard/app/(v8)/`) are documented in `docs/v8-refactor/conventions.md`. Every subsequent agent (PR-2 through PR-7) must read that file before starting, in addition to this AGENTS.md and the PRD.

## 8. PR-2 through PR-7: the six surfaces (parallelizable)

Each surface PR follows the same shape. Open them in parallel branches off `main` once PR-1 lands. Do not chain them off each other.

Branch naming: `v8/02-activity`, `v8/03-policy`, `v8/04-audit`, `v8/05-skills`, `v8/06-insights`, `v8/07-settings`.

For each surface:

1. Read PRD §4.X for that surface in full. Build only what §4.X specifies.
2. Add the routes under `apps/dashboard/app/(v8)/<surface>/` so they live in a route group flagged on `IA_V8`.
3. Add API endpoints under `apps/api/skillayer/v8/<surface>/`. Reuse existing models where the PRD's data shape matches. Add new SQLAlchemy models only where the PRD demands new entities.
4. Each tab specified in PRD §4.X is a sub-route, not a client-side toggle, so deep links work.
5. Tests required per surface: unit tests on new models, contract tests on new endpoints, one Playwright happy-path per tab. Aim 80%+ coverage on new code.
6. Update `docs/v8-refactor/06-pr-sequence.md` with the actual files changed once the PR opens, so future agents can audit drift between plan and execution.

Surface-specific notes (the PRD has full detail; these are reminders, not substitutes):

- **Activity** (PR-2): Live feed reuses the existing SSE feed at `/orgs/{id}/feed/stream`. Sessions reuses session records. Replay needs a new endpoint. Heatmap is a materialized view — Alembic migration required.
- **Policy** (PR-3): YAML DSL parser is a new module under `apps/api/skillayer/v8/policy/dsl/`. Decision verbs from PRD §4.2.1. Starter library lives in `apps/api/skillayer/v8/policy/starter_packs/` as YAML files committed to the repo.
- **Audit** (PR-4): Hash-chain implementation must be testable in isolation — put it under `apps/api/skillayer/v8/audit/chain.py` with property-based tests. Evidence-pack export is async (Celery / RQ — match what's already in use).
- **Skills** (PR-5): This is mostly relabel-and-move from v7. Registry, Score, Drift, Provenance, SkillQL, Repos already exist as separate v7 sidebar items. Their backing logic moves under `v8/skills/<tab>/`. **No algorithm changes** in this PR — that's a separate work stream.
- **Insights** (PR-6): Mostly composition over existing analytics endpoints. Risky-agents and Risky-repos rankings are new SQL views.
- **Settings** (PR-7): Largely a reorganization. RBAC scoping is the one new substantive piece — new `roles` and `role_bindings` tables if not already present.

## 9. PR-8: v7 deprecation (opens last, after user approval)

Branch: `v8/08-deprecate-v7`. Do not open until PR-2 through PR-7 are merged and the user has approved a deprecation date.

Scope:

- Replace the v7 sidebar component with `SidebarV8` unconditionally.
- Add 301 redirects for every v7 route to its v8 equivalent (per `01-route-map.md`).
- Mark v7-only API endpoints `@deprecated` with sunset dates in headers; do not remove yet.
- Add a banner to the dashboard for any tenant still on `IA_V8=false` warning of the deprecation timeline.
- Database tables backing cut surfaces (e.g. `ai_readiness_*`, `leaderboard_*`) are renamed with `_deprecated_v7_` prefix in this PR. Actual deletion is a follow-up PR after a 90-day cool-down.

## 10. Success criteria (per PR)

A PR is mergeable only when:

- [ ] All new routes 200 with `IA_V8=true`, all old routes 200 with `IA_V8=false`.
- [ ] No existing test fails. New tests cover at least 80% of new code.
- [ ] No new `any` types in TypeScript. No new untyped functions in Python.
- [ ] No new ESLint or Ruff errors. Existing warnings not increased.
- [ ] Alembic `upgrade` and `downgrade` both run cleanly against a copy of the staging DB.
- [ ] Playwright smoke tests pass on a preview deployment.
- [ ] PR description includes: scope, files touched, migration impact, rollback plan, screenshot of every new screen.
- [ ] No secret, API key, customer data, or `.env` content committed.

The whole refactor is "done" when:

- [ ] All eight PRs are merged.
- [ ] `IA_V8=true` is the default for all tenants.
- [ ] All 301 redirects from v7 routes are live and tested.
- [ ] PRD §3.3 disposition table is reflected exactly in the live product.
- [ ] The discovery doc (§5) has been re-run against the post-refactor codebase and confirms zero v7 sidebar items remain.

## 11. Anti-patterns (do not do these)

- Do not rewrite a surface from scratch when the PRD says "merge". Skills, Insights, and Settings are mostly relabel-and-reorganize — preserve the working code.
- Do not ship a single mega-PR. Reviewers cannot evaluate it.
- Do not modify `skilgen` (the OSS CLI) as part of this refactor.
- Do not change scoring algorithms, drift thresholds, or any analytical logic. PRD §4.4 explicitly says Skills work is relabel-only in this refactor.
- Do not introduce a new state-management library, UI framework, or ORM. Use what's there.
- Do not add a new background-job system. Reuse the existing async infrastructure.
- Do not "improve" things outside the explicit scope of the current PR, no matter how tempting. File a follow-up issue instead.
- Do not skip the discovery or plan gates. They are not optional.
- Do not delete v7 tables in PR-8. Rename only — deletion is a separate PR after cool-down.
- Do not mark a PR ready for review with failing CI, unresolved type errors, or TODOs introduced by the PR itself.

## 12. When to stop and ask

Stop and ask the user (do not proceed) if:

- Discovery (§5) reveals the actual stack differs from §3.
- Discovery reveals the codebase contains v7 surfaces the PRD doesn't mention, or omits surfaces the PRD assumes.
- A PR-0 mapping decision requires data loss, schema rename of a table with non-trivial row count, or modification of a billing-related table.
- Any work would touch `auth/`, `billing/`, or migrations from before this refactor began.
- Any third-party API contract change is implied (WorkOS, Vercel, Neon, the agent-hook protocol).
- The PRD and the existing implementation conflict in a way that isn't resolvable by re-reading PRD §11 (open questions).

Asking is cheap. Re-doing a botched refactor is not.

---

## 13. Quick reference card

| You're about to... | First check... |
|---|---|
| Edit any file | Have I completed §5 discovery? Is there an open PR-0? |
| Create a new route | Is it under `(v8)` route group? Does it gate on `IA_V8`? |
| Add a new endpoint | Is it under `apps/api/skillayer/v8/`? Is it documented in `03-api-map.md`? |
| Write a migration | Does it have a tested `downgrade()`? Does it touch only the tables in `04-data-map.md`? |
| Delete or rename anything | Have I read §11 anti-patterns and §9 deprecation rules? |
| Open a PR | Have I run §10 success criteria as a checklist in the PR description? |
| Run tests | Have I scoped to the package I changed? |
| Modify `auth/`, `billing/`, or `skilgen/` | **Stop. Ask.** |
| Start a parallel surface PR (PR-2..7) | Have I read `docs/v8-refactor/conventions.md` from PR-1, plus this file and the PRD? |

---

*v8.0.1 — Last updated when the prompt set was finalized. If you need to update this file as part of the refactor, do it in PR-0 only.*
