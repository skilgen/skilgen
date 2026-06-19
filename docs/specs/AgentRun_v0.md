# AgentRun Webhook Spec v0

AgentRun is Skillayer's vendor-neutral event format for AI coding agent sessions. Any agent vendor can POST one event when a session starts, updates, or completes so Skillayer can attribute code, loaded skills, and outcomes without depending on vendor-specific logs.

## Endpoint

```http
POST https://api.skillayer.com/orgs/{org_id}/agent-runs
Authorization: Bearer sk-...
Content-Type: application/json
```

The API key is the same org API key used by `/repos/{repo_id}/skills/load`.

## JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://skillayer.com/schemas/agent-run-v0.json",
  "title": "AgentRun v0",
  "type": "object",
  "required": ["spec_version", "session_id", "agent", "skills_loaded"],
  "properties": {
    "spec_version": { "const": "0" },
    "run_id": { "type": "string" },
    "session_id": { "type": "string" },
    "agent": {
      "type": "object",
      "required": ["vendor", "product"],
      "properties": {
        "vendor": { "type": "string" },
        "product": { "type": "string" },
        "version": { "type": "string" },
        "runtime": { "type": "string" }
      }
    },
    "repo_id": { "type": "string" },
    "repo": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "full_name": { "type": "string" },
        "name": { "type": "string" }
      }
    },
    "user": {
      "type": "object",
      "properties": {
        "login": { "type": "string" },
        "email": { "type": "string" },
        "name": { "type": "string" }
      }
    },
    "started_at": { "type": "string", "format": "date-time" },
    "ended_at": { "type": "string", "format": "date-time" },
    "skills_loaded": {
      "type": "array",
      "items": {
        "oneOf": [
          { "type": "string" },
          {
            "type": "object",
            "properties": {
              "id": { "type": "string" },
              "domain": { "type": "string" },
              "skill_path": { "type": "string" },
              "score": { "type": "number" }
            }
          }
        ]
      }
    },
    "code_artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["file_path"],
        "properties": {
          "file_path": { "type": "string" },
          "tool": { "type": "string" },
          "before_hash": { "type": "string" },
          "after_hash": { "type": "string" },
          "diff": { "type": "string" },
          "content": { "type": "string" },
          "ts": { "type": "string", "format": "date-time" }
        }
      }
    },
    "outcome": { "enum": ["success", "needs_rework", "unknown"] },
    "metadata": { "type": "object" }
  }
}
```

## Versioning

`spec_version` uses a string major version. Vendors must keep backwards-compatible additions within `0`. Breaking field changes require a new major version and endpoint negotiation.

## Examples

### Claude Code

```json
{
  "spec_version": "0",
  "session_id": "claude-2026-04-27-001",
  "agent": { "vendor": "Anthropic", "product": "Claude Code", "version": "1.0", "runtime": "claude_code" },
  "repo": { "full_name": "acme/payments" },
  "user": { "login": "ravi" },
  "started_at": "2026-04-27T14:00:00Z",
  "ended_at": "2026-04-27T14:18:00Z",
  "skills_loaded": [{ "domain": "auth", "skill_path": ".skillayer/skills/auth/SKILL.md" }],
  "code_artifacts": [{ "file_path": "src/auth/middleware.py", "tool": "Edit", "after_hash": "sha256...", "diff": "--- a/src/auth/middleware.py\n+++ b/src/auth/middleware.py\n..." }],
  "outcome": "success"
}
```

### Codex

```json
{
  "spec_version": "0",
  "session_id": "codex-run-8842",
  "agent": { "vendor": "OpenAI", "product": "Codex CLI", "runtime": "codex_cli" },
  "repo": { "full_name": "acme/api" },
  "skills_loaded": ["agents", "cli", "core"],
  "code_artifacts": [{ "file_path": "apps/api/routes/review.py", "tool": "Write", "content": "..." }],
  "outcome": "needs_rework"
}
```

### Cursor

```json
{
  "spec_version": "0",
  "session_id": "cursor-session-12",
  "agent": { "vendor": "Anysphere", "product": "Cursor", "runtime": "cursor" },
  "repo": { "full_name": "acme/web" },
  "skills_loaded": [{ "domain": "design_system" }],
  "code_artifacts": [{ "file_path": "components/Button.tsx", "tool": "AgentEdit", "diff": "..." }]
}
```

### Copilot

```json
{
  "spec_version": "0",
  "session_id": "copilot-workspace-33",
  "agent": { "vendor": "GitHub", "product": "Copilot Workspace", "runtime": "copilot" },
  "repo": { "full_name": "acme/mobile" },
  "skills_loaded": ["testing_conventions", "security_compliance"],
  "code_artifacts": [{ "file_path": "app/login.test.ts", "tool": "WorkspacePatch", "diff": "..." }]
}
```

### Devin

```json
{
  "spec_version": "0",
  "session_id": "devin-task-491",
  "agent": { "vendor": "Cognition", "product": "Devin", "runtime": "devin" },
  "repo": { "full_name": "acme/infra" },
  "skills_loaded": ["operational_knowledge"],
  "code_artifacts": [{ "file_path": "infra/main.tf", "tool": "Patch", "diff": "..." }],
  "metadata": { "task_url": "https://example.com/devin/task/491" }
}
```
