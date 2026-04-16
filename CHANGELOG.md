# Changelog

All notable changes to Skilgen will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [0.6.0] - Unreleased

### Added
- `Skilgen Score`, a repo-level quality standard for skill trees with groundedness, coverage, freshness, and structure subscores
- Opinionated score quality gates so stale, weakly grounded, low-coverage, or structurally incomplete skill systems cannot score artificially high
- Dynamic drill-down scoring for:
  - repo score
  - materialized domain scores
  - per-`SKILL.md` scores
  - inferred-only domains as a separate planning signal
- Score surfaces across the product:
  - `skilgen score`
  - `/score`
  - `/badge.svg`
  - eval scaffold and compare helpers
  - `skilgen-sync` GitHub Action
- `skilgen diff`, plus `/diff` and SDK diff access for showing stale skills, impacted domains, and freshness reasons
- Score history, trend, and regression tracking stored under `.skilgen/state/score-history.jsonl`
- Skill analytics with repo-local usage logging under `.skilgen/analytics/usage.jsonl`
- Evidence graph and architecture mode with:
  - `skilgen architecture`
  - `/architecture`
  - SDK architecture access
  - `ARCHITECTURE.md`
  - graph export in Mermaid and JSON forms
- Deeper source comprehension signals:
  - symbol graph
  - call graph
  - config/runtime graph
  - test-to-code mapping
- Multi-format document ingestion for:
  - Markdown, text, DOCX, PDF, HTML
  - JSON, YAML, XML, TOML, INI/CFG
  - CSV/TSV, XLSX, PPTX
- Extended repo scanning support for Java, Go, Rust, and COBOL/copybooks
- Private enterprise skill ingestion from URLs plus MCP policy packs for allow/deny/approval controls
- New docs and examples for architecture mode, evidence graph, score interpretation, diff workflow, legacy repos, enterprise repos, polyglot repos, and GitHub Actions

### Changed
- Refreshed the README to present Skilgen more clearly as a living skill system for coding agents
- Simplified onboarding and product positioning around self-updating skills, drift detection, enterprise MCP connectors, and external skill governance
- Made repo-local watcher and auto-update behavior git-aware so Skilgen can classify manual edits, head changes, merges, rebases, and related repository events
- Architecture synthesis now uses richer code evidence and source-graph signals instead of relying only on path heuristics
- Commands that reload project context now remember the last requirements file used for delivery, so diff/score/architecture remain consistent after requirements-backed runs

## [0.4.1] - Released

### Changed
- Refreshed the README to present Skilgen more clearly as a living skill system for coding agents
- Simplified onboarding and product positioning around self-updating skills, drift detection, enterprise MCP connectors, and external skill governance

## [0.4.0] - Released

### Added
- Enterprise skill ingestion and generation workflows
- Official OAuth-ready MCP connector catalog, recommendations, and activation policy gates
- Automatic repo-local skill refresh worker enabled through `skilgen init`
- Improved README onboarding with quick start, repo-local flow, and generated-skill-system examples
- Deep-Agents-driven dynamic domain graph planning
- Skill freshness state and selective refresh behavior
- In-flight run memory and agent decision planning
- Provider-aware model runtime retries and diagnostics
- External skills catalog with Skilgen-managed list/show/install flows across curated ecosystems
- External skill sync/remove flows and expanded multi-ecosystem source coverage
- Automatic external skill discovery and one-time auto-install for matching repositories
- External skill activation, lockfile metadata, normalized indexes, and trust-policy controls
- Adapter-aware external skill ranking, provenance surfacing, and preferred-pack recommendations

### Changed
- `AGENTS.md` generation now reflects inferred domains, prioritized skills, and memory loading guidance
- Skill generation can introduce free-form top-level domains beyond the seed taxonomy

## [0.1.0] - 2026-03-18

### Added
- Initial public Skilgen release
- CLI, SDK, and API for requirements and codebase-driven skill generation
- Model-backed runtime with multi-provider configuration
