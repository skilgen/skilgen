---
name: api
version: 0.6.0
domain: api
sub_domain: platform
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
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
### Inferred domain patterns
- repo-native app surface
- top-level implementation boundary
- folder-driven capability map
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.

## How-To
1. Start from the nearest evidence file in this inferred domain.
2. Keep the change within this repo-native surface before widening scope across sibling domains.
3. Use related roadmap or sibling skills when the change spans multiple surfaces.

## Traceability
- Generated from requirements source hash: `dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b`
- Domain path: `api/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
- app/SKILL.md
- cache/SKILL.md
- config/SKILL.md
- db/SKILL.md
- server/SKILL.md
- strategies/SKILL.md
- test/SKILL.md
- utils/SKILL.md
