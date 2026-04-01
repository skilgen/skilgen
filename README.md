<p align="center">
  <img src="docs/assets/skilgen.svg" alt="Skilgen" width="280" />
</p>

<h1 align="center">Skilgen</h1>

<p align="center">
  <strong>The living skill system for AI coding agents.</strong><br/>
  Turn a codebase, a PRD, or both into a self-updating skill tree that keeps agents in sync with your code as it evolves.
</p>

<p align="center">
  <a href="https://pypi.org/project/skilgen/"><img src="https://img.shields.io/pypi/v/skilgen?color=blue" alt="PyPI" /></a>
  <a href="https://github.com/skilgen/skilgen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/skilgen/skilgen" alt="License" /></a>
  <a href="https://github.com/skilgen/skilgen/stargazers"><img src="https://img.shields.io/github/stars/skilgen/skilgen?style=social" alt="Stars" /></a>
  <a href="https://agentskills.io/specification"><img src="https://img.shields.io/badge/Agent_Skills-compatible-green" alt="Agent Skills compatible" /></a>
</p>

---

## The Problem

Every AI coding agent — Claude Code, Codex, Copilot, Cursor — starts from scratch. It doesn't know your architecture, your domain boundaries, your implementation patterns, or your product requirements. You re-explain the same context in every conversation. You write skills by hand. They go stale the moment your code changes. There's no way to know if a skill still reflects reality.

## What Skilgen Does

Skilgen reads your codebase, your requirements, or both — and generates a complete, production-grade skill tree that agents can use immediately. Then it **watches your code and auto-regenerates stale skills when things change**.

```
skilgen deliver --project-root . --requirements docs/prd.docx
```

That one command produces:

```
.
├── FEATURES.md            # Product behavior inventory
├── REPORT.md              # Project-level understanding
├── TRACEABILITY.md        # Source → output reasoning
├── AGENTS.md              # Agent operating guide
└── skills/
    ├── MANIFEST.md        # Entry-point discovery
    ├── requirements/
    │   ├── SKILL.md       # PRD-grounded guidance
    │   └── SUMMARY.md
    ├── backend/
    │   ├── SKILL.md       # Backend domain guidance
    │   ├── api/SKILL.md
    │   ├── auth/SKILL.md
    │   ├── data/SKILL.md
    │   └── testing/SKILL.md
    ├── frontend/
    │   ├── SKILL.md
    │   └── components/SKILL.md
    └── roadmap/
        ├── SKILL.md
        └── phase-*/SKILL.md
```

Every generated skill references **real files, real patterns, and real domain boundaries** from your codebase — not generic LLM advice.

---

## How Skilgen Compares

| Capability | Skilgen | Anthropic<br/>`skill-creator` | OpenAI Codex<br/>`$skill-creator` | Skill Seekers | skills.sh /<br/>SkillKit |
|:---|:---:|:---:|:---:|:---:|:---:|
| Codebase → full skill tree | ✅ | — | — | Single file | — |
| PRD → skill tree | ✅ | — | — | — | — |
| Codebase + PRD combined | ✅ | — | — | — | — |
| Auto-update on code changes | ✅ | — | — | — | — |
| Freshness & drift detection | ✅ | — | — | — | — |
| Project memory across runs | ✅ | — | — | — | — |
| Domain graph with cross-refs | ✅ | — | — | — | — |
| Enterprise MCP connector catalog | ✅ | — | — | — | — |
| External skill trust scoring | ✅ | — | — | — | — |
| Multi-model provider support | ✅ | Claude only | OpenAI only | Claude / Gemini | N/A |
| Python SDK + HTTP API | ✅ | — | — | — | — |
| Eval / benchmark loop | — | ✅ | — | — | — |
| Skill install & distribution | Via catalog | Via plugin | Via `$skill-installer` | — | ✅ |

Anthropic and OpenAI ship **interactive wizards** that help you write one skill at a time. Skill Seekers generates a single skill file from docs or repos. skills.sh and SkillKit are distribution platforms for installing existing skills.

Skilgen generates an **entire living skill tree** — grounded in your actual codebase and requirements — that auto-updates, tracks drift, and remembers project context across runs.

---

## Why Skilgen

### Skills That Stay Alive

Other tools generate a skill file and forget about it. Skilgen is a **living system**.

Set `update_trigger: auto` in your config and Skilgen runs a background worker that watches your project. When Claude Code, Codex, or any tool changes a file, Skilgen detects it, identifies which skills are affected, and regenerates only what's stale.

```bash
skilgen autoupdate enable --project-root .

# Skills auto-regenerate when your code changes.
# No manual intervention. No stale context. Ever.
```

### It Knows When Skills Are Out of Date

Skilgen tracks the freshness of every generated skill against every source file. At any point you can ask:

```bash
skilgen status --project-root .
```

And it tells you which source files changed, which domains are impacted, and which skills need a refresh — with a clear reason why.

No other tool does this.

### Codebase + PRD = Highest Fidelity

Most skill generators work from either code or docs. Skilgen can take both and cross-reference them:

- **Codebase only** -> skills grounded in what exists today
- **PRD only** -> skills grounded in what you intend to build
- **Both together** -> skills that bridge implementation reality with product intent

```bash
# From codebase only
skilgen deliver --project-root .

# From a PRD only
skilgen intent --requirements docs/prd.docx

# Both together for the best output
skilgen deliver --project-root . --requirements docs/prd.docx
```

### Deep Analysis, Not a Prompt Wrapper

Skilgen doesn't send your codebase to an LLM with a single prompt and hope for the best. It runs a **multi-agent analysis pipeline** that decomposes your project into frameworks, signals, domains, relationships, features, and a roadmap — then synthesizes all of that into a coherent skill tree with cross-references.

The result: skills that understand your backend routes talk to your auth layer, that your frontend components depend on specific API contracts, and that your test suite covers certain domains but not others.

### Project Memory

Skilgen remembers across runs. It persists project context — domains, priorities, architectural decisions, and freshness state — so each subsequent run is smarter than the last. It knows what changed, what to skip, and what to focus on.

### Enterprise MCP Connector Discovery

Skilgen ships with a curated catalog of enterprise MCP connectors — Jira, Confluence, Slack, GitHub Enterprise, GitLab, Azure, Terraform, Datadog, Snowflake, Stripe, Figma, and more — each with verified source URLs, OAuth metadata, and enterprise-readiness flags.

```bash
# Auto-detect which connectors your codebase needs
skilgen connectors recommend --project-root .

# Activate one
skilgen connectors activate jira --project-root .
```

Skilgen scans your codebase, detects which tools you use, and recommends only what's relevant — respecting your allowlist, denylist, and security policy.

### External Skill Sources With Trust Scoring

Skilgen catalogs skill collections from across the ecosystem — Anthropic, LangChain, Hugging Face, AgentSkills.io, and community sources — and scores each by trust level so you know what you're installing.

```bash
# Browse available sources
skilgen skills list

# Install from the catalog
skilgen skills install --slug anthropic-skills

# Rank by trust
skilgen skills rank

# Lock versions for reproducibility
skilgen skills lock export
```

Enterprise teams can enforce policy: restrict trust levels, allowlist specific sources, and lock versions across the organization.

### Enterprise Skill Packs

Ingest organization-wide skills from shared repos or internal paths — coding standards, architectural guidelines, security conventions — and have agents load them alongside project-local skills.

```bash
# Ingest from a git repo
skilgen enterprise ingest --name corporate-standards \
  --git-url https://github.com/your-org/engineering-skills.git

# Generate from internal source files
skilgen enterprise generate --name auth-patterns \
  --source-paths src/auth/ docs/auth-spec.md
```

### Works With Every Major Model Provider

```yaml
model_provider: openai        # or anthropic, gemini, huggingface, groq, openrouter
model: gpt-4.1-mini           # any model from your provider
api_key_env: OPENAI_API_KEY   # auto-mapped per provider
```

No API key? Skilgen falls back to a **local deterministic runtime** — faster, no cost, still functional.

---

## Quick Start

```bash
pip install skilgen
```

```bash
# Initialize config
skilgen init --project-root .

# See what Skilgen detects in your codebase
skilgen fingerprint --project-root .

# Generate the full skill tree
skilgen deliver --project-root .

# Or combine with a PRD for the highest-fidelity output
skilgen deliver --project-root . --requirements docs/prd.docx

# Enable auto-update (skills regenerate when code changes)
skilgen autoupdate enable --project-root .
```

Requires Python 3.11+.

---

## Commands

| Command | What It Does |
|---|---|
| `skilgen init` | Write a default `skilgen.yml` config |
| `skilgen fingerprint` | Detect frameworks, stack, and project shape |
| `skilgen map` | Build an import relationship map |
| `skilgen analyze` | Full framework, signal, and relationship analysis |
| `skilgen decide` | Recommend which skills to refresh and prioritize |
| `skilgen intent` | Parse a requirements file into structured intent |
| `skilgen features` | Build a feature inventory from code + requirements |
| `skilgen plan` | Generate a phased roadmap |
| `skilgen deliver` | Run the full generation flow |
| `skilgen update` | Refresh outputs for selected domains |
| `skilgen preview` | Dry-run: see what would be generated without writing |
| `skilgen watch` | Foreground file watcher with continuous regeneration |
| `skilgen autoupdate` | Manage the background auto-update daemon |
| `skilgen status` | Show freshness state and generated output status |
| `skilgen report` | Summary report for the project |
| `skilgen validate` | Validate generated outputs and skill references |
| `skilgen doctor` | Diagnose runtime, model config, and API key setup |
| `skilgen skills` | Discover, install, and manage external skill sources |
| `skilgen enterprise` | Ingest and generate enterprise-wide skill packs |
| `skilgen connectors` | Discover and manage approved MCP connectors |
| `skilgen scan` | Generate docs and skills (alias for deliver) |
| `skilgen serve` | Run the HTTP API server |

---

## Python SDK

```python
import skilgen

# Generate the full skill tree
skilgen.deliver_project("docs/prd.docx", ".")

# Fingerprint the codebase
result = skilgen.fingerprint_codebase(".")

# Get freshness status
status = skilgen.project_status(".")

# Start/stop auto-update
skilgen.start_auto_update(".", requirements="docs/prd.docx")
skilgen.stop_auto_update(".")

# Manage external skills
skilgen.install_skill_source(".", slug="anthropic-skills")
skilgen.rank_skill_sources(".")

# Enterprise features
skilgen.recommend_project_mcp_connectors(".")
skilgen.activate_project_mcp_connector("jira", ".")

# Background jobs
job = skilgen.start_deliver_job("docs/prd.docx", ".")
skilgen.get_job_status(job["job_id"])
```

---

## HTTP API

Run `skilgen serve` to start the API server. Every CLI command is available as an HTTP endpoint for CI pipelines, platform integrations, and internal tooling.

---

## Configuration

`skilgen init` writes a `skilgen.yml` with sensible defaults:

```yaml
include_paths:
  - .
exclude_paths:
  - .git
  - __pycache__
  - .venv
  - node_modules
  - .skilgen

skill_depth: 2
update_trigger: auto           # auto | watch | manual

# Model — pick your provider
model_provider: anthropic      # openai | anthropic | gemini | huggingface | groq | openrouter
model: claude-sonnet-4-5
api_key_env: ANTHROPIC_API_KEY

# External skills governance
auto_install_external_skills: true
external_skills_policy_mode: permissive   # permissive | restrictive
external_skills_allowed_trust_levels:
  - official
  - spec
  - community
  - curated

# Enterprise MCP connector policy
auto_activate_mcp_connectors: true
mcp_connectors_require_official_source: true
mcp_connectors_require_oauth: true

# Enterprise skill sources
enterprise_skill_paths: []
enterprise_skill_git_urls: []
```

---

## Agent Skills Compatible

Skilgen generates skills that follow the [Agent Skills open standard](https://agentskills.io/specification). Every `SKILL.md` output works with:

- **Claude Code** — drop into `.claude/skills/`
- **OpenAI Codex** — drop into `.agents/skills/`
- **GitHub Copilot** — discovered automatically in VS Code
- **Cursor, Windsurf, Gemini CLI, OpenCode, Roo Code** — all compatible

---

## Best For

- **AI-first teams** that use Claude Code, Codex, or Copilot daily
- **Enterprise codebases** with complex domain boundaries and compliance needs
- **Greenfield projects** starting from a PRD — get agent-ready skills before writing code
- **Existing repos** where agents keep making the same mistakes because they lack context
- **Platform teams** building internal developer tools around AI agents

---

## Status

- **v0.4.0** — stable, published on [PyPI](https://pypi.org/project/skilgen/)
- 6 model providers supported
- Auto-update, freshness tracking, and project memory are production-ready
- Curated external skill catalog with trust scoring and version locking
- Enterprise MCP connector discovery with OAuth and security metadata
- Full Python SDK, CLI, and HTTP API

---

## Contributing

Contributions are welcome. See the repo for guidelines.

## License

[MIT](LICENSE)

---

<p align="center">
  <strong>Stop re-explaining your codebase to every agent.</strong><br/>
  Let Skilgen build the context layer that keeps them smart.
</p>
