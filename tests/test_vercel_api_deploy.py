from __future__ import annotations

import json
from pathlib import Path

from scripts.deploy_api import api_project_link, deploy_command, load_project_link


ROOT = Path(__file__).resolve().parents[1]


def test_vercel_api_config_targets_python_api_entrypoint() -> None:
    config = json.loads((ROOT / "vercel.api.json").read_text(encoding="utf-8"))

    assert config["builds"][0]["src"] == "apps/api/api/index.py"
    assert config["builds"][0]["use"] == "@vercel/python"
    assert config["routes"][0]["dest"] == "apps/api/api/index.py"


def test_deploy_command_uses_local_api_config_without_turbo_build() -> None:
    command = deploy_command(production=True, config_path=Path("vercel.api.json"))

    assert command == ["vercel", "deploy", "--local-config", "vercel.api.json", "--prod"]
    assert "turbo" not in " ".join(command)
    assert "npm" not in " ".join(command)


def test_api_project_link_restores_previous_root_link(tmp_path: Path) -> None:
    root_link = tmp_path / ".vercel" / "project.json"
    api_link = tmp_path / "apps" / "api" / ".vercel" / "project.json"
    original = {"projectId": "web", "orgId": "team", "projectName": "skillayer-web"}
    api = {"projectId": "api", "orgId": "team", "projectName": "skillayer-api"}
    root_link.parent.mkdir(parents=True)
    api_link.parent.mkdir(parents=True)
    root_link.write_text(json.dumps(original), encoding="utf-8")
    api_link.write_text(json.dumps(api), encoding="utf-8")

    with api_project_link(root_link=root_link, api_link=api_link):
        assert load_project_link(root_link)["projectName"] == "skillayer-api"

    assert load_project_link(root_link)["projectName"] == "skillayer-web"
