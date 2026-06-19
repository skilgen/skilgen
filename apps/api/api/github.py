from __future__ import annotations

from datetime import datetime, timedelta, timezone
import io
from pathlib import Path
import time
import zipfile

import httpx
from jose import jwt

from packages.db.config import settings


_INSTALLATION_TOKENS: dict[int, tuple[str, float]] = {}


def _github_app_jwt() -> str:
    if not settings.GITHUB_APP_ID or not settings.GITHUB_APP_PRIVATE_KEY:
        raise RuntimeError("GitHub App credentials are not configured")
    now = datetime.now(timezone.utc)
    payload = {
        "iat": int((now - timedelta(seconds=60)).timestamp()),
        "exp": int((now + timedelta(minutes=9)).timestamp()),
        "iss": settings.GITHUB_APP_ID,
    }
    return jwt.encode(payload, settings.GITHUB_APP_PRIVATE_KEY, algorithm="RS256")


def get_installation_token(installation_id: int) -> str:
    cached = _INSTALLATION_TOKENS.get(installation_id)
    if cached is not None and cached[1] > time.time() + 60:
        return cached[0]
    token = _github_app_jwt()
    response = httpx.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    access_token = str(payload["token"])
    expires_at = datetime.fromisoformat(str(payload["expires_at"]).replace("Z", "+00:00")).timestamp()
    _INSTALLATION_TOKENS[installation_id] = (access_token, expires_at)
    return access_token


async def clone_repo(full_name: str, installation_id: int, target_dir: Path) -> None:
    token = get_installation_token(installation_id)

    # Vercel's Python runtime does not provide a git binary, so download the
    # repository archive directly from the GitHub API.
    url = f"https://api.github.com/repos/{full_name}/zipball"

    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        response = await client.get(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        response.raise_for_status()

    target_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        members = zf.namelist()
        if members:
            prefix = members[0].split("/")[0] + "/"
            for member in members:
                if member == prefix:
                    continue
                relative_name = member[len(prefix) :]
                if not relative_name:
                    continue
                target_path = target_dir / relative_name
                if member.endswith("/"):
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    target_path.write_bytes(zf.read(member))

    print(f"Downloaded and extracted {full_name} to {target_dir}")
