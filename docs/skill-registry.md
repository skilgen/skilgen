# Skill Registry

The Skill Registry is the reusable knowledge layer of Skillayer. It lets teams
publish a high-value skill once and import it into other repositories without
copying files by hand.

## What the Registry Is

A registry entry has:

- a source skill ID
- name and description
- tags
- visibility settings
- import count
- the actual skill content

That makes it possible to treat institutional knowledge as a reusable package.

## Publishing a Skill

CLI example:

```bash
skilgen skills publish \
  --skill-id skill_123 \
  --name "Payments API" \
  --description "Auth, rate limits, error patterns" \
  --tag api --tag payments
```

Publishing rules:

- the skill must belong to the current org
- the skill must contain usable content
- tags are optional but strongly recommended

API equivalent:

```bash
curl -X POST https://api.skillayer.com/registry/publish \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill_id":"skill_123","name":"Payments API","description":"Auth, rate limits, error patterns","tags":["api","payments"]}'
```

## Importing a Skill

CLI example:

```bash
skilgen skills import \
  --registry-id reg_123 \
  --target-dir ./skills
```

API equivalent:

```bash
curl -X POST https://api.skillayer.com/registry/reg_123/import \
  -H "Authorization: Bearer $TOKEN"
```

Import behavior:

- the content is returned by the API
- `import_count` is incremented atomically
- the CLI writes the content into the target directory

## Browsing the Registry

Browse from:

- dashboard: `/dashboard/registry`
- API: `GET /registry`

Useful query options:

- `search`
- `tag`
- `sort=imports|score|newest`

## Public vs Private

Visibility choices:

- **private**: only the owning org can use it
- **public**: visible in registry browse flows

This lets teams decide whether a skill is internal policy or reusable public
knowledge.

## import_count

`import_count` tracks reuse. It matters because it shows which pieces of
institutional knowledge are actually valuable across repos.

High import counts often mean:

- the skill is broadly useful
- it should be maintained carefully
- it may deserve stronger freshness monitoring

## Request Body For Registry Publish

Typical publish body:

```json
{
  "skill_id": "skill_123",
  "name": "Payments API",
  "description": "Auth, error handling, and rate limiting",
  "tags": ["api", "payments"],
  "is_public": false
}
```

Recommended validation:

- `skill_id` must exist and belong to the current org
- `name` must be non-empty
- `description` should explain why the skill is reusable
- `tags` should reflect domain and capability

## Good Registry Hygiene

Publish skills that are:

- stable across multiple repos
- specific enough to be actionable
- maintained by a clear owning team

Avoid publishing skills that are:

- too repo-specific to be reused elsewhere
- stale or known to be superseded
- just thin wrappers around generic coding advice

## When To Import Versus Regenerate

Import a registry skill when the knowledge is intentionally shared across repos,
such as a common Payments API contract or a company-wide incident triage
process.

Regenerate locally when the knowledge depends on repo-specific code, schema, or
deployment state.
