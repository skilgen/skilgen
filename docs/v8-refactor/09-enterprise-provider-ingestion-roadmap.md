# Enterprise Provider Ingestion Roadmap

This roadmap turns the current local/provider-normalized Activity work into an enterprise Skillayer product. The enterprise contract is: admins connect GitHub and provider compliance APIs once, Skillayer passively ingests every coding-agent run, normalizes it into governance telemetry, enriches it with repo/PR context, and shows useful end-to-end insight for every developer.

## Required Product Rule

Cost and usage metrics must always show provenance:

- `provider_reported`: value came directly from a provider compliance, usage, billing, or enterprise telemetry API.
- `skillayer_estimated`: Skillayer calculated the amount from provider token usage and pricing rules.
- `unknown`: source did not expose enough information.

UI labels, API payloads, evidence packages, and PR verification notes must not imply an estimated cost is provider-billed cost.

## Missing Enterprise Capabilities

1. Real provider adapters
   - OpenAI Compliance API adapter.
   - Anthropic Compliance API adapter.
   - GitHub Copilot usage/audit adapter.
   - Cursor, Windsurf, Claude Code, and other enterprise telemetry adapters where available.
   - Current `/sync` is a readiness contract unless the connector has a real provider pull implementation.

2. Secure credential storage
   - Move agent compliance connector secrets out of `org.settings`.
   - Store encrypted provider credentials with OAuth/API-token flows, rotation, test connection, scope display, and least-privilege permission checks.

3. Background scheduled ingestion
   - Add scheduled cursor workers that continuously pull provider APIs.
   - Workers must store cursor, last sync, last success, last failure, coverage gaps, and retention-window risk.

4. Identity mapping
   - Map provider users to company users by email, GitHub login, SSO subject, provider user id, and coding-agent local identity.
   - Insights must explain unmatched users instead of silently grouping them incorrectly.

5. Provider-to-GitHub enrichment
   - Reuse the AgentRun PR join behavior for provider events that include repo, branch, commit, head SHA, or PR metadata.
   - Show tokens/cost/model/reasoning by PR and link to GitHub commits/PRs when known.

6. Admin setup UX
   - Build real setup flows: Connect OpenAI, Connect Anthropic, Install GitHub App, Test connection, Start sync, Last synced, Coverage gaps.
   - Empty/blocked states must explain the exact next admin action.

## Build Order

1. Enterprise connector credential model.
2. OpenAI Compliance adapter.
3. Anthropic Compliance adapter.
4. Background cursor sync worker.
5. Identity mapping table.
6. GitHub enrichment for provider events.
7. Connector setup UI with test/sync/coverage status.

## Automation Slot Rules

The sequential automation must work one slot at a time. A slot is complete only when all gates pass:

- Backend endpoints touched by the slot are tested with real or seeded production-shaped data.
- Dashboard UX is tested with browser automation on desktop and mobile.
- Screenshots are captured for changed user flows.
- UX usefulness is assessed from the admin/end-user perspective: what problem does this solve, what decision can the user make, and what action can they take next?
- PR notes list org/account/repo, commands, endpoint URLs, data used, screenshots, and whether usage/cost values are provider-reported or Skillayer-estimated.
- The next slot starts only after the current slot is implemented, verified, documented, committed, pushed, and PR proof is updated.

If a slot is blocked by credentials or provider access, the automation must build the safe scaffolding, mark the provider pull as blocked with the exact missing credential/scope, and move only to the next unblocked slice when the current slot has no remaining local work.
