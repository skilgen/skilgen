---
name: roadmap
version: 0.6.0
domain: roadmap
sub_domain: platform
last_updated: 2026-04-23
triggered_by: requirements_pipeline
source_hash: 2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a
references:
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
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.
- `@radix-ui/react-label` in `packages/ui/package.json` is medium; npm install @radix-ui/react-label.

## How-To
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `split`.

## Traceability
- Generated from requirements source hash: `2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a`
- Domain path: `roadmap/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- phase-0/SKILL.md
- phase-1/SKILL.md
- phase-2/SKILL.md
- phase-3/SKILL.md
