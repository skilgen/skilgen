---
name: platform-generators
version: 0.6.0
domain: platform
sub_domain: platform-generators
last_updated: 2026-05-11
triggered_by: requirements_pipeline
source_hash: 62b179fa1c51832fd76b316533c2ecc6fa80c151575bfeb27249fb3a3ac90703
richness_score: 94
score:
  total: 94
  groundedness: 22
  coverage: 22
  freshness: 25
  structure: 25
references:
  - ../SKILL.md
  - ../../requirements/SKILL.md
  - ../../roadmap/SKILL.md
status: active
---

# Platform Generators Skill

## Overview
Artifact materialization guidance for docs, skills, dashboards, and output rendering flows.

## Check These Paths First
- {{project_root}}/skilgen/generators/__init__.py
- {{project_root}}/skilgen/generators/package.py
- {{project_root}}/skilgen/generators/skills.py

## Patterns
### Inferred child domain patterns
- artifact rendering
- materialization flow
- repo-local outputs
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

### skilgen/generators/package.py (python)
```python
class ProjectAnalysisBundle:
    fingerprint: object
    signals: object
    import_graph: dict[str, list[str]]
    codebase_context: object
    evidence_graph: object
    architecture: object


ProgressCallback = Callable[[str], None]


def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
```

### skilgen/generators/skills.py (python)
```python
def _emit_progress(progress_callback: ProgressCallback | None, message: str) -> None:
    if progress_callback is not None:
        progress_callback(message)


def _signal_bullets(items: list[str], fallback: str, limit: int = 5) -> list[str]:
    if not items:
        return [fallback]
    bullets = [f"Detected: `{item}`" for item in items[:limit]]
    if len(items) > limit:
        bullets.append(f"Detected {len(items) - limit} more matching files elsewhere in the repo.")
    return bullets
```

## Traceability
- Generated from requirements source hash: `62b179fa1c51832fd76b316533c2ecc6fa80c151575bfeb27249fb3a3ac90703`
- Domain path: `platform/platform-generators`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
