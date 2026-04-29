from __future__ import annotations

import hashlib
import hmac
import json
from datetime import UTC, datetime
from typing import Any


MANIFEST_VERSION = "1"


def _canonical_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_manifest(
    *,
    pr: Any,
    attribution: Any,
    repo: Any,
    org_api_key: str,
    policy_outcome: str = "pass",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "version": MANIFEST_VERSION,
        "issued_at": datetime.now(UTC).isoformat(),
        "repo": getattr(repo, "full_name", "") or "",
        "pr_number": getattr(pr, "github_pr_number", None),
        "pr_title": getattr(pr, "title", None) or "",
        "agent": {
            "runtime": getattr(attribution, "primary_agent", None),
            "confidence": getattr(attribution, "confidence", None),
            "sessions": getattr(attribution, "sessions", None) or [],
        },
        "skills_loaded": getattr(attribution, "skills_loaded", None) or [],
        "skills_violated": [
            {
                "skill_name": finding.get("skill_name") or finding.get("title"),
                "severity": finding.get("severity"),
                "file_path": finding.get("file_path"),
                "line_number": finding.get("line_number"),
            }
            for finding in (getattr(attribution, "skills_violated", None) or [])
            if isinstance(finding, dict)
        ],
        "risk": {
            "score": getattr(attribution, "risk_score", None),
            "tier": getattr(attribution, "risk_tier", None),
            "breakdown": getattr(attribution, "risk_breakdown", None) or {},
        },
        "policy_outcome": policy_outcome,
    }
    signature = hmac.new(org_api_key.encode(), _canonical_payload(payload).encode(), hashlib.sha256).hexdigest()
    return {**payload, "signature": signature}


def verify_manifest(manifest: dict[str, Any], org_api_key: str) -> bool:
    payload = dict(manifest)
    signature = payload.pop("signature", None)
    if not signature:
        return False
    expected = hmac.new(org_api_key.encode(), _canonical_payload(payload).encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(str(signature), expected)
