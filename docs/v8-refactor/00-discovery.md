# v8 Refactor Phase A Discovery

Date: 2026-05-03  
Branch: `v8/00-discovery`  
Kickoff commit: `2d034e6` (`chore(v8): add AGENTS.md brief and PRD-v8 for refactor kickoff`)  
Sources: `docs/AGENTS.md` v8 brief, `docs/PRD-v8.docx`, repo inspection, `gh pr list`, Alembic files, and a Python coverage run.

## 1. Repository layout

Top three levels, annotated:

```text
.
|-- .github/                         CI, release, Vercel, and Skilgen sync workflows.
|-- .skilgen/                        Generated local Skilgen state, telemetry, policy, and memory.
|-- apps/
|   |-- api/                         FastAPI service, Alembic migrations, API tests, Vercel config.
|   |-- dashboard/                   Next.js 15 dashboard app; authenticated Skillayer product UI.
|   |-- web/                         Next.js marketing/web app.
|   `-- worker/                      Worker image and Celery/async worker entrypoint.
|-- docs/
|   |-- AGENTS.md                    v8 governance-plane brief used for this work.
|   |-- PRD-v8.docx                  v8 product source of truth.
|   |-- screenshots/                 Existing QA and smoke screenshots.
|   |-- specs/                       Public specs such as AgentRun.
|   `-- v8-refactor/                 New discovery/planning docs for this refactor.
|-- extensions/
|   |-- jetbrains-skillayer/         JetBrains extension skeleton.
|   `-- vscode-skillayer/            VS Code extension package.
|-- infra/
|   |-- docker/                      Docker Compose deployment configs.
|   |-- helm/                        Helm chart for Skillayer.
|   `-- scripts/                     Install/deploy helper scripts.
|-- packages/
|   |-- config/                      Shared TS config, ESLint, Tailwind config.
|   |-- db/                          SQLAlchemy models, DB config, package-level Alembic.
|   |-- types/                       Shared TypeScript types.
|   `-- ui/                          Shared UI package.
|-- skilgen/                         OSS CLI/library package. Out of scope for v8 app refactor.
|-- tests/                           Python tests for OSS CLI plus app-adjacent functionality.
|-- package.json                     npm workspaces root.
`-- pyproject.toml                   Python package and dependency config.
```

Stack note: the brief says API service code is under `apps/api/skillayer/`, but the actual app uses `apps/api/api/`. The auth entrypoint is `apps/api/api/auth.py`. The hook exists at `skilgen/hooks/claude_code_hook.py`, not repo root. User approved treating `apps/api/api/` as the effective API root for Phase A.

## 2. Sidebar inventory

Current sidebar is defined inline in `apps/dashboard/app/dashboard/layout.tsx`, not a standalone `Sidebar.tsx`. It renders:

- `primaryNavItems` at `apps/dashboard/app/dashboard/layout.tsx:225`.
- `secondaryNavGroups` at `apps/dashboard/app/dashboard/layout.tsx:237`.
- a conditional `Admin` item when `NEXT_PUBLIC_ADMIN_EMAILS` contains the signed-in user email.

| Item | Route | Rendering file |
| --- | --- | --- |
| Overview | `/dashboard` | `apps/dashboard/app/dashboard/page.tsx` |
| Repos | `/dashboard/repos` | `apps/dashboard/app/dashboard/repos/page.tsx` |
| Skills | `/dashboard/skills` | `apps/dashboard/app/dashboard/skills/page.tsx` |
| PR Inbox | `/dashboard/agent-prs` | `apps/dashboard/app/dashboard/agent-prs/page.tsx` |
| Review | `/dashboard/review` | `apps/dashboard/app/dashboard/review/page.tsx` |
| Agent Scorecard | `/dashboard/agent-scorecard` | `apps/dashboard/app/dashboard/agent-scorecard/page.tsx` |
| AI Readiness | `/dashboard/ai-readiness` | `apps/dashboard/app/dashboard/ai-readiness/page.tsx` |
| Connect Agent | `/dashboard/connect` | `apps/dashboard/app/dashboard/connect/page.tsx` |
| Settings | `/dashboard/settings` | `apps/dashboard/app/dashboard/settings/page.tsx` |
| My Code Today | `/dashboard/my-code-today` | `apps/dashboard/app/dashboard/my-code-today/page.tsx` |
| Leaderboard | `/dashboard/leaderboard` | `apps/dashboard/app/dashboard/leaderboard/page.tsx` |
| Analytics | `/dashboard/analytics` | `apps/dashboard/app/dashboard/analytics/page.tsx` |
| Agent Performance | `/dashboard/eval` | `apps/dashboard/app/dashboard/eval/page.tsx` |
| Heatmap | `/dashboard/heatmap` | `apps/dashboard/app/dashboard/heatmap/page.tsx` |
| Intelligence | `/dashboard/intelligence` | `apps/dashboard/app/dashboard/intelligence/page.tsx` |
| SkillQL | `/dashboard/skillql` | `apps/dashboard/app/dashboard/skillql/page.tsx` |
| Skill Gaps | `/dashboard/eval/gaps` | `apps/dashboard/app/dashboard/eval/gaps/page.tsx` |
| Skill Debt | `/dashboard/debt` | `apps/dashboard/app/dashboard/debt/page.tsx` |
| Knowledge Risk | `/dashboard/knowledge-risk` | `apps/dashboard/app/dashboard/knowledge-risk/page.tsx` |
| Red Flags | `/dashboard/red-flags` | `apps/dashboard/app/dashboard/red-flags/page.tsx` |
| A/B Tests | `/dashboard/eval/ab-tests` | `apps/dashboard/app/dashboard/eval/ab-tests/page.tsx` |
| Registry | `/dashboard/registry` | `apps/dashboard/app/dashboard/registry/page.tsx` |
| Sessions | `/dashboard/sessions` | `apps/dashboard/app/dashboard/sessions/page.tsx` |
| Digest | `/dashboard/digest` | `apps/dashboard/app/dashboard/digest/page.tsx` |
| Autopilot | `/dashboard/autopilot` | `apps/dashboard/app/dashboard/autopilot/page.tsx` |
| Sources | `/dashboard/sources` | `apps/dashboard/app/dashboard/sources/page.tsx` |
| Coverage SLA | `/dashboard/sla` | `apps/dashboard/app/dashboard/sla/page.tsx` |
| Half-life | `/dashboard/half-life` | `apps/dashboard/app/dashboard/half-life/page.tsx` |
| Dependency Graph | `/dashboard/registry/dependency-graph` | `apps/dashboard/app/dashboard/registry/dependency-graph/page.tsx` |
| Teams | `/dashboard/teams` | `apps/dashboard/app/dashboard/teams/page.tsx` |
| Audit | `/dashboard/audit` | `apps/dashboard/app/dashboard/audit/page.tsx` |
| Admin | `/dashboard/admin` | `apps/dashboard/app/dashboard/admin/page.tsx` |

Additional dashboard routes not in the sidebar include `/dashboard/memory` (redirects to `/dashboard/ai-readiness`), `/dashboard/onboarding`, `/dashboard/upgrade`, nested repo/skill/time-machine/version routes, registry detail routes, admin child routes, session details, billing, and `/dashboard/connect/agent-run-spec`.

## 3. v7 to v8 mapping audit

PRD §3.3 heading: "What v7 items map where".

| v7 item | PRD disposition | v8 location | Found in code? |
| --- | --- | --- | --- |
| Overview | Cut | Activity is the new homepage | Yes: `/dashboard` |
| Repos | Merge | Skills -> Repos tab | Yes: `/dashboard/repos` |
| Skills | Keep | Skills top-level | Yes: `/dashboard/skills` |
| PR Inbox | Merge | Activity filter `action_type = pr_open` | Yes: `/dashboard/agent-prs` |
| Review | Merge | Policy -> Approvals | Yes: `/dashboard/review` |
| Agent Scorecard | Merge | Insights -> Risky agents | Yes: `/dashboard/agent-scorecard` |
| AI Readiness | Cut | Remove entirely | Yes: `/dashboard/ai-readiness` |
| Connect Agent | Move | Settings -> Connectors | Yes: `/dashboard/connect` |
| My Code Today | Cut | Remove | Yes: `/dashboard/my-code-today` |
| Leaderboard | Cut | Remove | Yes: `/dashboard/leaderboard` |
| Analytics | Merge | Insights -> Fleet KPIs | Yes: `/dashboard/analytics` |
| Agent Performance | Merge | Insights -> Risky agents inverse view | Yes: `/dashboard/eval` |
| Heatmap | Merge | Activity -> Heatmap tab | Yes: `/dashboard/heatmap` |
| Intelligence | Cut | Remove | Yes: `/dashboard/intelligence` |
| SkillQL | Merge | Skills -> SkillQL tab | Yes: `/dashboard/skillql` |
| Skill Gaps | Merge | Skills -> Score filter coverage | Yes: `/dashboard/eval/gaps` |
| Skill Debt | Merge | Skills -> Score filters structure/freshness | Yes: `/dashboard/debt` |
| Knowledge Risk | Merge | Insights -> Risky repos | Yes: `/dashboard/knowledge-risk` |
| Red Flags | Merge | Policy -> Violations | Yes: `/dashboard/red-flags` |
| A/B Tests | Cut | Revisit at `$5M ARR` | Yes: `/dashboard/eval/ab-tests` |
| Registry | Merge | Skills -> Registry tab | Yes: `/dashboard/registry` |
| Sessions | Merge | Activity -> Sessions tab | Yes: `/dashboard/sessions` |
| Digest | Cut | Notification setting | Yes: `/dashboard/digest` |
| Autopilot | Merge | Policy -> Rules | Yes: `/dashboard/autopilot` |
| Sources | Merge | Skills -> Repos tab | Yes: `/dashboard/sources` |
| Coverage SLA | Merge | Insights -> Coverage SLA tab | Yes: `/dashboard/sla` |
| Half-life | Merge | Skills -> Drift tab | Yes: `/dashboard/half-life` |
| Dependency Graph | Merge | Skills -> Provenance tab | Yes: `/dashboard/registry/dependency-graph` |
| Teams | Merge | Settings -> Teams | Yes: `/dashboard/teams` |
| Audit (v7) | Promote | Audit top-level | Yes: `/dashboard/audit` |

PRD-named v7 item missing from code: none.

Sidebar item in code not named by PRD §3.3: `Admin` (`/dashboard/admin`), conditional for users in `NEXT_PUBLIC_ADMIN_EMAILS`.

## 4. API surface inventory

Effective API root is `apps/api/api/`. FastAPI includes routers in `apps/api/api/index.py`.

Where possible, endpoints are mapped to sidebar items:

- Activity: feed, sessions, agent PRs, heatmap, replay, commits/check.
- Policy: review, red flags, policies, policy-check, autopilot.
- Audit: audit-log, audit exports/webhook, manifest endpoints.
- Skills: skills, repos/skills, registry, skillql, sources, half-life, dependency graph.
- Insights: stats, analytics, runtime breakdown, agent scorecard, leaderboard, knowledge risk, SLA.
- Settings: org settings, api-key, connect/status, Slack/email digest, Stripe, teams/admin.

Every route endpoint found under `apps/api/api/routes/`:

```text
admin.py
  POST /admin/rollup-usage
  GET /admin/overview
  GET /admin/orgs
  GET /admin/orgs/{org_id}
  GET /admin/orgs/{org_id}/usage
  POST /admin/orgs/{org_id}/suspend
  POST /admin/orgs/{org_id}/unsuspend
  DELETE /admin/orgs/{org_id}
  GET /admin/users
  GET /admin/logins
  GET /admin/metrics/export

agent_runs.py
  POST /orgs/{org_id}/agent-runs

autopilot.py
  GET /orgs/{org_id}/autopilot/queue
  POST /orgs/{org_id}/autopilot/trigger
  POST /orgs/{id}/autopilot/deduplicate
  GET /orgs/{org_id}/autopilot/tasks/{task_id}/preview
  POST /orgs/{org_id}/autopilot/tasks/{task_id}/skip
  POST /orgs/{org_id}/autopilot/{task_id}/generate-improvement
  POST /orgs/{org_id}/autopilot/{task_id}/approve
  POST /orgs/{org_id}/autopilot/tasks/{task_id}/approve
  POST /orgs/{org_id}/autopilot/{task_id}/reject

cron.py
  POST /cron/standup
  POST /cron/digest

digest.py
  GET /orgs/{org_id}/digest/config
  PUT /orgs/{org_id}/digest/config
  POST /orgs/{org_id}/digest/preview
  GET /orgs/{org_id}/digest/preview
  POST /orgs/{org_id}/digest/send-now
  POST /orgs/{org_id}/digest/send

eval.py (included with prefix /eval)
  POST /eval/orgs/{org_id}/tasks
  POST /eval/orgs/{org_id}/tasks/batch
  GET /eval/orgs/{org_id}/eval/summary
  GET /eval/orgs/{org_id}/eval/sessions
  POST /eval/orgs/{org_id}/eval/sessions/{session_id}/outcome
  GET /eval/orgs/{org_id}/roi
  POST /eval/orgs/{org_id}/ab-tests
  GET /eval/orgs/{org_id}/ab-tests
  GET /eval/orgs/{org_id}/ab-tests/{test_id}
  POST /eval/orgs/{org_id}/ab-tests/{test_id}/conclude
  GET /eval/orgs/{org_id}/skill-gaps
  GET /eval/orgs/{org_id}/eval/gaps
  PATCH /eval/orgs/{org_id}/skill-gaps/{gap_id}
  POST /eval/orgs/{org_id}/skill-gaps/{gap_id}/acknowledge
  POST /eval/orgs/{org_id}/eval/gaps/{gap_id}/acknowledge
  POST /eval/orgs/{org_id}/skill-gaps/{gap_id}/resolve
  POST /eval/orgs/{org_id}/eval/gaps/{gap_id}/resolve
  GET /eval/orgs/{org_id}/benchmark
  POST /eval/orgs/{org_id}/eval-sessions

feed.py
  GET /orgs/{org_id}/feed/recent
  GET /orgs/{org_id}/feed/stream

health.py
  GET /health

me.py
  GET /me/org

metrics.py
  GET /metrics

orgs.py
  GET /orgs/bootstrap
  GET /orgs/{org_id}/setup-status
  GET /orgs/{org_id}/connect/status
  GET /orgs/{org_id}/api-key
  POST /orgs/{org_id}/auth/login-event
  POST /orgs/{org_id}/api-key/rotate
  GET /orgs/{org_id}/action-items
  GET /orgs/{org_id}/sources
  POST /orgs/{org_id}/sources/test
  POST /orgs/{org_id}/sources/connect
  POST /orgs/{org_id}/sources/refresh
  GET /orgs/{org_id}/enterprise-skills
  POST /orgs/{org_id}/enterprise-skills
  POST /orgs/{org_id}/skills/{skill_id}/push
  GET /orgs/{org_id}/intelligence/insights
  GET /orgs/{org_id}
  GET /orgs/{org_id}/repos
  GET /orgs/{org_id}/stats
  GET /orgs/{org_id}/overview/score-trend
  POST /orgs/{org_id}/repos/{repo_id}/analyse
  GET /orgs/{org_id}/skill-heatmap
  GET /orgs/{org_id}/analytics/criticality
  GET /orgs/{org_id}/analytics/skill-coload-tree
  POST /orgs/{org_id}/analytics/improvement-suggestions
  GET /orgs/{org_id}/analytics/highlight-risks
  GET /orgs/{org_id}/runtime-breakdown
  GET /orgs/{org_id}/sessions
  POST /orgs/{org_id}/sessions/{session_id}/tag
  GET /orgs/{org_id}/intelligence
  GET /orgs/{org_id}/memory-queue
  PATCH /orgs/{org_id}/memory-queue/{stub_id}
  GET /orgs/{org_id}/knowledge-velocity
  GET /orgs/{org_id}/red-flags
  GET /orgs/{org_id}/red-flags/dismissed
  POST /orgs/{org_id}/red-flags/dismiss
  DELETE /orgs/{org_id}/red-flags/dismiss
  GET /orgs/{org_id}/half-life
  POST /orgs/{org_id}/half-life/refresh
  POST /orgs/{org_id}/half-life/buffer
  GET /orgs/{org_id}/skill-debt
  POST /orgs/{org_id}/debt/run-analysis
  GET /orgs/{org_id}/debt/gaps
  POST /orgs/{org_id}/debt/gaps/{gap_id}/generate
  POST /orgs/{org_id}/debt/gaps/generate-all
  POST /orgs/{org_id}/dependency-graph/compute
  GET /orgs/{org_id}/dependency-graph/status
  GET /orgs/{org_id}/dependency-graph/repo/{repo_id}
  GET /orgs/{org_id}/dependency-graph/cross-repo
  GET /orgs/{org_id}/team-rollup
  GET /orgs/{org_id}/teams/rollup
  GET /orgs/{org_id}/teams/rollup-summary
  GET /orgs/{org_id}/audit-log
  GET /orgs/{org_id}/audit-log/export
  GET /orgs/{org_id}/audit-log/event-types
  GET /orgs/{org_id}/audit-log/stats
  POST /orgs/{org_id}/audit-log/webhook
  GET /orgs/{org_id}/policies
  POST /orgs/{org_id}/policies
  PATCH /orgs/{org_id}/policies/{policy_id}
  DELETE /orgs/{org_id}/policies/{policy_id}
  GET /orgs/{org_id}/policy-templates
  GET /orgs/{org_id}/policy-check
  POST /orgs/{org_id}/policy-check/ci
  GET /orgs/{org_id}/llm-config
  POST /orgs/{org_id}/llm-config
  DELETE /orgs/{org_id}/llm-config
  POST /orgs/{org_id}/llm-config/test
  POST /orgs/{org_id}/skillql
  GET /orgs/{org_id}/skillql/suggestions
  POST /orgs/{org_id}/skills/search
  GET /orgs/{org_id}/knowledge-concentration
  POST /orgs/{org_id}/skill-ai-actions/preview
  POST /orgs/{org_id}/skill-ai-actions/push
  GET /orgs/{org_id}/agent-connection/status
  POST /orgs/{org_id}/knowledge-risk/{risk_id}/generate-and-push
  POST /orgs/{org_id}/knowledge-risk/generate-all
  POST /orgs/{org_id}/knowledge-risk/{risk_id}/dismiss
  GET /orgs/{org_id}/teams/summary
  GET /orgs/{org_id}/teams
  GET /orgs/{org_id}/available-repos
  POST /orgs/{org_id}/refresh-repo-languages
  POST /orgs/{org_id}/connect-repos
  GET /orgs/{org_id}/coverage-summary
  GET /orgs/{org_id}/agent-scorecard
  GET /orgs/{org_id}/developer-leaderboard
  GET /orgs/{org_id}/agent-prs
  GET /orgs/{org_id}/agent-prs/{pr_id}
  GET /orgs/{org_id}/agent-prs/{pr_id}/manifest
  POST /orgs/{org_id}/agent-prs/{pr_id}/manifest/verify
  GET /orgs/{org_id}/my-code-today
  GET /orgs/{org_id}/standup
  PATCH /orgs/{org_id}/settings/slack
  PATCH /orgs/{org_id}/settings/email-digest
  POST /orgs/{org_id}/digest/send
  POST /orgs/{org_id}/standup/send
  GET /orgs/{org_id}/memory-score
  GET /orgs/{org_id}/settings
  POST /orgs/{org_id}/settings/anthropic-key
  PATCH /orgs/{org_id}/settings
  POST /orgs/{org_id}/test-notification
  GET /orgs/{org_id}/analytics
  POST /orgs/{org_id}/sync-analytics

registry.py
  POST /registry/orgs/{org_id}/publish
  GET /registry/orgs/{org_id}/entries
  GET /registry/orgs/{org_id}/skill-map
  GET /registry/orgs/{org_id}/skill-tree
  POST /registry/orgs/{org_id}/chat-create
  POST /registry/orgs/{org_id}/chat-create/push
  POST /registry/orgs/{org_id}/search
  GET /registry/orgs/{org_id}/entries/{entry_id}
  POST /registry/orgs/{org_id}/entries/{entry_id}/install
  PATCH /registry/orgs/{org_id}/entries/{entry_id}/deprecate
  GET /registry/orgs/{org_id}/dependency-graph
  POST /registry/orgs/{org_id}/dependency-scan
  GET /registry/marketplace
  GET /registry/marketplace/{entry_id}
  POST /registry/marketplace/{entry_id}/install
  GET /registry/orgs/{org_id}/half-life
  POST /registry/orgs/{org_id}/half-life/refresh
  GET /registry/skills/{skill_id}/half-life
  GET /registry/orgs/{org_id}/compatibility-matrix
  POST /registry/orgs/{org_id}/import
  GET /registry
  POST /registry/publish
  POST /registry/import-skill-file
  GET /registry/{registry_id}
  POST /registry/{registry_id}/import

repos.py
  GET /repos/{repo_id}
  GET /repos/{repo_id}/score-badge
  GET /repos/{repo_id}/badge.svg
  GET /repos/{repo_id}/skills
  GET /repos/{repo_id}/skills/{skill_id}/snapshots
  GET /repos/{repo_id}/skills/{skill_id}/snapshots/{snapshot_id}
  GET /repos/{repo_id}/skills/{skill_id}/snapshots/{snapshot_id}/diff
  POST /repos/{repo_id}/skills/{skill_id}/snapshots
  POST /repos/{repo_id}/skills/{skill_id}/rollback/{snapshot_id}
  GET /repos/{repo_id}/skills/{skill_id}/usage-stats
  GET /repos/{repo_id}/skills/snapshot
  GET /repos/{repo_id}/skills/timeline
  GET /repos/{repo_id}/skills/{skill_id}/improvement-plan
  POST /repos/{repo_id}/skills/{skill_id}/improve
  PATCH /repos/{repo_id}/skills/{skill_id}/content
  POST /repos/{repo_id}/sessions
  GET /repos/{repo_id}/sessions
  GET /repos/{repo_id}/knowledge-velocity
  GET /repos/{repo_id}/score-history
  GET /repos/{repo_id}/score-forecast
  GET /repos/{repo_id}/skills/{skill_id}/versions/{version_id}/diff
  GET /repos/{repo_id}/skill-sources
  GET /repos/{repo_id}/dependencies
  GET /repos/{repo_id}/runs
  GET /repos/{repo_id}/prs/{pr_number}/attribution
  GET /repos/{repo_id}/prs/{pr_number}/risk
  POST /repos/{repo_id}/commits/{sha}/check
  POST /repos/{repo_id}/check
  POST /repos/{repo_id}/analyse
  POST /repos/{repo_id}/analyze-source
  POST /repos/{repo_id}/backfill-categories
  POST /repos/{repo_id}/sync-analytics
  GET /repos/{repo_id}/skills/load

review.py
  POST /repos/{repo_id}/review
  POST /orgs/{org_id}/review/scan-diff
  POST /orgs/{org_id}/review/scan-repo-prs
  GET /orgs/{org_id}/review/scan-status/{job_id}
  GET /orgs/{org_id}/review/history
  GET /repos/{repo_id}/review/history

sessions.py
  POST /repos/{repo_id}/sessions
  PATCH /repos/{repo_id}/sessions/{session_id}
  POST /repos/{repo_id}/sessions/artifacts
  POST /repos/{repo_id}/sessions/{session_id}/close
  GET /repos/{repo_id}/agent-sessions
  GET /repos/{repo_id}/agent-sessions/{session_id}
  GET /repos/{repo_id}/sessions/{session_id}/replay
  GET /orgs/{org_id}/sessions

skills.py
  GET /skills/{skill_id}
  GET /skills/{skill_id}/versions
  GET /skills/{skill_id}/versions/{version_id}
  POST /skills/{skill_id}/usage

sla.py
  GET /orgs/{org_id}/sla
  POST /orgs/{org_id}/sla
  PUT /orgs/{org_id}/sla/{policy_id}
  DELETE /orgs/{org_id}/sla/{policy_id}
  POST /orgs/{org_id}/sla/{policy_id}/check

slack.py
  POST /webhooks/slack/command

stripe.py
  POST /stripe/webhook
  POST /stripe/create-checkout-session
  POST /stripe/create-portal-session
  GET /stripe/subscription

webhook.py
  POST /webhook/github

worker.py
  POST /worker/analyse
```

## 5. DB schema inventory

`DATABASE_URL`, `DATABASE_URL_UNPOOLED`, `POSTGRES_URL`, and `PGHOST` are unset in the local environment, and no live non-secret DB connection was available. Row counts were therefore not queried. Every row count below is `not available`.

Tables found from `packages/db/models` and `apps/api/alembic/versions`:

| Table | Row count | Evidence |
| --- | --- | --- |
| `ab_tests` | not available | model + migration |
| `agent_load_events` | not available | model + migration |
| `agent_sessions` | not available | model + migration |
| `agent_tasks` | not available | model + migration |
| `analysis_runs` | not available | model + migration |
| `audit_events` | not available | model + migration |
| `autopilot_tasks` | not available | model + migration |
| `commits` | not available | model + migration |
| `coverage_gaps` | not available | model + migration |
| `cross_repo_opportunities` | not available | model + migration |
| `dependencies` | not available | model + migration |
| `dependency_graph_cache` | not available | model + migration |
| `digest_configs` | not available | model + migration |
| `eval_sessions` | not available | model + migration |
| `flag_dismissals` | not available | model + migration |
| `half_life_cache` | not available | model + migration |
| `jobs` | not available | model + migration |
| `login_events` | not available | model only |
| `marketplace_installs` | not available | model + migration |
| `org_llm_configs` | not available | model + migration |
| `org_policies` | not available | model + migration |
| `orgs` | not available | model + migration |
| `pr_attributions` | not available | model + migration |
| `pr_comments` | not available | model + migration |
| `pr_review_findings` | not available | model + migration |
| `pr_reviews` | not available | model + migration |
| `pull_requests` | not available | model + migration |
| `registry_skills` | not available | model + migration |
| `repos` | not available | model + migration |
| `review_runs` | not available | model + migration |
| `score_history` | not available | model + migration |
| `skill_dependencies` | not available | model + migration |
| `skill_gaps` | not available | model + migration |
| `skill_half_lives` | not available | model + migration |
| `skill_memory_stubs` | not available | model + migration |
| `skill_registry_entries` | not available | model + migration |
| `skill_snapshots` | not available | model only |
| `skill_usage_events` | not available | model + migration |
| `skill_versions` | not available | model + migration |
| `skills` | not available | model + migration |
| `sla_policies` | not available | model + migration |
| `source_connections` | not available | model + migration |

Tables matching v7 cut concepts:

- `ab_tests`: PRD says A/B Tests are cut/revisit at `$5M ARR`.
- `digest_configs`: PRD says Digest is cut and becomes notification settings.
- No tables found with names matching `ai_readiness_*`, `leaderboard_*`, `my_code_today_*`, or `intelligence_*`.

## 6. Existing feature flags

No dedicated feature-flag framework was found. No `IA_V8` flag exists yet.

Mechanisms in use:

| Mechanism | Current local value | Example/default value | Notes |
| --- | --- | --- | --- |
| Environment variables | Mostly unset locally | `apps/api/.env.example`, `apps/dashboard/.env.example` | Runtime configuration, deploy mode, admin gating, integrations. |
| `DEPLOYMENT_MODE` | unset | `workos` | Controls auth behavior per `apps/api/.env.example`. |
| `NEXT_PUBLIC_ADMIN_EMAILS` | unset | none | Gates Admin sidebar item and admin pages in dashboard. |
| `NEXT_PUBLIC_POSTHOG_KEY` | unset | empty | Enables PostHog only in production if set. |
| `DATABASE_URL` / `DATABASE_URL_UNPOOLED` | unset | placeholder | Required for API DB access/migrations. |
| `CRON_SECRET` | unset | empty | Protects cron endpoints. |
| `QSTASH_*` | unset | placeholders | Background queue/webhook signing configuration. |
| `STRIPE_*` | unset | placeholders | Billing integration configuration. |
| Org DB settings | not queryable locally | `orgs.settings`, notification columns | Used for app settings; no v8 flag row currently exists. |
| `flag_dismissals` table | not queryable locally | DB table | Tracks red-flag dismissals, not feature rollout flags. |

Current values per environment could not be fully enumerated because Vercel/Neon environment variables are not available locally and should not be read from `.env` secrets. The checked-in examples show intended defaults but not deployed values.

## 7. Test coverage per package

Command run:

```bash
uv run --with coverage coverage run -m pytest tests apps/api/tests
uv run --with coverage coverage report --include='skilgen/*,apps/api/*,packages/*,apps/worker/*'
```

Result: `734 passed, 266 warnings in 348.36s`.

Package-level Python coverage:

| Package | Coverage | Below 60%? |
| --- | ---: | --- |
| `apps/api` | 66.8% | No |
| `packages/db` | 97.2% | No |
| `skilgen` | 80.6% | No |

Total included Python coverage: 75%.

Notable low-coverage files inside otherwise passing packages:

- `apps/api/api/analysis.py`: 23%
- `apps/api/api/github.py`: 25%
- `apps/api/api/pr_comment.py`: 56%
- `apps/api/api/routes/admin.py`: 36%
- `apps/api/api/routes/digest.py`: 28%
- `apps/api/api/routes/feed.py`: 24%
- `apps/api/api/routes/orgs.py`: 56%
- `apps/api/api/routes/registry.py`: 46%
- `apps/api/api/routes/repos.py`: 47%
- `apps/api/api/routes/review.py`: 43%
- `apps/api/api/routes/sessions.py`: 51%
- `apps/api/api/routes/worker.py`: 59%
- `apps/api/api/services/autopilot.py`: 49%
- `apps/api/api/services/github_pr.py`: 16%
- `apps/api/api/services/half_life.py`: 12%
- `apps/api/api/services/knowledge_concentration.py`: 45%
- `apps/api/api/services/llm_config.py`: 33%
- `apps/api/api/services/skill_generator.py`: 19%

Frontend coverage: no Jest/Vitest unit coverage script or coverage artifact found. Dashboard has E2E specs under `apps/dashboard/e2e`, but no package-level coverage percentage was available.

## 8. Merged PRs and recent migrations

Merged PRs in the last 30 days from `RaviChanduUmmadisetti/skilgen`:

| PR | Merged | Title | Branch |
| --- | --- | --- | --- |
| #23 | 2026-04-30 | fix: restore dashboard data visibility | `qa/fix-dashboard-data-surfaces` |
| #22 | 2026-04-30 | fix: restore missing analytics data surfaces | `qa/fix-connect-runtime-status` |
| #21 | 2026-04-30 | fix: merge runtime aliases in analytics | `qa/fix-runtime-breakdown-aliases` |
| #20 | 2026-04-30 | fix: count active agents from skill loads | `qa/fix-active-agent-stats` |
| #19 | 2026-04-30 | fix: handle timezone-aware PR timestamps | `qa/fix-my-code-today-timestamps` |
| #18 | 2026-04-30 | fix: show developer PR activity and align setup counts | `qa/fix-data-visibility` |
| #17 | 2026-04-30 | fix: flush active jobs during status polling | `qa/fix-ci-final` |
| #16 | 2026-04-30 | fix: stabilize CI and metrics compatibility | `qa/fix-ci-final` |
| #15 | 2026-04-30 | fix: restore CI compatibility and dashboard build | `qa/fix-ci-after-data` |
| #14 | 2026-04-30 | fix: restore dashboard skill data and org status | `qa/fix-dashboard-data` |
| #13 | 2026-04-30 | fix: comprehensive dashboard auth, agent labels, and org resolution | `deploy/vercel-main` |
| #12 | 2026-04-29 | feat: admin panel, login tracking, signed manifests, SkillQL, Time Machine, email digest, Slack slash command | `fix/deploy-api-and-web-final` |
| #11 | 2026-04-29 | Add audit log, digests, SkillQL, snapshots, and IDE plugin | `deploy/p5-live` |
| #10 | 2026-04-29 | Add signed manifests and VS Code checks | `fix/p5-provenance-vscode-trends` |
| #9 | 2026-04-29 | Add developer leaderboard | `fix/developer-leaderboard` |
| #8 | 2026-04-29 | Deploy Phase 4 implementation | `fix/deploy-phase4` |
| #6 | 2026-04-29 | Phase 4: agent scorecard and policy engine | `fix/deploy-api-and-web` |
| #5 | 2026-04-24 | fix(api): allow bootstrap analysis queueing | `feat/dashboard-overhaul` |
| #4 | 2026-04-24 | feat: full dashboard overhaul - skills, auth fix, UX | `feat/dashboard-overhaul` |
| #3 | 2026-04-24 | fix(deploy): web monorepo deploy and verify Neon migration blocker | `fix/deploy-api-and-web` |

Last 10 Alembic migration files by recent git history:

| Migration file | Commit/date | Commit title |
| --- | --- | --- |
| `apps/api/alembic/versions/20260430_0007_sla_policies_guard.py` | `1d63cd4` / 2026-04-30 | fix: merge runtime aliases in connect status (#22) |
| `apps/api/alembic/versions/20260430_0006_fix_skill_schema_drift.py` | `b5a3f44` / 2026-04-30 | fix: restore dashboard skill data and org status |
| `apps/api/alembic/versions/20260430_0005_admin_login_events.py` | `3abc554` / 2026-04-29 | feat: admin panel, login tracking, signed manifests, SkillQL, Time Machine, email digest, Slack slash command |
| `apps/api/alembic/versions/20260430_0002_org_slack_command.py` | `2be7a54` / 2026-04-28 | Add governance logs, digests, SkillQL, and snapshots |
| `apps/api/alembic/versions/20260430_0003_org_email_digest.py` | `2be7a54` / 2026-04-28 | Add governance logs, digests, SkillQL, and snapshots |
| `apps/api/alembic/versions/20260430_0004_skill_snapshots.py` | `2be7a54` / 2026-04-28 | Add governance logs, digests, SkillQL, and snapshots |
| `apps/api/alembic/versions/20260430_0001_pr_attribution_manifest.py` | `45f6ba2` / 2026-04-28 | feat: add provenance manifests and vscode checks |
| `apps/api/alembic/versions/20260426_0003_agent_jobs_half_life_opportunities.py` | `9d6d50b` / 2026-04-28 | feat: phase 4 agent scorecard and policy engine (#8) |
| `apps/api/alembic/versions/20260426_0004_add_digest_config.py` | `9d6d50b` / 2026-04-28 | feat: phase 4 agent scorecard and policy engine (#8) |
| `apps/api/alembic/versions/20260426_0004_autopilot_improvement_queue.py` | `9d6d50b` / 2026-04-28 | feat: phase 4 agent scorecard and policy engine (#8) |

## Risks I flagged

1. Stack-path drift from the brief: the API lives under `apps/api/api/`, not `apps/api/skillayer/`; auth is `apps/api/api/auth.py`, not `apps/api/skillayer/auth/`; and the hook is under `skilgen/hooks/claude_code_hook.py`. PR-0 must normalize conventions before parallel PRs start.
2. Root `AGENTS.md` is still the generated Skilgen contract. The v8 brief is committed as `docs/AGENTS.md` for this branch by user direction. Future agents may read the wrong contract unless PR-0 resolves this.
3. `Admin` is an actual sidebar surface not named in PRD §3.3. It is gated by `NEXT_PUBLIC_ADMIN_EMAILS`, but v8 routing/redirect plans must explicitly decide whether it remains outside the six-item IA or moves under Settings/Audit.
4. Several v8 destination surfaces already partially exist under v7 routes and endpoints (policy, audit, manifests, agent PRs, my-code-today, standup, digest, SkillQL). The plan must avoid rebuilding working behavior and must preserve bookmarked URLs with redirects.
5. Cut surfaces still have data/API artifacts: `ab_tests` and `digest_configs` tables exist, and digest/A-B endpoints exist. PR-0 must plan deprecation/renaming without deletion or data loss.
6. No `IA_V8` or feature-flag framework exists. PR-1 must introduce env + tenant override semantics carefully and document the rollout contract.
7. DB row counts could not be captured because no non-secret DB connection was configured locally. Any migration plan that touches existing data must be re-run against staging or a sanitized clone before approval.
8. API surface is very broad and concentrated in `apps/api/api/routes/orgs.py` (7k+ lines, 56% file coverage). Moving v7 surfaces could cause regressions unless PRs carve small endpoint boundaries first.
9. Frontend package-level coverage is unavailable. Existing Playwright/E2E specs do not provide coverage percentages, so v8 shell and surface PRs need explicit smoke tests.
10. Recent PRs on 2026-04-29 and 2026-04-30 touched the same governance, dashboard data, runtime aliases, digest, manifest, SkillQL, and admin areas that v8 will reorganize. PR-0 should treat these as fresh, high-conflict zones.
