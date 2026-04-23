---
name: platform-cli
version: 0.6.0
domain: platform
sub_domain: platform-cli
last_updated: 2026-04-23
triggered_by: requirements_pipeline
source_hash: 2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Cli Skill

## Overview
Operator-facing CLI guidance for command surfaces, progress reporting, and repo-local execution flows.

## Check These Paths First
- {{project_root}}/skilgen/cli/__init__.py
- {{project_root}}/skilgen/cli/main.py

## Patterns
### Inferred child domain patterns
- command surfaces
- operator UX
- progress orchestration
### Dependency signals
- `@eslint/js` in `packages/config/package.json` is medium; npm install @eslint/js.
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.
- `@radix-ui/react-label` in `packages/ui/package.json` is medium; npm install @radix-ui/react-label.

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a`
- Domain path: `platform/platform-cli`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
