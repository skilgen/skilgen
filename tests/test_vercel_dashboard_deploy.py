from __future__ import annotations

import json
from pathlib import Path

from scripts.deploy_dashboard import dashboard_project_link, deploy_command, load_project_link


def test_dashboard_deploy_command_supports_production_flag() -> None:
    assert deploy_command(production=True) == ["vercel", "deploy", "--prod"]
    assert deploy_command(production=False) == ["vercel", "deploy"]


def test_dashboard_project_link_restores_root_link(tmp_path: Path) -> None:
    root_link = tmp_path / ".vercel" / "project.json"
    dashboard_link = tmp_path / "apps" / "dashboard" / ".vercel" / "project.json"
    root_link.parent.mkdir(parents=True)
    dashboard_link.parent.mkdir(parents=True)
    original = {"projectId": "web", "orgId": "team", "projectName": "skillayer-web"}
    dashboard = {"projectId": "dashboard", "orgId": "team", "projectName": "skillayer-dashboard"}
    root_link.write_text(json.dumps(original), encoding="utf-8")
    dashboard_link.write_text(json.dumps(dashboard), encoding="utf-8")

    with dashboard_project_link(root_link=root_link, dashboard_link=dashboard_link):
        assert load_project_link(root_link)["projectName"] == "skillayer-dashboard"

    assert load_project_link(root_link)["projectName"] == "skillayer-web"
