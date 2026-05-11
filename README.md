# Skillayer

Skillayer is a governance plane for AI coding agents. It helps platform, security, and engineering leadership answer the questions that matter once Claude Code, Codex, Cursor, GitHub Copilot, and internal agents are active across a company:

- What did agents do across repos, tools, sessions, and users?
- Which actions violated policy, and were they blocked, approved, or sent for more review?
- Which skills are trusted, stale, drifted, quarantined, or bound to policy?
- Can audit evidence be exported with attribution, policy decisions, and tamper-evident history?
- Where is fleet risk increasing across agents, repos, skills, and critical operations?

The current product direction is defined by `docs/PRD-v8.docx`: Skillayer v8 reduces the product to six enterprise surfaces and treats the older skill-generation system as the substrate underneath the governance experience.

## Product Surfaces

The migrated v8 app lives under `apps/dashboard/app/(v8)` and uses the Skillayer governance shell.

| Surface | Purpose | Key Routes |
| --- | --- | --- |
| Activity | The default investigation homepage for live agent activity, sessions, replay, and heatmaps. | `/activity`, `/activity/live-feed`, `/activity/sessions`, `/activity/replay`, `/activity/heatmap` |
| Policy | The control plane for YAML rules, violations, human approvals, quarantine, and starter policy packs. | `/policy/rules`, `/policy/violations`, `/policy/approvals`, `/policy/quarantine` |
| Audit | Compliance evidence, hash-chain verification, audit reports, SIEM-ready exports, and evidence packages. | `/audit/event-log`, `/audit/reports`, `/audit/exports`, `/audit/evidence-packages` |
| Skills | The artifact substrate: registry, score, drift, provenance, SkillQL, and repo coverage. | `/skills/registry`, `/skills/score`, `/skills/drift`, `/skills/provenance`, `/skills/skillql`, `/skills/repos` |
| Insights | Fleet trends and risk posture: KPIs, developer track, risky agents/repos, coverage SLA, and agent compliance metrics. | `/insights/fleet-kpis`, `/insights/developer-track`, `/insights/agent-compliance-metrics`, `/insights/intelligence-usage`, `/insights/access-grants`, `/insights/provider-coverage`, `/insights/coverage-sla` |
| Settings | Enterprise administration for teams, RBAC, SSO, connectors, admin audit, notifications, and billing. | `/settings/teams`, `/settings/rbac`, `/settings/sso`, `/settings/connectors`, `/settings/admin-audit` |

## Implemented v8 Capabilities

Current feature slices tracked in `FEATURES.md` include:

- Setup readiness next actions for the migrated Activity shell.
- URL-shareable Activity live-feed investigation filters.
- Policy starter-pack adoption with YAML preview, decision verbs, compliance tags, and signed-in apply controls.
- Policy review actions for approvals and quarantine, including persisted approval decisions.
- Coverage SLA critical-operation taxonomy loading from `apps/api/api/v8/insights/critical_ops.yaml`.
- Metadata-only agent compliance event ingestion for configured provider connectors, including model tier, access grants, tools/MCP, files, policy decisions, tokens, cost, latency, warnings, violations, and error metrics.
- Agent compliance sync readiness for configured connectors, including cursor-resume planning, retention windows, formal-vs-operational source type, provider-adapter blockers, and next actions before live pulls run.
- Queued agent compliance ingest jobs for metadata-only provider pages, with cursor state, job status, and no raw prompt/chat/file/tool-parameter storage.
- Policy evaluation of normalized agent compliance events, including matched rules, decisions, tags, and metadata-only retention in the migrated Policy surface.
- Activity agent compliance sessions that group normalized provider/coding-agent telemetry by session id with tools, files, tokens, cost, policy decisions, and risk while keeping raw content hidden.
- Consolidated agent compliance metrics for provider, developer, model, repo, session, tool, MCP, file, policy, approval, retention, token, cost, latency, warning, violation, and error rollups.
- Provider coverage monitoring for configured compliance connectors, highlighting silent, stale, and 30-day retention-risk sources before provider logs become unrecoverable.
- v8 Audit APIs for event log, reports, exports, evidence packages, hash-chain verification, and WORM root publishing.
- v8 Skills APIs and screens for registry, score, drift, provenance, SkillQL, and repos.
- v8 Settings APIs and screens for connectors and RBAC foundations.

## Architecture

This repo is a monorepo with three main product layers:

| Area | Location | Notes |
| --- | --- | --- |
| Dashboard | `apps/dashboard` | Next.js App Router dashboard. v8 routes live in `apps/dashboard/app/(v8)`. |
| API | `apps/api` | FastAPI backend. v8 routers live in `apps/api/api/v8`. |
| Shared database models | `packages/db` | SQLAlchemy models, migrations, and shared persistence definitions. |

Important v8 backend modules:

- `apps/api/api/v8/activity`: activity feed, sessions, replay, and heatmap data.
- `apps/api/api/v8/policy`: policy DSL, starter packs, approvals, quarantine, and RBAC hooks.
- `apps/api/api/v8/audit`: hash-chain audit log, reports, exports, WORM roots, and evidence packages.
- `apps/api/api/v8/skills`: registry, score, drift, provenance, SkillQL, and repo skill coverage.
- `apps/api/api/v8/insights`: fleet KPIs, risky agents/repos, coverage SLA, and consolidated agent compliance metrics.
- `apps/api/api/v8/settings`: connectors, RBAC, and admin settings foundations.

## Local Development

Install dependencies from the repo root:

```bash
npm install
python -m pip install -r apps/api/requirements.txt
```

Run the dashboard:

```bash
npm --workspace apps/dashboard run dev
```

Run the API with the environment expected by your local setup:

```bash
uvicorn apps.api.api.index:app --reload
```

Useful dashboard checks:

```bash
npm run lint --workspace apps/dashboard
npm run type-check --workspace apps/dashboard
npm run build --workspace apps/dashboard
```

Useful targeted API checks:

```bash
python -m pytest apps/api/tests/test_v8_activity_api.py -q
python -m pytest apps/api/tests/test_v8_policy.py -q
python -m pytest apps/api/tests/test_v8_insights.py -q
```

If `pytest` is unstable in a local Python version, run the touched test functions directly and document the reason in the PR.

## Feature Delivery Rules

Automation and human contributors should follow this loop:

1. Pick one coherent PRD feature slice.
2. Implement backend, frontend, docs, and tests as needed.
3. Verify every touched backend endpoint.
4. Verify migrated v8 UX with desktop and mobile screenshots.
5. Run a separate evaluator pass.
6. Fix evaluator blockers.
7. Commit and push only after evaluator approval.
8. Open or update a GitHub PR for the automation run with feature summary, verification results, evaluator result, and screenshot proof.

The migrated v8 shell is the UX source of truth. Do not target legacy `/dashboard` screenshots when a v8 route exists.

## Screenshot References

Existing migrated-shell screenshots are stored under:

- `docs/v8-refactor/screenshots`
- `docs/v8-refactor/screenshots/pr-1`

New feature PRs should attach fresh desktop and mobile screenshots for changed v8 screens. Screenshot capture failures should be treated as blockers unless explicitly accepted by the reviewer.

## Documentation Map

- `docs/PRD-v8.docx`: Product requirements and roadmap.
- `docs/v8-refactor/01-route-map.md`: v8 route inventory.
- `docs/v8-refactor/02-component-map.md`: dashboard component map.
- `docs/v8-refactor/03-api-map.md`: backend API map.
- `docs/v8-refactor/04-data-map.md`: data and persistence map.
- `docs/v8-refactor/05-flag-rollout.md`: IA/v8 rollout plan.
- `docs/v8-refactor/06-pr-sequence.md`: PR sequencing plan.
- `docs/v8-refactor/integration-log.md`: running integration and verification log.
- `FEATURES.md`: feature inventory and completed slices.

## Naming

Use **Skillayer** for the product, dashboard, SaaS, governance shell, and customer-facing documentation. Some package names, historical docs, generated examples, and CLI artifacts may still contain `skilgen` while the migration is in progress; do not use that legacy name for new customer-facing product copy.
