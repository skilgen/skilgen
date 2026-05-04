# PR-0 Open Questions

These require user/product answers before PR-2 through PR-7 can land.

## Contract and repo layout

1. Should the root `AGENTS.md` be replaced with the v8 brief, or should `docs/AGENTS.md` remain the v8 operating contract?
2. Should PR-1 add any compatibility import aliases, or is the final convention simply `apps/api/api/v8/<surface>/` with no aliases?
3. Should `skilgen/hooks/claude_code_hook.py` remain the stable hook path, or should a non-OSS app-owned hook path be introduced later?

## Information architecture

4. Where does the conditional `Admin` sidebar surface live in v8: outside primary IA, Settings -> Admin action audit, Audit, or removed from tenant-facing nav?
5. Should `/dashboard` redirect to `/dashboard/activity` immediately when `IA_V8=true`, or should Activity render at `/dashboard` with `/dashboard/activity` as canonical?
6. Are v8 tabs required as literal URL sub-routes for all six surfaces, or may some use query-param tabs where legacy components already depend on query state?

## Data and migrations

7. Should the per-tenant `IA_V8` override live in `orgs.settings.feature_flags`, a new `org_feature_flags` table, or a dedicated `orgs.ia_v8_enabled` column?
8. Can staging/sanitized DB row counts be provided before any PR that plans `_deprecated_v7_` renames?
9. Should `ab_tests` and `digest_configs` be renamed in PR-8 exactly, or only after an additional post-PR-8 cooldown?

## Surface behavior

10. For PRD-cut surfaces such as My Code Today and Leaderboard, should any user-visible cards survive inside Activity/Insights, or should only backend data be reused?
11. For Digest, should existing email sending remain fully available through Settings, or should manual preview/send be removed from UI?
12. For A/B Tests, should API endpoints receive deprecation headers in PR-8 even though the table is preserved?

## Governance and security

13. Q13 (PR-3 work item, not open question): The existing code uses three policy decision verbs (`block/warn/log`). PRD §4.2.1 specifies six (`allow/deny/require_approval/log_only/redact/route_to_dlp`). PR-3 must extend the verb enum, map existing rows to new verbs (`block→deny`, `warn→require_approval`, `log→log_only`), and deprecate the old names.
14. Which WORM storage targets must Audit support first: S3 Object Lock, GCS Bucket Lock, Azure Immutable Blob, or all three?
15. Which async system is authoritative for evidence-package exports: existing Celery/worker, QStash, or DB-polled jobs?
16. Is RBAC in PR-7 required for all tenants, or Enterprise-only?

## Testing and rollout

17. What is the first tenant/org to receive `IA_V8=true` during pilot?
18. Should v8 placeholder routes in PR-1 be visible to admin users only, or any tenant with the flag enabled?
19. What browser/device matrix is required for Playwright screenshots in the v8 surface PRs?
20. Should frontend coverage be introduced as part of PR-1, or are Playwright smoke tests sufficient for this refactor?
21. When v8 surface PRs add columns or views to existing v7 tables, are v7 endpoints required to remain bit-for-bit identical in response shape, or are additive non-breaking changes acceptable?
