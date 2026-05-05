# v8 Integration Log

Branch: `v8/integration`  
Base: `origin/main` at `8b89630`  
Scope: PR-2 through PR-7 in one integration PR. PR-8 deprecation is out of scope.

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
