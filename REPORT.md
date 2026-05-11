# Report

## Summary
- Detected domains: requirements, platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Feature inventory entries: 18
- Backend route files: 4
- Frontend route files: 0
- Component files: 0
- Service files: 1
- Test files: 87
- Data model files: 1
- Persistence files: 2
- Background job files: 2
- Auth files: 5
- State files: 0
- Design system files: 0
- Architecture domains: 3

## Generated Outputs
- ANALYSIS.md
- ARCHITECTURE.md
- FEATURES.md
- REPORT.md
- TRACEABILITY.md
- skills/MANIFEST.md
- skills/GRAPH.md
- skills/<domain>/SKILL.md
- skills/<domain>/SUMMARY.md

## Recommended Starting Points
- Backend: start from `skilgen/api/__init__.py`
- Services: start from `skilgen/api/service.py`

## Architecture Highlights
- `requirements`: Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.
- `platform`: Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- `roadmap`: Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## External Skill Packs
- Installed packs: 2
- Active packs: 2
- Preferred packs to load first:
  - `awesome-copilot` (score 87, trust `official`, license `MIT License`)
  - `agentskills-spec` (score 58, trust `spec`, license `Apache License`)

## External Skill Provenance
- `agentskills-spec` from `https://github.com/agentskills/agentskills.git` at `2d3e01f590f68bee2cb76a3200823e93b2cc9eaa`
- `awesome-copilot` from `https://github.com/github/awesome-copilot.git` at `e07740bdd8e878cde35e3ee23eb2c1ab7afee864`
