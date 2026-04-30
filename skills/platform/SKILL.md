---
name: platform
version: 0.6.0
domain: platform
sub_domain: platform
last_updated: 2026-04-30
triggered_by: requirements_pipeline
source_hash: 2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26
richness_score: 100
score:
  total: 100
  groundedness: 25
  coverage: 25
  freshness: 25
  structure: 25
references:
  - ../requirements/SKILL.md
  - ../roadmap/SKILL.md
  - runtime/SKILL.md
  - agents/SKILL.md
  - cli/SKILL.md
  - core/SKILL.md
  - generators/SKILL.md
  - scripts/SKILL.md
status: active
---

# Platform Skill

## Overview
Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.

## Check These Paths First
- {{project_root}}/skilgen/__init__.py
- {{project_root}}/skilgen/autoupdate.py
- {{project_root}}/skilgen/agents/__init__.py
- {{project_root}}/skilgen/agents/architecture_planner.py

## Patterns
### Architecture responsibilities
- Tooling and runtime domain covering Skilgen's internal engine, CLI, planners, generators, and maintenance scripts.
- Coordinates subdomains: platform-runtime, platform-agents, platform-cli, platform-core.
- tooling platform
- generation engine
### Inferred domain patterns
- tooling platform
- generation engine
- repo-local operating surface
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.
### Architecture evidence
- Evidence: `skilgen/__init__.py`
- Evidence: `skilgen/autoupdate.py`
- Evidence: `skilgen/agents/__init__.py`
- Evidence: `skilgen/agents/architecture_planner.py`
- Evidence: `skilgen/cli/__init__.py`
### Dependency signals
- `@eslint/js` in `packages/config/package.json` is medium; npm install @eslint/js.
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.
- `@radix-ui/react-label` in `packages/ui/package.json` is medium; npm install @radix-ui/react-label.

## Anti-patterns
- **Introduce a second pattern for the same workflow**: Don't introduce a second pattern for the same workflow — duplicated conventions make agent edits unreliable
- **Remove nearby verification steps**: Don't remove nearby verification steps — future agents need a fast way to prove behaviour still works
- **Leave file references vague**: Don't leave file references vague — agents waste time searching and may edit the wrong boundary

## How-To
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `split`.

## Code Examples

### skilgen/__init__.py (python)
```python
"""Skilgen package."""

from skilgen.agents import fingerprint_project
from skilgen.autoupdate import auto_update_status, ensure_auto_update_worker, stop_auto_update_worker
from skilgen.delivery import run_delivery
from skilgen.sdk import (
    activate_project_mcp_connector,
    activate_skill_source,
    analyze_project,
    architecture_project,
    project_dashboard,
    cancel_job,
    deactivate_project_mcp_connector,
    deactivate_skill_source,
```

### skilgen/autoupdate.py (python)
```python
def _state_dir(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "state"


def _state_path(project_root: str | Path) -> Path:
    return _state_dir(project_root) / "autoupdate.json"


def _requirements_record_path(project_root: str | Path) -> Path:
    return _state_dir(project_root) / "autoupdate-requirements.txt"


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()
```

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `platform/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../requirements/SKILL.md
- ../roadmap/SKILL.md
- runtime/SKILL.md
- agents/SKILL.md
- cli/SKILL.md
- core/SKILL.md
- generators/SKILL.md
- scripts/SKILL.md
