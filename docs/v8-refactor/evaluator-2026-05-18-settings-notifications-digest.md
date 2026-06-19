# Evaluator — 2026-05-18 — Settings notifications digest

## Scope
- v8 Settings → Notifications now supports digest frequency selection, HTML preview, and a send-now (test) action backed by the existing digest engine.
- v8 Settings notifications endpoints are now RBAC-gated (`settings.notifications.read` / `settings.notifications.manage`) instead of unauthenticated.

## Backend
- Added wrappers under `apps/api/api/v8/settings/router.py`:
  - `GET  /v8/orgs/{org_id}/settings/notifications/digest`
  - `PUT  /v8/orgs/{org_id}/settings/notifications/digest`
  - `GET  /v8/orgs/{org_id}/settings/notifications/digest/preview`
  - `POST /v8/orgs/{org_id}/settings/notifications/digest/preview`
  - `POST /v8/orgs/{org_id}/settings/notifications/digest/send-now`
- RBAC catalog updated in `apps/api/api/v8/settings/rbac/dependencies.py`:
  - Added `settings.notifications.read`.

## Frontend UX
- `apps/dashboard/app/(v8)/settings/notifications/notifications-panel.tsx`
  - Frequency selector (daily/weekly/monthly).
  - Preview dialog rendering the digest HTML in an iframe.
  - “Send test” action posting to `.../send-now` with an optional recipient override.
  - Save now hydrates from the API response when successful.

## Verification
- API tests:
  - `python -m pytest apps/api/tests/test_v8_settings_rbac.py -q` (pass)
- Dashboard checks:
  - `npm --workspace apps/dashboard run type-check` (pass)
  - `npm --workspace apps/dashboard run lint` (pass)

## UX proof (screenshots)
- ❌ Blocked: this environment cannot produce real browser screenshots for local dev servers.
  - Playwright Chromium headless shell crashes (`SIGTRAP`) and cannot be killed (`kill EPERM`) when attempting screenshots.
  - System Chrome headless screenshot attempts abort (exit `134`) and do not emit images.
- Not PR-ready until desktop + mobile screenshots are captured for:
  - `/settings/notifications`
  - (optional but preferred) the preview dialog state

## Evaluator result
- ❌ FAIL (blocked on screenshot proof gate).

