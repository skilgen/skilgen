---
name: platform-generators
version: 0.6.0
domain: platform
sub_domain: platform-generators
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Generators Skill

## Overview
Artifact materialization guidance for docs, skills, dashboards, and output rendering flows.

## Check These Paths First
- {{project_root}}/skilgen/generators/__init__.py
- {{project_root}}/skilgen/generators/package.py
- {{project_root}}/skilgen/generators/skills.py

## Patterns
### Inferred child domain patterns
- artifact rendering
- materialization flow
- repo-local outputs

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `platform/platform-generators`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
