# v8 Refactor Conventions

These conventions are established by PR-1 and apply to PR-2 through PR-8.

## Paths

- v8 API path convention: `apps/api/api/v8/<surface>/`
- v8 dashboard route convention: `apps/dashboard/app/(v8)/<surface>/`

## IA_V8 Flag Helpers

Server helper:

```python
async def is_v8(org_id: str, db: AsyncSession | None = None) -> bool
```

Location: `apps/api/api/v8/flags.py`

The helper reads the tenant override from `orgs.settings.feature_flags.IA_V8`, then `IA_V8_DEFAULT`, then `false`. It uses a request-scoped ContextVar cache.

Client/dashboard helper:

```ts
export async function isDashboardV8Enabled(orgId: string): Promise<boolean>
export const isV8ForOrg: (orgId: string) => Promise<boolean>
```

Location: `apps/dashboard/lib/flags.ts`

The dashboard helper is server-side only. It reads the WorkOS/AuthKit session for the bearer token, calls the API flag endpoint when possible, and falls back to `IA_V8_DEFAULT` when no tenant override can be read.

## Sidebar Contract

- `SidebarLegacy` is an extraction from `apps/dashboard/app/dashboard/layout.tsx`; flag-off rendering must remain visually and functionally identical to main.
- `SidebarV8` contains exactly six top-level items, in order: Activity, Policy, Audit, Skills, Insights, Settings.
- PR-2 through PR-7 may add sub-navigation inside each surface, but must not add more primary sidebar items.

## Routing

- Tabs are URL sub-routes, not query-param tabs.
- Do not introduce new query-param tab state for v8 surfaces.
- Old v7 routes remain valid until PR-8 redirects are explicitly approved.

## Branches And Commits

- Branch naming: `v8/0X-<surface>`
- Commit messages use Conventional Commits with `v8` scope: `feat(v8):`, `chore(v8):`, `docs(v8):`, `test(v8):`, or `fix(v8):`.

## Per-Tenant Override Read Order

1. Tenant override: `orgs.settings.feature_flags.IA_V8`
2. Environment default: `IA_V8_DEFAULT`
3. `false`

Q7 decision: PR-1 uses the existing `orgs.settings` JSON carrier instead of adding a dedicated column or table, because PR-0 identified it as stable enough for low-risk tenant overrides.
