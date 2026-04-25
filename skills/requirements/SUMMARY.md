# Requirements Summary

## Architecture responsibilities
- Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.
- requirements-first planning
- skill scaffolding

## Evidence paths
- `README.md`

## Planning Inputs
- <h2 align="center">The living skill system for AI coding agents</h2>
- Every agent session starts from zero. Skilgen ends that.<br/>
- Generate, govern, and keep your codebase's agent knowledge current automatically.
- A hand-written `CLAUDE.md` captures what you remember about your codebase on the day you write it. Skilgen generates repo-local agent context from actual code evidence, requirements inputs, architecture domains, and config signals, then refreshes that context as the code changes. A hand-written file drifts silently. Skilgen gives you generated artifacts, freshness tracking, and a score that tells you when the skill system is no longer trustworthy.
- Every agent session starts from zero. It reads files, infers structure, guesses patterns, and then the session ends. The next session repeats the same exploration. Skilgen captures that understanding once, stores it as versioned repo-local skills and docs grounded in real repository evidence, and makes it available to every session, every tool, and every engineer on the team.
- Run `skilgen dashboard` and get a branded HTML surface for score health, architecture domains, evidence graph, dependency signals, freshness, analytics, and agent readiness in one place.
- skilgen dashboard --project-root . --requirements docs/requirements.docx
- - [Anthropic claude-agent-sdk-python dashboard](docs/examples/README.md#anthropic-claude-agent-sdk-python)
- - [LibreChat dashboard + generated skills](docs/examples/README.md#librechat)
- ### Live Generated Skills
- Skilgen does not just draw a dashboard. It materializes a repo-local skill system that agents can load before editing code.
- Before = the repo with no generated skill system yet. After = the same repo after `skilgen deliver`.
