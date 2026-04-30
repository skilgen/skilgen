---
name: platform-agents
version: 0.6.0
domain: platform
sub_domain: platform-agents
last_updated: 2026-04-30
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

# Platform Agents Skill

## Overview
Planner and inference guidance for domain graphing, architecture synthesis, and decision intelligence.

## Check These Paths First
- {{project_root}}/skilgen/agents/__init__.py
- {{project_root}}/skilgen/agents/architecture_planner.py
- {{project_root}}/skilgen/agents/codebase_signals.py
- {{project_root}}/skilgen/agents/decision_planner.py

## Patterns
### Inferred child domain patterns
- domain inference
- architecture synthesis
- agent planning logic
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

### skilgen/agents/__init__.py (python)
```python
from skilgen.agents.codebase_signals import analyze_codebase, collect_code_evidence, collect_structural_evidence
from skilgen.agents.architecture_planner import build_architecture_blueprint
from skilgen.agents.evidence_graph import build_evidence_graph
from skilgen.agents.language_parsers import parse_language_evidence
from skilgen.agents.decision_planner import build_agent_decision
from skilgen.agents.domain_graph_planner import build_domain_graph
from skilgen.agents.feature_extractor import extract_features
from skilgen.agents.framework_fingerprint import fingerprint_project
from skilgen.agents.model_registry import resolve_model_settings
from skilgen.agents.relationship_mapper import build_import_graph
from skilgen.agents.requirements_parser import parse_requirements_file
from skilgen.agents.roadmap_planner import build_roadmap_plan
from skilgen.agents.source_graphs import (
    build_call_graph,
```

### skilgen/agents/architecture_planner.py (python)
```python
def _redact_snippet_lines(lines: list[str], *, limit: int) -> list[str]:
    redacted: list[str] = []
    for line in lines[:limit]:
        updated = line
        updated = updated.replace("api_key", "[redacted]")
        updated = updated.replace("apikey", "[redacted]")
        updated = updated.replace("password", "[redacted]")
        updated = updated.replace("secret", "[redacted]")
        updated = updated.replace("token", "[redacted]")
        redacted.append(updated[:180])
    return redacted


def _evidence_graph_payload(project_root: Path, evidence_graph: EvidenceGraph) -> dict[str, object]:
```

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `platform/platform-agents`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
- ../../roadmap/SKILL.md
