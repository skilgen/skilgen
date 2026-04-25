# Skilgen Agent Contract

## Project Overview
This repository was generated or refreshed by Skilgen to help coding agents work from project-specific context instead of generic prompts.
The current input mode was: `codebase only`.

## How To Work In This Repo
1. Open `skills/MANIFEST.md` first.
2. Open the most specific inferred child skill before changing code.
3. Use `FEATURES.md`, `REPORT.md`, and `TRACEABILITY.md` to understand intent, current shape, and evidence.
4. Keep generated references relative so the skill tree stays portable across repos.
5. When backend behavior changes, test every touched endpoint before closing the task.

## Skillayer Integration
Before coding, load skills from `https://api.skillayer.com/repos/65c1eff3-a026-4185-bf2c-e9291ac52eeb/skills/load` using `API-Key: $SKILLAYER_API_KEY`.
Use loaded skills as repo-specific operating guidance.

## Inferred Domains
- `platform` (0.90): Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- `roadmap` (0.84): Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## Skill Entry Points
- `skills/MANIFEST.md`: Start here to discover the generated skill tree.
- `skills/platform/SKILL.md`: Parent skill for the inferred `platform` domain.
- `skills/roadmap/SKILL.md`: Parent skill for the inferred `roadmap` domain.

## External Skill Packs
- `agentskills-spec` (spec, trust `spec`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/agentskills-spec`
- `anthropic-skills` (anthropic, trust `official`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/anthropic-skills`
- `huggingface-skills` (huggingface, trust `official`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/huggingface-skills`
- `huggingface-upskill` (huggingface, trust `official`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/huggingface-upskill`
- `langchain-skills` (langchain, trust `official`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/langchain-skills`
- `langsmith-skills` (langchain, trust `official`): installed at `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/langsmith-skills`

## Active External Skill Packs
- `agentskills-spec` (skill-spec, trust score 7): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/agentskills-spec`
- `anthropic-skills` (anthropic-skills, trust score 7): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/anthropic-skills`
- `huggingface-skills` (huggingface-skills, trust score 8): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/huggingface-skills`
- `huggingface-upskill` (huggingface-skills, trust score 8): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/huggingface-upskill`
- `langchain-skills` (langchain-skills, trust score 7): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/langchain-skills`
- `langsmith-skills` (langchain-skills, trust score 7): load from `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work/.skilgen/external-skills/sources/langsmith-skills`

## External Skill Policy
- Policy mode: `permissive`
- Auto install enabled: `True`
- Auto activate enabled: `True`

## Preferred External Skill Packs
- `anthropic-skills` (score 87): Detected Claude/Anthropic repo hints.
- `huggingface-skills` (score 75): Trust level `official` and ecosystem fit for this repo.
- `langchain-skills` (score 63): Trust level `official` and ecosystem fit for this repo.
- `huggingface-upskill` (score 61): Trust level `official` and ecosystem fit for this repo.
- `agentskills-spec` (score 58): Detected SKILL.md-style files or an existing skills tree.
- `langsmith-skills` (score 55): Trust level `official` and ecosystem fit for this repo.

## Enterprise Skill Packs
- No enterprise skill packs are currently active.

## MCP Connectors
- `azure` (Microsoft Azure, source `official`, auth `oauth2`): Connect agents to Azure services with the official Azure MCP server.
- `compass` (Atlassian, source `official`, auth `oauth2`): Use the Atlassian MCP server to access Compass service ownership and software catalog context.
- `confluence` (Atlassian, source `official`, auth `oauth2`): Search and read internal documentation, playbooks, and architecture notes.
- `github-enterprise` (GitHub, source `official`, auth `oauth2`): Read enterprise repositories, pull requests, and actions state.
- `jira` (Atlassian, source `official`, auth `oauth2`): Track issues, delivery state, and engineering workflows.
- `slack` (Slack, source `official`, auth `oauth2`): Read team communication context and incident coordination threads.
- `stripe` (Stripe, source `official`, auth `oauth2`): Work with customers, products, payments, and billing through Stripe's official MCP endpoints.
- `terraform` (HashiCorp, source `official`, auth `oauth2`): Inspect infrastructure definitions, plans, and cloud rollout workflows.

## Recommended MCP Connectors
- `jira` (source `official`, oauth `True`): Detected connector keywords: jira, atlassian.
- `confluence` (source `official`, oauth `True`): Detected connector keywords: confluence.
- `compass` (source `official`, oauth `True`): Detected connector keywords: atlassian compass, compass.
- `github-enterprise` (source `official`, oauth `True`): Detected connector keywords: github.
- `azure` (source `official`, oauth `True`): Detected connector keywords: azure.
- `stripe` (source `official`, oauth `True`): Detected connector keywords: stripe.

## Suggested External Skill Packs
- `awesome-agent-skills-heilcheng`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-skillmatic`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-voltagent`: Recommended directory of adjacent agent skills.
- `awesome-llm-skills`: Recommended directory of adjacent agent skills.
- `curated-ai-agent-skills`: Recommended curated cross-agent collection.
- `skill-seekers`: Recommended tooling for converting docs and repos into skills.

## Recommended Start Order
- Input mode: `codebase only`
- Detected domains: platform, platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Decision planner refresh recommendation: `True`
- Decision planner reason: Source changes were detected and the impacted domains should be refreshed before the next coding task.
- Load these prioritized skills first:
- `skills/platform/SKILL.md`
- `skills/roadmap/SKILL.md`
- `.skilgen/external-skills/normalized/anthropic-skills/SUMMARY.md`
- `.skilgen/external-skills/normalized/huggingface-skills/SUMMARY.md`
- `.skilgen/external-skills/normalized/langchain-skills/SUMMARY.md`
- Load decision memory in this order:
  - `.skilgen/memory/current_run.json`
  - `.skilgen/state/freshness.json`
  - `.skilgen/external-skills/lock.json`
  - `.skilgen/memory/runs/run-4d2fa3b2b305.json`
  - `.skilgen/external-skills/normalized/anthropic-skills/SUMMARY.md`
  - `.skilgen/external-skills/normalized/anthropic-skills/index.json`
  - `.skilgen/external-skills/normalized/huggingface-skills/SUMMARY.md`
  - `.skilgen/external-skills/normalized/huggingface-skills/index.json`
  - `.skilgen/external-skills/normalized/langchain-skills/SUMMARY.md`
  - `.skilgen/external-skills/normalized/langchain-skills/index.json`

## Skill Telemetry Hook
- When you actually open a repo skill file to use it during implementation, record that load with Skilgen analytics.
- Built-in hook command:
  - `python -m skilgen.cli.main analytics --project-root . --record-skill skills/backend/SKILL.md --context codex_live --agent codex`
- Record the most specific child skill you actually used, not just the parent skill Skilgen recommended.
- Use `codex_live`, `claude_code_live`, or another explicit runtime context so live metrics stay separate from planner warmups.
- Optional session metadata:
  - `python -m skilgen.cli.main analytics --project-root . --record-skill skills/backend/api/SKILL.md --context codex_live --agent codex --session-id task-123 --task "implement billing retry"`

## Generated Docs
- `ANALYSIS.md`: Machine-readable project analysis.
- `FEATURES.md`: Feature inventory from codebase and optional requirements.
- `REPORT.md`: Human-readable summary and suggested starting points.
- `TRACEABILITY.md`: Why outputs were generated and what evidence they came from.

## Execution Rules
- Prefer the generated skill guidance over ad-hoc prompting.
- If backend behavior changes, test all affected endpoints before closing the task.
- When adding new reusable patterns, update the relevant skill file and manifest references.
- Treat `AGENTS.md` as the top-level contract and the `skills/` tree as the operating system for coding agents.
- Use `TRACEABILITY.md` whenever you need to explain why a generated skill or document exists.

## Project Root
- `/Users/ravichanduummadisetti/Library/CloudStorage/OneDrive-Personal/skilgen/skilgen-upstream-work`
