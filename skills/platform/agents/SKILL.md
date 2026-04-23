---
name: platform-agents
version: 0.6.0
domain: platform
sub_domain: platform-agents
last_updated: 2026-04-23
triggered_by: requirements_pipeline
source_hash: 2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Agents Skill

## Overview
Planner and inference guidance for domain graphing, architecture synthesis, and decision intelligence.

## Check These Paths First
- {{project_root}}/skilgen/agents/__init__.py
- {{project_root}}/skilgen/agents/architecture_planner.py
- {{project_root}}/skilgen/agents/codebase_signals.py
- {{project_root}}/skilgen/agents/decision_planner.py

## Patterns
### Inferred child domain patterns
- domain inference
- architecture synthesis
- agent planning logic
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
- Domain path: `platform/platform-agents`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
