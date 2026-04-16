---
name: client
version: 0.6.0
domain: client
sub_domain: platform
last_updated: 2026-04-14
triggered_by: requirements_pipeline
source_hash: dc7b33e727a01556bb8e686c6a682aa18f2673d91f204183d3b07226913ee47b
references:
  - ../roadmap/SKILL.md
  - src/SKILL.md
status: active
---

# Client Skill

## Overview
Frontend application guidance for the user-facing client, routes, UI composition, and client-side runtime behavior.

## Check These Paths First
- {{project_root}}/client/src/@types/i18next.d.ts
- {{project_root}}/client/src/@types/react.d.ts
- {{project_root}}/client/src/App.jsx
- {{project_root}}/client/src/Providers/ActivePanelContext.tsx

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
- Domain path: `client/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
- src/SKILL.md
