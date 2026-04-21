# Traceability

This file maps requirements and detected code evidence to the generated Skilgen outputs.

## Requirements Source
- Source file: `codebase-only input`
- Source hash: `54b3e3912fb4`

## Intent To Output Mapping
### Endpoints
- Intent: Detected route: skilgen/api/__init__.py
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: skilgen/api/jobs.py
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: skilgen/api/server.py
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: skilgen/api/service.py
  Domain: `backend`
  Evidence: `skilgen/api/__init__.py`, `skilgen/api/jobs.py`, `skilgen/api/server.py`, `skilgen/api/service.py`, `skilgen/core/auth_tokens.py`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`

### UI Flows
- No items extracted for this category.

### Feature Planning
- Intent: Codebase-only scan
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Generate skills from the current repository structure
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: skilgen/api/__init__.py
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: skilgen/api/jobs.py
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: skilgen/api/server.py
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: skilgen/api/service.py
  Domain: `operations`
  Evidence: `skilgen/api/jobs.py`, `tests/test_jobs.py`, `tests/__init__.py`, `tests/oidc_test_utils.py`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`

## Domain Evidence

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
- Key files: `scripts/bump_version.py`, `scripts/run_requirements_pipeline.py`
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
- Installed `huggingface-skills` from `https://github.com/huggingface/skills.git`
  Trust: `official` score `8`
  License: `Apache License`
- Installed `huggingface-upskill` from `https://github.com/huggingface/upskill.git`
  Trust: `official` score `8`
  License: `Apache License`
- Installed `langchain-skills` from `https://github.com/langchain-ai/langchain-skills.git`
  Trust: `official` score `7`
  License: `unknown`
- Installed `langsmith-skills` from `https://github.com/langchain-ai/langsmith-skills.git`
  Trust: `official` score `7`
  License: `unknown`

### Preferred External Packs
- `anthropic-skills`: Detected Claude/Anthropic repo hints.
- `huggingface-skills`: Detected Hugging Face package usage.
- `langchain-skills`: Detected LangChain/LangGraph/Deep Agents dependencies.
- `langsmith-skills`: Detected LangSmith observability or tracing usage.
- `huggingface-upskill`: Detected Hugging Face evaluation or teacher/student workflow hints.

## Enterprise Skill Traceability
- No active enterprise skills were installed for this run.

## MCP Connector Traceability
- Active connector `azure` (Microsoft Azure): Connect agents to Azure services with the official Azure MCP server.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/Azure/azure-mcp`
- Active connector `compass` (Atlassian): Use the Atlassian MCP server to access Compass service ownership and software catalog context.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/atlassian/atlassian-mcp-server`
- Active connector `confluence` (Atlassian): Search and read internal documentation, playbooks, and architecture notes.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://www.atlassian.com/platform/remote-mcp-server`
- Active connector `github-enterprise` (GitHub): Read enterprise repositories, pull requests, and actions state.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp`
- Active connector `jira` (Atlassian): Track issues, delivery state, and engineering workflows.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://www.atlassian.com/platform/remote-mcp-server`
- Active connector `slack` (Slack): Read team communication context and incident coordination threads.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://api.slack.com/automation/mcp`
- Active connector `terraform` (HashiCorp): Inspect infrastructure definitions, plans, and cloud rollout workflows.
  Source status: `official`; auth: `oauth2`; official source verified: `True`
  Authorization status: `pending_oauth`
  Official source: `https://github.com/mcp/hashicorp/terraform-mcp-server`

### Recommended MCP Connectors
- `jira` (`official`, oauth `True`): Detected connector keywords: jira, atlassian.
- `confluence` (`official`, oauth `True`): Detected connector keywords: confluence.
- `compass` (`official`, oauth `True`): Detected connector keywords: atlassian compass, compass.
- `slack` (`official`, oauth `True`): Detected connector keywords: slack.
- `github-enterprise` (`official`, oauth `True`): Detected connector keywords: github.
- `azure` (`official`, oauth `True`): Detected connector keywords: azure.

## Gaps And Next Actions
- This run was codebase-only, so roadmap and intent guidance came from implementation signals rather than a product spec.
