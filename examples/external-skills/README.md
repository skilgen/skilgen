# External Skills Example

Use this flow when you want Skilgen to act as a one-stop shop for skill ecosystems outside the current repo.

## Run

```bash
skilgen skills list
skilgen skills detect --project-root .
skilgen skills install anthropic-skills --project-root .
skilgen skills rank --project-root .
skilgen skills lock-export --project-root .
skilgen skills import awesome-agent-skills-voltagent --project-root . --limit 5
```

## Best For

- installing official ecosystem packs into a repo-local Skilgen registry
- importing downstream packs from curated directory sources
- exporting a reproducible external-skills setup to another repo
- helping agents load the strongest external packs first based on repo fit, trust, and provenance
