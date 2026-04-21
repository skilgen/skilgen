---
name: platform-runtime
version: 0.6.0
domain: platform
sub_domain: platform-runtime
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Runtime Skill

## Overview
Runtime orchestration guidance for package-level entrypoints, delivery orchestration, and repo-wide integration surfaces.

## Check These Paths First
- {{project_root}}/skilgen/__init__.py
- {{project_root}}/skilgen/autoupdate.py
- {{project_root}}/skilgen/deep_agents_core.py
- {{project_root}}/skilgen/deep_agents_runtime.py

## Patterns
### Inferred child domain patterns
- runtime orchestration
- repo-wide coordination
- package entrypoints

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `platform/platform-runtime`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
