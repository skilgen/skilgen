# API Reference

## Authentication

Authenticated routes expect:

```text
Authorization: Bearer {token}
```

The dashboard uses a WorkOS-backed session and passes the token to server-side
fetch helpers. Public routes such as `/health`, `/metrics`, and `GET /registry`
do not require auth.

## Base URL

```text
https://api.skillayer.com
```

## Error Format

Structured errors use:

```json
{"detail":"specific message","code":"ERROR_CODE"}
```

## Endpoints

### GET /health

**Auth required:** No  
**Description:** health check for API and DB connectivity

**Response**

```json
{"status":"ok","db":"ok"}
```

### GET /metrics

**Auth required:** No  
**Description:** cached aggregate platform metrics

### GET /repos/{id}

**Auth required:** Yes  
**Description:** repository metadata and latest score

### GET /repos/{id}/score-badge

**Auth required:** No  
**Description:** SVG score badge

### GET /repos/{id}/dependencies

**Auth required:** Yes  
**Description:** dependency risk report

### GET /repos/{id}/skill-sources

**Auth required:** Yes  
**Description:** source coverage grouped by source type and skill category

**Example response**

```json
{
  "sources": [
    {
      "source_type": "openapi",
      "skill_category": "internal_tools",
      "skill_count": 2,
      "avg_score": 72,
      "last_analysed_at": "2026-04-23T10:00:00Z"
    }
  ],
  "coverage_map": {
    "codebase_architecture": {"covered": true, "skill_count": 4, "avg_score": 68},
    "code_style": {"covered": false, "skill_count": 0, "avg_score": null},
    "testing_conventions": {"covered": true, "skill_count": 1, "avg_score": 70},
    "internal_tools": {"covered": true, "skill_count": 2, "avg_score": 72},
    "security_compliance": {"covered": false, "skill_count": 0, "avg_score": null},
    "design_system": {"covered": false, "skill_count": 0, "avg_score": null},
    "data_schema": {"covered": false, "skill_count": 0, "avg_score": null},
    "operational_knowledge": {"covered": false, "skill_count": 0, "avg_score": null}
  },
  "coverage_score": 38
}
```

### POST /repos/{id}/analyze-source

**Auth required:** Yes  
**Description:** queue a focused non-code source analysis

**Request body**

```json
{"source_type":"openapi","path":"api/openapi.yaml"}
```

**Response**

```json
{"job_id":"de305d54-75b4-431b-adb2-eb6b9e546014","status":"queued","source_type":"openapi"}
```

### GET /skills/{id}

**Auth required:** Yes  
**Description:** full skill detail including score, content, source type, stale state, and versions

### POST /skills/{id}/usage

**Auth required:** Yes  
**Description:** record a skill load event

**Request body**

```json
{"agent_runtime":"codex","session_id":"sess_123"}
```

### GET /orgs/{id}/stats

**Auth required:** Yes  
**Description:** overview stats for dashboard landing page

### GET /orgs/{id}/settings

**Auth required:** Yes  
**Description:** org-level score threshold, Slack, GitHub App, and billing state

### PATCH /orgs/{id}/settings

**Auth required:** Yes  
**Description:** update settings such as score threshold and notification toggles

### POST /orgs/{id}/test-notification

**Auth required:** Yes  
**Description:** send a Slack test notification

### GET /orgs/{id}/analytics

**Auth required:** Yes  
**Description:** 30-day analytics summary

### GET /orgs/{id}/coverage-summary

**Auth required:** Yes  
**Description:** repo-by-repo coverage rollup

### GET /registry

**Auth required:** No  
**Description:** browse registry entries

### POST /registry/publish

**Auth required:** Yes  
**Description:** publish a skill into the registry

### GET /registry/{id}

**Auth required:** No  
**Description:** fetch registry detail and content

### POST /registry/{id}/import

**Auth required:** Yes  
**Description:** increment `import_count` and return skill content

### POST /stripe/create-checkout-session

**Auth required:** Yes  
**Description:** start a paid checkout session

### POST /stripe/create-portal-session

**Auth required:** Yes  
**Description:** create a Stripe customer portal session

### POST /stripe/webhook

**Auth required:** No  
**Description:** Stripe-signed webhook endpoint

### POST /admin/rollup-usage

**Auth required:** Admin secret header  
**Description:** reset stale usage counters

## Request And Response Schemas

### `GET /repos/{id}/skill-sources`

Response shape:

```json
{
  "sources": [
    {
      "source_type": "openapi",
      "skill_category": "internal_tools",
      "skill_count": 3,
      "avg_score": 72,
      "last_analysed_at": "2026-04-23T18:35:00Z"
    }
  ],
  "coverage_map": {
    "codebase_architecture": {
      "covered": true,
      "skill_count": 4,
      "avg_score": 68
    }
  },
  "coverage_score": 25
}
```

Common error codes:

- `401` unauthenticated request
- `403` repo outside org scope
- `500` database or aggregation failure

### `POST /repos/{id}/analyze-source`

Accepted `source_type` values:

- `openapi`
- `graphql`
- `postman`
- `terraform`
- `kubernetes`
- `helm`
- `dbt`
- `sql_schema`
- `kafka`
- `sarif`
- `sbom`
- `security_policy`
- `runbook`
- `confluence`
- `notion`
- `incident`

Request example:

```bash
curl -X POST https://api.skillayer.com/repos/repo_123/analyze-source \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_type":"terraform","path":"infra/terraform"}'
```

Response example:

```json
{
  "job_id": "8fe7f9dc-b849-4498-a4c7-c650f3d5d324",
  "status": "queued",
  "source_type": "terraform"
}
```

### `GET /orgs/{id}/coverage-summary`

Response example:

```json
{
  "repos": [
    {
      "repo_id": "repo_123",
      "name": "payments-service",
      "coverage_score": 50,
      "missing_categories": [
        "design_system",
        "operational_knowledge",
        "security_compliance",
        "testing_conventions"
      ]
    }
  ],
  "org_coverage_score": 31,
  "most_missing_category": "operational_knowledge"
}
```

## Curl Examples

### Repository Detail

```bash
curl https://api.skillayer.com/repos/repo_123 \
  -H "Authorization: Bearer $TOKEN"
```

Typical success payload includes repo metadata, latest score rollup, timestamps,
and a score summary used by the dashboard repo list and detail screens.

### Repository Dependencies

```bash
curl https://api.skillayer.com/repos/repo_123/dependencies \
  -H "Authorization: Bearer $TOKEN"
```

This response includes package counts, vulnerability rollups, and dependency
risk detail suitable for rendering the dashboard dependency tab.

### Skill Detail

```bash
curl https://api.skillayer.com/skills/skill_123 \
  -H "Authorization: Bearer $TOKEN"
```

Skill detail responses typically include:

- `id`
- `repo_id`
- `domain`
- `title`
- `content`
- `score_total`
- `score_groundedness`
- `score_coverage`
- `score_freshness`
- `score_structure`
- `source_type`
- `skill_category`
- `load_count_30d`
- `last_loaded_at`
- `is_stale`

### Registry Browse

```bash
curl "https://api.skillayer.com/registry?search=payments&sort=imports"
```

Registry listing responses are optimized for browse experiences and usually
contain light cards rather than the full `SKILL.md` payload.

### Registry Publish

```bash
curl -X POST https://api.skillayer.com/registry/publish \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "skill_123",
    "name": "Payments API",
    "description": "Auth, error handling, and rate limiting",
    "tags": ["api", "payments"],
    "is_public": false
  }'
```

Validation rules:

- the source skill must belong to the authenticated org
- the skill must have non-empty content
- tags must be strings
- name and description are required

### Usage Tracking

```bash
curl -X POST https://api.skillayer.com/skills/skill_123/usage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_runtime":"codex","session_id":"sess_123"}'
```

The API records the event, updates rolling counters, and stores the latest load
timestamp in UTC.

## Error Reference

Common structured errors:

```json
{"detail":"Repository not found in organisation scope","code":"FORBIDDEN"}
```

```json
{"detail":"Invalid source_type","code":"INVALID_SOURCE_TYPE"}
```

```json
{"detail":"Database query failed","code":"INTERNAL_ERROR"}
```

Expect the following status classes:

- `400` malformed request body or validation error
- `401` missing or invalid bearer token
- `403` authenticated but not allowed for the requested org or repo
- `404` missing resource
- `409` duplicate publish or conflicting state transition
- `422` semantically invalid request body
- `500` unexpected server failure

## Operational Notes

- Timestamps are returned in UTC ISO-8601 format.
- Org-scoped routes compare the requested org ID to the current WorkOS session.
- Database writes use parameterized SQL or ORM constructs only.
- Background analysis routes return quickly and do not block on parser runtime.
- Public routes are safe for badges, health checks, and read-only registry browse
  flows.
