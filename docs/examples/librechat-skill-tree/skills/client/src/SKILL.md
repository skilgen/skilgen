---
name: client-src
version: 0.6.0
domain: client
sub_domain: client-src
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Client Src Skill

## Overview
Client guidance for the `src` surface and its closely related implementation seams.

## Check These Paths First
- {{project_root}}/client/src/@types/i18next.d.ts
- {{project_root}}/client/src/@types/react.d.ts
- {{project_root}}/client/src/App.jsx
- {{project_root}}/client/src/Providers/ActivePanelContext.tsx

## Patterns
### Inferred child domain patterns
- client surface: src
- Stay close to the repo-native folder seam before widening scope.

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent surface contract before widening the boundary.
3. Prefer sibling skills when the change crosses adjacent child seams.

## Traceability
- Generated from requirements source hash: `dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b`
- Domain path: `client/client-src`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
