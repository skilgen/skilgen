# Evaluator — 2026-05-18 — Activity feed backfill + Heatmap metrics + Insights intelligence usage

This evaluator pass reviews the current working diff on branch `v8/next-feature-loop`.

## Scope (changed surfaces)
- API: v8 Activity feed backfill + heatmap summary/model/trend metrics, agent run ingestion metadata preservation, v8 Insights intelligence usage expansion, and v8 bootstrap hardening for optional governance tables.
- Dashboard (v8): Activity Live feed rows now show token/cost + replay links, Activity Heatmap adds summary metrics and model/trend views, Insights Intelligence Usage adds token/cost totals, peak usage, task/model rollups, PR/code-push usage, and routing recommendations.
- Persistence: SQLite async URL normalization for `DATABASE_URL=sqlite:///...` (auto-upgrades to `sqlite+aiosqlite://...`).

## Backend verification
- ✅ Targeted tests:
  - `python -m pytest apps/api/tests/test_agent_runs.py apps/api/tests/test_orgs_api.py apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_insights.py apps/api/tests/test_v8_skills.py -q`
- ✅ Endpoint contract spot-check against seeded SQLite demo (requires `aiosqlite` importable):
  - Seed: `SKILLAYER_DEMO_DB=/private/tmp/skillayer_v8_seed_20260518_01.db python scripts/seed_v8_sqlite_demo.py`
  - Run API:
    - `DATABASE_URL=sqlite:////private/tmp/skillayer_v8_seed_20260518_01.db DEPLOYMENT_MODE=bootstrap IA_V8_DEFAULT=1 python -m uvicorn apps.api.api.index:app --port 59999`
  - Verified `200`:
    - `GET /health`
    - `GET /orgs/bootstrap`
    - `GET /v8/orgs/org_skilgen/insights/intelligence-usage`
    - `GET /v8/orgs/org_skilgen/repos/repo_skilgen/activity/heatmap`
    - `GET /v8/orgs/org_skilgen/repos/repo_skilgen/activity/sessions/sess_ext_1/replay`
    - `GET /v8/orgs/org_skilgen/audit/event-log`
    - `GET /v8/orgs/org_skilgen/policy/rules`
    - `GET /v8/orgs/org_skilgen/skills/registry`

## Frontend verification
- ✅ Dashboard checks:
  - `npm --workspace apps/dashboard run type-check`
  - `npm --workspace apps/dashboard run lint`
- ✅ Dashboard dev server starts against the seeded API:
  - `IA_V8_DEFAULT=1 NEXT_PUBLIC_API_URL=http://127.0.0.1:59999 API_URL=http://127.0.0.1:59999 npm --workspace apps/dashboard run dev -- --port 4330`

## UX proof (screenshots)
- ✅ Desktop + mobile screenshots captured for the primary changed v8 screens:
  - `docs/v8-refactor/screenshots/2026-05-16-activity-insights-intelligence/activity-heatmap-desktop.png`
  - `docs/v8-refactor/screenshots/2026-05-16-activity-insights-intelligence/activity-heatmap-mobile.png`
  - `docs/v8-refactor/screenshots/2026-05-16-activity-insights-intelligence/insights-intelligence-usage-desktop.png`
  - `docs/v8-refactor/screenshots/2026-05-16-activity-insights-intelligence/insights-intelligence-usage-mobile.png`

## PR readiness
- ✅ Ready once verification commands above are re-run on this diff and results copied into the PR body.
