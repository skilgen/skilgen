# Traceability

This file maps requirements and detected code evidence to the generated Skilgen outputs.

## Requirements Source
- Source file: `README.md`
- Source hash: `62b179fa1c51`

## Intent To Output Mapping
### Endpoints
- Intent: | Surface | Purpose | Key Routes |
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: - Coverage SLA critical-operation taxonomy loading from `apps/api/api/v8/insights/critical_ops.yaml`.
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: - v8 Audit APIs for event log, reports, exports, evidence packages, hash-chain verification, and WORM root publishing.
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: - v8 Skills APIs and screens for registry, score, drift, provenance, SkillQL, and repos.
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: - v8 Settings APIs and screens for connectors and RBAC foundations.
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: | Dashboard | `apps/dashboard` | Next.js App Router dashboard. v8 routes live in `apps/dashboard/app/(v8)`. |
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/parsers/sql_schema.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`

### UI Flows
- Intent: The migrated v8 app lives under `apps/dashboard/app/(v8)` and uses the Skillayer governance shell.
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: | Dashboard | `apps/dashboard` | Next.js App Router dashboard. v8 routes live in `apps/dashboard/app/(v8)`. |
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Run the dashboard:
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: npm --workspace apps/dashboard run dev
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Useful dashboard checks:
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: npm run lint --workspace apps/dashboard
  Domain: `frontend`
  Evidence: requirements-driven only
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`

### Feature Planning
- Intent: Current feature slices tracked in `FEATURES.md` include:
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: ## Feature Delivery Rules
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: 1. Pick one coherent PRD feature slice.
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: 8. Open or update a GitHub PR for the automation run with feature summary, verification results, evaluator result, and screenshot proof.
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: New feature PRs should attach fresh desktop and mobile screenshots for changed v8 screens. Screenshot capture failures should be treated as blockers unless explicitly accepted by the reviewer.
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: - `FEATURES.md`: feature inventory and completed slices.
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`

## Domain Evidence

### requirements
- Key files: `README.md`
- Key patterns: requirements-first planning, skill scaffolding, agent operating guidance
- Sub-domains: none

### platform
- Key files: `skilgen/__init__.py`, `skilgen/autoupdate.py`, `skilgen/agents/__init__.py`, `skilgen/agents/architecture_planner.py`, `skilgen/cli/__init__.py`, `skilgen/cli/main.py`, `skilgen/core/__init__.py`, `skilgen/core/analytics.py`
- Key patterns: tooling platform, generation engine, repo-local operating surface
- Sub-domains: platform-runtime, platform-agents, platform-cli, platform-core, platform-generators, platform-scripts

### platform-runtime
- Key files: `skilgen/__init__.py`, `skilgen/autoupdate.py`, `skilgen/deep_agents_core.py`, `skilgen/deep_agents_runtime.py`, `skilgen/delivery.py`, `setup.py`
- Key patterns: runtime orchestration, repo-wide coordination, package entrypoints
- Sub-domains: none

### platform-agents
- Key files: `skilgen/agents/__init__.py`, `skilgen/agents/architecture_planner.py`, `skilgen/agents/codebase_signals.py`, `skilgen/agents/decision_planner.py`, `skilgen/agents/domain_graph_planner.py`, `skilgen/agents/evidence_graph.py`
- Key patterns: domain inference, architecture synthesis, agent planning logic
- Sub-domains: none

### platform-cli
- Key files: `skilgen/cli/__init__.py`, `skilgen/cli/main.py`
- Key patterns: command surfaces, operator UX, progress orchestration
- Sub-domains: none

### platform-core
- Key files: `skilgen/core/__init__.py`, `skilgen/core/analytics.py`, `skilgen/core/audit.py`, `skilgen/core/auth_tokens.py`, `skilgen/core/config.py`, `skilgen/core/context.py`
- Key patterns: shared models, freshness and scoring, validation primitives
- Sub-domains: none

### platform-generators
- Key files: `skilgen/generators/__init__.py`, `skilgen/generators/package.py`, `skilgen/generators/skills.py`
- Key patterns: artifact rendering, materialization flow, repo-local outputs
- Sub-domains: none

### platform-scripts
- Key files: `scripts/bump_version.py`, `scripts/deploy_api.py`, `scripts/deploy_dashboard.py`, `scripts/deploy_web.py`, `scripts/run_requirements_pipeline.py`
- Key patterns: maintenance automation, release helpers, pipeline scripts
- Sub-domains: none

### roadmap
- Key files: `skills/roadmap/SKILL.md`, `REPORT.md`
- Key patterns: phase-based delivery, sequenced implementation planning, traceable next steps
- Sub-domains: roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3

### roadmap-phase-0
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-1
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-2
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-3
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

## Architecture Traceability

### requirements
- Summary: Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.
- Evidence paths: `README.md`
- Recommended skill path: `skills/requirements/SKILL.md`

### platform
- Summary: Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- Evidence paths: `skilgen/__init__.py`, `skilgen/autoupdate.py`, `skilgen/agents/__init__.py`, `skilgen/agents/architecture_planner.py`, `skilgen/cli/__init__.py`, `skilgen/cli/main.py`
- Recommended skill path: `skills/platform/SKILL.md`

### roadmap
- Summary: Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.
- Evidence paths: `skills/roadmap/SKILL.md`, `REPORT.md`
- Recommended skill path: `skills/roadmap/SKILL.md`

## Generated Outputs
- `ANALYSIS.md` for full machine-readable project analysis
- `ARCHITECTURE.md` for evidence-backed domain architecture
- `FEATURES.md` for detected and planned feature inventory
- `REPORT.md` for human-readable summary
- `skills/MANIFEST.md` and `skills/GRAPH.md` for skill discovery
- `skills/<domain>/SKILL.md` for domain-specific execution guidance

## External Skill Traceability
- Policy mode: `permissive`
- Installed `agentskills-spec` from `https://github.com/agentskills/agentskills.git`
  Trust: `spec` score `7`
  License: `Apache License`
- Installed `anthropic-skills` from `https://github.com/anthropics/skills.git`
  Trust: `official` score `7`
  License: `unknown`
- Installed `awesome-copilot` from `https://github.com/github/awesome-copilot.git`
  Trust: `official` score `8`
  License: `MIT License`

### Preferred External Packs
- `anthropic-skills`: Detected Claude/Anthropic repo hints.
- `awesome-copilot`: Detected GitHub Copilot instructions or workspace setup.
- `agentskills-spec`: Detected SKILL.md-style files or an existing skills tree.

## Enterprise Skill Traceability
- No active enterprise skills were installed for this run.

## MCP Connector Traceability
- Active connector `azure` (Microsoft Azure): Connect agents to Azure services with the official Azure MCP server.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/Azure/azure-mcp`
- Active connector `azure-kubernetes` (Microsoft Azure): Inspect Kubernetes clusters through Microsoft's official Azure-backed Kubernetes MCP server.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/Azure/mcp-kubernetes`
- Active connector `compass` (Atlassian): Use the Atlassian MCP server to access Compass service ownership and software catalog context.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/atlassian/atlassian-mcp-server`
- Active connector `confluence` (Atlassian): Search and read internal documentation, playbooks, and architecture notes.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://www.atlassian.com/platform/remote-mcp-server`
- Active connector `datadog` (Datadog): Inspect metrics, traces, monitors, and production signals.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://docs.datadoghq.com/llm_observability/instrumentation/mcp/`
- Active connector `figma` (Figma): Bring design context directly into coding workflows through Figma's official MCP server.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/mcp/com.figma.mcp/mcp`
- Active connector `github-enterprise` (GitHub): Read enterprise repositories, pull requests, and actions state.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp`
- Active connector `jira` (Atlassian): Track issues, delivery state, and engineering workflows.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://www.atlassian.com/platform/remote-mcp-server`

### Recommended MCP Connectors
- `jira` (`official`, oauth `True`): Detected connector keywords: jira, atlassian.
- `confluence` (`official`, oauth `True`): Detected connector keywords: confluence.
- `compass` (`official`, oauth `True`): Detected connector keywords: atlassian compass, compass.
- `slack` (`official`, oauth `True`): Detected connector keywords: slack.
- `datadog` (`official`, oauth `True`): Detected connector keywords: datadog.
- `github-enterprise` (`official`, oauth `True`): Detected connector keywords: github.

## Gaps And Next Actions
- No major delivery gaps were inferred from the current codebase and requirement inputs.
