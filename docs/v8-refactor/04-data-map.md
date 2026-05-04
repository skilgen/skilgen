# PR-0 Data Map

Source inputs: SQLAlchemy models under `packages/db/models`, Alembic migrations under `apps/api/alembic/versions`, and PRD sections 3.3 and 4.1-4.6.

No SQL is written in PR-0. No v7 table is proposed for deletion. Tables backing cut surfaces are marked for eventual `_deprecated_v7_` prefix rename only in PR-8 or later, per `docs/AGENTS.md` section 9.

Gate: No `_deprecated_v7_` rename ships in PR-8 or any later PR without a documented row count from staging or a sanitized clone, recorded in this file.

Required before PR-1: read-only access to staging or a sanitized clone, so row counts can be filled in for every table marked `deprecate-later` or `keep/extend`.

Row counts were unavailable during discovery because no non-secret DB connection was configured locally.

## Table dispositions

| Table | v8 disposition | Migration needed later | Notes |
| --- | --- | --- | --- |
| `ab_tests` | deprecate-later | PR-8 rename to `_deprecated_v7_ab_tests` only after approval | PRD cuts A/B Tests. |
| `agent_load_events` | keep/reuse | None initially | Activity feed and Skills usage substrate. |
| `agent_sessions` | keep/reuse | Add v8 indexes only if query plans need them | Activity Sessions/Replay. |
| `agent_tasks` | keep/reuse | None initially | Insights Risky agents. |
| `analysis_runs` | keep/reuse | None initially | Skills Repos/Score. |
| `audit_events` | keep/extend | Add hash-chain columns or companion table in Audit PR | Audit Event log. |
| `autopilot_tasks` | keep/reuse | None initially | Policy Rules auto-approval. |
| `commits` | keep/reuse | None initially | Audit and provenance. |
| `coverage_gaps` | keep/reuse | None initially | Skills Score coverage filter. |
| `cross_repo_opportunities` | keep/reuse | None initially | Insights/Skills opportunities. |
| `dependencies` | keep/reuse | None initially | Skills Provenance. |
| `dependency_graph_cache` | keep/reuse | None initially | Skills Provenance. |
| `digest_configs` | deprecate-later | PR-8 rename to `_deprecated_v7_digest_configs` only after notification replacement ships | PRD cuts Digest route; notification settings remain. |
| `eval_sessions` | keep/reuse | None initially | Insights Risky agents. |
| `flag_dismissals` | keep/reuse | None initially | Policy Violations dismissals. |
| `half_life_cache` | keep/reuse | None initially | Skills Drift. |
| `jobs` | keep/reuse | None initially | Existing async job infra. |
| `login_events` | keep/reuse | None initially | Settings admin audit / Admin. |
| `marketplace_installs` | keep/reuse | None initially | Skills Registry. |
| `org_llm_configs` | keep/reuse | None initially | Settings. |
| `org_policies` | keep/extend | Possible policy DSL metadata columns in PR-3 | Policy Rules. |
| `orgs` | keep/extend | PR-1 add IA_V8 tenant override field or settings key | Feature rollout. |
| `pr_attributions` | keep/extend | Possible manifest/evidence indexes in PR-4 | Audit and Insights. |
| `pr_comments` | keep/reuse | None initially | Policy Approvals/Review. |
| `pr_review_findings` | keep/reuse | None initially | Policy Approvals/Violations. |
| `pr_reviews` | keep/reuse | None initially | Policy Approvals. |
| `pull_requests` | keep/reuse | None initially | Activity and Audit. |
| `registry_skills` | keep/reuse | None initially | Skills Registry. |
| `repos` | keep/reuse | None initially | Skills Repos and Insights. |
| `review_runs` | keep/reuse | None initially | Policy Approvals. |
| `score_history` | keep/reuse | None initially | Skills Score and Insights. |
| `skill_dependencies` | keep/reuse | None initially | Skills Provenance. |
| `skill_gaps` | keep/reuse | None initially | Skills Score coverage filter. |
| `skill_half_lives` | keep/reuse | None initially | Skills Drift. |
| `skill_memory_stubs` | keep/reuse | None initially | Skills/Insights if still surfaced. |
| `skill_registry_entries` | keep/reuse | None initially | Skills Registry. |
| `skill_snapshots` | keep/reuse | None initially | Skills Provenance/Time Machine. |
| `skill_usage_events` | keep/reuse | None initially | Skills usage analytics. |
| `skill_versions` | keep/reuse | None initially | Skills Registry/Provenance. |
| `skills` | keep/reuse | None initially | Skills core table. |
| `sla_policies` | keep/reuse | None initially | Insights Coverage SLA. |
| `source_connections` | keep/reuse | None initially | Skills Repos and Settings Connectors. |

## New data objects proposed by v8

No migrations in PR-0. These are candidate migration names and directions for later PRs.

| Future PR | Migration name | Direction |
| --- | --- | --- |
| PR-1 IA shell | `add_ia_v8_tenant_override` | Add nullable/default-off tenant override, likely in `orgs.settings` or a dedicated column/table. Downgrade removes only the override carrier. |
| PR-2 Activity | `add_activity_heatmap_view` | Add materialized view or indexed query support for Activity Heatmap if existing endpoints cannot meet query needs. Downgrade drops the view/index only. |
| PR-3 Policy | `add_policy_dsl_metadata` | Add DSL/source/version fields to policy storage if `org_policies` cannot represent v8 rules. Downgrade removes added columns after data copy. |
| PR-3 Policy | `add_skill_quarantine_state` | Add quarantine state if no existing skill status field supports it. Downgrade removes state after migration-safe fallback. |
| PR-4 Audit | `add_audit_hash_chain` | Add hash-chain fields or companion table for tamper-evident event log. Downgrade removes companion data only after export/backup in test DB. |
| PR-4 Audit | `add_evidence_package_jobs` | Add evidence package job/status records if `jobs` is insufficient. Downgrade drops companion table. |
| PR-6 Insights | `add_risky_agent_repo_views` | Add SQL views/materialized views for risky agents/repos. Downgrade drops views. |
| PR-7 Settings | `add_roles_and_role_bindings` | Add RBAC tables only if no existing role model exists. Downgrade drops tables. |

## v7 cut table handling

- `ab_tests`: do not delete. In PR-8, after all v8 surfaces are live and a deprecation date is approved, copy/rename by introducing `_deprecated_v7_ab_tests` according to the two-release rule.
- `digest_configs`: do not delete. In PR-8 or later, only rename after Settings notification controls replace the Digest dashboard route.
- No `ai_readiness_*`, `leaderboard_*`, `my_code_today_*`, or `intelligence_*` tables were found.

## Required follow-up before any data migration

- Re-run this map with row counts against staging or a sanitized clone.
- Confirm whether `orgs.settings` is acceptable for per-tenant `IA_V8` override or if a dedicated table is required.
- Confirm whether billing columns on `orgs` are in scope for Settings display only; no billing table edits are proposed.
