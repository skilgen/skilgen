---
name: platform-runtime
version: 0.6.0
domain: platform
sub_domain: platform-runtime
last_updated: 2026-05-11
triggered_by: requirements_pipeline
source_hash: 8b23ea8a0e8cf72fff2cfcd6890faa6970d61df0fc06f29f9576437064dcf128
richness_score: 96
score:
  total: 96
  groundedness: 24
  coverage: 22
  freshness: 25
  structure: 25
references:
  - ../SKILL.md
  - ../../requirements/SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Runtime Skill

## Overview
Runtime orchestration guidance for package-level entrypoints, delivery orchestration, and repo-wide integration surfaces.

## Check These Paths First
- {{project_root}}/skilgen/__init__.py
- {{project_root}}/skilgen/autoupdate.py
- {{project_root}}/skilgen/deep_agents_core.py
- {{project_root}}/skilgen/deep_agents_runtime.py

## Patterns
### Inferred child domain patterns
- runtime orchestration
- repo-wide coordination
- package entrypoints
### Dependency signals
- `@eslint/js` in `packages/config/package.json` is medium; npm install @eslint/js.
- `@playwright/test` in `apps/dashboard/package.json` is medium; npm install @playwright/test.
- `@radix-ui/react-avatar` in `packages/ui/package.json` is medium; npm install @radix-ui/react-avatar.
- `@radix-ui/react-dialog` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dialog.
- `@radix-ui/react-dropdown-menu` in `packages/ui/package.json` is medium; npm install @radix-ui/react-dropdown-menu.

## Anti-patterns
- **Introduce a second pattern for the same workflow**: Don't introduce a second pattern for the same workflow — duplicated conventions make agent edits unreliable
- **Remove nearby verification steps**: Don't remove nearby verification steps — future agents need a fast way to prove behaviour still works
- **Leave file references vague**: Don't leave file references vague — agents waste time searching and may edit the wrong boundary

## How-To
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

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
- Generated from requirements source hash: `8b23ea8a0e8cf72fff2cfcd6890faa6970d61df0fc06f29f9576437064dcf128`
- Domain path: `platform/platform-runtime`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
