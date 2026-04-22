from __future__ import annotations

from typing import Any

import httpx
import pytest

from apps.api.api import pr_comment


class FakeAsyncClient:
    response: httpx.Response
    requests: list[dict[str, Any]] = []

    async def __aenter__(self) -> FakeAsyncClient:
        return self

    async def __aexit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        self.requests.append({"method": "GET", "url": url, **kwargs})
        return self.response

    async def patch(self, url: str, **kwargs: Any) -> httpx.Response:
        self.requests.append({"method": "PATCH", "url": url, **kwargs})
        return self.response


@pytest.fixture(autouse=True)
def fake_github_client(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeAsyncClient.requests = []
    monkeypatch.setattr(
        pr_comment,
        "get_installation_token",
        lambda installation_id: "token",
    )
    monkeypatch.setattr(pr_comment.httpx, "AsyncClient", FakeAsyncClient)


@pytest.mark.anyio
async def test_find_existing_comment_returns_none_when_no_skillayer_comment_exists() -> None:
    FakeAsyncClient.response = httpx.Response(
        200,
        json=[
            {"id": 101, "body": "A regular review comment"},
            {"id": 102, "body": "Skilgen Score without the footer marker"},
        ],
    )

    comment_id = await pr_comment.find_existing_comment("owner/repo", 7, 123)

    assert comment_id is None
    assert FakeAsyncClient.requests == [
        {
            "method": "GET",
            "url": "https://api.github.com/repos/owner/repo/issues/7/comments",
            "headers": {
                "Authorization": "Bearer token",
                "Accept": "application/vnd.github+json",
            },
            "timeout": 10.0,
        }
    ]


@pytest.mark.anyio
async def test_find_existing_comment_returns_id_when_skillayer_comment_found() -> None:
    FakeAsyncClient.response = httpx.Response(
        200,
        json=[
            {"id": 201, "body": "Unrelated"},
            {
                "id": 202,
                "body": "## Skilgen Score: 74/100\n\n<sub>Powered by Skillayer skillayer.com</sub>",
            },
        ],
    )

    comment_id = await pr_comment.find_existing_comment("owner/repo", 8, 456)

    assert comment_id == 202


@pytest.mark.anyio
async def test_update_pr_comment_makes_patch_request() -> None:
    FakeAsyncClient.response = httpx.Response(200, json={"id": 303})

    updated = await pr_comment.update_pr_comment("owner/repo", 303, 789, "updated body")

    assert updated is True
    assert FakeAsyncClient.requests == [
        {
            "method": "PATCH",
            "url": "https://api.github.com/repos/owner/repo/issues/comments/303",
            "json": {"body": "updated body"},
            "headers": {
                "Authorization": "Bearer token",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            "timeout": 10.0,
        }
    ]
