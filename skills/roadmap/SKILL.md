---
name: roadmap
version: 0.6.0
domain: roadmap
sub_domain: platform
last_updated: 2026-05-11
triggered_by: requirements_pipeline
source_hash: c171704dd887f8990846851c5a45af9608249e298e246d492cefbbe5c11913a0
richness_score: 83
score:
  total: 83
  groundedness: 8
  coverage: 25
  freshness: 25
  structure: 25
references:
  - ../requirements/SKILL.md
  - phase-0/SKILL.md
  - phase-1/SKILL.md
  - phase-2/SKILL.md
  - phase-3/SKILL.md
status: active
---

# Roadmap Skill

## Overview
Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## Check These Paths First
- {{project_root}}/skills/roadmap/SKILL.md
- {{project_root}}/REPORT.md

## Patterns
### Architecture responsibilities
- Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.
- Coordinates subdomains: roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3.
- phase-based delivery
- sequenced implementation planning
### Inferred domain patterns
- phase-based delivery
- sequenced implementation planning
- traceable next steps
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.
### Architecture evidence
- Evidence: `skills/roadmap/SKILL.md`
- Evidence: `REPORT.md`
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
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `split`.

## Code Examples

### REPORT.md
```
# Report

## Summary
- Detected domains: requirements, platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Feature inventory entries: 18
- Backend route files: 4
- Frontend route files: 0
- Component files: 0
- Service files: 1
- Test files: 87
- Data model files: 1
- Persistence files: 2
- Background job files: 2
- Auth files: 5
```

## Traceability
- Generated from requirements source hash: `c171704dd887f8990846851c5a45af9608249e298e246d492cefbbe5c11913a0`
- Domain path: `roadmap/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../requirements/SKILL.md
- phase-0/SKILL.md
- phase-1/SKILL.md
- phase-2/SKILL.md
- phase-3/SKILL.md
