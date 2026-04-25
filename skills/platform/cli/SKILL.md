---
name: platform-cli
version: 0.6.0
domain: platform
sub_domain: platform-cli
last_updated: 2026-04-25
triggered_by: requirements_pipeline
source_hash: 2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26
richness_score: 84
score:
  total: 84
  groundedness: 12
  coverage: 22
  freshness: 25
  structure: 25
references:
  - ../SKILL.md
  - ../../requirements/SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Cli Skill

## Overview
Operator-facing CLI guidance for command surfaces, progress reporting, and repo-local execution flows.

## Check These Paths First
- {{project_root}}/skilgen/cli/__init__.py
- {{project_root}}/skilgen/cli/main.py

## Patterns
### Inferred child domain patterns
- command surfaces
- operator UX
- progress orchestration
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
1. Start from the nearest evidence file in this child domain.
2. Keep the change aligned with the parent domain contract before widening the boundary.
3. Prefer cross-linked sibling skills when the change spans multiple closely related surfaces.

## Code Examples

### skilgen/cli/main.py (python)
```python
def emit_progress(message: str) -> None:
    print(f"[skilgen] {message}", file=sys.stderr)


def _write_memory_session_template(project_root: Path, output: str | None = None) -> Path:
    session_id = str(uuid.uuid4())
    path = Path(output).resolve() if output else project_root / ".skilgen" / "sessions" / f"{session_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "session_id": session_id,
        "agent_runtime": "claude_code",
        "task_description": "Implement JWT refresh token rotation",
        "engineer_login": "janedoe",
        "duration_minutes": 47,
```

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `platform/platform-cli`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
