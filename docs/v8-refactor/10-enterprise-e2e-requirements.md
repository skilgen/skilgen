# Skillayer Enterprise End-to-End Requirements

**Status:** Draft v1 — 2026-05-19
**Owner:** Ravi (with v8 working group)
**Scope:** Wire every Skillayer surface (API, dashboard, CLI, provider adapters) into a single
enterprise-grade flow that a non-admin end user can sign up for, connect their local coding
agents to, and produce repo + metric coverage from — without ever uploading raw prompts,
chats, diffs, or file contents.

This document is the single source of truth for the "enterprise-wide end-to-end" milestone.
Anything not covered here is out of scope for this milestone and must be filed as a follow-up.

### Product thesis

Skillayer is a **deep coding-agent activity platform** for enterprises. The product must
show what coding agents are actually doing in the background across a company: which
tools they called, which files they touched, which commands they ran, which repos and
PRs they affected, which models and access scopes they used, and where that activity
creates policy, audit, risk, skill, and cost signals.

The core enterprise promise is:

- If an admin connects GitHub, Skillayer automatically pulls repo, PR, commit, branch,
  author, review, and approval metadata for enrichment.
- If an admin or developer installs Skillayer locally, Skillayer automatically pulls
  metadata-only Codex Desktop, Codex CLI, and Claude Code activity from local session
  stores.
- If an admin connects OpenAI or Anthropic compliance APIs, Skillayer automatically
  pulls provider-side agent/compliance metadata.
- All sources must converge into one normalized, metadata-only activity graph.

Every run must be explainable to both a developer and an admin:

- What did the agent do?
- What external APIs or providers did it touch?
- What commands did it run?
- What files did it edit or inspect?
- What permissions and access scope did it have?
- Was it running with full access, default sandbox permissions, or auto-review style
  approval?
- What risk did the run create?
- Which policy or compliance rules did it violate, if any?
- What should a human do next?

Every feature must follow an enterprise information hierarchy:

1. **Overall:** show the company/org-wide picture first: totals, trend, risk, coverage,
   compliance state, and the most important action.
2. **Segments:** let admins break the overall picture down by team, repo, runtime,
   provider, policy, developer, and time window.
3. **Entities:** let users drill into a repo, developer, PR, model, connector, policy, or
   run.
4. **Events:** only after the overview and entity context, show the deepest event-level
   detail: tool calls, commands, files, MCP, external APIs, access posture, and policy
   evidence.

If a feature starts at raw event detail without first answering "what is happening across
the enterprise?", it is incomplete.

### Naming and implementation boundary

This milestone is a **Skillayer** product milestone. Product-facing commands, config
paths, installers, dashboard copy, and docs must not require customers to know or install
"Skilgen".

The current repository still contains legacy/internal Skilgen package code and scripts.
Those files may be reused as implementation scaffolding where it is the fastest safe path,
but roadmap items must be expressed as Skillayer surfaces:

- Product-facing local helper command: `skillayer-agent`.
- Product-facing local config: `~/.skillayer/agent.json`.
- Existing `scripts/import_codex_sessions.py` may remain as a compatibility entry point
  during migration, but new user docs should point at `skillayer-agent`.
- The sample repo `ravichanduummadisetti/skilgen` is local proof data only, not an
  enterprise product dependency.

---

## 1. Goals and non-goals

### 1.1 Goals

1. **End-user self-serve login.** Any developer with a corporate email can sign in to
   Skillayer (WorkOS SSO when the org is provisioned, magic-link for individual signups,
   GitHub OAuth as a third option), land in the dashboard, and reach a working `/dashboard/connect`
   experience without an admin pre-provisioning their account.
2. **Enterprise activation must feel automatic.** Once the org connects GitHub and/or
   installs the Skillayer local helper, Skillayer should start pulling every available
   metadata-only signal without a manual per-repo or per-session workflow:
   - **GitHub connected:** pull repositories, PRs, commits, branches, authors, reviews,
     and installation metadata needed to attribute agent work to real engineering
     evidence.
   - **Skillayer local helper installed:** discover and import local Codex Desktop,
     Codex CLI, and Claude Code sessions first, including tool calls, files modified,
     token/cost estimates, access scope, MCP usage, commands, searches, and repo cwd.
   - **Provider compliance connected:** pull OpenAI and Anthropic compliance metadata
     on a cursor-backed schedule, then join it to GitHub and identity records.
3. **One normalized metadata pipeline.** Local agent capture, GitHub enrichment, and
   provider compliance pull all write the same metadata-only `AgentRun` /
   `agent.compliance` shape so Activity, Insights, Policy, Audit, and Skills do not need
   source-specific hacks.
4. **Repo + metric extraction from chat history.** Every imported session must end up
   attributed to the right repo (by `cwd` / project-root match), with full coding-agent
   metrics (tool calls, files edited, tokens, cost, access scope, MCP usage) populated
   in Activity, Insights, Policy, Audit, and Skills surfaces.
5. **Run-level risk and access explainability.** Every run must expose its external API
   calls, shell commands, permission posture, access scope, compliance state, risk score,
   and human-readable risk reasons.
6. **Developer/admin friendly UX.** Every feature in this milestone must answer:
   "Would a developer or admin actually use this to understand, govern, or improve agent
   work?" If not, the UX must be changed before the feature is considered done.
7. **Overview-to-drilldown product shape.** Every feature must start with the overall
   enterprise picture, then allow drilldown into teams/repos/developers/runs/events
   without forcing users to begin in raw detail.
8. **Enterprise verification checklist.** A documented matrix of which flows pass today,
   which need glue, and a repeatable verification command (`make verify-enterprise`)
   that exercises the whole chain end-to-end against a seeded SQLite + dashboard build.

### 1.2 Non-goals

- Capturing raw prompts, agent chat text, file contents, diffs, or tool arguments
  (explicit PRD-v8 constraint — `content_retention: metadata-only` is contractual).
- Replacing the existing admin panel (`/dashboard/admin`) — admin stays as-is.
- Multi-region data residency, BYO-KMS, on-prem deploy — those are post-milestone.
- New analytic surfaces — this milestone only fills the data pipeline; downstream
  surfaces (Activity, Insights, etc.) already exist and only need data to flow.
- GitHub as a source for local prompt/chat history. GitHub gives repo/PR/commit evidence
  and enrichment; local coding-agent session files and provider compliance APIs provide
  agent telemetry.
- Generic productivity surveillance. Skillayer is about coding-agent actions, codebase
  impact, governance, and compliance evidence, not keystroke monitoring or employee
  screen surveillance.

---

## 2. What already exists (do not rebuild)

Verified against current `v8/next-feature-loop` (commit `a3f4685`, 2026-05-19).

| Capability | Where | Notes |
| --- | --- | --- |
| WorkOS AuthKit middleware | [apps/dashboard/middleware.ts](../../apps/dashboard/middleware.ts) | Falls back to a "preview" header when env vars are missing; gates `/dashboard`, `/activity`, `/policy`, `/audit`, `/skills`, `/insights`, `/settings`, `/api/admin/*`. |
| WorkOS sign-in + callback routes | [apps/dashboard/app/sign-in/page.tsx](../../apps/dashboard/app/sign-in/page.tsx), [apps/dashboard/app/callback/route.ts](../../apps/dashboard/app/callback/route.ts) | Self-serve entry lives on `/sign-in`; callback warms JIT provisioning via `POST /me/provision`. |
| `/dashboard/connect` page | [apps/dashboard/app/dashboard/connect/page.tsx](../../apps/dashboard/app/dashboard/connect/page.tsx) | Renders connection status cards for GitHub, API key, skills, agent loads. Reads `${API_URL}/orgs/{org_id}/connect/status`. |
| Connectors catalog (Settings → Connectors) | [apps/api/api/v8/settings/connectors_registry.py](../../apps/api/api/v8/settings/connectors_registry.py), [apps/dashboard/app/(v8)/settings/connectors/page.tsx](../../apps/dashboard/app/\(v8\)/settings/connectors/page.tsx) | Covers GitHub/GitLab/Bitbucket, Jira/Linear, Slack, Splunk/Datadog/Sentinel, S3 Object Lock/GCS/Azure Immutable Blob, Sigstore/SLSA, Anthropic, OpenAI, plus coding-agent slots for Windsurf, Aider, Copilot, GitLab Duo, MCP. |
| Anthropic + OpenAI compliance sync adapters | [apps/api/api/v8/settings/router.py](../../apps/api/api/v8/settings/router.py) | Scaffolded; emit `agent.compliance` audit records via the metadata-only ingest contract. |
| Codex Desktop + Claude Code JSONL → `AgentRun` importer | [scripts/import_codex_sessions.py](../../scripts/import_codex_sessions.py) | Already parses tool calls, files, tokens, cost, access scope. CLI flags: `--codex-home`, `--claude-home`, `--providers`, `--project-root`, `--org-id`, `--api-url`, `--token`. |
| `POST /orgs/{org_id}/agent-runs` ingest | [apps/api/api/routes/agent_runs.py](../../apps/api/api/routes/agent_runs.py) | Receives the importer payloads. Already redacts raw content keys server-side. |
| Activity / Insights / Policy / Audit v8 surfaces | [apps/dashboard/app/(v8)/](../../apps/dashboard/app/\(v8\)/) | All driven by normalized `agent.compliance` events; populated automatically when ingest is wired. |

---

## 3. Functional verification matrix — current state

Run before and after each milestone PR. ✅ = passes today, ◐ = partial, ❌ = missing.

| Flow | Status | What to run | Notes |
| --- | --- | --- | --- |
| Dashboard type-check | ✅ | `npm --workspace apps/dashboard run typecheck` | Verified 2026-05-19 pre-push. |
| Dashboard build | ✅ | `npm --workspace apps/dashboard run build` | Verified 2026-05-19 pre-push. |
| API py-compile for touched files | ✅ | `python -m compileall apps/api/api` | Verified 2026-05-19 pre-push. |
| API pytest (full) | ✅ | `pytest apps/api/tests -q` | Verified 2026-05-21; keep `make verify-enterprise` as the CI gate. |
| Replay / Sessions / Live-feed pagination | ✅ | Manual browser walk (logged 2026-05-19). | Keep the Playwright smoke (`apps/dashboard/e2e/`) for this. |
| WorkOS SSO sign-in | ◐ | Local `.env` with all four `WORKOS_*` vars, hit `/sign-in`. | Works when configured; routes to `/dashboard/connect`. |
| Self-serve magic-link sign-up | ◐ | Local `.env` with all four `WORKOS_*` vars, hit `/sign-in` → Send magic link. | UX + JIT provisioning shipped; local preview uses `auth=magic-link-preview` without WorkOS. |
| GitHub repo/PR/commit enrichment | ✅ | Connect GitHub App, inspect repo/PR links in Insights. | Keep this as the canonical repo evidence backbone. |
| Codex Desktop import (single dev) | ✅ | `python scripts/import_codex_sessions.py --providers codex --org-id <org> --token <key>` | Verified end-to-end against the local API. |
| Claude Code import (single dev) | ✅ | `python scripts/import_codex_sessions.py --providers claude --org-id <org> --token <key>` | Same script; uses `~/.claude/projects/**/*.jsonl`. |
| Codex CLI import | ✅ | `python -m unittest tests.test_codex_cli_runtime -v` | Codex CLI writes to `~/.codex/sessions` like Codex Desktop. Runtime tagging is verified via `session_meta.client='codex-cli'` (or `originator='Codex CLI'`) → `agent.runtime='codex_cli'`. |
| Cursor import | ✅ | `python -m unittest tests.test_cursor_importer -v` | `packages.skillayer_agent.local_importer.build_cursor_agent_run_payloads` parses `state.vscdb` metadata, tool calls, commands, edited files, searches, tokens, and Cursor runtime identity without raw prompts/diffs. |
| Windsurf import | ✅ | `python -m unittest tests.test_windsurf_importer -v` | `packages.skillayer_agent.local_importer.build_windsurf_agent_run_payloads` parses local Windsurf JSONL metadata into the same commands/files/searches/tokens AgentRun evidence shape. |
| Anthropic compliance pull | ✅ | Settings → Connectors → Anthropic → "Queue sync"; `python -m unittest tests.test_anthropic_compliance_sync -v`. | Real admin compliance API pull, cursor persistence, retry-after blocked state, and metadata-only normalization are implemented. |
| OpenAI compliance pull | ✅ | Settings → Connectors → OpenAI → "Queue sync"; `python -m unittest tests.test_openai_compliance_sync -v`. | Real organization audit-log pull, cursor persistence, event filters, and metadata-only normalization are implemented. |
| Repo attribution from `cwd` | ✅ | Inspect `metadata.cwd` and `repo.full_name` on imported runs. | Works whenever `--project-root` matches the agent's cwd. |
| Activity / Insights / Audit population from imported runs | ✅ | After import, visit `/activity/replay`, `/insights/developer-track`, `/audit/evidence-packages`. | Already wired; no glue needed. |

`make verify-enterprise` (to be added in §10) should chain the green rows above into one
command. Cursor/Windsurf importers are valuable expansion work, but they are not allowed
to block the first enterprise-saleable milestone, which is GitHub enrichment + Codex /
Claude local metadata + OpenAI / Anthropic compliance metadata.

---

## 4. End-user login

### 4.1 Modes (in priority order)

1. **WorkOS SSO (existing).** Used when the org has an AuthKit connection configured.
   No change needed; we only fix discovery — the dashboard `/` landing page must show a
   "Sign in with your work account" button that routes to `/sign-in`.
2. **Magic-link self-serve (new).** Any developer with a verified corporate email
   creates a personal org on first login. Implemented with WorkOS Passwordless API
   (Magic Auth). One screen: enter email → receive link → land at `/dashboard/connect`.
3. **GitHub OAuth (new, optional).** Re-uses the existing GitHub App for sign-in only
   (no install). Adds a "Sign in with GitHub" button on `/sign-in`. Useful for the
   solo-dev / try-before-you-buy persona.

### 4.2 Provisioning rules

- First successful sign-in for an unrecognised email triggers **JIT org creation**:
  - Create `orgs` row (`plan='free'`, `is_suspended=false`).
  - Create `users` row, bind to the org with role `owner`.
  - Generate an `orgs.api_key` (used by the local-agent importer).
  - Emit `audit_events` row `event_type='org.created'`, `actor=<user>`.
- Subsequent sign-ins with the same domain join the existing org as `developer` unless
  the org has `auto_join_domain=false` (settable in `/settings`). This matches the
  Vercel / Linear self-serve model and keeps day-1 zero-friction.

### 4.3 Tasks

| # | Task | Owner | Files / interfaces |
| --- | --- | --- | --- |
| L1 | Add public landing route `/` with "Sign in" CTA when no session. | dashboard | `apps/dashboard/app/page.tsx` |
| L2 | Add `/sign-in/page.tsx` with three buttons (SSO, Magic-link, GitHub). | dashboard | `apps/dashboard/app/sign-in/page.tsx` (currently a `route.ts` — convert to `page.tsx` + a server action). |
| L3 | Magic-link send + verify endpoints. | dashboard + WorkOS | `app/api/auth/magic-link/send/route.ts`, `app/api/auth/magic-link/verify/route.ts`. Use `@workos-inc/node` Passwordless. |
| L4 | GitHub OAuth sign-in route. | dashboard | `app/api/auth/github/route.ts` + `callback` branch in existing `/callback`. |
| L5 | JIT org/user provisioning in `/callback`. | api | Add `orgs.ensure_from_login(email, name, source)` helper; call from `/callback`. |
| L6 | Settings → Members → "Auto-join by domain" toggle. | full-stack | `apps/api/api/v8/settings/router.py`, `apps/dashboard/app/(v8)/settings/teams/page.tsx`. |
| L7 | `tests/test_jit_provisioning.py` covering new-email, returning-email, suspended-org, mismatched-domain. | api | New file. |
| L8 | Playwright smoke: sign in via magic-link → land on `/dashboard/connect`. | dashboard | `apps/dashboard/e2e/auth-entry.spec.ts`. |

### 4.4 Current PR-L status

- ✅ L1: public landing route is implemented.
- ✅ L2: `/sign-in` is a real page with SSO, email magic-link, and staged GitHub entry.
- ✅ L3: magic-link send and verify routes exist. Local preview safely routes corporate
  email submissions to the Connect experience when WorkOS is not configured; production
  uses WorkOS Passwordless MagicLink sessions.
- ✅ L4: GitHub OAuth entry is enabled via AuthKit (`/api/auth/github`) and forwards
  to the canonical Connect flow.
- ✅ L5: JIT org/user provisioning lands on the API (`/me/provision`) and is invoked
  from the dashboard callback (`/callback`) on successful AuthKit login.
- ✅ L6: Settings → Teams includes an "Auto-join by domain" toggle backed by
  `orgs.auto_join_domain`.
- ✅ L7: `apps/api/tests/test_jit_provisioning.py` covers new email, returning email,
  suspended org, and auto-join disabled.
- ◐ L8: Playwright smoke covers the local-preview magic-link path and screenshots the
  auth entry. Full email-link inbox verification remains for the WorkOS-configured
  staging pass.

Latest verification for this sub-slice (2026-05-20):

- `npm --workspace apps/dashboard run type-check`
- `npm --workspace apps/dashboard run build`
- `python -m pytest apps/api/tests/test_jit_provisioning.py -q`
- `python -m pytest apps/api/tests/test_me_provision_endpoint.py -q`
- `python -m pytest apps/api/tests/test_v8_settings_teams_auto_join.py -q`
- `npx --workspace apps/dashboard playwright test e2e/auth-entry.spec.ts` (blocked in this Codex automation environment: Chromium exits `SIGTRAP`/`SIGABRT` + `kill EPERM`; run manually on a normal dev machine)
- `git push origin v8/next-feature-loop` (blocked in this Codex automation environment: no GitHub HTTPS credentials; `fatal: could not read Username for 'https://github.com': Device not configured`)

Push workaround in this repo:

```sh
GIT_DIR=.git_writable GIT_WORK_TREE=. git push origin v8/next-feature-loop
```

---

## 5. Path A — local-agent capture (Skillayer local helper)

Path A is the "install Skillayer and it pulls local agent evidence" motion. The first
enterprise-saleable version must cover Codex Desktop, Codex CLI, and Claude Code because
those are already close to working and already expose the tool calls, file targets,
commands, searches, tokens, cost estimates, access scope, and MCP metadata Skillayer
needs. Cursor and Windsurf remain expansion runtimes after the core path is green.

### 5.1 User experience

1. Admin connects GitHub and invites developers or installs Skillayer local helper
   through the enterprise rollout instructions.
2. Developer signs in (§4), lands on the canonical Connect experience, clicks "Install
   Skillayer locally" if the helper is not already deployed.
3. Connect page shows a code block:
   ```sh
   curl -fsSL https://skillayer.com/install.sh | sh
   skillayer-agent connect  # opens browser, OAuth device flow, writes ~/.skillayer/agent.json
   skillayer-agent sync     # one-shot import of all local agent sessions
   skillayer-agent watch    # optional: tail new sessions in the background
   ```
4. As soon as `skillayer-agent sync` posts the first payload, the connect-page status card flips
   to "Connected" via `connect_status.agent_runtimes`.
5. On every subsequent `sync` or `watch` tick, Skillayer imports all newly discovered
   supported local agent sessions under the configured project roots and joins them to
   GitHub repo/PR/commit evidence when available.
6. Enterprise admins must be able to confirm fleet coverage: which developers have the
   helper installed, which runtimes were detected, last sync time, events imported,
   files/tools/commands observed, and what repo attribution is missing.

### 5.2 Agent runtimes covered

| Runtime | Local store | Parser status | Owner |
| --- | --- | --- | --- |
| Codex Desktop | `~/.codex/sessions/**/*.jsonl` + `~/.codex/session_index.jsonl` | ✅ Core milestone. Implemented in `scripts/import_codex_sessions.py:build_agent_run_payloads`; move behind Skillayer helper boundary. | platform |
| Codex CLI | `~/.codex/sessions/**/*.jsonl` (same store; differing `session_meta`) | ✅ Core milestone. Reuses Codex parser and tags `agent_runtime='codex_cli'` when session metadata identifies CLI clients. | platform |
| Claude Code | `~/.claude/projects/**/*.jsonl` | ✅ Core milestone. `build_claude_agent_run_payloads`; move behind Skillayer helper boundary. | platform |
| Cursor | `~/Library/Application Support/Cursor/User/workspaceStorage/**/state.vscdb` | ✅ Expansion parser. Implemented in `packages.skillayer_agent.local_importer.build_cursor_agent_run_payloads`; gated by selecting provider `cursor`. | platform |
| Windsurf | `~/.codeium/windsurf/conversations/**/*.jsonl` | ✅ Expansion parser. Implemented in `packages.skillayer_agent.local_importer.build_windsurf_agent_run_payloads`; gated by selecting provider `windsurf`. | platform |

### 5.3 Skillayer local helper design

New product-facing helper command: `skillayer-agent`. It imports local Codex Desktop,
Codex CLI, Claude Code, Cursor, and Windsurf metadata without uploading raw prompts,
chat text, diffs, file contents, or tool arguments.

Implementation may initially reuse `scripts/import_codex_sessions.py` for the heavy
lifting, but the roadmap must not introduce a customer-facing `skilgen` dependency.
The reusable import code should live behind a Skillayer-owned helper boundary. If the
legacy `skilgen` package is used temporarily, keep it an internal compatibility layer
and document the removal/migration path in the PR.

```text
skillayer-agent connect             OAuth device flow against dashboard, writes config
skillayer-agent connect --token X   Manual API-key fallback for air-gapped users
skillayer-agent sync                One-shot import (calls importers; respects --project-root)
skillayer-agent watch               Long-running fswatch-based tail (macOS uses fsevents,
                                    Linux inotify, Windows ReadDirectoryChangesW)
skillayer-agent status              Prints which runtimes are detected + last upload time
```

Config lives at `~/.skillayer/agent.json` (mode `0600`):
```json
{
  "api_url": "https://api.skillayer.com",
  "org_id": "org_xyz",
  "api_key": "...",
  "project_roots": [{"path": "/Users/.../customer-repo", "repo_full_name": "acme/customer-repo"}],
  "providers": ["codex", "claude", "cursor", "windsurf"]
}
```

Enterprise rollout should also support an admin-provisioned config mode so teams can
deploy `skillayer-agent` through MDM, fleet scripts, or developer bootstrap tooling
without asking every developer to manually paste an org token.

OAuth device flow endpoints (new on the API):
- `POST /v1/device/code` → `{device_code, user_code, verification_uri, interval, expires_in}`
- `POST /v1/device/token` → polled by the CLI until the user confirms in the browser.

### 5.4 Cursor parser spec

- **Discovery.** Walk `~/Library/Application Support/Cursor/User/workspaceStorage/*/state.vscdb`
  (SQLite). Each workspace row contains a `workspace.folder` URI (gives us the `cwd`) and
  a `chat-data` JSON blob holding the message timeline.
- **Per-conversation extraction.** For each conversation:
  - `started_at` = first message timestamp, `ended_at` = last.
  - `model` = `assistant.modelInfo.name`.
  - For each `tool_call` event: increment `tool_calls`, classify as edit/search/list
    using the same heuristics as `_record_claude_tool` in `import_codex_sessions.py`.
  - For `edit_file` / `multi_edit`: record `file_targets[relative_path]` with
    `after_hash = sha256(tool + relative_path)`.
  - Tokens: Cursor exposes `usage.prompt_tokens` / `usage.completion_tokens` per
    message — feed into `_record_claude_usage`-equivalent (split out a generic
    `_record_usage` helper).
- **Repo attribution.** Use `workspace.folder` URI as `cwd`; pass through
  `_belongs_to_project`.
- **Output.** `agent_vendor='Cursor'`, `agent_product='Cursor'`, `agent_runtime='cursor'`,
  `source_provider='cursor_local'`, `source_record_type='cursor_state_vscdb'`.

### 5.5 Tasks

| # | Task | Owner | Files |
| --- | --- | --- | --- |
| A1 | Refactor `scripts/import_codex_sessions.py` into a reusable Skillayer local-agent importer boundary + keep the script as a compatibility entry point. | platform | ✅ `packages.skillayer_agent.local_importer` is now the Skillayer-owned importer boundary; the legacy script remains available for existing automation. |
| A2 | Add `skillayer-agent connect` / `sync` / `watch` / `status` commands. | platform | ✅ `skillayer-agent sync`, `status`, manual-token `connect --token`, browser/device-flow `connect`, and polling `watch` are implemented behind `packages.skillayer_agent.cli`. |
| A3 | OAuth device-flow endpoints on the API. | api | ✅ `apps/api/api/routes/device_flow.py`, `DeviceAuthorization`, and migration `20260520_0006_device_authorizations.py` back the CLI browser approval flow. |
| A4 | Cursor parser per §5.4. | platform | ✅ `packages.skillayer_agent.local_importer.build_cursor_agent_run_payloads` plus `tests/test_cursor_importer.py`. |
| A5 | Windsurf parser. | platform | ✅ `packages.skillayer_agent.local_importer.build_windsurf_agent_run_payloads` plus `tests/test_windsurf_importer.py`. |
| A6 | Tag Codex CLI runs distinctly from Codex Desktop. | platform | ✅ Codex Desktop now emits `codex_desktop`; Codex CLI emits `codex_cli`. |
| A7 | `tests/test_cursor_importer.py`, `tests/test_windsurf_importer.py`, `tests/test_codex_cli_runtime.py`. | platform | ✅ Codex CLI, Cursor, and Windsurf parser tests are complete. |
| A8 | Dashboard: surface per-runtime "last upload" / token / cost counters in `/dashboard/connect`. | dashboard | ✅ `/dashboard/connect` now shows runtime health for Codex Desktop, Codex CLI, Claude Code, Cursor, and Windsurf with uploads, commands, files, tokens, and cost. |
| A9 | `install.sh` one-liner installer (downloads versioned Skillayer local-helper artifact + writes `skillayer-agent` shim). | platform | ✅ `scripts/install.sh` creates an isolated helper venv, installs a local checkout or versioned package spec, and writes a `skillayer-agent` shim. Release artifact hosting remains a release-engineering follow-up. |

---

## 6. Path B — provider compliance pull

Path B is the "connect provider compliance and Skillayer pulls org-wide telemetry"
motion. This is core enterprise value, not a nice-to-have: some customers will prefer
provider-admin telemetry over local installs, and larger customers will want both local
helper evidence and compliance API evidence reconciled into one view.

### 6.1 Anthropic compliance API

- Endpoint: `GET https://api.anthropic.com/v1/admin/compliance/api/messages`
  (cursor-paginated). Returns metadata-only event rows.
- The scaffold in `apps/api/api/v8/settings/router.py` already builds the request and
  ships normalized rows into `audit_events` with `event_type='agent.compliance'`.
- **Required to ship:**
  - Persist cursor in `source_connection_cursors` (table already exists).
  - Map `workspace_id` → `repos.full_name` via the per-org GitHub install (best effort;
    if the workspace can't be matched, leave `repo_id=null` and surface in
    `/insights/provider-coverage` as "unattributed").
  - Map `actor` → `users` row by email; fall back to the JIT provisioning path (§4.2).
  - Rate-limit backoff respecting Anthropic's `retry-after` headers.
  - Test: replay a 200-event compliance fixture, assert idempotent re-runs (same
    cursor → zero duplicate inserts).

### 6.2 OpenAI compliance API

- Endpoint: `GET https://api.openai.com/v1/organization/audit_logs?event_types[]=...`
- Same shape as §6.1; same cursor + mapping requirements.

### 6.3 Tasks

| # | Task | Files |
| --- | --- | --- |
| B1 | Wire real HTTP call in OpenAI adapter, with cursor persistence + idempotency. | ✅ `apps/api/api/v8/settings/openai_compliance_adapter.py` now calls the OpenAI audit-log endpoint, normalizes metadata-only events, resumes with `after` cursor, keeps provider event ids stable for duplicate suppression, and is covered by `tests/test_openai_compliance_sync.py`. |
| B2 | Wire real HTTP call in Anthropic adapter, with cursor persistence + idempotency. | ✅ `apps/api/api/v8/settings/anthropic_compliance_adapter.py` now calls the Anthropic compliance messages endpoint, resumes with cursor, respects `retry-after` failure posture, normalizes metadata-only Claude usage/cache/cost/access evidence, and is covered by `tests/test_anthropic_compliance_sync.py`. |
| B3 | Job worker schedules a sync every 15 min per connected adapter. | ✅ `/worker/agent-compliance/provider-sync` queues due OpenAI/Anthropic provider sync jobs, skips connectors with queued/running jobs, preserves cursor resume state, and records the next 15-minute window. |
| B4 | Surface adapter health in `/dashboard/connect` and `/settings/connectors`. | ✅ `/orgs/{org_id}/connect/status` now returns provider sync health for OpenAI/Anthropic, and `/dashboard/connect` shows compliance API coverage beside runtime health before setup instructions. |

---

## 6A. GitHub enrichment backbone

GitHub is the repo evidence backbone for enterprise selling. Connecting GitHub should
pull all metadata Skillayer needs to enrich agent and compliance events:

- Repositories, default branches, installation state, and repo ownership metadata.
- Pull requests, PR ids/numbers, authors, reviewers, labels, head/base branches, head
  SHA, merge SHA, state, timestamps, and URLs.
- Commits and branch heads needed to match provider events by `commit_sha`, `head_sha`,
  `branch`, `repo.full_name`, or PR number/id.
- Review and approval metadata needed by Policy and Audit surfaces.

GitHub does **not** replace local agent capture or provider compliance APIs. It is the
join layer that turns raw agent/provider metadata into repo, PR, commit, reviewer, and
policy evidence.

### 6A.1 Tasks

| # | Task | Files |
| --- | --- | --- |
| G1 | Treat GitHub connection as a first-class Connect requirement and show whether repo/PR/commit enrichment is active. | `/dashboard/connect`, `/settings/connectors`, existing GitHub connector APIs. |
| G2 | Ensure local-agent and provider-compliance events join to GitHub by repo full name, PR number/id, branch, head SHA, or commit SHA. | Insights/Activity enrichment services. |
| G3 | Surface unmatched GitHub gaps as action items, not silent misses. | `/insights/provider-coverage`, `/insights/identity-mapping`, `/settings/connectors`. |

### 6A.2 Current PR-G status

- ✅ G1: `/dashboard/connect` and `/settings/connectors` surface GitHub enrichment active/pending with PR/commit counts + join gaps.
- ✅ G2: Provider-compliance ingest and local-agent ingest attach `github_enrichment_status` + `git_url` by joining on repo name/id, PR number/id, branch, and head/commit SHA.
- ✅ G3: Join gaps show as actionable coverage gaps (not silent misses) in Provider Coverage and Settings → Connectors.
- ✅ Operational: PR-G commits are pushed and PR proof is recorded in PR #11.

---

## 7. Cracking repos + metrics from chat history

This is the question the user explicitly asked. Here is the contract.

### 7.1 Repo attribution

A chat-history record becomes an `AgentRun` attributed to a repo when **at least one of**:

1. `cwd` (Codex `turn_context.cwd`, Claude `cwd`, Cursor `workspace.folder`) resolves
   under a configured `project_root` (`~/.skillayer/agent.json:project_roots[].path`).
2. Any `file_targets` path resolves under that `project_root`.
3. The runtime's session metadata contains an explicit `repo` field (rare; Anthropic
   compliance and OpenAI compliance both supply `workspace_id` which we map server-side).

The current implementation lives in
[`_belongs_to_project`](../../scripts/import_codex_sessions.py:62) — it is the canonical
predicate and must be reused unchanged across Codex, Claude, Cursor, Windsurf.

Repo name resolution chain (first hit wins):

1. CLI flag `--repo-full-name` or `--repo-id` (explicit).
2. `git config --get remote.origin.url` resolved at `project_root`.
3. `project_root` directory name (fallback for unversioned folders).

### 7.2 Metrics derived per session

The importer already produces these. They are the canonical metric surface and downstream
dashboards must not invent new shapes:

- `tokens_input`, `tokens_output`, `tokens_total`, `tokens_cached_input`,
  `tokens_reasoning_output`, plus Claude cache-creation 5m/1h splits.
- `cost_usd` (provider-aware: `_openai_rates`, `_claude_base_rates`).
- `tool_calls`, `mcp_tools`, `tool_permissions`, `access_scope`, `full_access`.
- `activity_metrics.{edited_files,explored_files,searches,lists,commands,tool_calls,mcp_tools}`.
- `activity_details.{edited_files,explored_files,searches,lists,commands,tools}` (the
  redacted human-readable summaries — commands run through `_redact_command`).
- `file_targets[path] = {file_path, tool, after_hash}` (no diff body, no contents).
- `reasoning_effort` + derived `reasoning_mode` (`fast`/`normal`/`high`).
- `cwd`, `model`, `approval_policy`, `sandbox_policy`, `permission_profile`.
- `provider`, `agent_provider`, `agent_vendor`, `agent_product`, `agent_runtime`,
  `source_provider`, `source_record_types[]`.

### 7.2A Deep activity events

Skillayer must preserve event-level depth wherever the source exposes it safely. Session
rollups are not enough for the enterprise product. The normalized metadata pipeline must
be able to answer:

- Which tool was called, by which runtime, at what time, in which repo/session.
- Whether the tool was an edit, write, read, search, list, shell command, MCP call,
  approval request, provider action, or unknown tool.
- Which file path was targeted and whether it was edited, explored, searched, listed, or
  generated. Store path and hashes only; never store file bodies or diffs.
- Which shell command category ran, with redacted command summaries only.
- Which MCP server/tool names were used and whether they required elevated permissions.
- Which approval policy, sandbox/access scope, and permission profile applied.
- Which model/reasoning mode/tokens/cost estimate or provider-reported cost was tied to
  the event/session.
- Which GitHub repo/PR/commit/branch evidence the event could be joined to.
- Which external API/provider endpoint category was contacted when the source exposes it
  safely, including OpenAI, Anthropic, GitHub, package registries, cloud APIs, MCP
  servers, or other networked tools. Store provider/domain/category and count; do not
  store request bodies, secrets, or raw tool arguments.

Downstream surfaces may aggregate these events, but ingestion must keep the deepest
metadata granularity available so an admin can inspect what happened instead of seeing
only high-level totals.

### 7.2B Run risk, access, and compliance view

Every imported run must have a risk/access/compliance summary that can power a useful
run-detail UX:

- `risk_score` and `risk_level` (`low`, `medium`, `high`, `critical`).
- `risk_reasons[]` with short human-readable reasons such as "full filesystem access",
  "network-capable MCP tool used", "shell command touched production config", "many
  files edited", "unattributed repo", or "provider event missing GitHub evidence".
- `permission_profile`, `approval_policy`, `sandbox_policy`, `access_scope`, and
  `full_access`.
- `compliance_status` (`passed`, `warning`, `failed`, `unknown`) and
  `policy_violations[]`.
- `external_api_calls.count`, grouped by provider/domain/category where available.
- `commands.count` plus redacted command summaries and command categories.
- `file_targets.count`, grouped by edit/read/search/list/generated.
- `mcp_tools.count`, server/tool names, and elevated-permission indicators.
- `human_next_action`, for example "review command", "map repo", "approve exception",
  "rotate token", or "no action".

The run-detail UX must make this understandable without forcing admins to read raw JSON.
Developers should see what the agent did and how to make future runs safer. Admins should
see whether the run was compliant, what it had access to, and why it was risky.

### 7.2B Current PR-R status (2026-05-20)

- ✅ Persisted run-level risk/access/compliance summary fields on `agent_sessions` via `apps/api/alembic/versions/20260520_0005_agent_run_risk_access.py`.
- ✅ `/orgs/{org_id}/agent-runs` now derives and stores `risk_score`, `risk_level`, `compliance_status`, access posture fields, and summarized counts (commands/MCP/file targets) per imported run.
- ✅ v8 Activity session payloads now include access posture (`approval_policy`, `sandbox_policy`, `permission_profile`, `access_scope`, `full_access`), GitHub join evidence (`git_url`, `github_enrichment_status`, `github_enrichment_gap`), and policy violation summaries where present.
- ✅ `/activity/replay/:sessionId` first viewport now shows risk level, compliance status, access summary, GitHub join status/link, and a human next action callout before drilling into files/commands/tools evidence.
- ✅ External API/provider call breakdown is preserved as metadata-only provider/domain/category counts and surfaced in the replay drill-down. Per-MCP elevated-permission indicators will expand automatically as source runtimes expose that detail.

### 7.3 What is intentionally NOT extracted

Any new parser **must** drop these on the floor — server also re-redacts as a defence
in depth, but parsers are the first line:

- Message text (`user_message.content`, `agent_message.content`).
- `function_call.arguments` body (only the shape — name, tool, redacted command summary).
- File contents (`Read.contents`, `Write.contents`, `Edit.old_string` / `new_string`).
- Unified-diff bodies (only the file path + hash).
- API keys / tokens / passwords (already scrubbed by `_redact_command`).

If a parser is found leaking any of the above, treat it as a P0 incident; the server
ingest will reject the payload but we lose evidence.

---

## 8. Data model deltas

All migrations land in `apps/api/alembic/versions/` with the date prefix convention.

| Migration | Purpose |
| --- | --- |
| `20260520_0001_jit_user_provisioning.py` | Add `users.source` (`workos`, `magic_link`, `github_oauth`), `orgs.auto_join_domain` (bool, default true), index on `users.email`. |
| `20260520_0002_device_authorizations.py` | New table backing the OAuth device flow (`device_code`, `user_code`, `org_id`, `user_id`, `approved_at`, `expires_at`). |
| `20260520_0003_agent_runtime_metadata.py` | Add `agent_runs.agent_runtime` (already in metadata JSON; promote to column for indexed filters) + index on `(org_id, agent_runtime, started_at)`. |
| `20260520_0004_source_connection_cursors.py` (if not already) | Persistent cursor storage for Anthropic/OpenAI sync. |
| `20260520_0005_agent_run_risk_access.py` | Persist run-level risk/access/compliance fields for indexed run-detail views: `risk_score`, `risk_level`, `compliance_status`, `permission_profile`, `approval_policy`, `sandbox_policy`, `access_scope`, `full_access`, external API call counts, command counts, MCP counts, file target counts, and policy violation summary. |

---

## 8A. Run-detail UX requirements

All Skillayer UX must use progressive disclosure: overview first, drilldown second,
raw event detail last. Enterprise admins need to orient at org scale before deciding
where to investigate.

For every feature:

- Start with the overall enterprise picture: totals, trends, risk/compliance summary,
  coverage state, and highest-priority action.
- Provide drilldowns by team, repo, developer, runtime, provider, model, policy, and time
  window as relevant.
- Provide entity pages for repos, developers, PRs, runs, connectors, policies, and
  evidence packages.
- Provide raw event-level metadata only after the user has enough context to understand
  why that event matters.

The run-detail page is a core enterprise surface. If this UX is confusing, the product
will not sell. Each run detail must be developer/admin friendly:

- **At-a-glance header:** repo, branch/PR/commit, runtime, model, actor, started/ended
  time, duration, risk level, compliance status, and cost/tokens.
- **What happened:** timeline or grouped sections for tool calls, file targets, commands,
  searches/lists, MCP usage, external API/provider calls, and approvals.
- **Access posture:** clear labels for full access, default sandbox, auto-review,
  approval policy, permission profile, and network/MCP capabilities.
- **Risk explanation:** risk score, top reasons, policy violations, and the human next
  action.
- **Evidence joins:** GitHub repo/PR/commit links where matched; explicit "missing
  attribution" action when unmatched.
- **Developer usefulness:** show enough detail for a developer to understand and improve
  the run without exposing raw prompts or file contents.
- **Admin usefulness:** show enough detail for an admin to audit, approve, quarantine, or
  tune policy without reading JSON.

Before shipping any UI feature, ask and answer in the PR/evaluator notes:

1. Would a developer use this to understand what the agent did?
2. Would an admin use this to assess risk, access, and compliance?
3. Does the page start with the overall enterprise picture before drilling down?
4. Can users drill from overall → segment → entity → event without losing context?
5. Is the important action visible within the first viewport?
6. Are empty/error/unattributed states actionable?
7. Is raw metadata transformed into a clear product explanation?

### 8A.1 No-compromise enterprise UX gates

These gates apply to every automation-built dashboard slice. A feature is not complete
when the data is present; it is complete only when an enterprise reviewer can scan,
decide, and act without reading raw rows or JSON.

- **Triage over tables.** Dangerous runs must announce themselves visually; benign,
  grounded runs must recede. Security leads and compliance reviewers scan for danger
  first, then drill into evidence.
- **Overview before evidence.** Start every surface with the overall state, risk,
  coverage, trend, and primary action. Only then expose grouped entities, runs, and
  event-level details.
- **Skill coverage is first-class.** Because Skillayer's thesis is that agents grounded
  in skill docs are safer, skill coverage must appear in summary KPIs, run/session
  cards, and run-detail verdicts. "Read `SKILL.md` as a file" is not the same as
  "loaded skill docs as agent context"; the UX must explain the difference.
- **One primary action.** Each review surface must have exactly one loud primary action.
  Secondary actions are quiet outline/ghost controls.
- **No raw metadata leak.** No raw JSON, duplicate file panels, fabricated network-call
  counts, or repeated boilerplate such as "Agent session - No skill loads recorded".
- **No noisy repetition.** Repeated evidence must be grouped by issue type, severity,
  entity, or step range. Do not render long piles of duplicate one-line cards.
- **Responsive proof required.** Browser verification at desktop and mobile widths is a
  release gate. Screenshots or equivalent browser checks must prove no clipped text,
  broken radii, overlapping controls, or unusable horizontal sprawl.

### 8A.2 Activity Live feed enterprise design contract

The Activity Live feed (`/activity/live-feed`) is the enterprise triage queue. It must
let a security or governance lead scan 50 agent runs in a few seconds and identify the
runs requiring attention.

Required design:

- Constrain the feed column to approximately `1080px` and center it; do not stretch
  session cards across ultra-wide monitors.
- Keep the KPI strip, compact one-row filters, active-filter chips, Live indicator, and
  Grouped/Chronological toggle.
- KPI tiles:
  - Agent sessions and Spend are neutral secondary-surface tiles.
  - Skill coverage and High-risk runs become alarm tiles only when unhealthy.
  - Low coverage must include a visible track pinned to the real value and a context
    line such as "50 of 50 runs loaded 0 skills".
- Grouped view default sort is highest risk first, not pure reverse chronology.
- Every session card has:
  - a 4px inner risk rail preserving rounded corners (`red >=70`, `amber 40-69`,
    `green <40`);
  - a right-side verdict column with prominent risk score, band label, skill-coverage
    segments, and a quiet Replay button;
  - a left header with agent, model, repo, timestamp, and correctly cased outcome;
  - a plain-language summary sentence;
  - one quiet metadata line, not a chip soup;
  - specific danger chips from the shared classifier, or a calm "Grounded · no flags"
    chip for clean runs.
- Expanded state shows individual actions as a compact list, not nested mini-cards and
  not duplicate risk badges.
- Forbidden regressions: "1 actions" chips, giant solid Replay blocks, repeated
  "Agent session - No skill loads recorded", uniform card styling that hides risk, and
  raw event tables as the default grouped experience.

Latest verification snapshot (2026-05-21): the live feed uses the constrained triage
layout, alarm KPI tiles, risk rails, verdict columns, highest-risk-first grouped sort,
quiet Replay buttons, clean danger chips, and compact expanded action lists.

### 8A.3 Activity Replay enterprise forensic design contract

The Activity Replay page (`/activity/replay/[sessionId]?repo=...`) is the single-run
forensic review surface. It must answer, in order: what happened, why it was flagged,
and what the reviewer should do.

Required design:

- Route naming uses `[sessionId]` consistently. Any links from Live feed or other
  surfaces must resolve to `/activity/replay/[sessionId]?repo=...`.
- Header shows agent + repo, truncated/copyable run id, one metadata line, and actions.
  "Acknowledge run" is the only primary/loud action; "Create policy rule" and "Export"
  are quiet secondary actions.
- Risk verdict panel:
  - score marker is clamped and never clips at `0` or `100`;
  - contributor bars sum exactly to the displayed risk score;
  - verdict facts size naturally and do not create giant empty boxes;
  - recommended action is concise and concrete.
- Replay trace is an interactive serpentine flowchart:
  - D3 computes node coordinates;
  - grouped node labels use clean title case (`Searches x2`, `Commands x7`,
    `Tools x5`, `Explored x14`);
  - destructive/high-risk nodes stand out with decisive red styling without chaotic
    oversized rings;
  - clicking a grouped node selects its first step, while expanding requires an
    explicit count/expand affordance;
  - the detail panel shows exact command/file/query, policy decision, action type,
    result, risk score, and flagged severity/title/reason.
- Flagged Activity is a grouped triage panel:
  - group by `{severity, title}`;
  - show severity, title, count, representative commands, reason, and step links;
  - expand group to show all matching commands;
  - sort Critical, High, Medium, then count descending.
- Evidence stays compact:
  - summary strip, files-touched tree, shell-command dense log, searches, and network;
  - network calls mean real outbound HTTP only;
  - empty states are muted single lines;
  - long commands scroll/wrap inside monospace cells without breaking layout.
- The shared danger classifier is the single source of truth for Replay flagged
  activity, Live feed danger chips, and risk contributors. It must use shell-token
  parsing for redirects so quoted strings, regexes, sed expressions, heredocs, and
  JavaScript/Python comparisons containing `>` do not become false destructive flags.

Latest verification snapshot (2026-05-21): the Replay page has grouped flagged
findings, tokenized classifier regression tests, unclipped risk marker, clean flowchart
labels, explicit group expansion, one primary action, no raw JSON, no duplicated file
panels, and no fabricated network-call counts.

---

## 9. Settings & env vars

Cloud (Vercel + Neon):

```
# Dashboard
NEXT_PUBLIC_API_URL=https://api.skillayer.com
NEXT_PUBLIC_WORKOS_REDIRECT_URI=https://app.skillayer.com/callback
WORKOS_API_KEY=...
WORKOS_CLIENT_ID=...
WORKOS_COOKIE_PASSWORD=<>=32 chars>
WORKOS_PASSWORDLESS_FROM=auth@skillayer.com
GITHUB_OAUTH_CLIENT_ID=...
GITHUB_OAUTH_CLIENT_SECRET=...
IA_V8_DEFAULT=true   # routes /dashboard/* legacy URLs to v8 surfaces

# API
DATABASE_URL=postgres://...neon...
ADMIN_SECRET=...
ANTHROPIC_COMPLIANCE_API_KEY=...
OPENAI_ADMIN_API_KEY=...
SKILLAYER_VERSION=1.0.0
SKILLAYER_INSTANCE=cloud
```

Local dev fallback (`.env.example` already covers most): if any of the WorkOS vars are
missing, middleware drops into "preview" mode and skips auth — keep this behaviour, it
is what unblocks the type-check / build verification commands.

---

## 10. Verification gate (`make verify-enterprise`)

Add a Makefile target chaining the green flows from §3 plus the new ones from §4–§6.
Until every row below passes, the milestone is not done.

```makefile
verify-enterprise:
	npm --workspace apps/dashboard run type-check
	npm --workspace apps/dashboard run build
	python -m compileall apps/api/api packages/skillayer_agent scripts
	python -m pytest apps/api/tests/test_device_flow.py apps/api/tests/test_connect_status.py apps/api/tests/test_v8_settings_rbac.py -q
	python -m unittest tests.test_openai_compliance_sync tests.test_anthropic_compliance_sync tests.test_agent_runs_smoke tests.test_skillayer_agent_cli tests.test_codex_cli_runtime tests.test_import_codex_sessions -v
	python scripts/import_codex_sessions.py --providers codex,claude --dry-run --project-root .
	python -m packages.skillayer_agent.cli status --providers codex,claude --project-root . --dry-run --json
```

Acceptance for the milestone:

1. `make verify-enterprise` returns 0 on a freshly cloned checkout with seed data.
2. A new end user can run, on their own machine, against staging:
   - Visit `https://app-staging.skillayer.com` → click "Sign in" → magic-link email →
     land on the canonical Connect experience.
   - Connect GitHub and see repositories/PR/commit enrichment marked active.
   - Run the three CLI lines from §5.1.
   - See their Codex Desktop / Codex CLI / Claude Code sessions appear in
     `/activity/replay` within one minute, attributed to the right repo, with token /
     cost / tool / file-modification metrics populated.
3. Same end user can alternately skip the CLI, connect Anthropic + OpenAI in
   `/settings/connectors`, wait for the next sync tick, and see the same coverage in
   `/insights/agent-compliance-metrics`, enriched by GitHub wherever repo/PR/commit
   metadata is available.

---

## 11. Sequencing (PR plan)

PRs in this order. Each is independently mergeable behind a feature flag. The first
enterprise-saleable milestone is login + GitHub enrichment + Skillayer local helper for
Codex/Claude + OpenAI/Anthropic compliance pull. Cursor, Windsurf, watch mode, and the
installer are expansion after that core path is working.

1. **PR-L (login)** — §4 tasks L1–L8 + migration 0001. Flag:
   `FF_SELF_SERVE_AUTH`.
2. **PR-G (GitHub enrichment backbone)** — §6A tasks G1–G3. Make GitHub connection
   the repo/PR/commit evidence backbone for all local-agent and provider-compliance
   telemetry.
3. **PR-A1 (Skillayer importer boundary)** — Task A1. Refactor the current Codex /
   Claude importer into a reusable Skillayer local-agent boundary while keeping the
   existing script as a compatibility entry point.
4. **PR-A2 (`skillayer-agent` sync/status)** — ✅ Task A2 partial. Product-facing
   `skillayer-agent sync` and `skillayer-agent status` now cover Codex Desktop,
   Codex CLI-compatible Codex JSONL, and Claude Code through the Skillayer importer
   boundary. Manual-token `skillayer-agent connect --token` writes
   `~/.skillayer/agent.json`; browser/device-flow connect is covered by PR-A4 and
   watch mode is covered by PR-X3.
5. **PR-A3 (Codex CLI tag + connect UX)** — ✅ Tasks A6, A8. Codex CLI is now
   distinct from Codex Desktop, and `/dashboard/connect` shows per-runtime
   upload/token/cost/command/file health before setup instructions.
6. **PR-R (run risk/access/compliance detail)** — ✅ §7.2B and §8A. Persisted
   run-level risk/access/compliance fields (migration `20260520_0005_agent_run_risk_access.py`)
   and upgraded the v8 Activity Replay run-detail UX to surface risk level, compliance
   status, access posture (approval/sandbox/permission profile), GitHub evidence joins,
   policy violations, external API call counts, and human next actions without exposing
   raw prompts/diffs.
7. **PR-B1 (OpenAI real sync)** — ✅ Task B1. Pull real OpenAI compliance metadata with
   cursor persistence and idempotency. The OpenAI adapter now calls
   `GET /v1/organization/audit_logs`, forwards event-type filters and resume cursor,
   maps provider usage/cost/risk/access/repo metadata into Skillayer's metadata-only
   compliance event shape, and keeps stable provider event ids so router ingestion can
   skip duplicate replays.
8. **PR-B2 (Anthropic real sync)** — ✅ Task B2. Pull real Anthropic compliance metadata
   with cursor persistence and idempotency. The Anthropic adapter now calls
   `GET /v1/admin/compliance/api/messages`, forwards workspace/page/cursor settings,
   respects `retry-after` blocked state, maps Claude native token/cache/cost and
   risk/access/repo metadata into Skillayer's metadata-only compliance event shape,
   and keeps stable provider event ids so router ingestion can skip duplicate replays.
9. **PR-B3 (worker schedule)** — ✅ Task B3. `/worker/agent-compliance/provider-sync`
   now scans connected OpenAI/Anthropic compliance adapters, queues only due jobs,
   waits when a prior provider-sync job is still queued/running, and records the next
   15-minute sync window for connector health.
10. **PR-B4 (provider status health)** — ✅ Task B4. `/orgs/{org_id}/connect/status`
   now returns OpenAI/Anthropic provider sync health, and `/dashboard/connect` shows
   compliance API coverage beside local runtime health before setup instructions.
11. **PR-A4 (device flow + connect command)** — ✅ Task A3 plus remaining A2.
   `skillayer-agent connect` now starts the browser/device flow, polls for approval,
   and writes `~/.skillayer/agent.json`; `connect --token` remains the air-gapped
   fallback.
12. **PR-V (verify-enterprise Makefile)** — ✅ §10. `make verify-enterprise` chains
    the core API, provider sync, local helper, compile, dashboard type-check, dashboard
    build, and dry-run importer checks so CI can fail closed on the enterprise path.
13. **PR-X1 (Cursor parser)** — ✅ Tasks A4, A7. `skillayer-agent --providers cursor`
    can now import Cursor `state.vscdb` metadata-only sessions into the same AgentRun
    evidence shape as Codex and Claude, including commands, edits, searches, tokens,
    and runtime identity.
14. **PR-X2 (Windsurf parser)** — ✅ Tasks A5, A7. `skillayer-agent --providers windsurf`
    can now import Windsurf JSONL metadata-only sessions into the same AgentRun
    evidence shape as Codex, Claude, and Cursor, including commands, edits, searches,
    tokens, and runtime identity.
15. **PR-X3 (watch mode)** — ✅ remaining A2. `skillayer-agent watch` now polls local
    agent stores, posts only newly discovered session IDs, records local state, and
    supports `--once` / `--dry-run` for fleet bootstrap verification.
16. **PR-X4 (installer)** — ✅ Task A9. `scripts/install.sh` now supports dry-run,
    local checkout installs, explicit package specs, versioned installs, and a
    `skillayer-agent` shim under the admin-selected bin directory.

---

## 12. Risks and open questions

| # | Question | Action |
| --- | --- | --- |
| Q1 | Cursor's `state.vscdb` schema is undocumented and version-skewed. | Pin parser to the schema observed in Cursor ≥ 0.40; gate behind `FF_AGENT_CURSOR`; ship a `cursor-fixture-capture` script that anonymises a real DB into a test fixture. |
| Q2 | Windsurf JSONL location on Linux / Windows. | Confirm during PR-A3 by running Windsurf on each OS; document in this file before merge. |
| Q3 | Magic-link domain-auto-join — what about Gmail / personal addresses? | Default: personal-domain emails (gmail.com, outlook.com, ...) always create a fresh org and never auto-join. Maintain block list in `apps/api/api/services/personal_domains.py`. |
| Q4 | OAuth device-flow rate limiting. | Cap to 10 outstanding device codes per IP per 5 min; reject with `slow_down` per RFC 8628. |
| Q5 | Provenance of imported cost numbers. | They are estimates (per `_openai_rates` / `_claude_base_rates`). Surface a "cost estimated" badge in Insights; never call them billing-grade. |
| Q6 | Multi-machine same user. | The CLI registers the machine ID (`uname -n` + first MAC) under `users.devices`; admin can revoke a single machine's key without rotating the org-wide API key. |

---

## 13. Definition of done

- All §3 rows are ✅.
- `make verify-enterprise` is green on `main`.
- The §10 acceptance walkthrough is recorded as a Loom / video and linked from the PR
  that lands PR-V.
- ✅ This document is referenced from `docs/v8-refactor/06-pr-sequence.md` and from the
  root `README.md` quickstart section (2026-05-20).
