---
name: e2e-setup
version: 0.6.0
domain: e2e
sub_domain: e2e-setup
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# E2E Setup Skill

## Overview
E2E guidance for the `setup` surface and its closely related implementation seams.

## Check These Paths First
- {{project_root}}/e2e/setup/authenticate.ts
- {{project_root}}/e2e/setup/cleanupUser.ts
- {{project_root}}/e2e/setup/global-setup.local.ts
- {{project_root}}/e2e/setup/global-setup.ts

## Patterns
### Inferred child domain patterns
- e2e surface: setup
- Stay close to the repo-native folder seam before widening scope.

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent surface contract before widening the boundary.
3. Prefer sibling skills when the change crosses adjacent child seams.

## Traceability
- Generated from requirements source hash: `dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b`
- Domain path: `e2e/e2e-setup`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
