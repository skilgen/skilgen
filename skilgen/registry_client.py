"""Client helpers for publishing and importing Skillayer registry skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class RegistryClientError(RuntimeError):
    """Raised when the Skillayer registry API request fails."""


def _api_key() -> str:
    """Load the Skillayer API key from the environment."""
    api_key = os.getenv("SKILLAYER_API_KEY", "").strip()
    if not api_key:
        raise RegistryClientError("SKILLAYER_API_KEY is required")
    return api_key


def _api_url(api_url: str) -> str:
    """Normalize the registry API base URL."""
    normalized = api_url.strip().rstrip("/")
    if not normalized:
        raise RegistryClientError("Skillayer API URL is required")
    return normalized


def _request_json(api_url: str, path: str, body: dict[str, object]) -> dict[str, object]:
    """Send an authenticated JSON POST to the Skillayer API."""
    payload = json.dumps(body).encode("utf-8")
    request = Request(
        f"{_api_url(api_url)}{path}",
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=10) as response:
            return cast(dict[str, object], json.loads(response.read().decode("utf-8")))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RegistryClientError(f"Skillayer API returned {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RegistryClientError(f"Unable to reach Skillayer API: {exc.reason}") from exc


def publish_skill(
    *,
    api_url: str,
    skill_file: Path,
    skill_id: str,
    name: str,
    description: str,
    tags: list[str],
    is_public: bool,
) -> dict[str, object]:
    """Validate and publish a local skill file through the Skillayer registry API."""
    if not skill_file.exists() or not skill_file.is_file():
        raise RegistryClientError(f"Skill file does not exist: {skill_file}")
    if skill_file.name != "SKILL.md":
        raise RegistryClientError("Registry publish expects a SKILL.md file")
    if not skill_file.read_text(encoding="utf-8").strip():
        raise RegistryClientError("Skill file is empty")
    return _request_json(
        api_url,
        "/registry/publish",
        {
            "skill_id": skill_id,
            "name": name,
            "description": description,
            "tags": tags,
            "is_public": is_public,
        },
    )


def import_skill(*, api_url: str, registry_id: str, target_dir: Path) -> dict[str, object]:
    """Download a registry skill and write it as SKILL.md in an existing directory."""
    if not target_dir.exists() or not target_dir.is_dir():
        raise RegistryClientError(f"Target directory does not exist: {target_dir}")
    response = _request_json(api_url, f"/registry/{registry_id}/import", {})
    content = response.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RegistryClientError("Registry response did not include skill content")
    output_path = target_dir / "SKILL.md"
    output_path.write_text(content, encoding="utf-8")
    enriched = dict(response)
    enriched["path"] = str(output_path)
    return enriched
