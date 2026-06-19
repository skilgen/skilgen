# Evaluator: Enterprise Connector Setup UX

Date: 2026-05-19
Slot: PR-15 / enterprise connector setup UI with test, sync, and coverage status
Org/account/repo: `org_skilgen` / `Skilgen` / `ravichanduummadisetti/skilgen`

## Scope

Added an enterprise setup contract to the agent compliance connector endpoint and surfaced it on Settings -> Connectors as an admin setup path:

- Install GitHub App
- Connect OpenAI
- Connect Anthropic
- Test connections
- Start sync
- Review coverage gaps

The UX tells an admin whether Skillayer is ready to passively ingest coding-agent runs and exactly what is still missing before developer, repo, PR, commit, token, and cost rollups can be trusted.

## Endpoint Verification

Endpoint:

```bash
curl -sS 'http://127.0.0.1:8000/v8/orgs/org_skilgen/settings/connectors/agent-compliance' \
  | jq '{configured_count, enabled_count, setup_complete: .enterprise_setup.setup_complete, github_connected: .enterprise_setup.github_connected, gaps: .enterprise_setup.coverage_gaps, steps: [.enterprise_setup.steps[] | {label,status,next_action}]}'
```

Seeded production-shaped data:

- SQLite bootstrap database: `/private/tmp/skillayer_v8_seed.db`
- OpenAI Compliance fixture connection configured, tested, and synced.
- Anthropic Compliance fixture connection configured, tested, and synced.
- GitHub App intentionally not connected so the UI can prove a coverage-gap state.

Observed result:

- `configured_count`: 2
- `enabled_count`: 2
- `setup_complete`: false
- `github_connected`: false
- Coverage gap: `GitHub App is not connected`
- OpenAI, Anthropic, Test connections, and Start sync steps are complete.
- Test connections next action: `Monitor credential health`
- Start sync next action: `Monitor sync freshness`

## Browser Verification

Local services:

- API: `http://127.0.0.1:8000`
- Dashboard: `http://127.0.0.1:4325`

Browser automation command:

```bash
node <<'NODE'
const { chromium } = require('playwright');
// Open /settings/connectors at desktop and mobile widths, assert the enterprise setup path,
// provider steps, GitHub coverage gap, and complete-step next actions are visible, then screenshot.
NODE
```

Assertions passed for desktop and mobile:

- `Enterprise setup path`
- `GitHub App is not connected`
- `Connect OpenAI`
- `Connect Anthropic`
- `Next: Monitor credential health`
- `Next: Monitor sync freshness`

Screenshots:

- `docs/v8-refactor/screenshots/2026-05-19-connector-setup-ux/connectors-setup-desktop.png`
- `docs/v8-refactor/screenshots/2026-05-19-connector-setup-ux/connectors-setup-mobile.png`

## Automated Checks

```bash
python -m pytest apps/api/tests/test_v8_settings_rbac.py -q
```

Result: 48 passed, 11 warnings.

```bash
npm --workspace apps/dashboard run type-check -- --pretty false
```

Result: passed.

## Usefulness Validation

This is useful because an enterprise admin can now answer:

- What must be connected before Skillayer can ingest all developer coding-agent activity?
- Are provider credentials stored, tested, and synced?
- Is GitHub enrichment available for repo, PR, commit, and branch context?
- Which setup gap blocks trustworthy rollups?
- What is the next action?

The current seeded state correctly tells the admin: provider compliance APIs are connected and synced, but GitHub App installation is still required before provider runs can be enriched with repository and PR evidence.

## UX Validation

- No duplicate tabs were introduced.
- The connector page scrolls on desktop and mobile.
- Empty or incomplete enterprise setup is not silent; it shows a high-severity coverage gap and next action.
- Complete steps no longer show misleading next actions.
- Text is visible without clipped labels in the verified viewports.

## Token And Cost Provenance

This slot does not create new token or cost calculations. It preserves the existing compliance connector provenance model:

- Provider-reported values must remain labeled as provider-reported when they come from compliance or usage APIs.
- Skillayer-estimated values must remain labeled as Skillayer-estimated when derived from token usage.
- Unknown values must not be presented as billed cost.

The setup path itself is metadata-only; it does not display spend totals.
