# Roadmap Summary

## Architecture responsibilities
- Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.
- Coordinates subdomains: roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3.
- phase-based delivery
- sequenced implementation planning

## Evidence paths
- `skills/roadmap/SKILL.md`
- `REPORT.md`

## Roadmap Context
- # Skillayer
- Skillayer is a governance plane for AI coding agents. It helps platform, security, and engineering leadership answer the questions that matter once Claude Code, Codex, Cursor, GitHub Copilot, and internal agents are active across a company:
- - What did agents do across repos, tools, sessions, and users?
- - Which skills are trusted, stale, drifted, quarantined, or bound to policy?
- - Where is fleet risk increasing across agents, repos, skills, and critical operations?
- The current product direction is defined by `docs/PRD-v8.docx`: Skillayer v8 reduces the product to six enterprise surfaces and treats the older skill-generation system as the substrate underneath the governance experience.
- The migrated v8 app lives under `apps/dashboard/app/(v8)` and uses the Skillayer governance shell.
- | Activity | The default investigation homepage for live agent activity, sessions, replay, and heatmaps. | `/activity`, `/activity/live-feed`, `/activity/sessions`, `/activity/replay`, `/activity/heatmap` |
- | Skills | The artifact substrate: registry, score, drift, provenance, SkillQL, and repo coverage. | `/skills/registry`, `/skills/score`, `/skills/drift`, `/skills/provenance`, `/skills/skillql`, `/skills/repos` |
- | Insights | Fleet trends and risk posture: KPIs, developer track, risky agents/repos, coverage SLA, and agent compliance metrics. | `/insights/fleet-kpis`, `/insights/developer-track`, `/insights/agent-compliance-metrics`, `/insights/intelligence-usage`, `/insights/access-grants`, `/insights/provider-coverage`, `/insights/coverage-sla` |
- Current feature slices tracked in `FEATURES.md` include:
- - Metadata-only agent compliance event ingestion for configured provider connectors, including model tier, access grants, tools/MCP, files, policy decisions, tokens, cost, latency, warnings, violations, and error metrics.
