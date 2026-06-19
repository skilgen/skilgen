# Polyglot Repo Example

Use this pattern for repos that mix multiple implementation stacks, for example:

- Python services
- TypeScript frontends
- Java or Go backends
- Rust utilities

Recommended flow:

```bash
skilgen init --project-root .
skilgen deliver --project-root . --requirements docs/roadmap.pptx
skilgen architecture --project-root . --json
skilgen score --project-root .
```

Why this is useful:

- Skilgen can reason over multiple source formats in one repo
- architecture mode can surface cross-language domain boundaries
- the skill tree can reflect the actual operating model instead of forcing one-language assumptions
