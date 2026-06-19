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
- `plugins` (0.82): Folder-native guidance for the repo's `plugins` surface, using its own implementation boundary instead of a static backend/frontend assumption.
- `scripts` (0.82): Folder-native guidance for the repo's `scripts` surface, using its own implementation boundary instead of a static backend/frontend assumption.
- `roadmap` (0.84): Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.

## Skill Entry Points
- `skills/MANIFEST.md`: Start here to discover the generated skill tree.
- `skills/plugins/SKILL.md`: Parent skill for the inferred `plugins` domain.
- `skills/scripts/SKILL.md`: Parent skill for the inferred `scripts` domain.
- `skills/roadmap/SKILL.md`: Parent skill for the inferred `roadmap` domain.

## External Skill Packs
- `anthropic-skills` (anthropic, trust `official`): installed at `/private/tmp/claude-code/.skilgen/external-skills/sources/anthropic-skills`
- `huggingface-skills` (huggingface, trust `official`): installed at `/private/tmp/claude-code/.skilgen/external-skills/sources/huggingface-skills`
- `huggingface-upskill` (huggingface, trust `official`): installed at `/private/tmp/claude-code/.skilgen/external-skills/sources/huggingface-upskill`

## Active External Skill Packs
- `anthropic-skills` (anthropic-skills, trust score 7): load from `/private/tmp/claude-code/.skilgen/external-skills/sources/anthropic-skills`
- `huggingface-skills` (huggingface-skills, trust score 8): load from `/private/tmp/claude-code/.skilgen/external-skills/sources/huggingface-skills`
- `huggingface-upskill` (huggingface-skills, trust score 8): load from `/private/tmp/claude-code/.skilgen/external-skills/sources/huggingface-upskill`

## External Skill Policy
- Policy mode: `permissive`
- Auto install enabled: `True`
- Auto activate enabled: `True`

## Preferred External Skill Packs
- `anthropic-skills` (score 87): Detected Claude/Anthropic repo hints.
- `huggingface-skills` (score 82): Detected Hugging Face package usage.
- `huggingface-upskill` (score 68): Detected Hugging Face evaluation or teacher/student workflow hints.

## Enterprise Skill Packs
- No enterprise skill packs are currently active.

## MCP Connectors
- `azure` (Microsoft Azure, source `official`, auth `oauth2`): Connect agents to Azure services with the official Azure MCP server.
- `azure-kubernetes` (Microsoft Azure, source `official`, auth `oauth2`): Inspect Kubernetes clusters through Microsoft's official Azure-backed Kubernetes MCP server.
- `datadog` (Datadog, source `official`, auth `oauth2`): Inspect metrics, traces, monitors, and production signals.
- `github-enterprise` (GitHub, source `official`, auth `oauth2`): Read enterprise repositories, pull requests, and actions state.
- `jira` (Atlassian, source `official`, auth `oauth2`): Track issues, delivery state, and engineering workflows.
- `slack` (Slack, source `official`, auth `oauth2`): Read team communication context and incident coordination threads.
- `terraform` (HashiCorp, source `official`, auth `oauth2`): Inspect infrastructure definitions, plans, and cloud rollout workflows.

## Recommended MCP Connectors
- `jira` (source `official`, oauth `True`): Detected connector keywords: jira, atlassian.
- `slack` (source `official`, oauth `True`): Detected connector keywords: slack.
- `datadog` (source `official`, oauth `True`): Detected connector keywords: datadog.
- `github-enterprise` (source `official`, oauth `True`): Detected connector keywords: github.
- `azure` (source `official`, oauth `True`): Detected connector keywords: azure.
- `azure-kubernetes` (source `official`, oauth `True`): Detected connector keywords: aks.
- `terraform` (source `official`, oauth `True`): Detected connector keywords: terraform, hashicorp.
- `sentry` (source `official`, oauth `True`): Detected connector keywords: sentry.

## Suggested External Skill Packs
- `awesome-agent-skills-heilcheng`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-skillmatic`: Recommended directory of adjacent agent skills.
- `awesome-agent-skills-voltagent`: Recommended directory of adjacent agent skills.
- `awesome-llm-skills`: Recommended directory of adjacent agent skills.
- `curated-ai-agent-skills`: Recommended curated cross-agent collection.
- `skill-seekers`: Recommended tooling for converting docs and repos into skills.

## Recommended Start Order
- Input mode: `codebase only`
- Detected domains: plugins, plugins-hookify, scripts, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Decision planner refresh recommendation: `False`
- Decision planner reason: No source changes were detected, so agents can reuse the current skill tree and run memory.
- Load these prioritized skills first:
- `skills/plugins/SKILL.md`
- `skills/scripts/SKILL.md`
- `skills/roadmap/SKILL.md`
- `.skilgen/external-skills/normalized/anthropic-skills/SUMMARY.md`
- `.skilgen/external-skills/normalized/huggingface-skills/SUMMARY.md`
- `.skilgen/external-skills/normalized/huggingface-upskill/SUMMARY.md`
- Load decision memory in this order:
  - `.skilgen/memory/current_run.json`
  - `.skilgen/state/freshness.json`
  - `.skilgen/external-skills/lock.json`
  - `.skilgen/memory/runs/run-0e40bd952a3f.json`
  - `.skilgen/external-skills/normalized/anthropic-skills/SUMMARY.md`
  - `.skilgen/external-skills/normalized/anthropic-skills/index.json`
  - `.skilgen/external-skills/normalized/huggingface-skills/SUMMARY.md`
  - `.skilgen/external-skills/normalized/huggingface-skills/index.json`
  - `.skilgen/external-skills/normalized/huggingface-upskill/SUMMARY.md`
  - `.skilgen/external-skills/normalized/huggingface-upskill/index.json`

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
- `/private/tmp/claude-code`
