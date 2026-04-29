# Skill Graph

This file summarizes the generated skill tree and cross references.

## Architecture Blueprint
- Headline: Evidence-backed architecture blueprint for the codebase
- Summary: Skilgen identified 3 top-level architecture domains from 90 evidence items and 13 domain graph nodes. Parser backends in use: empty, python-ast, regex. Source comprehension currently tracks 173 symbol-bearing files, 170 call-bearing files, 72 mapped tests, and 6 workspace packages.
- Hotspots:
  - Dominant languages: python.

## Materialization Decisions
### requirements
- decision: `keep`
- parent: `skills/requirements/SKILL.md`
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Keep as a first-class boundary because confidence is 0.99, 1 evidence paths cluster around one coherent responsibility set, and the boundary is clearer as a single skill than as shallower splits.
### platform
- decision: `split`
- parent: `skills/platform/SKILL.md`
- child skills:
  - `skills/platform/runtime/SKILL.md` (materialized)
  - `skills/platform/agents/SKILL.md` (materialized)
  - `skills/platform/cli/SKILL.md` (materialized)
  - `skills/platform/core/SKILL.md` (materialized)
  - `skills/platform/generators/SKILL.md` (materialized)
  - `skills/platform/scripts/SKILL.md` (materialized)
- cross-links:
  - `skills/requirements/SKILL.md`
  - `skills/roadmap/SKILL.md`
- rationale: Split because 6 concrete child skill surfaces emerged from 6 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around platform-runtime, platform-agents, platform-cli.
### roadmap
- decision: `split`
- parent: `skills/roadmap/SKILL.md`
- child skills:
  - `skills/roadmap/phase-0/SKILL.md` (materialized)
  - `skills/roadmap/phase-1/SKILL.md` (materialized)
  - `skills/roadmap/phase-2/SKILL.md` (materialized)
  - `skills/roadmap/phase-3/SKILL.md` (materialized)
- cross-links:
  - `skills/requirements/SKILL.md`
- rationale: Split because 4 concrete child skill surfaces emerged from 2 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around roadmap-phase-0, roadmap-phase-1, roadmap-phase-2.

## requirements/SKILL.md
- domain: `requirements`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`

## platform/SKILL.md
- domain: `platform`
- sub_domain: `platform`
- references:
  - `../requirements/SKILL.md`
  - `../roadmap/SKILL.md`
  - `runtime/SKILL.md`
  - `agents/SKILL.md`
  - `cli/SKILL.md`
  - `core/SKILL.md`
  - `generators/SKILL.md`
  - `scripts/SKILL.md`

## roadmap/SKILL.md
- domain: `roadmap`
- sub_domain: `platform`
- references:
  - `../requirements/SKILL.md`
  - `phase-0/SKILL.md`
  - `phase-1/SKILL.md`
  - `phase-2/SKILL.md`
  - `phase-3/SKILL.md`

## platform/runtime/SKILL.md
- domain: `platform`
- sub_domain: `platform-runtime`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/agents/SKILL.md
- domain: `platform`
- sub_domain: `platform-agents`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/cli/SKILL.md
- domain: `platform`
- sub_domain: `platform-cli`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/core/SKILL.md
- domain: `platform`
- sub_domain: `platform-core`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/generators/SKILL.md
- domain: `platform`
- sub_domain: `platform-generators`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/scripts/SKILL.md
- domain: `platform`
- sub_domain: `platform-scripts`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
  - `../../roadmap/SKILL.md`

## roadmap/phase-0/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-0`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`

## roadmap/phase-1/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-1`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`

## roadmap/phase-2/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-2`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`

## roadmap/phase-3/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-3`
- references:
  - `../SKILL.md`
  - `../../requirements/SKILL.md`
