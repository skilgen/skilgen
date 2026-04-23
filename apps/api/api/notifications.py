from __future__ import annotations

from typing import Any

import httpx

from packages.db.models import Org, Skill


async def post_slack_message(webhook_url: str, payload: dict[str, Any]) -> None:
    """Post a JSON payload to Slack using a bounded request timeout."""
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.post(webhook_url, json=payload)
        response.raise_for_status()


def build_test_notification_message(org: Org) -> dict[str, Any]:
    """Build the Slack message used by the org settings test action."""
    return {
        "text": f"Skillayer test notification for {org.name}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Skillayer notification test*\nWorkspace: `{org.name}`\nScore threshold: `{org.score_threshold}`",
                },
            }
        ],
    }


def build_stale_skill_message(org: Org, repo_full_name: str, skills: list[Skill]) -> dict[str, Any]:
    """Build a Slack alert for frequently loaded stale skills."""
    fields = [
        {
            "type": "mrkdwn",
            "text": f"*{skill.domain}*\nFreshness {int(skill.score_freshness or 0)} / Loads {int(skill.load_count_30d or 0)}",
        }
        for skill in skills[:10]
    ]
    return {
        "text": f"Skillayer found stale high-usage skills in {repo_full_name}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Stale skill alert*\n{repo_full_name} has {len(skills)} frequently loaded skill(s) below freshness 20.",
                },
            },
            {"type": "section", "fields": fields},
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": f"Workspace: `{org.name}`"}],
            },
        ],
    }
