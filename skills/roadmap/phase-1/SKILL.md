---
name: roadmap-phase-1
version: 0.6.0
domain: roadmap
sub_domain: roadmap-phase-1
last_updated: 2026-05-11
triggered_by: requirements_pipeline
source_hash: c171704dd887f8990846851c5a45af9608249e298e246d492cefbbe5c11913a0
richness_score: 72
score:
  total: 72
  groundedness: 0
  coverage: 22
  freshness: 25
  structure: 25
references:
  - ../SKILL.md
  - ../../requirements/SKILL.md
status: active
---

# Roadmap Phase 1 Skill

## Overview
Roadmap phase node for phase-1 planning and sequencing guidance.

## Check These Paths First
- {{project_root}}/skills/roadmap/SKILL.md

## Patterns
### Inferred child domain patterns
- phase sequencing
- delivery planning
### Dependency signals
- `@eslint/js` in `packages/config/package.json` is medium; npm install @eslint/js.
- `@playwright/test` in `apps/dashboard/package.json` is medium; npm install @playwright/test.
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.

## Anti-patterns
- **Introduce a second pattern for the same workflow**: Don't introduce a second pattern for the same workflow — duplicated conventions make agent edits unreliable
- **Remove nearby verification steps**: Don't remove nearby verification steps — future agents need a fast way to prove behaviour still works
- **Leave file references vague**: Don't leave file references vague — agents waste time searching and may edit the wrong boundary

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `c171704dd887f8990846851c5a45af9608249e298e246d492cefbbe5c11913a0`
- Domain path: `roadmap/roadmap-phase-1`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
