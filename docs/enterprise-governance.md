# Enterprise Governance

Skilgen’s enterprise mode lets teams combine repo-local skills with centrally governed skills, private sources, and approved MCP connectors.

## What it covers

- enterprise skill ingestion from:
  - local paths
  - private Git repositories
  - approved URLs
- connector policy packs for:
  - allow lists
  - deny lists
  - approval-required connectors
  - skill-to-tool binding hints
- activation traceability inside `.skilgen/`

## Typical setup

```yaml
enterprise_skill_paths:
  - ./enterprise/platform-skills
enterprise_skill_git_urls:
  - git@github.company.com:platform/internal-skills.git
enterprise_skill_urls:
  - https://confluence.company.internal/export/engineering-playbook.md
mcp_policy_pack_path: ./policy/mcp-policy.json
```

## Why it matters

This gives coding agents the same repo-local operating context, but with enterprise-approved policies around private knowledge and runtime tool access.
