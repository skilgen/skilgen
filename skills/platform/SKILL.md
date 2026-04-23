---
name: platform
version: 0.6.0
domain: platform
sub_domain: platform
last_updated: 2026-04-23
triggered_by: requirements_pipeline
source_hash: 2b845af34337743bca28b87aa1fb2621357bc8d71cba4772d869b351c815ef8a
references:
  - ../roadmap/SKILL.md
  - runtime/SKILL.md
  - agents/SKILL.md
  - cli/SKILL.md
  - core/SKILL.md
  - generators/SKILL.md
  - scripts/SKILL.md
status: active
---

# Platform Skill

## Overview
Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.

## Check These Paths First
- {{project_root}}/skilgen/__init__.py
- {{project_root}}/skilgen/autoupdate.py
- {{project_root}}/skilgen/agents/__init__.py
- {{project_root}}/skilgen/agents/architecture_planner.py

## Patterns
### Architecture responsibilities
- Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- Coordinates subdomains: platform-runtime, platform-agents, platform-cli, platform-core.
- tooling platform
- generation engine
### Inferred domain patterns
- tooling platform
- generation engine
- repo-local operating surface
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.
### Architecture evidence
- Evidence: `skilgen/__init__.py`
- Evidence: `skilgen/autoupdate.py`
- Evidence: `skilgen/agents/__init__.py`
- Evidence: `skilgen/agents/architecture_planner.py`
- Evidence: `skilgen/cli/__init__.py`
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
- Domain path: `platform/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
- runtime/SKILL.md
- agents/SKILL.md
- cli/SKILL.md
- core/SKILL.md
- generators/SKILL.md
- scripts/SKILL.md
