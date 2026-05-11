# Features

Search this file before implementing any feature to avoid duplicating work.

| Feature Name | Domain | Location | Description | Status | Last Modified |
| --- | --- | --- | --- | --- | --- |
| Requirements-driven scan | requirements | `README.md` | Parse the requirements input and generate skills and project docs. | active | current |
| Project folder analysis | analysis | `skilgen` | Analyze the input folder and generate outputs into that same folder. | active | current |
| Backend route: skilgen/api/__init__.py | backend | `skilgen/api/__init__.py` | Detected route or handler implementation in the scanned codebase. | active | current |
| Backend route: skilgen/api/jobs.py | backend | `skilgen/api/jobs.py` | Detected route or handler implementation in the scanned codebase. | active | current |
| Backend route: skilgen/api/server.py | backend | `skilgen/api/server.py` | Detected route or handler implementation in the scanned codebase. | active | current |
| Backend route: skilgen/api/service.py | backend | `skilgen/api/service.py` | Detected route or handler implementation in the scanned codebase. | active | current |
| | Surface | Purpose | Key Routes | | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| - Coverage SLA critical-operation taxonomy loading from `apps/api/api/v8/insight | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| - v8 Audit APIs for event log, reports, exports, evidence packages, hash-chain v | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| - v8 Skills APIs and screens for registry, score, drift, provenance, SkillQL, an | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| - v8 Settings APIs and screens for connectors and RBAC foundations. | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| | Dashboard | `apps/dashboard` | Next.js App Router dashboard. v8 routes live in | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| The migrated v8 app lives under `apps/dashboard/app/(v8)` and uses the Skillayer | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| | Dashboard | `apps/dashboard` | Next.js App Router dashboard. v8 routes live in | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| Run the dashboard: | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| npm --workspace apps/dashboard run dev | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| Useful dashboard checks: | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| npm run lint --workspace apps/dashboard | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| HTTP API surface | api | `skilgen/api/server.py` | Exposes health, fingerprint, map, intent, features, plan, deliver, status, report, and validate endpoints. | active | current |
| Settings agent compliance event ingestion | full-stack | `apps/api/api/v8/settings/router.py`, `apps/api/tests/test_v8_settings_rbac.py`, `apps/dashboard/app/(v8)/settings/connectors/page.tsx` | Normalizes metadata-only provider compliance and coding-agent events into `agent.compliance` audit records with model, intelligence tier, access, tool, MCP, file, policy, token, cost, latency, warning, violation, and error metrics while dropping raw prompts, chats, file content, diffs, and tool parameters. | active | current |
| Insights provider coverage | full-stack | `apps/api/api/v8/insights/router.py`, `apps/api/tests/test_v8_insights.py`, `apps/dashboard/app/(v8)/insights/provider-coverage/page.tsx`, `apps/dashboard/app/(v8)/insights/_components/insights-shell.tsx` | Compares configured compliance connectors with recent metadata-only agent compliance events so operators can see active, silent, stale, and 30-day retention-risk provider sources without inventing connected state. | active | current |
| Insights agent compliance metrics | full-stack | `apps/api/api/v8/insights/router.py`, `apps/api/tests/test_v8_insights.py`, `apps/dashboard/app/(v8)/insights/agent-compliance-metrics/page.tsx`, `apps/dashboard/app/(v8)/insights/_components/insights-shell.tsx` | Consolidates normalized compliance API and coding-agent telemetry metrics across providers, developers, models, repos, sessions, tools, MCP calls, files, policy decisions, approvals, source record types, retention states, tokens, cost, latency, warnings, violations, and errors. | active | current |
