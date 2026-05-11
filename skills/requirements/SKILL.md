---
name: requirements
version: 0.6.0
domain: requirements
sub_domain: platform
last_updated: 2026-05-11
triggered_by: requirements_pipeline
source_hash: bc99826420bcc9ec80326abf758ead610a25b25d2d4cbb96b0589c0ea7fa2855
richness_score: 83
score:
  total: 83
  groundedness: 8
  coverage: 25
  freshness: 25
  structure: 25
references:
  - ../roadmap/SKILL.md
status: active
---

# Requirements Skill

## Overview
Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.

## Check These Paths First
- {{project_root}}/README.md

## Patterns
### Architecture responsibilities
- Planning and product-intent domain used to keep the skill tree aligned with requirements and changing scope.
- requirements-first planning
- skill scaffolding
### Inferred domain patterns
- requirements-first planning
- skill scaffolding
- agent operating guidance
### Dynamic topology
- This parent skill was inferred from the current repo and may expand or contract as the codebase evolves.
### Architecture evidence
- Evidence: `README.md`
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
1. Start from the architecture evidence paths before broadening the scope of the change.
2. Use the listed responsibilities to keep changes inside the right domain boundary.
3. Refresh this parent skill whenever the architecture blueprint or top evidence files change materially.
4. Honor the current materialization decision for this domain: `keep`.

## Code Examples

### README.md
```
# Skillayer

Skillayer is a governance plane for AI coding agents. It helps platform, security, and engineering leadership answer the questions that matter once Claude Code, Codex, Cursor, GitHub Copilot, and internal agents are active across a company:

- What did agents do across repos, tools, sessions, and users?
- Which actions violated policy, and were they blocked, approved, or sent for more review?
- Which skills are trusted, stale, drifted, quarantined, or bound to policy?
- Can audit evidence be exported with attribution, policy decisions, and tamper-evident history?
- Where is fleet risk increasing across agents, repos, skills, and critical operations?

The current product direction is defined by `docs/PRD-v8.docx`: Skillayer v8 reduces the product to six enterprise surfaces and treats the older skill-generation system as the substrate underneath the governance experience.

## Product Surfaces
```

## Traceability
- Generated from requirements source hash: `bc99826420bcc9ec80326abf758ead610a25b25d2d4cbb96b0589c0ea7fa2855`
- Domain path: `requirements/platform`
- Read `../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../roadmap/SKILL.md
