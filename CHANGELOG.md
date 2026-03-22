# Changelog

All notable changes to Skilgen will be documented in this file.

The format is based on Keep a Changelog and this project follows Semantic Versioning.

## [0.2.0] - Unreleased

### Added
- Deep-Agents-driven dynamic domain graph planning
- Skill freshness state and selective refresh behavior
- In-flight run memory and agent decision planning
- Provider-aware model runtime retries and diagnostics
- External skills catalog with Skilgen-managed list/show/install flows across curated ecosystems
- External skill sync/remove flows and expanded multi-ecosystem source coverage
- Automatic external skill discovery and one-time auto-install for matching repositories

### Changed
- `AGENTS.md` generation now reflects inferred domains, prioritized skills, and memory loading guidance
- Skill generation can introduce free-form top-level domains beyond the seed taxonomy

## [0.1.0] - 2026-03-18

### Added
- Initial public Skilgen release
- CLI, SDK, and API for requirements and codebase-driven skill generation
- Model-backed runtime with multi-provider configuration
