---
name: requirements
version: 0.6.0
domain: requirements
sub_domain: platform
last_updated: 2026-04-30
triggered_by: requirements_pipeline
source_hash: 2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26
richness_score: 83
score:
  total: 83
  groundedness: 8
  coverage: 25
  freshness: 25
  structure: 25
references:
  - ../roadmap/SKILL.md
status: active
---

# Requirements Skill

## Overview
Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.

## Check These Paths First
- {{project_root}}/README.md

## Patterns
### Architecture responsibilities
- Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.
- requirements-first planning
- skill scaffolding
### Inferred domain patterns
- requirements-first planning
- skill scaffolding
- agent operating guidance
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.
### Architecture evidence
- Evidence: `README.md`
### Dependency signals
- `@eslint/js` in `packages/config/package.json` is medium; npm install @eslint/js.
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.
- `@radix-ui/react-label` in `packages/ui/package.json` is medium; npm install @radix-ui/react-label.

## Anti-patterns
- **Introduce a second pattern for the same workflow**: Don't introduce a second pattern for the same workflow — duplicated conventions make agent edits unreliable
- **Remove nearby verification steps**: Don't remove nearby verification steps — future agents need a fast way to prove behaviour still works
- **Leave file references vague**: Don't leave file references vague — agents waste time searching and may edit the wrong boundary

## How-To
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `keep`.

## Code Examples

### README.md
```
<p align="center">
  <img src="docs/assets/skilgen.svg" alt="Skilgen" width="480" />
</p>

<h2 align="center">The living skill system for AI coding agents</h2>

<p align="center">
  Every agent session starts from zero. Skilgen ends that.<br/>
  Generate, govern, and keep your codebase's agent knowledge current automatically.
</p>

<p align="center">
  <a href="https://pypi.org/project/skilgen/"><img src="https://img.shields.io/pypi/v/skilgen?color=efd37a&labelColor=0d1117&label=skilgen" alt="PyPI" /></a>
  <a href="https://pypi.org/project/skilgen/"><img src="https://img.shields.io/pypi/pyversions/skilgen?color=8fd9a8&labelColor=0d1117" alt="Python" /></a>
```

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `requirements/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
