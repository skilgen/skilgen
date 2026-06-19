# Evaluator — 2026-05-16 — Activity + Insights intelligence usage (metadata-only)

This evaluator pass reviews the current working diff on branch `v8/next-feature-loop` (uncommitted at time of evaluation).

## Scope (changed surfaces)
- API: v8 Activity feed/session fallback + v8 Insights intelligence usage expansion, plus supporting routes (`/orgs/*`, `/orgs/*/api-key`, `/orgs/bootstrap`, `/orgs/*/agent-runs`).
- Dashboard (v8): Activity Heatmap metrics + Replay client null-safe hardening, Insights Intelligence Usage expanded panels (tokens/cost/peak/task+PR summaries/recommendations).
- Persistence: SQLite async URL normalization + a committed demo seed script.

## Backend verification
- ✅ Targeted tests pass (repo's default Python 3.13 env):
  - `python -m pytest apps/api/tests/test_agent_runs.py apps/api/tests/test_orgs_api.py apps/api/tests/test_v8_activity_api.py apps/api/tests/test_v8_insights.py -q`
- ✅ No contract regressions observed in touched tests (56 passed).
- ⚠️ Non-blocking warnings: FastAPI `on_event` deprecation; `datetime.utcnow()` deprecations.
- ✅ Seeded demo API bootstraps with SQLite when run from a local venv that includes `aiosqlite`:
  - `python scripts/seed_v8_sqlite_demo.py`
  - `python -m venv /private/tmp/skillayer-py313-venv && /private/tmp/skillayer-py313-venv/bin/pip install -r apps/api/requirements.txt`
  - `DATABASE_URL=sqlite:////private/tmp/skillayer_v8_seed.db DEPLOYMENT_MODE=bootstrap IA_V8_DEFAULT=1 /private/tmp/skillayer-py313-venv/bin/python -m uvicorn apps.api.api.index:app --host 127.0.0.1 --port 59999 --lifespan off`
  - Verified: `GET /health` and `GET /orgs/bootstrap` return `200`.

## Frontend verification
- ✅ Dashboard checks pass:
  - `npm --workspace apps/dashboard run type-check`
  - `npm --workspace apps/dashboard run lint`
- ✅ Dashboard dev server starts against the seeded API:
  - `IA_V8_DEFAULT=1 API_URL=http://127.0.0.1:59999 NEXT_PUBLIC_API_URL=http://127.0.0.1:59999 npm --workspace apps/dashboard run dev -- --hostname 127.0.0.1 --port 3000`
- ❌ Screenshot proof is blocked in this environment (desktop + mobile).

## UX quality (manual review requirements)
- Blocked: this environment cannot produce real browser screenshots for local dev servers:
  - Codex in-app browser (Browser Use `iab`) blocks navigation to local origins (e.g. `http://127.0.0.1:3000` and `http://localhost:3000`) due to a persisted local-origin deny policy.
  - Playwright/Chromium screenshot attempts still crash or fail in this environment (e.g. `SIGTRAP` / `kill EPERM`).
  - Computer Use app control is gated by interactive approvals and is not available in this automation context.
  - `agent-browser --engine lightpanda` generates placeholder images (no graphical rendering engine), so those screenshots are not acceptable as UX proof.

## PR readiness
- ❌ Not PR-ready until the screenshot gate is satisfied (or explicitly waived by the reviewer).

## Notes
- Unblock options:
  - Allow local origins in the Codex in-app browser origin policy, then re-capture screenshots (recommended).
  - Or explicitly waive screenshot proof for this PR.
