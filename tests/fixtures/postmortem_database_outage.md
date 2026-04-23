# Database Outage PIR

## Summary

The primary Postgres cluster rejected write connections for the orders workflow for 47 minutes.
The incident was detected by checkout error budget burn alerts.

## Impact

- Checkout write requests returned 500s for 18% of attempts.
- Support received 23 customer tickets about failed order placement.

## Timeline

| Time | Event |
| --- | --- |
| 2026-03-04T14:05Z | Error budget burn alert fired for orders checkout. |
| 2026-03-04T14:12Z | Database failover was attempted by the on-call engineer. |
| 2026-03-04T14:52Z | Connection pool limits were reduced and writes recovered. |

## Root Cause

- Connection pool saturation exhausted writer slots on the primary database.

## Contributing Factors

- Migration backfill jobs were allowed to run during peak checkout traffic.
- The pool saturation alert was routed as a warning instead of a page.

## Action Items

- [ ] Add a preflight check that pauses backfills during peak traffic windows.
- [ ] Promote database pool saturation alerts to paging severity.

## What Went Well

- Runbook links in the alert helped responders find the failover procedure quickly.

## What Went Wrong / Lessons Learned

- Backfill jobs did not have a concurrency budget tied to live database pressure.
- The first responder had to search Slack for the current database owner.
