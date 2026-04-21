---
name: platform-cli
version: 0.6.0
domain: platform
sub_domain: platform-cli
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
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

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `platform/platform-cli`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
