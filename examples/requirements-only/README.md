# Requirements-Only Example

Use this mode when the product exists as a PRD, feature brief, or requirements document but the codebase is still early or empty.

## Run

```bash
skilgen doctor --project-root .
skilgen intent --requirements docs/product-requirements.docx
skilgen plan --requirements docs/product-requirements.docx --project-root .
skilgen deliver --requirements docs/product-requirements.docx --project-root .
```

## Best For

- greenfield products
- roadmap planning before implementation
- generating requirements, roadmap, and starter skill guidance
