# Provider GitHub Enrichment Evaluator

Date: 2026-05-19

## Slot

Enterprise roadmap slot 6: GitHub enrichment for provider events.

## Scope Verified

- Provider compliance events now preserve GitHub context when events include repo, PR number, PR id, branch, head SHA, commit SHA, or Git URLs.
- Provider events are joined to `repos` and `pull_requests` when matching rows exist.
- Missing joins are labeled as coverage gaps instead of silently fabricating PR ids.
- Intelligence usage exposes `github_enrichment_status`, `github_enrichment_gap`, and Git links for Tokens by PR / Code Push.

## Test Data

Org/account/repo:

- Org: `org_skilgen`
- Repo: `ravichanduummadisetti/skilgen`

Seeded production-shaped local proof data:

- `OpenAI Compliance Platform` formal compliance event, PR #11, `provider_reported` cost/tokens, `github_enrichment_status=matched`, Git URL `https://github.com/skilgen/skilgen/pull/11`.
- `Anthropic Compliance API` formal compliance event, commit `e60a760`, `provider_reported` cost/tokens, `github_enrichment_status=missing`, coverage gap explaining no local PR/commit row matched.

## Endpoint Proof

- `GET http://127.0.0.1:8000/v8/orgs/org_skilgen/settings/connectors/agent-compliance`
  - OpenAI and Anthropic connectors were enabled, encrypted, connected, and in fixture success state.
- `GET http://127.0.0.1:8000/v8/orgs/org_skilgen/insights/intelligence-usage?window_days=30`
  - Returned top PR/code-push rows with Git URLs, `github_enrichment_status`, `github_enrichment_gap`, token totals, and cost.

## Commands

```bash
python -m pytest apps/api/tests/test_v8_settings_rbac.py apps/api/tests/test_v8_insights.py -q
npm --workspace apps/dashboard run type-check -- --pretty false
curl -sS 'http://127.0.0.1:8000/v8/orgs/org_skilgen/insights/intelligence-usage?window_days=30' | jq '.pr_push_usage[:3]'
```

## Browser Proof

URL:

- `http://127.0.0.1:4325/insights/intelligence-usage`

Screenshots:

- Desktop: `docs/v8-refactor/screenshots/2026-05-19-provider-github-enrichment/intelligence-usage-desktop.png`
- Mobile: `docs/v8-refactor/screenshots/2026-05-19-provider-github-enrichment/intelligence-usage-mobile.png`

Browser checks:

- Desktop: `matched=1 links=2 gaps=11`
- Mobile: `matched=1 links=2 gaps=11`
- In-app browser check found the visible `Skillayer enterprise provider ingestion` PR card, `Open Git evidence` links, and `Git coverage gap` labels.

## Usefulness Assessment

Decision enabled:

- Admins can see which provider-reported coding-agent spend maps to a real GitHub PR or commit.
- Admins can click to the PR/commit evidence when the provider supplied enough metadata.
- Admins can see coverage gaps when provider metadata does not join cleanly, which makes the next action clear: install GitHub enrichment or fix provider metadata coverage.

No UX compromise:

- The Intelligence usage page keeps Tokens by PR / Code Push as the decision surface.
- Rows with Git evidence show a direct link.
- Rows without a clean join show a visible coverage-gap explanation.
- Cost and token values remain metadata-only and provider provenance is preserved as `provider_reported` when supplied by provider fixtures.

## Result

Evaluator result: pass.

Remaining enterprise work moves to roadmap slot 7: connector setup UI with test/sync/coverage status.
