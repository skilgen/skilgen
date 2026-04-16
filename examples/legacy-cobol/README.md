# Legacy COBOL Repo Example

Use this pattern when your repo contains COBOL programs, copybooks, and batch-oriented flows.

Recommended flow:

```bash
skilgen init --project-root .
skilgen deliver --project-root . --requirements docs/modernization-plan.pdf
skilgen architecture --project-root . --json
skilgen diff --project-root .
```

What Skilgen will pick up:

- `.cbl`, `.cob`, and `.cpy`
- legacy program paths
- copybooks
- batch/job-style areas
- architecture domains driven by real code evidence instead of only modern web patterns
