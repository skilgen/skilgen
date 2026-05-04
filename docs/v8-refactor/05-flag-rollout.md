# PR-0 Flag Rollout Plan

Feature flag: `IA_V8`

Goal: one switch controls the v8 information architecture without breaking legacy routes, API contracts, or tenant-specific rollout.

## Current state

- No `IA_V8` flag exists.
- No LaunchDarkly or equivalent feature flag service was found.
- Existing gating uses environment variables and org settings.
- Admin sidebar visibility uses `NEXT_PUBLIC_ADMIN_EMAILS`.
- `orgs.settings` exists as JSON-like tenant configuration and is the lowest-risk per-tenant override carrier unless PR-1 chooses a dedicated column.

## Read order

PR-1 should implement one helper on the API side and one helper on the dashboard side.

Effective value:

1. Per-tenant override, if set.
2. Environment default, if set.
3. `false`.

Proposed environment variables:

| Variable | Scope | Default | Meaning |
| --- | --- | --- | --- |
| `IA_V8_DEFAULT` | API/dashboard server runtime | `false` | Global default for all tenants. |
| `NEXT_PUBLIC_IA_V8` | Dashboard client only if unavoidable | unset | Avoid unless a client component cannot receive server-computed value. |

Per-tenant override:

```json
{
  "feature_flags": {
    "IA_V8": true
  }
}
```

Preferred storage: `orgs.settings.feature_flags.IA_V8` if current JSON settings are stable. Alternative: add `org_feature_flags(org_id, key, value, created_at, updated_at)` in PR-1. PR-1 must choose one and document it in `docs/v8-refactor/conventions.md`.

## Where the flag is checked

| Layer | Check point | Behavior when false | Behavior when true |
| --- | --- | --- | --- |
| Dashboard shell | `apps/dashboard/app/dashboard/layout.tsx` after shell org is loaded | Render legacy sidebar and legacy route tree | Render `SidebarV8` and v8 route links |
| Dashboard v8 routes | v8 route layouts/pages | Redirect to legacy equivalent or 404 only for never-public v8 URLs | Render v8 page |
| API v8 endpoints | Dependency/helper in `apps/api/api` | Return 404 or 403 for v8-only endpoints | Serve v8 endpoint |
| API legacy endpoints | Existing router handlers | Continue serving | Continue serving unless PR-8 deprecates |
| Redirects | PR-8 middleware/route-level redirect map | Old URLs remain 200 | Old URLs 301 to v8 equivalents after deprecation approval |

## Rollout phases

1. PR-1: add flag plumbing with default off; add six placeholder routes and v8 sidebar behind flag.
2. PR-2 through PR-7: each surface checks `IA_V8`; legacy routes stay live.
3. Tenant pilot: set per-tenant override true for one internal/test org.
4. Broader rollout: set override true for named beta tenants.
5. Default-on: set env `IA_V8_DEFAULT=true` after all surface PRs are merged and approved.
6. PR-8: add v7 redirects and deprecation headers after user-approved deprecation date.

## Rollback plan

Immediate rollback:

- Set tenant override `feature_flags.IA_V8=false`, or remove the override.
- If env default was enabled, set `IA_V8_DEFAULT=false`.
- No migrations should be required to roll back route visibility.

Data rollback:

- PR-1 flag migration must have a downgrade.
- Surface migrations must not be required for the legacy IA to keep working.
- Do not delete or hard-rename v7 data until PR-8 and later follow-up cooldown.

## Tests required in PR-1

- With `IA_V8=false`, legacy sidebar still contains the current v7 items.
- With `IA_V8=true`, sidebar contains exactly Activity, Policy, Audit, Skills, Insights, Settings.
- Tenant override beats environment default.
- Missing tenant override falls back to env.
- Existing legacy routes still 200 with flag off.

## Risk fixes addressed

- Resolves missing `IA_V8` risk by defining env + tenant override.
- Avoids root contract confusion by requiring PR-1 conventions doc to name `docs/AGENTS.md` until root `AGENTS.md` is resolved.
- Avoids accidental app-wide rollout by defaulting off.
