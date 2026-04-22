from __future__ import annotations

import httpx


def get_installation_token(installation_id: int) -> str:
    """Fetch a GitHub installation token through the API GitHub helper."""
    from apps.api.api.github import get_installation_token as fetch_installation_token

    return fetch_installation_token(installation_id)


def _response_ok(response: httpx.Response) -> bool:
    """Return whether an HTTPX response completed successfully."""
    return bool(getattr(response, "ok", response.is_success))


async def find_existing_comment(
    full_name: str,
    pr_number: int,
    installation_id: int,
) -> int | None:
    """Find an existing Skillayer PR comment. Returns comment_id or None."""
    token = get_installation_token(installation_id)
    url = f"https://api.github.com/repos/{full_name}/issues/{pr_number}/comments"
    async with httpx.AsyncClient() as client:
        res = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10.0,
        )
        if not _response_ok(res):
            return None
        for comment in res.json():
            body = comment.get("body", "")
            if (
                "Skilgen Score" in body
                and "Powered by" in body
                and "skillayer.com" in body
            ):
                return comment["id"]
    return None


async def update_pr_comment(
    full_name: str,
    comment_id: int,
    installation_id: int,
    body: str,
) -> bool:
    """Update an existing PR comment."""
    token = get_installation_token(installation_id)
    url = f"https://api.github.com/repos/{full_name}/issues/comments/{comment_id}"
    async with httpx.AsyncClient() as client:
        res = await client.patch(
            url,
            json={"body": body},
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=10.0,
        )
        print(f"PR comment updated: {res.status_code}")
        return res.status_code == 200
