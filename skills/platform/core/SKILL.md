---
name: platform-core
version: 0.6.0
domain: platform
sub_domain: platform-core
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

# Platform Core Skill

## Overview
Shared core guidance for scoring, freshness, diffing, context loading, and validation primitives.

## Check These Paths First
- {{project_root}}/skilgen/core/__init__.py
- {{project_root}}/skilgen/core/analytics.py
- {{project_root}}/skilgen/core/audit.py
- {{project_root}}/skilgen/core/auth_tokens.py

## Patterns
### Inferred child domain patterns
- shared models
- freshness and scoring
- validation primitives
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

### skilgen/core/analytics.py (python)
```python
def _compute_richness_score(content: str, spec: object) -> dict[str, int]:
    lines = content.splitlines()
    words = len(content.split())

    code_blocks = content.count("```") // 2
    file_refs = sum(
        1
        for line in lines
        if "/" in line
        and any(line.strip().rstrip("`").endswith(ext) for ext in [".py", ".ts", ".js", ".go", ".rb", ".java"])
    )
    groundedness = min(25, code_blocks * 8 + file_refs * 2)

    has_antipatterns = "anti-pattern" in content.lower() or "## anti" in content.lower()
```

### skilgen/core/audit.py (python)
```python
def audit_log_path(project_root: str | Path) -> Path:
    return Path(project_root).resolve() / ".skilgen" / "audit" / "events.jsonl"


def central_audit_log_path() -> Path | None:
    raw_root = os.getenv("SKILGEN_AUDIT_LOG_ROOT", "").strip()
    if not raw_root:
        return None
    return Path(raw_root).resolve() / "audit" / "events.jsonl"


def _write_audit_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
```

## Traceability
- Generated from requirements source hash: `8b23ea8a0e8cf72fff2cfcd6890faa6970d61df0fc06f29f9576437064dcf128`
- Domain path: `platform/platform-core`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
