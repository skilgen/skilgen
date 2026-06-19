# Local QA screenshots (2026-05-11)

This folder stores the screenshot proof used by the v8 migration automation runs.

## Mobile proof (missing)

The automation is currently blocked on mobile-width screenshots (~375–390px viewport) for the v8 routes below.

Save each file next to the existing desktop screenshot using the exact `*-mobile.png` filename:

| Screenshot | Route |
| --- | --- |
| `activity-home-mobile.png` | `/activity` |
| `activity-live-feed-mobile.png` | `/activity/live-feed` |
| `activity-compliance-events-mobile.png` | `/activity/compliance-events` |
| `activity-compliance-sessions-mobile.png` | `/activity/compliance-sessions` |
| `activity-sessions-mobile.png` | `/activity/sessions` |
| `activity-replay-index-mobile.png` | `/activity/replay` |
| `activity-replay-detail-mobile.png` | `/activity/replay/sess_skilgen_codex_1?repo=repo_skilgen` |
| `activity-heatmap-mobile.png` | `/activity/heatmap?repo_id=all&hours=720&include_deny_rate=false` |
| `skills-repos-mobile.png` | `/skills/repos` |
| `insights-intelligence-usage-mobile.png` | `/insights/intelligence-usage` |

Notes:

- These must be captured from the migrated v8 shell routes (`apps/dashboard/app/(v8)`), not legacy `/dashboard/*`.
- If your dev server isn’t on `127.0.0.1:4325`, use the same paths on your actual host/port.
