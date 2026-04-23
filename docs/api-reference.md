# API Reference

Base URL: `https://api.skillayer.com`

Authenticated endpoints require `Authorization: Bearer <WorkOS JWT>`.

## Health and Metrics

### `GET /health`

No auth. Returns service and database status.

```json
{"status":"ok","db":"ok"}
```

### `GET /metrics`

No auth. Returns cached platform counters: uptime, runs, skills, orgs, repos, average score, and last run time.

## Repositories

### `GET /repos/{id}`

Returns repo metadata, latest score, skill count, language, default branch, and installation id.

### `GET /repos/{id}/score-badge`

Returns SVG badge. Query: `style=flat|flat-square|for-the-badge`.

### `GET /repos/{id}/dependencies`

Auth required. Returns high, medium, healthy dependency groups, total count, and risk score.

### `GET /repos/{id}/skill-sources`

Auth required. Returns source types, generated skills, eight-category coverage map, and coverage score.

### `POST /repos/{id}/analyze-source`

Auth required.

```json
{"source_type":"openapi","path":"api/openapi.yaml"}
```

Returns:

```json
{"job_id":"run_123","status":"queued"}
```

## Skills

### `GET /skills/{id}`

Returns domain, path, content, score, source type, category, stale state, usage, and version metadata.

### `POST /skills/{id}/usage`

Auth required.

```json
{"agent_runtime":"codex","session_id":"sess_123"}
```

## Organizations

### `GET /orgs/{id}/stats`

Returns repo count, average score, skill count, active agents, and 30-day score trend.

### `GET /orgs/{id}/coverage-summary`

Auth required. Returns per-repo coverage scores and most missing category.

### `GET /orgs/{id}/settings`

Auth required. Returns threshold, Slack settings, GitHub App status, and recent deliveries.

### `PATCH /orgs/{id}/settings`

Auth required. Accepts `name`, `score_threshold`, `slack_webhook_url`, `notify_on_pr`, and `notify_on_stale`.

### `POST /orgs/{id}/test-notification`

Auth required. Sends a Slack test notification.

### `GET /orgs/{id}/analytics`

Auth required. Returns skill usage analytics.

## Registry

`GET /registry`, `POST /registry/publish`, `GET /registry/{id}`, and `POST /registry/{id}/import` support browse, publish, detail, and import flows.

## Stripe

`POST /stripe/create-checkout-session`, `POST /stripe/create-portal-session`, `GET /stripe/subscription`, and `POST /stripe/webhook` support billing. The webhook is authenticated by Stripe signature rather than user auth.

## Admin

`POST /admin/rollup-usage` requires the admin secret header.

## Errors

Structured errors use:

```json
{"detail":"specific message","code":"ERROR_CODE"}
```
