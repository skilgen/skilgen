---
name: roadmap
version: 0.6.0
domain: roadmap
sub_domain: platform
last_updated: 2026-04-19
triggered_by: requirements_pipeline
source_hash: 54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5
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
- Evidence: `REPORT.md`

## How-To
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `split`.

## Traceability
- Generated from requirements source hash: `54b3e3912fb4021cf8ea6032910bff2e5c26f6f56e460b806b6bfabad40cd6e5`
- Domain path: `roadmap/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- phase-0/SKILL.md
- phase-1/SKILL.md
- phase-2/SKILL.md
- phase-3/SKILL.md
