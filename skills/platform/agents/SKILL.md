---
name: platform-agents
version: 0.6.0
domain: platform
sub_domain: platform-agents
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
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

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `platform/platform-agents`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../roadmap/SKILL.md
