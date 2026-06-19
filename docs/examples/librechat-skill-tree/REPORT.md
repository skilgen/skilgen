# Report

## Summary
- Detected domains: api, api-app, api-cache, api-config, api-db, api-server, api-strategies, api-test, api-utils, client, client-src, config, config-translations, e2e, e2e-setup, e2e-specs, packages, packages-api, packages-client, packages-data-provider, packages-data-schemas, roadmap, roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3
- Feature inventory entries: 25
- Backend route files: 870
- Frontend route files: 91
- Component files: 1041
- Service files: 122
- Test files: 487
- Data model files: 70
- Persistence files: 37
- Background job files: 9
- Auth files: 121
- State files: 102
- Design system files: 45
- Architecture domains: 6

## Generated Outputs
- ANALYSIS.md
- ARCHITECTURE.md
- FEATURES.md
- REPORT.md
- TRACEABILITY.md
- skills/MANIFEST.md
- skills/GRAPH.md
- skills/<domain>/SKILL.md
- skills/<domain>/SUMMARY.md

## Recommended Starting Points
- Backend: start from `api/app/clients/BaseClient.js`
- Services: start from `api/server/services/ActionService.js`
- Frontend routes: start from `api/server/routes/__test-utils__/convos-route-mocks.js`
- Components: start from `api/app/clients/BaseClient.js`

## Architecture Highlights
- `api`: Backend application guidance for API routes, services, persistence, auth, and runtime orchestration under the repo's `api/` surface.
- `client`: Frontend application guidance for the user-facing client, routes, UI composition, and client-side runtime behavior.
- `config`: Configuration guidance for runtime configuration, feature flags, translation setup, and environment-driven behavior.
- `e2e`: End-to-end testing guidance for browser workflows, setup, and cross-surface regression coverage.
- `packages`: Shared package guidance for reusable internal packages that support the app runtime and product surfaces.

## External Skill Packs
- Installed packs: 0
- Active packs: 0
- No active external skill packs have been ranked yet.

## External Skill Provenance
- No external skill packs have been installed yet.
