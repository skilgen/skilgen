from __future__ import annotations

import httpx


ScoreDict = dict[str, int]


def get_installation_token(installation_id: int) -> str:
    """Fetch a GitHub installation token through the API GitHub helper."""
    from apps.api.api.github import get_installation_token as fetch_installation_token

    return fetch_installation_token(installation_id)


def _score_label(total: int) -> tuple[str, str]:
    """Return the score status emoji and label for a total score."""
    if total >= 85:
        return "🟢", "Excellent"
    if total >= 70:
        return "🟡", "Good"
    if total >= 50:
        return "🟠", "Needs work"
    return "🔴", "Poor"


def _delta_suffix(total: int, base: ScoreDict | None) -> str:
    """Return the total score comparison suffix for the headline."""
    if not base:
        return ""
    delta = total - base.get("total", 0)
    if delta > 0:
        return f" (+{delta} vs base)"
    if delta < 0:
        return f" ({delta} vs base)"
    return " (no change vs base)"


def _delta_cell(current_value: int, base: ScoreDict | None, key: str) -> str:
    """Return markdown-formatted score delta for a table cell."""
    if not base:
        return "—"
    delta = current_value - base.get(key, 0)
    if delta > 0:
        return f"`+{delta}`"
    if delta < 0:
        return f"`{delta}`"
    return "—"


def _response_ok(response: httpx.Response) -> bool:
    """Return whether an HTTPX response completed successfully."""
    return bool(getattr(response, "ok", response.is_success))


def build_comment(
    current: ScoreDict,
    base: ScoreDict | None,
    run_id: str,
) -> str:
    """Build the Skillayer pull request score comment body."""
    total = current.get("total", 0)
    emoji, label = _score_label(total)
    delta_line = _delta_suffix(total, base)

    groundedness = current.get("groundedness", 0)
    coverage = current.get("coverage", 0)
    freshness = current.get("freshness", 0)
    structure = current.get("structure", 0)

    return f"""## {emoji} Skilgen Score: {total}/100{delta_line}

**{label}** — AI agent readiness for this branch

| Dimension | Score | Change |
|---|---|---|
| Groundedness | {groundedness}/25 | {_delta_cell(groundedness, base, 'groundedness')} |
| Coverage | {coverage}/25 | {_delta_cell(coverage, base, 'coverage')} |
| Freshness | {freshness}/25 | {_delta_cell(freshness, base, 'freshness')} |
| Structure | {structure}/25 | {_delta_cell(structure, base, 'structure')} |

<details>
<summary>What is the Skilgen Score?</summary>

The Skilgen Score measures how well your codebase
is documented for AI coding agents.

- **Groundedness** — skills backed by real code evidence
- **Coverage** — % of codebase mapped to skill domains
- **Freshness** — skills up to date with latest changes
- **Structure** — skill files well-formed and complete

[View full report on Skillayer →](https://app.skillayer.com)

</details>

<sub>Powered by [Skillayer](https://skillayer.com) · Run ID: `{run_id[:8]}`</sub>"""


async def find_existing_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
) -> int | None:
    """Find an existing Skillayer PR comment and return its comment ID."""
    token = get_installation_token(installation_id)
    url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10.0,
        )
        if not _response_ok(response):
            return None
        for comment in response.json():
            body = comment.get("body", "")
            if "Skilgen Score" in body and "Powered by" in body and "skillayer.com" in body:
                return int(comment["id"])
    return None


async def update_pr_comment(
    full_name: str,
    comment_id: int,
    installation_id: int,
    body: str,
) -> bool:
    """Update an existing Skillayer PR comment."""
    token = get_installation_token(installation_id)
    url = f"https://api.github.com/repos/{full_name}/issues/comments/{comment_id}"
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            url,
            json={"body": body},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10.0,
        )
        print(f"PR comment updated: {response.status_code}")
        return response.status_code == 200


async def post_pr_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
    run_id: str,
    current_score: ScoreDict,
    base_score: ScoreDict | None,
) -> bool:
    """Create or update the Skillayer score comment on a GitHub pull request."""
    token = get_installation_token(installation_id)
    body = build_comment(current_score, base_score, run_id)

    existing_id = await find_existing_comment(full_name, pr_number, installation_id)
    if existing_id is not None:
        return await update_pr_comment(full_name, existing_id, installation_id, body)

    url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"body": body},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10.0,
        )
        print(f"PR comment posted: {response.status_code}")
        return response.status_code == 201
