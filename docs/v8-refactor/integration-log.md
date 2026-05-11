# v8 Integration Log

Branch: `v8/integration`  
Base: `origin/main` at `8b89630`  
Scope: PR-2 through PR-7 in one integration PR. PR-8 deprecation is out of scope.

## 2026-05-11 — Audit agent compliance evidence packages

- Backend: evidence packages now include `agent-compliance-summary.json`, manifest-level metadata-only retention, consolidated coding-agent compliance metrics, and explicit raw-content exclusion keys.
- Backend: agent compliance events written into evidence packages are sanitized so raw prompts, chat content, diffs, file content, and tool arguments are not exported.
- Frontend: `/audit/evidence-packages` now shows a migrated Skillayer workflow for selecting controls, queueing packages, checking included files, reviewing covered compliance metrics, and confirming excluded raw-content keys.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_audit_reports_exports.py apps/api/tests/test_v8_audit_router_units.py -q` -> `14 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
- UX screenshot gate:
  - Desktop and mobile proof captured with a local mock API after queueing a package:
    - `docs/v8-refactor/screenshots/automation-20260511/audit-agent-compliance-evidence-packages-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/audit-agent-compliance-evidence-packages-mobile.png`

## 2026-05-11 — Settings admin audit workflow

- Backend: `/v8/orgs/{org_id}/settings/admin-audit` now accepts actor, event type, resource type, severity, window, and limit filters.
- Backend: response now includes admin audit summary, severity counts, event-type mix, and resource coverage rollups for settings/member/API-key governance events.
- Frontend: `/settings/admin-audit` now provides filter controls, summary KPIs, event/resource rollups, severity badges, and responsive event rows in the migrated Skillayer Settings shell.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> `18 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
- UX screenshot gate:
  - Desktop and mobile proof captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/settings-admin-audit-workflow-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/settings-admin-audit-workflow-mobile.png`

## Subagent assignments

| Surface | Agent branch | Status | Notes |
| --- | --- | --- | --- |
| Activity | `v8/integration-activity` | Merged (`cf76b1b`) | Depends on Skills sensitivity tier migration for richer repo tier data; must handle missing tier gracefully. |
| Policy | `v8/integration-policy` | Merged (`247aadd`) | Settings RBAC is now present; approval mutations delegate through the RBAC dependency interface. |
| Audit | `v8/integration-audit` | Merged (`c8792b2`) | Hash chain and WORM root publication; no payloads to WORM. |
| Skills | `v8/integration-skills` | Merged (`1d2ca7f`) | Introduces `repos.sensitivity_tier`; no Skilgen Score algorithm changes. |
| Insights | `v8/integration-insights` | Merged (`d465d4b`) | Reads from existing analytics sources; no new analytics framework. |
| Settings | `v8/integration-settings` | Merged (`11cf218`) | Introduces RBAC tables/middleware; no WorkOS/auth/billing behavior changes. |

## Migration order

1. Skills: `repos.sensitivity_tier`, if needed.
2. Settings: RBAC tables/middleware.
3. Audit: audit hash-chain carrier.
4. Activity: heatmap view/indexes.
5. Policy: decision verbs / DSL metadata / quarantine state.
6. Insights: risky-agent/repo views.

Actual Alembic order after convergence:

1. `20260504_0001` -> `20260505_0001_add_repo_sensitivity_tier.py`
2. `20260505_0001` -> `20260505_0002_settings_rbac.py`
3. `20260505_0002` -> `20260505_0003_audit_hash_chain.py`
4. `20260505_0003` -> `20260505_0004_activity_heatmap_index.py`
5. `20260505_0004` -> `20260505_0005_policy_verbs_dsl.py`
6. `20260505_0005` -> `20260505_0006_v8_insights_risk_views.py`

Final required verification:

1. `alembic upgrade head` against a fresh test DB.
2. `alembic downgrade base`.
3. `alembic upgrade head`.
4. Repeat the sequence three times during Phase D.

## Conflicts resolved

- Settings merge after Skills:
  - `apps/api/api/index.py`: both branches registered new v8 routers. Resolution keeps both `v8_skills_router` and `v8_settings.router`.
  - `apps/dashboard/e2e/ia-v8.spec.ts`: Skills added real Skills tab coverage while Settings added real Settings coverage. Resolution keeps all six v8 surfaces and marks Skills/Settings as non-placeholder surfaces.
- Audit merge after Settings:
  - `apps/api/api/index.py`: Audit also registered a v8 router. Resolution keeps Audit, Skills, and Settings router registrations.
- Activity merge after Audit:
  - `apps/api/api/index.py`: Activity added another v8 router registration. Resolution keeps Activity, Audit, Skills, and Settings router registrations.
- Policy merge after Activity:
  - `apps/api/api/index.py`: Policy added another v8 router registration. Resolution keeps Activity, Audit, Policy, Skills, and Settings router registrations.
  - `apps/dashboard/e2e/ia-v8.spec.ts`: Policy added heading-aware v8 surface checks. Resolution keeps Skills and Settings real-surface checks and marks Activity, Policy, Audit, Skills, and Settings as non-placeholder after their merges.
  - `docs/v8-refactor/integration-log.md`: Policy branch had pre-merge status notes. Resolution keeps parent merge history and updates Policy to merged after Settings.
- Insights merge after Policy:
  - `apps/api/api/index.py`: Insights added another v8 router registration. Resolution keeps all six v8 surface router registrations.
  - `apps/dashboard/e2e/ia-v8.spec.ts`: Insights made the Insights top-level route real. Resolution marks all six v8 surfaces as non-placeholder.

## Test runs

- After Skills merge:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_skills.py apps/api/tests/test_v8_flags.py -q` -> `12 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- After Settings merge:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py apps/api/tests/test_v8_flags.py -q` -> `15 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- After Audit merge:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_audit_chain.py apps/api/tests/test_v8_audit_migration.py apps/api/tests/test_v8_audit_reports_exports.py apps/api/tests/test_v8_audit_router_units.py apps/api/tests/test_v8_flags.py -q` -> `23 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- After Activity merge:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_activity_view_model.py apps/api/tests/test_v8_flags.py -q` -> `21 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- After Policy merge:
  - Initial policy focused test failed because Policy expected Settings RBAC to be unavailable before convergence.
  - Resolution: updated Policy test expectation to available after Settings merge and aligned approval dependency with `policy.approvals.approve`.
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_policy.py apps/api/tests/test_v8_settings_rbac.py apps/api/tests/test_v8_flags.py -q` -> `24 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- After Insights merge:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py apps/api/tests/test_v8_flags.py -q` -> `14 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
- Migration order repair:
  - Initial convergence had parallel Alembic heads and duplicate `20260505_0002` revision ids.
  - Resolution rewired revisions into the required Skills -> Settings -> Audit -> Activity -> Policy -> Insights chain.
  - `cd apps/api && ../../../skilgen-upstream-work/.venv/bin/python -m alembic heads` -> single head `20260505_0006`.
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_audit_migration.py apps/api/tests/test_v8_policy.py apps/api/tests/test_v8_settings_rbac.py apps/api/tests/test_v8_insights.py -q` -> `34 passed`.
- Phase C fresh-DB migration sequence blocker:
  - Attempted `alembic upgrade head -> downgrade base -> upgrade head` with `DATABASE_URL=sqlite:////tmp/skilgen_v8_integration_migration.db`.
  - The run failed before reaching any v8 migration at historical migration `a4c2e3f91b65_add_stripe_fields_to_orgs.py` because SQLite cannot execute `ALTER TABLE orgs ALTER COLUMN plan_seat_limit DROP DEFAULT`.
  - Checked for a local Postgres runner: `psql`, `pg_isready`, `postgres`, `initdb`, and `pg_ctl` are unavailable. Docker is installed but the daemon is not running (`Cannot connect to the Docker daemon at unix:///var/run/docker.sock`).
  - Status: v8 migration graph is linear and targeted migration tests pass, but the required full fresh-DB migration sequence cannot be completed in this environment until a Postgres test DB is available.
- Phase C Postgres migration sequence:
  - Used the provided Neon Postgres database with a fresh temporary schema via `PGOPTIONS=-c search_path=<schema>`, then dropped the schema after each attempt.
  - First Postgres run upgraded through head, including all v8 migrations, then failed during downgrade at historical migration `b2a7c8d9e0f1_add_autopilot_settings_and_flag_dismissals.py`: `ix_sla_policies_org_active` had already been dropped by the later SLA guard migration.
  - Resolution: made that historical downgrade drop `ix_sla_policies_org_active` only if the index is present. This does not change application behavior and allows the full downgrade chain to proceed through fresh-schema verification.
  - Second Postgres run upgraded through head and past the first downgrade fix, then failed during downgrade at historical migration `e2f4c6a8b9d0_add_org_notification_settings.py`: `slack_webhook_url` had already been dropped by the later Slack standup migration.
  - Resolution: made the historical org-notification downgrade drop its org columns only when present. This keeps the downgrade reversible across the actual linear migration chain.
  - Final Phase C sequence passed on a fresh temporary Neon schema: `alembic upgrade head -> alembic downgrade base -> alembic upgrade head`. The temporary schema was dropped after verification.
- Phase D test runs:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests -q` -> `260 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed with existing WorkOS Edge Runtime warnings.
  - Migration determinism: ran `alembic upgrade head -> downgrade base -> upgrade head` three times against fresh temporary Neon schemas via `PGOPTIONS=-c search_path=<schema>` -> all three cycles passed and schemas were dropped.
  - Initial Playwright run failed on stale/data-dependent legacy smoke tests (`skill-debt.spec.ts`, `skill-diff.spec.ts`). Resolution tightened the current Skill Health assertion and converted the no-data skill-diff path from skip to a passing empty-data smoke.
  - Re-run `npx playwright test e2e --workers=1` with explicit flag-off and flag-on dashboard servers -> `24 passed`.
- Phase D zero-observable-change stop:
  - Compared `origin/main` at `8b89630` with `v8/integration` at `IA_V8_DEFAULT=false` across 31 legacy `/dashboard/*` routes using Playwright screenshots and exact pixel comparison.
  - Result: failed. All 31 compared routes had pixel differences, ranging from `14574` to `28108` differing pixels.
  - Stop condition triggered: the visual diff found flag-off differences from main. No PR opened.
- Phase D zero-observable-change resolution:
  - Rebuilt the `origin/main` dashboard baseline before launching `next start`; the prior comparison used a stale `.next` artifact in the baseline worktree.
  - Sequential comparison then reduced to one dynamic timestamp diff on `/dashboard/eval/gaps` (`Last scan` differed by one second).
  - Final comparison captured baseline and integration pages in parallel per route: all 31 legacy `/dashboard/*` routes were pixel-identical with `IA_V8_DEFAULT=false`.
- Phase D performance smoke:
  - Policy evaluator 100-rule corpus: p95 `0.2273ms`, below the 50ms target.
  - v8 Insights dashboard 1M-action aggregate fixture: `/insights` rendered in `798.7ms`, below the 2s target.
- Final dashboard checks after e2e test edits: `npm --workspace apps/dashboard run type-check` -> passed; `npm --workspace apps/dashboard run lint` -> passed.

## 2026-05-10 — v8 Insights Coverage SLA critical-ops wiring

- Backend: `apps/api/api/v8/insights/router.py` now loads critical operations from `apps/api/api/v8/insights/critical_ops.yaml` (with safe fallback + cache) instead of hard-coding the placeholder list.
- Backend tests: added Coverage SLA contract tests for YAML override + invalid YAML fallback in `apps/api/tests/test_v8_insights.py`.
- Frontend: Coverage SLA tab now displays required skill categories per critical operation and includes a safe fallback message for empty `product_review_note`.
- Verification:
  - Backend syntax: ran `python -m py_compile apps/api/api/v8/insights/router.py apps/api/tests/test_v8_insights.py` -> passed.
  - Backend touched checks: directly invoked `test_coverage_sla_reads_critical_ops_from_yaml` and `test_coverage_sla_falls_back_when_critical_ops_yaml_invalid` with `MonkeyPatch` + temp YAML files -> passed.
  - Backend full file caveat: `python -m pytest apps/api/tests/test_v8_insights.py -q` exits with code `-1` and no output in the local Python 3.13 shell, so the touched contract checks above were used for this run.
  - Frontend: ran `npm run lint --workspace apps/dashboard`, `npm run type-check --workspace apps/dashboard`, and `npm run build --workspace apps/dashboard` -> passed.
- UX screenshot gate:
  - Production preview screenshots captured for the migrated Skillayer Coverage SLA empty state:
    - `docs/v8-refactor/screenshots/automation-20260510/coverage-sla-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260510/coverage-sla-mobile.png`
  - Data-backed production preview screenshots captured with a local mock API to prove the changed review note and required-category UI:
    - `docs/v8-refactor/screenshots/automation-20260510/coverage-sla-data-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260510/coverage-sla-data-mobile.png`
  - Browser checks confirmed the product-review note, `Requires: security_compliance, codebase_architecture`, `Requires: operational_knowledge`, repo card, gap state, and mobile `bodyWidth` equals the viewport width.

## 2026-05-10 — Agent compliance metadata ingestion slice

- Backend: `apps/api/api/v8/settings/router.py` adds `POST /v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-events` for configured agent-compliance connectors.
- Normalization: accepted provider events persist as metadata-only `agent.compliance` audit events with source-envelope hashes and all available provider, model, intelligence-tier, access, tool, MCP, file, policy, token, cost, latency, warning, violation, and error metrics.
- Privacy: raw prompts, chats, file content, diffs, tool parameters, and raw event bodies are stripped before persistence; stored metadata carries `content_retention=metadata-only` and `redaction_state=raw-content-dropped`.
- Frontend: Settings -> Connectors now shows last-ingest and total-ingested counts for each agent compliance connector so the UI distinguishes setup/readiness from actual event flow.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py apps/api/tests/test_v8_insights.py apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_audit_router_units.py -q` -> `47 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260510/agent-compliance-ingestion-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260510/agent-compliance-ingestion-mobile.png`

## 2026-05-11 — Insights provider coverage slice

- Backend: `apps/api/api/v8/insights/router.py` adds `GET /v8/orgs/{org_id}/insights/provider-coverage`.
- Coverage logic: compares configured agent-compliance connectors with recent metadata-only `agent.compliance` / `agent.telemetry` audit events and marks each provider as active, silent, stale, retention-risk, configured, or unconfigured.
- Retention framing: exposes days remaining in the configured retention window, defaulting to 30 days for OpenAI-style compliance-log urgency.
- Frontend: `apps/dashboard/app/(v8)/insights/provider-coverage/page.tsx` adds a migrated Insights tab with active provider, coverage-risk, configured-count, and per-provider evidence cards.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> `12 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/provider-coverage-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/provider-coverage-mobile.png`

## 2026-05-11 — Insights agent compliance metrics slice

- Backend: `apps/api/api/v8/insights/router.py` adds `GET /v8/orgs/{org_id}/insights/agent-compliance-metrics`.
- Metrics: consolidates metadata-only compliance and coding-agent telemetry across providers, developers, models, repos, sessions, tools, MCP tools, files, policy decisions, approvals, source record types, retention states, token counts, cost, latency, warnings, violations, and errors.
- Frontend: `apps/dashboard/app/(v8)/insights/agent-compliance-metrics/page.tsx` adds a migrated Insights tab for end-to-end developer tracking from normalized compliance API records.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> `13 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-metrics-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-metrics-mobile.png`

## 2026-05-11 — Agent compliance sync readiness slice

- Backend: `POST /v8/orgs/{org_id}/settings/connectors/{connector_id}/sync` now returns a metadata-only sync readiness plan instead of only mutating connector state.
- Readiness plan: records cursor-resume pagination, provider-adapter requirement, retention window, retention deadline, formal-compliance versus operational-telemetry source type, and explicit next actions before live pulls are enabled.
- Frontend: Settings -> Connectors displays the latest sync readiness plan for each configured agent compliance connector without marking the source connected.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> `15 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-sync-readiness-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-sync-readiness-mobile.png`

## 2026-05-11 — Agent compliance ingest jobs slice

- Backend: `POST /v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-jobs` queues metadata-only provider pages through the existing `jobs` model.
- Backend: `GET /v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-jobs/{job_id}` returns connector-scoped status and result metadata.
- Job contract: stores cursor-resume pagination state, event count, content retention, queued/running/completed/failed state, and reuses the existing normalizer that drops raw prompts, chat, file content, diffs, raw event bodies, and tool parameters.
- Frontend: Settings -> Connectors shows the last ingest job on each configured agent compliance connector and exposes a gated queue action without marking any provider connected.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> `17 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-ingest-jobs-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/agent-compliance-ingest-jobs-mobile.png`

## 2026-05-11 — Policy agent compliance evaluation slice

- Backend: `GET /v8/orgs/{org_id}/policy/agent-compliance` evaluates recent metadata-only `agent.compliance` audit events against enabled v8 Policy rules.
- Policy projection: maps provider, actor, repo, model, intelligence tier, access scope, file targets, MCP/tools, source record type, and sanitized metadata into the existing YAML DSL evaluator.
- Frontend: Policy now includes an Agent events tab showing evaluated compliance records, matched decisions, tags, rule reasons, and `metadata-only` retention without displaying raw prompts, chat, diffs, file content, or tool parameters.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_policy.py -q` -> `18 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed after the production build regenerated `.next/types`.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/policy-agent-compliance-events-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/policy-agent-compliance-events-mobile.png`

## 2026-05-11 — Activity agent compliance sessions slice

- Backend: `GET /v8/orgs/{org_id}/activity/compliance-sessions` groups metadata-only `agent.compliance` telemetry by provider session id.
- Session rollup: exposes provider, actor, repo, model, intelligence tier, access scopes, source record types, event count, tool calls, MCP tools, file targets, policy decisions, tokens, cost, errors, duration, and risk band.
- Frontend: Activity now includes an Agent sessions tab for provider/coding-agent telemetry sessions, separate from existing first-party `AgentSession` rows.
- Privacy: raw prompts, chat content, file content, diffs, raw event bodies, and tool parameters are not returned or displayed.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_activity_api.py -q` -> `14 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/activity-agent-compliance-sessions-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/activity-agent-compliance-sessions-mobile.png`

## 2026-05-11 — Insights compliance developer track slice

- Backend: `GET /v8/orgs/{org_id}/insights/developer-track` rolls up metadata-only `agent.compliance` and `agent.telemetry` records by actor.
- Developer rollup: exposes developer rank, events, sessions, providers, repos, models, tool calls, MCP tool calls, file targets, full-access/autonomous exposure, policy decisions, approvals, denials, tokens, cost, latency, warnings, violations, errors, source record types, last activity, and risk band.
- Frontend: Insights -> Developer track now uses the v8 compliance API instead of the legacy `/orgs/{org_id}/developer-leaderboard` endpoint.
- Privacy: raw prompts, chat content, file content, diffs, raw event bodies, and tool parameters are not returned or displayed.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> `16 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - UX screenshots captured:
    - `docs/v8-refactor/screenshots/automation-20260511/insights-compliance-developer-track-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/insights-compliance-developer-track-mobile.png`

## 2026-05-11 — Insights coverage SLA critical operations slice

- Backend: `apps/api/api/v8/insights/critical_ops.yaml` now carries Skillayer's default critical-operation taxonomy instead of a product-review placeholder.
- Taxonomy: defines commit provenance, privileged runtime changes, production data access, dependency/supply-chain changes, and policy-controlled coding-agent actions with required skill categories, sensitivity scope, evidence requirements, and SLA-hour targets.
- Frontend: Insights -> Coverage SLA displays SLA-hour targets, operation descriptions, and required evidence chips for each in-scope repo operation.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> `14 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/coverage-sla-critical-ops-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/coverage-sla-critical-ops-mobile.png`

## 2026-05-11 — Insights fleet quarantine KPI slice

- Backend: `GET /v8/orgs/{org_id}/insights/fleet-kpis` now reports `quarantined_skills` from `skill_registry_entries` instead of returning an unavailable placeholder.
- Metric contract: counts entries tagged `quarantined` plus retired/deprecated entries at the current and previous period boundaries.
- Frontend: existing Fleet KPI cards now render the quarantine metric as an available trend metric without UI changes.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> `15 passed`.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/fleet-kpi-quarantine-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/fleet-kpi-quarantine-mobile.png`

## 2026-05-11 — Insights policy violation MTTR KPI slice

- Backend: `GET /v8/orgs/{org_id}/insights/fleet-kpis` now reports `mttr_violations` from resolved Policy approval decisions instead of leaving it unavailable when reviewed decisions exist.
- Metric contract: uses terminal `approve` / `deny` records in `org.settings.v8_policy_approval_decisions[*].recorded_at` as the resolution timestamp and the matching policy creation time as the violation start anchor, reporting median hours for current and previous windows.
- Frontend: existing Fleet KPI cards now render MTTR as an hours metric without UI changes.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_insights.py -q` -> 16 passed.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/fleet-kpi-policy-mttr-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/fleet-kpi-policy-mttr-mobile.png`

## 2026-05-11 — Settings agent connector catalog coverage slice

- Backend: the v8 Settings connector registry now carries actionable source types, descriptions, and metric capabilities for Windsurf, Aider, GitHub Copilot, GitLab Duo, and internal MCP servers.
- Agent compliance readiness: internal MCP is included in the agent-compliance registry so MCP call, resource-scope, approval, latency, and error metadata can be configured and dry-run planned without live credentials.
- Frontend: the migrated Settings connector fallback catalog mirrors the required coding-agent and MCP sources so local or unauthenticated previews do not hide PRD-required connectors or imply fake connected state.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> 20 passed.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/settings-agent-connector-catalog-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/settings-agent-connector-catalog-mobile.png`

## 2026-05-11 — Skills registry governance evidence slice

- Frontend: the migrated Skill Registry now renders dependent agents and policy bindings for every skill row instead of hiding the governance evidence already returned by `/v8/orgs/{org_id}/skills/registry`.
- UX: registry summary cards now include distinct dependent-agent and policy-binding counts, and the table keeps governance evidence in a horizontally contained grid so mobile layouts do not force page-level overflow.
- Verification:
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/skills-registry-governance-evidence-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/skills-registry-governance-evidence-mobile.png`

## 2026-05-11 — Settings agent compliance actor fallback slice

- Backend: metadata-only agent compliance ingestion now falls back to the authenticated request actor when a provider event omits `actor_login`, preserving developer attribution in both the normalized audit event and metadata envelope.
- Safety: the migrated Connectors UI keeps live ingest jobs metadata-only and does not generate synthetic sample compliance events.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> 21 passed.
  - `git diff --check` -> passed.

## 2026-05-11 — Settings CI/CD connector catalog slice

- Backend: the v8 Settings connector registry now includes GitHub Actions, GitLab CI, and CircleCI with source types, descriptions, and capabilities for workflow/pipeline runs, jobs, artifacts, actor attribution, and test outcomes.
- Agent compliance readiness: CI/CD connectors are included in the metadata-only readiness registry so agent-driven build jobs can be configured and dry-run planned without live credentials.
- Frontend: the migrated Settings connector catalog now shows a CI/CD section in both API-backed and fallback states.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> 21 passed.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured with a local mock API:
    - `docs/v8-refactor/screenshots/automation-20260511/settings-cicd-connector-catalog-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/settings-cicd-connector-catalog-mobile.png`

## 2026-05-11 — Settings git provider connector catalog slice

- Backend: the v8 Settings connector registry now includes GitHub, GitLab, and Bitbucket source types, descriptions, and source-control capabilities for webhooks, post-receive events, commit signatures, and AI attribution headers.
- Frontend: the migrated Settings connector fallback catalog now shows GitHub, GitLab, and Bitbucket source-control cards instead of only GitHub.
- Verification:
  - `../skilgen-upstream-work/.venv/bin/python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` -> 22 passed.
  - `npm --workspace apps/dashboard run type-check` -> passed.
  - `npm --workspace apps/dashboard run lint` -> passed.
  - `npm --workspace apps/dashboard run build` -> passed.
  - `git diff --check` -> passed.
  - UX screenshots captured from the built fallback catalog:
    - `docs/v8-refactor/screenshots/automation-20260511/settings-git-provider-connector-catalog-desktop.png`
    - `docs/v8-refactor/screenshots/automation-20260511/settings-git-provider-connector-catalog-mobile.png`
