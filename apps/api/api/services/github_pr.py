from __future__ import annotations

import base64

import httpx

from apps.api.api.github import get_installation_token
from packages.db.models import Repo


async def create_skill_pr(
    repo: Repo,
    skill_path: str,
    skill_content: str,
    branch_name: str,
    pr_title: str,
    pr_body: str,
) -> dict:
    """Create or update an idempotent GitHub PR for a skill file."""
    if not repo.github_installation_id:
        raise ValueError("github_app_not_installed")
    token = await get_installation_token(int(repo.github_installation_id))
    owner, name = repo.full_name.split("/", 1)
    base_url = f"https://api.github.com/repos/{owner}/{name}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    async with httpx.AsyncClient(timeout=30) as client:
        base_ref = await client.get(f"{base_url}/git/ref/heads/{repo.default_branch}", headers=headers)
        base_ref.raise_for_status()
        sha = base_ref.json()["object"]["sha"]
        branch_ref = await client.get(f"{base_url}/git/ref/heads/{branch_name}", headers=headers)
        if branch_ref.status_code == 404:
            create_ref = await client.post(f"{base_url}/git/refs", headers=headers, json={"ref": f"refs/heads/{branch_name}", "sha": sha})
            create_ref.raise_for_status()
        elif branch_ref.status_code >= 400:
            branch_ref.raise_for_status()
        existing = await client.get(f"{base_url}/contents/{skill_path}", headers=headers, params={"ref": branch_name})
        payload = {
            "message": pr_title,
            "content": base64.b64encode(skill_content.encode()).decode(),
            "branch": branch_name,
        }
        if existing.status_code == 200:
            payload["sha"] = existing.json().get("sha")
        put_file = await client.put(f"{base_url}/contents/{skill_path}", headers=headers, json=payload)
        put_file.raise_for_status()
        pulls = await client.get(f"{base_url}/pulls", headers=headers, params={"head": f"{owner}:{branch_name}", "state": "open"})
        pulls.raise_for_status()
        open_prs = pulls.json()
        if open_prs:
            pr = open_prs[0]
        else:
            response = await client.post(
                f"{base_url}/pulls",
                headers=headers,
                json={"title": pr_title, "head": branch_name, "base": repo.default_branch, "body": pr_body},
            )
            response.raise_for_status()
            pr = response.json()
    return {"pr_url": pr["html_url"], "pr_number": int(pr["number"]), "branch": branch_name}
