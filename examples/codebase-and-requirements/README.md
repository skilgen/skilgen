# Codebase And Requirements Example

Use this mode when you want the highest-fidelity output. Skilgen combines implementation evidence from the codebase with product intent from the requirements document.

## Run

```bash
skilgen doctor --project-root .
skilgen analyze --requirements docs/product-requirements.docx --project-root .
skilgen features --requirements docs/product-requirements.docx --project-root .
skilgen plan --requirements docs/product-requirements.docx --project-root .
skilgen deliver --requirements docs/product-requirements.docx --project-root .
```

## Best For

- active products with evolving requirements
- aligning agents to both shipped behavior and planned scope
- producing the strongest `AGENTS.md`, traceability, and skill tree coverage
