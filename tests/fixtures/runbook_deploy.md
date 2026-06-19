---
owner: release-engineering
service: payments-api
---

# Deploy Service Runbook

Use this runbook when deploying the payments API to production.

## Steps

1. Confirm the release candidate and freeze window.
2. Run the deployment workflow from the release branch.
3. Notify the incident channel when the rollout starts.

## Verification

- Check `/health` returns 200 in every region.
- Confirm the deploy dashboard is green.
- Validate https://status.example.com/payments before closing the change.

## Warnings

- Do NOT skip the database backup.
- Never deploy while an active incident is open.
- Avoid force-pushing the release branch.

## Config

| setting | value |
| --- | --- |
| ROLLOUT_PERCENT | 25 |

```bash
kubectl rollout status deploy/payments-api -n prod
```

ROLLBACK_ENABLED=true
