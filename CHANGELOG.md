# Changelog

All notable changes to Skilgen will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [0.4.1] - Unreleased

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
