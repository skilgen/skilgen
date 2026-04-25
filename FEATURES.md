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
| # Export a provider key, or point Skilgen at a private model endpoint below. | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| export OPENAI_API_KEY="your_key" | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| # or ANTHROPIC_API_KEY / GOOGLE_API_KEY / GROQ_API_KEY / OPENROUTER_API_KEY | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| Current v0.6.0 breadth: `58` CLI entry points spanning delivery, architecture, d | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| Skilgen indexes every non-excluded file in the repo, not just files that happen  | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| Phase 1 corpus indexing never touches an LLM. For model-backed synthesis, Skilge | backend | `requirements` | Endpoint or route intent extracted from the requirements source. | planned | current |
| <a href="https://github.com/skilgen/skilgen/actions/workflows/ci.yml"><img src=" | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| ## Dashboard | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| Run `skilgen dashboard` and get a branded HTML surface for score health, archite | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| skilgen dashboard --project-root . --requirements docs/requirements.docx | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| `skilgen deliver --project-root .` already writes `skilgen-dashboard.html` autom | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| - [Anthropic claude-code dashboard](docs/examples/README.md#anthropic-claude-cod | frontend | `requirements` | User-facing flow extracted from the requirements source. | planned | current |
| HTTP API surface | api | `skilgen/api/server.py` | Exposes health, fingerprint, map, intent, features, plan, deliver, status, report, and validate endpoints. | active | current |
