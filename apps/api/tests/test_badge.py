from __future__ import annotations

import asyncio
from types import SimpleNamespace

from apps.api.api.routes import repos


class Db:
    def __init__(self, repo=None) -> None:
        self.repo = repo

    async def get(self, model, item_id: str):
        return self.repo


def _body(response) -> str:
    return response.body.decode()


def test_badge_svg_returns_200(monkeypatch) -> None:
    async def score(db, repo_id: str) -> int:
        return 73

    monkeypatch.setattr(repos, "_latest_repo_score_total", score)

    response = asyncio.run(repos.get_repo_certification_badge("repo_1", Db(SimpleNamespace(id="repo_1"))))

    assert response.status_code == 200
    assert response.media_type == "image/svg+xml"
    assert "<svg" in _body(response)
    assert "AI Ready &#183; 73/100" in _body(response)


def test_badge_svg_not_found() -> None:
    response = asyncio.run(repos.get_repo_certification_badge("missing", Db(None)))

    assert response.status_code == 200
    assert response.media_type == "image/svg+xml"
    assert "not configured" in _body(response)
    assert "#6b7280" in _body(response)


def test_badge_color_green(monkeypatch) -> None:
    async def score(db, repo_id: str) -> int:
        return 85

    monkeypatch.setattr(repos, "_latest_repo_score_total", score)

    response = asyncio.run(repos.get_repo_certification_badge("repo_1", Db(SimpleNamespace(id="repo_1"))))

    assert "#16a34a" in _body(response)


def test_badge_color_red(monkeypatch) -> None:
    async def score(db, repo_id: str) -> int:
        return 45

    monkeypatch.setattr(repos, "_latest_repo_score_total", score)

    response = asyncio.run(repos.get_repo_certification_badge("repo_1", Db(SimpleNamespace(id="repo_1"))))

    assert "#dc2626" in _body(response)
