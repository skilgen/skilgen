from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import time

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
    url = f"https://x-access-token:{token}@github.com/{full_name}.git"
    subprocess.run(
        ["git", "clone", "--depth", "1", url, str(target_dir)],
        check=True,
        timeout=120,
        capture_output=True,
        text=True,
    )
