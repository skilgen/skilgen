# Evaluator — 2026-05-17 — Activity + Insights intelligence usage (metadata-only)

This evaluator pass reviews the current working diff on branch `v8/next-feature-loop` (uncommitted at time of evaluation).

## Scope (changed surfaces)
- API: v8 Activity heatmap + replay, agent run ingestion metadata preservation, v8 Insights intelligence usage expansion, and v8 Skills surface hardening for bootstrap/demo databases.
- Dashboard (v8): Activity Heatmap UX/metrics + Replay null-safe hardening, Insights Intelligence Usage expanded panels.
- Persistence + demo: SQLite async URL normalization + demo seeding/import helpers.

## Backend verification
- ✅ Targeted tests pass:
  - `python -m pytest apps/api/tests/test_agent_runs.py apps/api/tests/test_orgs_api.py apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_insights.py apps/api/tests/test_v8_skills.py -q`
- ✅ Endpoint contract spot-check against seeded SQLite demo (requires `aiosqlite` on `PYTHONPATH`):
  - Seed: `SKILLAYER_DEMO_DB=/private/tmp/skillayer_v8_seed_20260517_01.db python scripts/seed_v8_sqlite_demo.py`
  - Run API:
    - `PYTHONPATH=/private/tmp/skillayer-pydeps DATABASE_URL=sqlite:////private/tmp/skillayer_v8_seed_20260517_01.db DEPLOYMENT_MODE=bootstrap IA_V8_DEFAULT=1 python -m uvicorn apps.api.api.index:app --port 59999`
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
- ✅ Dashboard checks pass:
  - `npm --workspace apps/dashboard run type-check`
  - `npm --workspace apps/dashboard run lint`
- ✅ Dashboard dev server starts against the seeded API:
  - `IA_V8_DEFAULT=1 NEXT_PUBLIC_API_URL=http://127.0.0.1:59999 API_URL=http://127.0.0.1:59999 npm --workspace apps/dashboard run dev -- --port 4330`

## UX proof (screenshots)
- ✅ Desktop screenshots exist for v8 routes under:
  - `docs/screenshots/local-qa-20260517/`
- ❌ Mobile screenshots (375px-ish viewport) are still missing for:
  - `/activity/heatmap`
  - `/insights/intelligence-usage`
- ❌ Automation capture remains blocked in this environment:
  - Playwright/Chromium screenshot runs crash (`kill EPERM` / `SIGTRAP`/`SIGABRT`).
  - Codex in-app browser navigation is blocked for local origins.
  - Computer Use `get_app_state` is denied (interactive approval).

## PR readiness
- ❌ Not PR-ready until mobile screenshot proof is added (or explicitly waived).
