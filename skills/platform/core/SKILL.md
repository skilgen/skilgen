---
name: platform-core
version: 0.6.0
domain: platform
sub_domain: platform-core
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
references:
  - ../SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Core Skill

## Overview
Shared core guidance for scoring, freshness, diffing, context loading, and validation primitives.

## Check These Paths First
- {{project_root}}/skilgen/core/__init__.py
- {{project_root}}/skilgen/core/analytics.py
- {{project_root}}/skilgen/core/audit.py
- {{project_root}}/skilgen/core/auth_tokens.py

## Patterns
### Inferred child domain patterns
- shared models
- freshness and scoring
- validation primitives

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `platform/platform-core`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
