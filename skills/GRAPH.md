# Skill Graph

This file summarizes the generated skill tree and cross references.

## Architecture Blueprint
- Headline: Evidence-backed architecture blueprint for the codebase
- Summary: Skilgen identified 2 top-level architecture domains from 38 evidence items and 12 domain graph nodes. Parser backends in use: empty, python-ast, regex. Source comprehension currently tracks 101 symbol-bearing files, 98 call-bearing files, 43 mapped tests, and 0 workspace packages.
- Hotspots:
  - Dominant languages: python.

## Materialization Decisions
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
  - `skills/roadmap/SKILL.md`
- rationale: Split because 6 concrete child skill surfaces emerged from 6 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around platform-runtime, platform-agents, platform-cli.
### roadmap
- decision: `split`
- parent: `skills/roadmap/SKILL.md`
- child skills:
  - `skills/roadmap/phase-0/SKILL.md` (planned)
  - `skills/roadmap/phase-1/SKILL.md` (planned)
  - `skills/roadmap/phase-2/SKILL.md` (planned)
  - `skills/roadmap/phase-3/SKILL.md` (planned)
- rationale: Split because 4 concrete child skill surfaces emerged from 2 grounded evidence paths. The parent skill can hold shared context while child skills isolate the distinct capability seams around roadmap-phase-0, roadmap-phase-1, roadmap-phase-2.

## platform/SKILL.md
- domain: `platform`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `runtime/SKILL.md`
  - `agents/SKILL.md`
  - `cli/SKILL.md`
  - `core/SKILL.md`
  - `generators/SKILL.md`
  - `scripts/SKILL.md`

## platform/runtime/SKILL.md
- domain: `platform`
- sub_domain: `platform-runtime`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/agents/SKILL.md
- domain: `platform`
- sub_domain: `platform-agents`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/cli/SKILL.md
- domain: `platform`
- sub_domain: `platform-cli`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/core/SKILL.md
- domain: `platform`
- sub_domain: `platform-core`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/generators/SKILL.md
- domain: `platform`
- sub_domain: `platform-generators`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## platform/scripts/SKILL.md
- domain: `platform`
- sub_domain: `platform-scripts`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`
