---
name: roadmap-phase-3
version: 0.6.0
domain: roadmap
sub_domain: roadmap-phase-3
last_updated: 2026-05-10
triggered_by: requirements_pipeline
source_hash: 2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26
richness_score: 72
score:
  total: 72
  groundedness: 0
  coverage: 22
  freshness: 25
  structure: 25
references:
  - ../SKILL.md
  - ../../requirements/SKILL.md
status: active
---

# Roadmap Phase 3 Skill

## Overview
Roadmap phase node for phase-3 planning and sequencing guidance.

## Check These Paths First
- {{project_root}}/skills/roadmap/SKILL.md

## Patterns
### Inferred child domain patterns
- phase sequencing
- delivery planning
- setup readiness surfaces expose the exact next action before a feature is marked complete
- activity investigation filters stay URL-shareable and match PRD live-feed dimensions
- policy starter packs must be inspectable, adoptable, and tied to explicit decision verbs
- policy review queues must expose clear reviewer actions while honoring auth and RBAC disabled states
- Insights Coverage SLA critical-operation taxonomy must be data-backed, product-reviewable, and visible in the migrated Skillayer UI
- User-facing documentation must use Skillayer branding and describe the actual migrated v8 surfaces
- Settings connector catalog UX must keep PRD-backed compliance telemetry, coding-agent, source-control, incident, WORM, and provenance entries visible without inventing connected state
- Insights intelligence usage must stay metadata-only by default while exposing model tier usage and full-access/tool-permission rollups from normalized audit events
- Insights access grants must provide a dedicated operator view for full-access, autonomous access, and tool-permission exposure from normalized agent compliance metadata without raw content retention
- Audit agent compliance trails must expose source-envelope evidence and governance metadata without raw prompt, chat, or file content by default
- Activity compliance event views must support live investigations from normalized agent metadata without duplicating raw content retention
- AgentRun ingestion must mirror session payloads into metadata-only agent compliance events, hashing a sanitized source envelope and dropping raw diffs, prompts, tool parameters, and file content from compliance metadata
- Policy agent-compliance predicates must target normalized provider, model/intelligence tier, access scope, tool/MCP permissions, and repo sensitivity metadata without retaining raw prompt or file content
- Settings agent compliance connector setup must store tenant configuration metadata only, keep content retention metadata-only by default, and never mark a provider connected unless tenant setup exists
- Settings agent compliance sync readiness must gate sync requests behind enabled connector setup, update cursor/status metadata only, and leave real provider ingestion jobs to the dedicated ingestion slice
- Audit WORM root targets must publish only audit-chain roots and Merkle proofs, expose S3/GCS/Azure readiness honestly, and avoid raw event payload retention
- Skills Score substrate must present Skilgen Score as open-rubric governance evidence inside the migrated Skillayer Skills IA, with visible groundedness, coverage, freshness, and structure subscores
- Skills Drift substrate must show half-life decay predictions as governance evidence, including churn inputs, confidence, regeneration queue state, and policy/audit signal framing
- Skills Provenance substrate must not import legacy dependency graph routes; it must show v8 skill version evidence, hashes, signatures, run lineage, approvers, and transparency-log readiness inside the migrated Skillayer Skills IA
- Skills SkillQL substrate must not import the legacy dashboard route; it must stay inside the migrated Skillayer Skills IA and call the v8 Skills SkillQL API for suggestions and governed query execution
- Insights developer track must use the compliance API with trend enabled and surface every returned developer metric, including sessions, files, lines, PR lifecycle, runtimes, skills, violations, warnings, compliance, risk distribution, top violations, trend, sparkline, rank, and last activity
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

## Traceability
- Generated from requirements source hash: `2837441a102548bef06fba7b2eca5d2c3dbc03490ce3cb2864d5e3ca6a4c3c26`
- Domain path: `roadmap/roadmap-phase-3`
- Read `../../../TRACEABILITY.md` for full requirement-to-output mapping.
- Use the detected file patterns in this skill before creating new structure.

## References
- ../SKILL.md
- ../../requirements/SKILL.md
