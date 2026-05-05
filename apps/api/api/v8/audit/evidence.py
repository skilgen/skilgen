from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO
import json
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile


def build_evidence_package_zip(
    *,
    org_id: str,
    control: str,
    period_start: str,
    period_end: str,
    events: list[dict[str, Any]],
    chain_root: dict[str, Any] | None,
    policies: list[dict[str, Any]] | None = None,
    skills: list[dict[str, Any]] | None = None,
) -> bytes:
    generated_at = datetime.now(UTC).isoformat()
    manifest = {
        "version": "1",
        "org_id": org_id,
        "control": control,
        "period": {"start": period_start, "end": period_end},
        "event_count": len(events),
        "chain_root": chain_root,
        "generated_at": generated_at,
        "index_format": "html",
    }
    index_html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{control} Evidence Package</title></head>
<body>
<h1>{control} Evidence Package</h1>
<p>Org: {org_id}</p>
<p>Period: {period_start} to {period_end}</p>
<p>Events: {len(events)}</p>
<p>Chain root: {(chain_root or {}).get("root_hash", "unavailable")}</p>
<h2>Contents</h2>
<ul>
  <li>manifest.json</li>
  <li>events.json</li>
  <li>policies.json</li>
  <li>skills.json</li>
  <li>chain-root.json</li>
</ul>
</body>
</html>
"""
    buffer = BytesIO()
    with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("index.html", index_html)
        archive.writestr("manifest.json", json.dumps(manifest, sort_keys=True, indent=2, default=str))
        archive.writestr("events.json", json.dumps(events, sort_keys=True, indent=2, default=str))
        archive.writestr("policies.json", json.dumps(policies or [], sort_keys=True, indent=2, default=str))
        archive.writestr("skills.json", json.dumps(skills or [], sort_keys=True, indent=2, default=str))
        archive.writestr("chain-root.json", json.dumps(chain_root or {}, sort_keys=True, indent=2, default=str))
    return buffer.getvalue()
