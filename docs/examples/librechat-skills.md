# LibreChat Generated Skills

This is a committed snapshot of the skill tree Skilgen generated for [danny-avila/LibreChat](https://github.com/danny-avila/LibreChat) at source commit `5cc783b`.

The goal of this example is to show what changes after Skilgen runs:

| Metric | Before Skilgen | With Skilgen |
| --- | ---: | ---: |
| Repo skill readiness | `20 / 100` | `87 / 100` |
| Groundedness | `0 / 25` | `20 / 25` |
| Coverage | `20 / 25` | `20 / 25` |
| Freshness | `0 / 25` | `25 / 25` |
| Structure | `0 / 25` | `21 / 25` |

The baseline is not a fake zero. LibreChat already has readable repo structure, so Skilgen credits the repo for coverage. The lift comes from materializing grounded skills, freshness tracking, and agent-facing operating artifacts.

## Generated Domains

Skilgen inferred repo-native domains from the actual LibreChat folder seams instead of forcing a static `backend/frontend` split.

| Domain | Purpose |
| --- | --- |
| `api` | API routes, services, persistence, auth, clients, runtime orchestration |
| `client` | User-facing client source, routes, UI composition, client runtime behavior |
| `config` | Runtime config, feature flags, translations, environment-driven behavior |
| `e2e` | Browser workflows, setup, regression coverage |
| `packages` | Shared internal packages used by app runtime and product surfaces |
| `roadmap` | Delivery sequencing and phase guidance |

## Skill Tree

The full generated `skills/` snapshot is committed at [`librechat-skill-tree/skills/MANIFEST.md`](librechat-skill-tree/skills/MANIFEST.md).

```text
skills/
├── MANIFEST.md
├── GRAPH.md
├── api/
│   ├── SKILL.md
│   ├── app/SKILL.md
│   ├── cache/SKILL.md
│   ├── config/SKILL.md
│   ├── db/SKILL.md
│   ├── server/SKILL.md
│   ├── strategies/SKILL.md
│   ├── test/SKILL.md
│   └── utils/SKILL.md
├── client/
│   ├── SKILL.md
│   └── src/SKILL.md
├── config/
│   ├── SKILL.md
│   └── translations/SKILL.md
├── e2e/
│   ├── SKILL.md
│   ├── setup/SKILL.md
│   └── specs/SKILL.md
├── packages/
│   ├── SKILL.md
│   ├── api/SKILL.md
│   ├── client/SKILL.md
│   ├── data-provider/SKILL.md
│   └── data-schemas/SKILL.md
└── roadmap/
    ├── SKILL.md
    ├── phase-0/SKILL.md
    ├── phase-1/SKILL.md
    ├── phase-2/SKILL.md
    └── phase-3/SKILL.md
```

## Example Skill: `api/SKILL.md`

```markdown
---
name: api
version: 0.6.0
domain: api
sub_domain: platform
references:
  - ../roadmap/SKILL.md
  - app/SKILL.md
  - cache/SKILL.md
  - config/SKILL.md
  - db/SKILL.md
  - server/SKILL.md
  - strategies/SKILL.md
  - test/SKILL.md
  - utils/SKILL.md
status: active
---

# Api Skill

## Overview
Backend application guidance for API routes, services, persistence, auth, and runtime orchestration under the repo's `api/` surface.

## Check These Paths First
- {{project_root}}/api/app/clients/BaseClient.js
- {{project_root}}/api/app/clients/OllamaClient.js
- {{project_root}}/api/app/clients/TextStream.js
- {{project_root}}/api/app/clients/index.js

## Patterns
- repo-native app surface
- top-level implementation boundary
- folder-driven capability map
```

## Example Skill: `packages/data-schemas/SKILL.md`

```markdown
---
name: packages-data-schemas
version: 0.6.0
domain: packages
sub_domain: packages-data-schemas
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Packages Data Schemas Skill

## Overview
Packages guidance for the `data-schemas` surface and its closely related implementation seams.

## Check These Paths First
- {{project_root}}/packages/data-schemas/misc/ferretdb/aclBitops.ferretdb.spec.ts
- {{project_root}}/packages/data-schemas/misc/ferretdb/migrationAntiJoin.ferretdb.spec.ts
- {{project_root}}/packages/data-schemas/misc/ferretdb/multiTenancy.ferretdb.spec.ts
- {{project_root}}/packages/data-schemas/misc/ferretdb/orgOperations.ferretdb.spec.ts

## Patterns
- packages surface: data-schemas
- Stay close to the repo-native folder seam before widening scope.
```

## Dashboard Snapshot

Open [`librechat-dashboard.html`](librechat-dashboard.html) locally to inspect the full generated dashboard, including:

- Before Skilgen vs With Skilgen score lift.
- Evidence Sankey.
- Dependency Sankey.
- Skill flow.
- Generated skill usefulness and operating artifacts.
