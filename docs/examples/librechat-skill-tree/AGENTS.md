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

## Inferred Domains
- `api` (0.87): Backend application guidance for API routes, services, persistence, auth, and runtime orchestration under the repo's `api/` surface.
- `client` (0.87): Frontend application guidance for the user-facing client, routes, UI composition, and client-side runtime behavior.
- `config` (0.87): Configuration guidance for runtime configuration, feature flags, translation setup, and environment-driven behavior.
- `e2e` (0.87): End-to-end testing guidance for browser workflows, setup, and cross-surface regression coverage.
- `packages` (0.87): Shared package guidance for reusable internal packages that support the app runtime and product surfaces.
- `roadmap` (0.84): Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## Skill Entry Points
- `skills/MANIFEST.md`: Start here to discover the generated skill tree.
- `skills/api/SKILL.md`: Parent skill for the inferred `api` domain.
- `skills/client/SKILL.md`: Parent skill for the inferred `client` domain.
- `skills/config/SKILL.md`: Parent skill for the inferred `config` domain.
- `skills/e2e/SKILL.md`: Parent skill for the inferred `e2e` domain.
- `skills/packages/SKILL.md`: Parent skill for the inferred `packages` domain.
- `skills/roadmap/SKILL.md`: Parent skill for the inferred `roadmap` domain.

## External Skill Packs
- No external skill packs have been installed yet.

## Active External Skill Packs
- No external skill packs are currently active.

## External Skill Policy
- Policy mode: `permissive`
- Auto install enabled: `True`
- Auto activate enabled: `True`

## Preferred External Skill Packs
- No active external skill packs have been ranked yet.

## Enterprise Skill Packs
- No enterprise skill packs are currently active.

## MCP Connectors
- No MCP connectors are currently active.

## Recommended MCP Connectors
- `github-enterprise` (source `official`, oauth `True`): Detected connector keywords: github.
- `azure` (source `official`, oauth `True`): Detected connector keywords: azure.
- `azure-kubernetes` (source `official`, oauth `True`): Detected connector keywords: aks.
- `figma` (source `official`, oauth `True`): Detected connector keywords: figma.

## Suggested External Skill Packs
- `awesome-agent-skills-heilcheng`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-skillmatic`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-voltagent`: Recommended directory of adjacent agent skills.
- `awesome-llm-skills`: Recommended directory of adjacent agent skills.
- `curated-ai-agent-skills`: Recommended curated cross-agent collection.
- `skill-seekers`: Recommended tooling for converting docs and repos into skills.
- `skills-benchmarks`: Recommended because LangChain/LangSmith was detected.

## Recommended Start Order
- Input mode: `codebase only`
- Detected domains: api, api-app, api-cache, api-config, api-db, api-server, api-strategies, api-test, api-utils, client, client-src, config, config-translations, e2e, e2e-setup, e2e-specs, packages, packages-api, packages-client, packages-data-provider, packages-data-schemas, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Decision planner refresh recommendation: `True`
- Decision planner reason: Source changes were detected and the impacted domains should be refreshed before the next coding task.
- Load these prioritized skills first:
- `skills/api/SKILL.md`
- `skills/client/SKILL.md`
- `skills/config/SKILL.md`
- `skills/e2e/SKILL.md`
- `skills/packages/SKILL.md`
- `skills/roadmap/SKILL.md`
- Load decision memory in this order:
  - `.skilgen/memory/current_run.json`
  - `.skilgen/state/freshness.json`
  - `.skilgen/external-skills/lock.json`

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
- `/tmp/librechat-dashboard-clean-0414`
