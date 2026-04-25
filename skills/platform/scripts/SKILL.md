---
name: platform-scripts
version: 0.6.0
domain: platform
sub_domain: platform-scripts
last_updated: 2026-04-25
triggered_by: requirements_pipeline
source_hash: 2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26
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

# Platform Scripts Skill

## Overview
Maintenance automation guidance for release helpers and repo scripts that support the generation pipeline.

## Check These Paths First
- {{project_root}}/scripts/bump_version.py
- {{project_root}}/scripts/deploy_api.py
- {{project_root}}/scripts/deploy_dashboard.py
- {{project_root}}/scripts/deploy_web.py

## Patterns
### Inferred child domain patterns
- maintenance automation
- release helpers
- pipeline scripts
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

### scripts/bump_version.py (python)
```python
def replace_version(path: Path, pattern: str, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, lambda match: f"{match.group(1)}{version}{match.group(3)}", text)
    if count != 1:
        raise SystemExit(f"Could not update version in {path}")
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bump Skilgen package version in tracked release files.")
    parser.add_argument("version", help="New version, for example 0.1.1")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
```

### scripts/deploy_api.py (python)
```python
def load_project_link(path: Path) -> dict[str, str]:
    """Load and validate a Vercel project link file."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED_PROJECT_KEYS.difference(payload)
    if missing:
        missing_keys = ", ".join(sorted(missing))
        raise ValueError(f"Vercel project link {path} is missing: {missing_keys}")
    return {key: str(payload[key]) for key in REQUIRED_PROJECT_KEYS}


def deploy_command(*, production: bool, config_path: Path) -> list[str]:
    """Build the Vercel CLI command for the API deployment."""
    command = ["vercel", "deploy", "--local-config", str(config_path)]
    if production:
```

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `platform/platform-scripts`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
