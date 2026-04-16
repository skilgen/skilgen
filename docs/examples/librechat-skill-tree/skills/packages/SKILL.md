---
name: packages
version: 0.6.0
domain: packages
sub_domain: platform
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
references:
  - ../roadmap/SKILL.md
  - api/SKILL.md
  - client/SKILL.md
  - data-provider/SKILL.md
  - data-schemas/SKILL.md
status: active
---

# Packages Skill

## Overview
Shared package guidance for reusable internal packages that support the app runtime and product surfaces.

## Check These Paths First
- {{project_root}}/packages/api/rollup.config.js
- {{project_root}}/packages/api/src/acl/accessControlService.spec.ts
- {{project_root}}/packages/api/src/acl/accessControlService.ts
- {{project_root}}/packages/api/src/admin/config.handler.spec.ts

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
- Domain path: `packages/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
- api/SKILL.md
- client/SKILL.md
- data-provider/SKILL.md
- data-schemas/SKILL.md
