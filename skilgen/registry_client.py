"""Client helpers for publishing and importing Skillayer registry skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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


def _request_json(api_url: str, path: str, body: dict[str, object], method: str = "POST") -> dict[str, object]:
    """Send an authenticated JSON POST to the Skillayer API."""
    payload = json.dumps(body).encode("utf-8") if method != "GET" else None
    request = Request(
        f"{_api_url(api_url)}{path}",
        data=payload,
        method=method,
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


def registry_publish(*, api_url: str, org_id: str, skill_id: str, version: str, visibility: str, tags: list[str], description: str) -> dict[str, object]:
    return _request_json(api_url, f"/registry/orgs/{org_id}/publish", {"skill_id": skill_id, "version": version, "visibility": visibility, "tags": tags, "description": description, "compatible_runtimes": ["claude-code", "codex", "cursor", "copilot", "gemini-cli"]})


def registry_list(*, api_url: str, org_id: str, visibility: str | None = None) -> dict[str, object]:
    query = urlencode({"visibility": visibility} if visibility else {})
    return _request_json(api_url, f"/registry/orgs/{org_id}/entries{f'?{query}' if query else ''}", {}, method="GET")


def registry_install(*, api_url: str, org_id: str, entry_id: str, repo_id: str | None) -> dict[str, object]:
    return _request_json(api_url, f"/registry/orgs/{org_id}/entries/{entry_id}/install", {"repo_id": repo_id})


def registry_import_file(*, api_url: str, org_id: str, repo_id: str, name: str, file_path: Path) -> dict[str, object]:
    if not file_path.exists():
        raise RegistryClientError(f"Import file does not exist: {file_path}")
    return _request_json(api_url, f"/registry/orgs/{org_id}/import", {"content": file_path.read_text(encoding="utf-8"), "source": file_path.name, "repo_id": repo_id, "name": name})


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
