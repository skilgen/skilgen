---
name: packages-client
version: 0.6.0
domain: packages
sub_domain: packages-client
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Packages Client Skill

## Overview
Packages guidance for the `client` surface and its closely related implementation seams.

## Check These Paths First
- {{project_root}}/packages/client/babel.config.js
- {{project_root}}/packages/client/jest.config.js
- {{project_root}}/packages/client/jest.setup.ts
- {{project_root}}/packages/client/rollup.config.js

## Patterns
### Inferred child domain patterns
- packages surface: client
- Stay close to the repo-native folder seam before widening scope.

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent surface contract before widening the boundary.
3. Prefer sibling skills when the change crosses adjacent child seams.

## Traceability
- Generated from requirements source hash: `dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b`
- Domain path: `packages/packages-client`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
