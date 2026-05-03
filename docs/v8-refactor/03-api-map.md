# PR-0 API Map

Source inputs: `docs/PRD-v8.docx` sections 3.2, 3.3, and 4.1-4.6; API inventory in `docs/v8-refactor/00-discovery.md`.

Effective API root: `apps/api/api/`. The v8 brief says `apps/api/skillayer/`; user approved treating `apps/api/api/` as the effective root during discovery. PR-1 should document the convention before any surface PR starts.

Disposition vocabulary:

- `keep`: endpoint remains part of the legacy contract and/or is reused by v8.
- `reuse-for-v8`: endpoint backs a v8 tab without changing signature.
- `wrap-for-v8`: add a v8 endpoint that calls existing logic, preserving legacy signature.
- `deprecate-after-v8`: mark as deprecated only in PR-8; do not remove.
- `new`: endpoint needed for v8 with proposed signature, no implementation in PR-0.

## Router-level disposition

| Router | Existing endpoints | v8 disposition |
| --- | ---: | --- |
| `admin.py` | 11 | Keep outside public six-item IA; decide Admin placement in open questions. |
| `agent_runs.py` | 1 | Reuse/wrap for Activity ingest. |
| `autopilot.py` | 9 | Reuse/wrap under Policy Rules. |
| `cron.py` | 2 | Keep; not a dashboard IA surface. |
| `digest.py` | 6 | Deprecate-after-v8; digest becomes notification settings. |
| `eval.py` | 20 | Split: risky agents/skill score reused; A/B tests deprecated after v8. |
| `feed.py` | 2 | Reuse-for-v8 Activity live feed. |
| `health.py` | 1 | Keep. |
| `me.py` | 1 | Keep. |
| `metrics.py` | 1 | Keep. |
| `orgs.py` | 80+ | Split into v8 Activity, Policy, Audit, Skills, Insights, Settings wrappers. |
| `registry.py` | 25 | Reuse/wrap under Skills Registry/Provenance/Drift. |
| `repos.py` | 32 | Reuse/wrap under Skills Repos, Activity Replay, Audit manifest. |
| `review.py` | 6 | Reuse/wrap under Policy Approvals. |
| `sessions.py` | 8 | Reuse/wrap under Activity Sessions/Replay. |
| `skills.py` | 4 | Reuse/wrap under Skills. |
| `sla.py` | 5 | Reuse/wrap under Insights Coverage SLA. |
| `slack.py` | 1 | Keep; settings/connector integration. |
| `stripe.py` | 4 | Keep; Settings Billing. |
| `webhook.py` | 1 | Keep; GitHub ingest. |
| `worker.py` | 1 | Keep; internal worker. |

## Existing endpoint disposition by router

### `admin.py`

All admin endpoints stay valid and out of the primary six-item IA pending the Admin open question: `POST /admin/rollup-usage`, `GET /admin/overview`, `GET /admin/orgs`, `GET /admin/orgs/{org_id}`, `GET /admin/orgs/{org_id}/usage`, `POST /admin/orgs/{org_id}/suspend`, `POST /admin/orgs/{org_id}/unsuspend`, `DELETE /admin/orgs/{org_id}`, `GET /admin/users`, `GET /admin/logins`, `GET /admin/metrics/export`.

Disposition: `keep`. Possible v8 wrapper target: Settings Admin Audit or Audit, TBD.

### `agent_runs.py`

| Endpoint | Disposition | v8 use |
| --- | --- | --- |
| `POST /orgs/{org_id}/agent-runs` | reuse-for-v8 | Activity ingest; PRD 4.1 and AgentRun ingest. |

### `autopilot.py`

All existing Autopilot task endpoints are `wrap-for-v8` under Policy Rules because PRD 3.3 maps Autopilot to `Policy -> Rules (auto-approval rules)`: queue, trigger, deduplicate, preview, skip, generate-improvement, approve, reject.

Proposed wrapper prefix: `/v8/orgs/{org_id}/policy/rules/autopilot/...`.

### `cron.py`

`POST /cron/standup` and `POST /cron/digest` are `keep`. These are internal scheduled jobs, not direct IA routes. Digest cron may remain while dashboard Digest moves into Settings notifications.

### `digest.py`

All digest endpoints are `deprecate-after-v8` for dashboard use, but not removed: `GET/PUT /orgs/{org_id}/digest/config`, `GET/POST /orgs/{org_id}/digest/preview`, `POST /orgs/{org_id}/digest/send-now`, `POST /orgs/{org_id}/digest/send`.

Proposed v8 wrapper: `/v8/orgs/{org_id}/settings/notifications/digest`.

### `eval.py`

| Endpoint group | Existing endpoints | Disposition | v8 use |
| --- | --- | --- | --- |
| Agent tasks/eval sessions | `/orgs/{org_id}/tasks`, `/tasks/batch`, `/eval/summary`, `/eval/sessions`, `/eval/sessions/{session_id}/outcome`, `/eval-sessions`, `/benchmark` | wrap-for-v8 | Insights Risky agents and Skills Score evidence. |
| ROI | `/orgs/{org_id}/roi` | reuse-for-v8 | Insights Fleet KPIs. |
| Skill gaps | `/orgs/{org_id}/skill-gaps`, `/eval/gaps`, gap patch/ack/resolve variants | wrap-for-v8 | Skills Score filter coverage. |
| A/B tests | `/orgs/{org_id}/ab-tests`, `/ab-tests/{test_id}`, `/conclude` | deprecate-after-v8 | PRD cuts A/B Tests until later. |

### `feed.py`

| Endpoint | Disposition | v8 use |
| --- | --- | --- |
| `GET /orgs/{org_id}/feed/recent` | reuse-for-v8 | Activity Live feed initial state. |
| `GET /orgs/{org_id}/feed/stream` | reuse-for-v8 | Activity SSE live stream. |

### `health.py`, `me.py`, `metrics.py`

`GET /health`, `GET /me/org`, and `GET /metrics` are `keep`.

### `orgs.py`

Key endpoint dispositions:

| Endpoint group | Existing endpoints | Disposition | v8 use |
| --- | --- | --- | --- |
| Bootstrap/auth/org context | `/orgs/bootstrap`, `/{org_id}`, `/me/org`, `/auth/login-event` | keep | Shell/settings context. |
| Setup/connect/API key | `/setup-status`, `/connect/status`, `/agent-connection/status`, `/api-key`, `/api-key/rotate`, `/available-repos`, `/connect-repos`, `/refresh-repo-languages` | wrap-for-v8 | Settings Connectors. |
| Repos/stats/overview | `/repos`, `/stats`, `/overview/score-trend`, `/coverage-summary` | wrap-for-v8 | Skills Repos and Insights KPIs. |
| Activity/session data | `/skill-heatmap`, `/sessions`, `/sessions/{session_id}/tag`, `/agent-prs`, `/agent-prs/{pr_id}`, `/my-code-today`, `/standup` | wrap-for-v8 | Activity tabs. My Code Today remains legacy/cut as a route but data may feed Activity. |
| Analytics/insights | `/analytics`, `/analytics/criticality`, `/analytics/skill-coload-tree`, `/analytics/improvement-suggestions`, `/analytics/highlight-risks`, `/runtime-breakdown`, `/memory-score`, `/knowledge-velocity`, `/knowledge-concentration`, `/knowledge-risk/...` | wrap-for-v8 | Insights and Skills Score. |
| Policy | `/red-flags`, `/red-flags/dismissed`, red-flag dismiss/restore, `/policies`, `/policy-templates`, `/policy-check`, `/policy-check/ci` | wrap-for-v8 | Policy Rules/Violations/Approvals. |
| Audit | `/audit-log`, `/audit-log/export`, `/audit-log/event-types`, `/audit-log/stats`, `/audit-log/webhook`, `/agent-prs/{pr_id}/manifest`, manifest verify | wrap-for-v8 | Audit Event log/Exports/Evidence. |
| Skills | `/enterprise-skills`, `/skills/{skill_id}/push`, `/skills/search`, `/skillql`, `/skillql/suggestions`, `/half-life`, `/skill-debt`, `/debt/...`, `/dependency-graph/...`, `/sources` | wrap-for-v8 | Skills Registry/Score/Drift/Provenance/SkillQL/Repos. |
| Settings | `/settings`, `/settings/slack`, `/settings/email-digest`, `/settings/anthropic-key`, `/llm-config`, `/llm-config/test`, `/teams`, `/teams/summary`, `/teams/rollup`, `/test-notification` | wrap-for-v8 | Settings tabs. |
| Digest send | `/digest/send`, `/standup/send` | keep/deprecate dashboard route only | Notification actions in Settings. |

### `registry.py`

All registry, marketplace, skill-map/tree, search, install/import, dependency-graph, compatibility, and half-life endpoints are `wrap-for-v8` under Skills. Legacy routes stay until PR-8 sunset headers.

### `repos.py`

| Endpoint group | Existing endpoints | Disposition | v8 use |
| --- | --- | --- | --- |
| Repo detail/skills | `/repos/{repo_id}`, `/skills`, skill snapshots, versions, content, usage stats | wrap-for-v8 | Skills Repos, Registry, Provenance. |
| Sessions/replay | `/sessions`, `/agent-sessions`, `/sessions/{session_id}/replay` | reuse/wrap-for-v8 | Activity Sessions/Replay. |
| Score/forecast/dependencies/runs | `/score-history`, `/score-forecast`, `/dependencies`, `/runs`, `/skill-sources` | wrap-for-v8 | Skills Score/Repos/Provenance, Insights. |
| PR attribution/risk | `/prs/{pr_number}/attribution`, `/prs/{pr_number}/risk` | wrap-for-v8 | Audit/Insights. |
| Commit checks | `/commits/{sha}/check`, `/check` | wrap-for-v8 | Policy enforcement. |
| Analyse/sync | `/analyse`, `/analyze-source`, `/backfill-categories`, `/sync-analytics` | keep | Internal/ops actions. |
| Agent skill load | `/skills/load` | keep | Stable ingest contract. |

### `review.py`

All review endpoints are `wrap-for-v8` under Policy Approvals: `/repos/{repo_id}/review`, `/orgs/{org_id}/review/scan-diff`, `/scan-repo-prs`, `/scan-status/{job_id}`, `/history`, and repo review history.

### `sessions.py`

All session endpoints are `reuse/wrap-for-v8` under Activity Sessions and Replay. Keep duplicate legacy session creation route for API contract compatibility.

### `skills.py`

All skill read/version/usage endpoints are `reuse/wrap-for-v8` under Skills.

### `sla.py`

All SLA CRUD/check endpoints are `wrap-for-v8` under Insights Coverage SLA.

### `slack.py`, `stripe.py`, `webhook.py`, `worker.py`

Keep existing endpoints. v8 surfaces may link to them via Settings Connectors/Billing, Activity ingest, or internal worker status, but no signature change is proposed in PR-0.

## Proposed new v8 endpoint signatures

No implementations in PR-0.

```text
GET  /v8/orgs/{org_id}/activity/feed
GET  /v8/orgs/{org_id}/activity/feed/stream
GET  /v8/orgs/{org_id}/activity/sessions
GET  /v8/orgs/{org_id}/activity/sessions/{session_id}
GET  /v8/repos/{repo_id}/activity/sessions/{session_id}/replay
GET  /v8/repos/{repo_id}/activity/heatmap

GET  /v8/orgs/{org_id}/policy/rules
POST /v8/orgs/{org_id}/policy/rules
PATCH /v8/orgs/{org_id}/policy/rules/{policy_id}
DELETE /v8/orgs/{org_id}/policy/rules/{policy_id}
GET  /v8/orgs/{org_id}/policy/violations
GET  /v8/orgs/{org_id}/policy/approvals
POST /v8/orgs/{org_id}/policy/approvals/{approval_id}/decision
GET  /v8/orgs/{org_id}/policy/quarantine
POST /v8/orgs/{org_id}/policy/quarantine/{skill_id}/decision

GET  /v8/orgs/{org_id}/audit/events
GET  /v8/orgs/{org_id}/audit/reports
POST /v8/orgs/{org_id}/audit/exports
POST /v8/orgs/{org_id}/audit/evidence-packages
GET  /v8/orgs/{org_id}/audit/evidence-packages/{package_id}

GET  /v8/orgs/{org_id}/skills/registry
GET  /v8/orgs/{org_id}/skills/score
GET  /v8/orgs/{org_id}/skills/drift
GET  /v8/orgs/{org_id}/skills/provenance
POST /v8/orgs/{org_id}/skills/skillql
GET  /v8/orgs/{org_id}/skills/repos

GET  /v8/orgs/{org_id}/insights/fleet-kpis
GET  /v8/orgs/{org_id}/insights/risky-agents
GET  /v8/orgs/{org_id}/insights/risky-repos
GET  /v8/orgs/{org_id}/insights/coverage-sla

GET  /v8/orgs/{org_id}/settings
PATCH /v8/orgs/{org_id}/settings
GET  /v8/orgs/{org_id}/settings/teams
GET  /v8/orgs/{org_id}/settings/rbac
GET  /v8/orgs/{org_id}/settings/sso
GET  /v8/orgs/{org_id}/settings/connectors
GET  /v8/orgs/{org_id}/settings/admin-audit
```

## Rules for PR-1 through PR-8

- Existing endpoints keep working while `IA_V8=false`.
- New v8 endpoints live under the current effective API package unless PR-1 formalizes a different convention.
- Sunset/deprecation headers are PR-8 only.
- No third-party API contract changes are proposed.
