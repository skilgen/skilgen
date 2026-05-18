# Feature Usefulness Audit - Skilgen V8

Local verification data:

- Org: `Skilgen`
- Repo: `ravichanduummadisetti/skilgen`
- Session: `sess_skilgen_codex_1`
- Evidence: `docs/screenshots/local-qa-20260511/`

## Product Standard

Every feature must answer a real operator question:

- What happened?
- Why does it matter?
- What should I do next?
- What proof can I attach to a PR, audit, or review?

If a route only renders raw telemetry, it is not useful enough.

## Useful Now

| Area | Feature | Useful question answered | Status |
| --- | --- | --- | --- |
| Activity | Live feed | What did agents do in this repo recently? | Useful with real session fallback |
| Activity | Sessions | Which agent sessions touched code, files, and skills? | Useful |
| Activity | Replay | Can I inspect one agent session end to end? | Useful after null timeline fix |
| Activity | Heatmap | When is peak agent activity and where do review signals cluster? | Useful after summary metrics |
| Policy | Rules | What actions require review, denial, or logging? | Useful after Skilgen rules data |
| Policy | Approvals | What needs a human decision before merge/release impact? | Useful |
| Policy | Agent events | Which agent events matched policy and why? | Useful |
| Policy | Quarantine | Which weak or risky skills should be paused or retired? | Useful |
| Skills | Repos | Which repos are connected and covered by generated skills? | Useful |
| Insights | Intelligence usage | Where are expensive models overused, and what should be downgraded? | Useful after intelligence layer build |

## Needs Rebuild Before Shipping Broadly

| Area | Feature | Gap | Better product shape |
| --- | --- | --- | --- |
| Activity | Compliance events | Too metadata-heavy by itself | Show investigation timeline: provider, actor, model, repo, decision, evidence hash |
| Activity | Compliance sessions | Useful data, weak decision framing | Group by “needs review”, “high token spend”, “policy matched”, “safe” |
| Audit | Event log | Can become a raw log dump | Add saved filters for PR evidence, policy decisions, model usage, and export readiness |
| Audit | Evidence packages | Valuable but abstract | Make it a PR/auditor package builder with screenshots, commands, data, and hash chain status |
| Audit | WORM roots | Too compliance-internal | Keep as secondary proof, link from evidence packages |
| Settings | Connectors | Useful, but should show data coverage health | Add “last useful event seen” and missing-data warnings |

## Secondary / Admin-Only

| Area | Feature | Reason |
| --- | --- | --- |
| Settings | Billing | Admin utility, not core agent governance |
| Settings | SSO/RBAC/Teams | Admin utility; useful when tied to approvals |
| Audit | Exports | Useful as an output action, not a primary discovery surface |

## Intelligence Layer Requirements

The intelligence layer should stay centered on:

- Peak usage by hour.
- Tokens and cost per PR/code push.
- Task type by model and model tier.
- High-reasoning usage on low-complexity tasks.
- Recommendations to downgrade to fast or balanced models unless risk, architecture, or failing tests justify escalation.
- Evidence that can be copied into PR validation: org, repo, commands, URLs, data, screenshots.

Implemented in this pass:

- `GET /v8/orgs/{org_id}/insights/intelligence-usage` now supports token/cost totals, peak usage, task-model usage, PR/code-push usage, and routing recommendations.
- `/insights/intelligence-usage` now renders model routing recommendations, task type by model, tokens per PR/code push, peak usage, total tokens, and cost.
