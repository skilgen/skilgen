# Enterprise Repo Example

Use this pattern when your team wants repo-native skills plus enterprise skill packs and governed MCP connectors.

Example config:

```yaml
enterprise_skill_paths:
  - ./enterprise/platform-skills
enterprise_skill_urls:
  - https://internal.example.com/skills/platform-pack.zip
mcp_policy_pack_path: ./policy/mcp-policy.json
```

Recommended flow:

```bash
skilgen init --project-root .
skilgen deliver --project-root . --requirements docs/platform-prd.docx
skilgen connectors recommend --project-root .
skilgen score --project-root . --history
```

What this gives you:

- repo-native skill generation
- enterprise skill ingestion
- MCP allow/deny/approval policy enforcement
- analytics and score history for engineering governance
