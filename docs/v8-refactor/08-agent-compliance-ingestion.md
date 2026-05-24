# Agent Compliance Ingestion Addendum

This addendum records the scope gap found after PRD v8 review: the PRD names coding-agent connectors but does not explicitly require provider compliance-log ingestion, model/intelligence-tier rollups, or full-access/tool-permission reporting.

## Source anchors

- OpenAI Compliance Platform: Enterprise and Edu customers can obtain audit and compliance data from a ChatGPT workspace. OpenAI describes append-only compliance log events plus stateful query APIs for audit, eDiscovery, DLP, and SIEM workflows, with the logs platform retaining data for 30 days.
- Anthropic Compliance API: Enterprise Primary Owners can enable the API and create compliance access keys to pull activity logs, chat data, and file content. Anthropic also notes audit log events are included.
- Claude Cowork OpenTelemetry: Cowork activity is not captured in Anthropic audit logs, Compliance API, or data exports. Cowork needs an OpenTelemetry connector for real-time prompts, tool/MCP invocations, file access, skills/plugins, approval decisions, model usage, token counts, cost, latency, and errors.

References:

- https://help.openai.com/en/articles/9261474-compliance-api-for-enterprise-customers
- https://support.claude.com/en/articles/13015708-access-the-compliance-api
- https://support.claude.com/en/articles/14477985-monitor-claude-cowork-activity-with-opentelemetry

## Product requirement

Skillayer v8 must ingest and normalize governance telemetry from coding agents and AI workspaces so admins can answer:

- Which users used ChatGPT, Codex/Codex CLI, Claude, Claude Code, Claude Cowork, Cursor, and other coding agents.
- Which users used very-high, high, medium, or low intelligence/model tiers.
- Which users granted full access or autonomous tool/file access.
- Which prompts, tool calls, MCP calls, file accesses, repo accesses, skills/plugins, approvals, denials, errors, model requests, token counts, and cost signals were observed, subject to tenant privacy controls.
- Which events are formal compliance records versus operational telemetry only.

## IA fit

| Surface | Fit |
| --- | --- |
| Settings -> Connectors | Configure OpenAI Compliance Platform, Anthropic Compliance API, Claude Cowork OTel, Claude Code, Codex CLI, Cursor, and other coding-agent sources. |
| Audit -> Event log | Store normalized immutable events with source, provider event id, user, model, intelligence tier, access scope, repo/file targets, policy decision, and source-envelope hash. |
| Activity -> Live feed/Sessions/Replay | Compose normalized events into agent sessions, replay timelines, file/tool activity, and live feed rows. |
| Insights -> Fleet KPIs/Risky agents | Add intelligence-tier usage, full-access grants, tool-permission exposure, and provider coverage rollups. |
| Policy -> Rules/Violations | Allow policies to target provider, model/intelligence tier, full-access grants, tool permissions, repo sensitivity, file paths, and MCP server/tool names. |

## Connector registry additions

First-class connector entries:

- OpenAI Compliance Platform: ChatGPT Enterprise/Edu compliance logs and metadata. Codex workspace events should be ingested here only if exposed by the tenant's OpenAI compliance contract; Codex CLI remains a separate hook/telemetry source.
- Anthropic Compliance API: Claude Enterprise activity logs, chat data, file content, and audit events.
- Claude Cowork OpenTelemetry: required because Cowork is not covered by Anthropic Compliance API/audit logs.
- Claude Code: coding-agent sessions, tool use, file access, skills, and permission decisions from supported hooks or telemetry.
- Codex CLI: local agent sessions, model/intelligence tier, command/tool access, file access, and approval decisions.
- Cursor: enterprise telemetry or local hooks for model tier, full-access grants, tool calls, and repo/workspace activity.

## Proposed API additions

The first implementation slice adds metadata-only event ingestion for configured connectors. Provider-specific pull jobs can now normalize into the same contract instead of each surface inventing its own payload shape.

```text
GET  /v8/orgs/{org_id}/settings/connectors/agent-compliance
POST /v8/orgs/{org_id}/settings/connectors/agent-compliance
POST /v8/orgs/{org_id}/settings/connectors/{connector_id}/sync
POST /v8/orgs/{org_id}/settings/connectors/{connector_id}/ingest-events
GET  /v8/orgs/{org_id}/audit/agent-compliance
GET  /v8/orgs/{org_id}/activity/compliance-events
GET  /v8/orgs/{org_id}/insights/intelligence-usage
GET  /v8/orgs/{org_id}/insights/access-grants
GET  /v8/orgs/{org_id}/insights/provider-coverage
```

The ingest endpoint accepts batches with provider event id, actor, provider, model, model tier, intelligence tier, access scope, full/autonomous access, tool permissions, MCP tools, repo/file targets, policy decision, approval status, violations, warnings, token counts, cost, latency, errors, session id, and source record type. Raw prompt, chat, file content, diffs, tool parameters, and raw event bodies are dropped before persistence. Stored records are `agent.compliance` audit events with `content_retention=metadata-only`, `redaction_state=raw-content-dropped`, and a sanitized source envelope hash.

Provider coverage compares tenant connector metadata with recent normalized audit events. It reports active, silent, stale, and retention-risk providers so operators can catch connector gaps before 30-day provider log retention windows make compliance evidence unrecoverable.

## Real metadata contract

Skillayer must not infer coding-agent usage from dashboard seed rows. The source of truth is normalized metadata from compliance APIs, provider telemetry, and local coding-agent hooks, joined with the existing GitHub integration when a PR number, PR id, branch, commit sha, or head sha is present.

`POST /orgs/{org_id}/agent-runs` now preserves the metadata needed by Activity and Insights:

| Field group | Source fields |
| --- | --- |
| Provider/runtime | `provider`, `agent_provider`, `source_provider`, agent vendor/product, runtime label |
| Model tier | `model`, `model_name`, `model_id`, `intelligence_tier`, `model_tier`, `reasoning_tier` |
| Work type | `task_type`, `task`, `workflow_type`, `intent` |
| Usage | `tokens_input`, `input_tokens`, `prompt_tokens`, `tokens_output`, `output_tokens`, `completion_tokens`, `tokens_total`, `total_tokens`, `cost_usd`, `estimated_cost_usd`, `latency_ms`, `duration_ms` |
| PR context | `pr_number`, `pull_request_number`, `pr_id`, `pull_request_id`, `pr_title`, `pull_request_title`, `head_sha`, `commit_sha`, `sha`, `branch`, `head_branch` |
| Access and policy | `access_scope`, `permission_scope`, `grant_scope`, `full_access`, `full_access_granted`, `autonomous_access`, `autonomous`, `policy_decision`, `decision`, `approval_status` |
| Tools and files | sanitized artifact tool names, `mcp_tools`, artifact file paths, `file_targets`, `files`, `file_scope` |

When PR metadata is present, ingestion resolves it against `pull_requests` for the tenant repo and stores `pr_id`, `pr_number`, `pr_title`, `head_sha`, and `branch` on the `agent.compliance` audit event. This lets the UI answer questions like "which model/reasoning tier pushed this PR?", "how many tokens did this PR consume?", and "which task types are spending high-reasoning tokens?" without relying on dummy Cursor/Codex sample rows.

Default retention remains metadata-only. Raw prompts, file content, diffs, and tool parameters stay out of the normalized audit event unless a future tenant setting explicitly enables content retention.

## Skillayer local agent helper (metadata-only)

For local QA, bootstrap demos, and the first enterprise local-helper rollout, Skillayer can ingest Codex Desktop, Codex CLI-compatible Codex JSONL, and Claude Code session metadata without storing raw prompts or diffs.

Use `skillayer sync` to convert local coding-agent sessions into `POST /orgs/{org_id}/agent-runs` payloads that preserve:
- model + reasoning metadata
- token/cost estimates (when present)
- tool permissions, MCP tools, and file targets (sanitized)
- activity counters (edited files, explored files, searches, lists, commands)

Example:

```bash
skillayer connect \\
  --api-url http://127.0.0.1:8000 \\
  --org-id org_skilgen \\
  --token sk-local-demo \\
  --repo-id repo_skilgen \\
  --project-root .

skillayer status --dry-run
skillayer sync --dry-run
skillayer sync
```

The legacy `scripts/import_codex_sessions.py` entry point and `skillayer-agent` alias remain available for existing automation while product-facing docs and installers move to `skillayer`.

## Proposed data additions

Candidate migrations for a follow-up connector-ingestion PR:

- `add_agent_compliance_connections`: tenant-scoped connector config metadata, provider, scopes, enabled source types, last cursor, last sync result. Secrets stay encrypted through the existing secret mechanism, not in plaintext.
- `add_agent_compliance_events`: normalized append-only event table with source envelope hash, provider event id, event type, actor, model, intelligence tier, access scope, tool/file/repo targets, policy decision, timestamps, and redaction state.
- `add_agent_access_grants`: derived table or materialized view for full-access/autonomous-access grants and approval decisions by user, provider, repo, and time window.
- `add_agent_model_usage_rollups`: derived table or materialized view for very-high/high/medium/low intelligence-tier usage, token/cost metrics, and provider coverage.

Raw prompts, chat content, file content, and tool parameters must be tenant-configurable and redactable. Default storage should be metadata-only unless the customer explicitly enables content retention.

## Rollout notes

- This is a follow-up to the v8 surfaces, not PR-8 deprecation.
- Do not fake connected status from the registry. A provider shows connected only when `source_connections` or the future compliance connection table has a tenant row.
- For OpenAI logs, implement continuous pulls because the public help article states a 30-day logs retention window.
- For Claude Cowork, use OTel ingestion and label it operational telemetry, not formal audit compliance, unless Anthropic changes that contract.
- All connector setup and sync actions require `settings.connectors.manage`; audit reads require `audit.read`; insights rollups require `insights.read`.

## Enterprise roadmap cross-reference

See `docs/v8-refactor/09-enterprise-provider-ingestion-roadmap.md` for the ordered enterprise build plan:

1. Enterprise connector credential model.
2. OpenAI Compliance adapter.
3. Anthropic Compliance adapter.
4. Background cursor sync worker.
5. Identity mapping table.
6. GitHub enrichment for provider events.
7. Connector setup UI with test/sync/coverage status.

Usage and cost values must expose provenance everywhere they appear. Provider-reported cost from compliance/usage APIs is not the same thing as Skillayer-estimated cost calculated from token counts. UI, API, audit evidence, and PR validation notes must label the source explicitly.
