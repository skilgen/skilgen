# Report

## Summary
- Detected domains: platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Feature inventory entries: 9
- Backend route files: 4
- Frontend route files: 0
- Component files: 0
- Service files: 1
- Test files: 45
- Data model files: 0
- Persistence files: 0
- Background job files: 2
- Auth files: 3
- State files: 0
- Design system files: 0
- Architecture domains: 2

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
- `platform`: Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- `roadmap`: Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## External Skill Packs
- Installed packs: 6
- Active packs: 6
- Preferred packs to load first:
  - `anthropic-skills` (score 87, trust `official`, license `unknown`)
  - `huggingface-skills` (score 87, trust `official`, license `Apache License`)
  - `langchain-skills` (score 80, trust `official`, license `unknown`)
  - `langsmith-skills` (score 77, trust `official`, license `unknown`)
  - `huggingface-upskill` (score 73, trust `official`, license `Apache License`)

## External Skill Provenance
- `agentskills-spec` from `https://github.com/agentskills/agentskills.git` at `8d8fcbc69e0c42e05922c2ffc287a3bbdef7b0a3`
- `anthropic-skills` from `https://github.com/anthropics/skills.git` at `2c7ec5e78b8e5d43ea02e90bb8826f6b9f147b0c`
- `huggingface-skills` from `https://github.com/huggingface/skills.git` at `061ab494cb145f43ae8f218939b99160e2c61c58`
- `huggingface-upskill` from `https://github.com/huggingface/upskill.git` at `2663c2141002b9bd0d1e342302f21b8f127be35d`
- `langchain-skills` from `https://github.com/langchain-ai/langchain-skills.git` at `f8115670953680937e66fd50923dff54d748c7f3`
- `langsmith-skills` from `https://github.com/langchain-ai/langsmith-skills.git` at `68c8bb6b4b7cb5b20870b7b6afb340f6c958b0e6`
