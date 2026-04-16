# Skill Graph

This file summarizes the generated skill tree and cross references.

## Architecture Blueprint
- Headline: Evidence-backed architecture blueprint for the LibreChat repository
- Summary: Skilgen inferred repo-native app surfaces directly from the top-level repository structure and materialized a skill tree from those boundaries.

## Materialization Decisions
### api
- decision: `split`
- parent: `skills/api/SKILL.md`
- child skills:
  - `skills/api/app/SKILL.md` (materialized)
  - `skills/api/cache/SKILL.md` (materialized)
  - `skills/api/config/SKILL.md` (materialized)
  - `skills/api/db/SKILL.md` (materialized)
  - `skills/api/server/SKILL.md` (materialized)
  - `skills/api/strategies/SKILL.md` (materialized)
  - `skills/api/test/SKILL.md` (materialized)
  - `skills/api/utils/SKILL.md` (materialized)
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.
### client
- decision: `split`
- parent: `skills/client/SKILL.md`
- child skills:
  - `skills/client/src/SKILL.md` (materialized)
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.
### config
- decision: `split`
- parent: `skills/config/SKILL.md`
- child skills:
  - `skills/config/translations/SKILL.md` (materialized)
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.
### e2e
- decision: `split`
- parent: `skills/e2e/SKILL.md`
- child skills:
  - `skills/e2e/setup/SKILL.md` (materialized)
  - `skills/e2e/specs/SKILL.md` (materialized)
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.
### packages
- decision: `split`
- parent: `skills/packages/SKILL.md`
- child skills:
  - `skills/packages/api/SKILL.md` (materialized)
  - `skills/packages/client/SKILL.md` (materialized)
  - `skills/packages/data-provider/SKILL.md` (materialized)
  - `skills/packages/data-schemas/SKILL.md` (materialized)
- cross-links:
  - `skills/roadmap/SKILL.md`
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.
### roadmap
- decision: `split`
- parent: `skills/roadmap/SKILL.md`
- child skills:
  - `skills/roadmap/phase-0/SKILL.md` (materialized)
  - `skills/roadmap/phase-1/SKILL.md` (materialized)
  - `skills/roadmap/phase-2/SKILL.md` (materialized)
  - `skills/roadmap/phase-3/SKILL.md` (materialized)
- rationale: Derived directly from the inferred repo-native domain graph for deterministic LibreChat generation.

## api/SKILL.md
- domain: `api`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `app/SKILL.md`
  - `cache/SKILL.md`
  - `config/SKILL.md`
  - `db/SKILL.md`
  - `server/SKILL.md`
  - `strategies/SKILL.md`
  - `test/SKILL.md`
  - `utils/SKILL.md`

## client/SKILL.md
- domain: `client`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `src/SKILL.md`

## config/SKILL.md
- domain: `config`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `translations/SKILL.md`

## e2e/SKILL.md
- domain: `e2e`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `setup/SKILL.md`
  - `specs/SKILL.md`

## packages/SKILL.md
- domain: `packages`
- sub_domain: `platform`
- references:
  - `../roadmap/SKILL.md`
  - `api/SKILL.md`
  - `client/SKILL.md`
  - `data-provider/SKILL.md`
  - `data-schemas/SKILL.md`

## roadmap/SKILL.md
- domain: `roadmap`
- sub_domain: `platform`
- references:
  - `phase-0/SKILL.md`
  - `phase-1/SKILL.md`
  - `phase-2/SKILL.md`
  - `phase-3/SKILL.md`

## api/app/SKILL.md
- domain: `api`
- sub_domain: `api-app`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/cache/SKILL.md
- domain: `api`
- sub_domain: `api-cache`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/config/SKILL.md
- domain: `api`
- sub_domain: `api-config`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/db/SKILL.md
- domain: `api`
- sub_domain: `api-db`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/server/SKILL.md
- domain: `api`
- sub_domain: `api-server`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/strategies/SKILL.md
- domain: `api`
- sub_domain: `api-strategies`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/test/SKILL.md
- domain: `api`
- sub_domain: `api-test`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## api/utils/SKILL.md
- domain: `api`
- sub_domain: `api-utils`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## client/src/SKILL.md
- domain: `client`
- sub_domain: `client-src`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## config/translations/SKILL.md
- domain: `config`
- sub_domain: `config-translations`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## e2e/setup/SKILL.md
- domain: `e2e`
- sub_domain: `e2e-setup`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## e2e/specs/SKILL.md
- domain: `e2e`
- sub_domain: `e2e-specs`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## packages/api/SKILL.md
- domain: `packages`
- sub_domain: `packages-api`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## packages/client/SKILL.md
- domain: `packages`
- sub_domain: `packages-client`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## packages/data-provider/SKILL.md
- domain: `packages`
- sub_domain: `packages-data-provider`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## packages/data-schemas/SKILL.md
- domain: `packages`
- sub_domain: `packages-data-schemas`
- references:
  - `../SKILL.md`
  - `../../roadmap/SKILL.md`

## roadmap/phase-0/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-0`
- references:
  - `../SKILL.md`

## roadmap/phase-1/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-1`
- references:
  - `../SKILL.md`

## roadmap/phase-2/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-2`
- references:
  - `../SKILL.md`

## roadmap/phase-3/SKILL.md
- domain: `roadmap`
- sub_domain: `roadmap-phase-3`
- references:
  - `../SKILL.md`
