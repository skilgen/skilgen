from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from apps.api.api.routes import device_flow
from packages.db.models import DeviceAuthorization, Org


class Result:
    def __init__(self, value=None) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value

    def scalars(self):
        return self

    def all(self):
        if self.value is None:
            return []
        if isinstance(self.value, list):
            return self.value
        return [self.value]


class Db:
    def __init__(self, org: Org | None = None) -> None:
        self.org = org
        self.authorizations: list[DeviceAuthorization] = []
        self.committed = False

    def add(self, item):
        if isinstance(item, DeviceAuthorization):
            self.authorizations.append(item)

    async def execute(self, stmt):
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        if "WHERE device_authorizations.client_ip =" in compiled:
            ip = compiled.split("device_authorizations.client_ip = '", 1)[-1].split("'", 1)[0]
            return Result(
                [
                    authorization
                    for authorization in self.authorizations
                    if authorization.client_ip == ip
                    and authorization.status == "pending"
                    and authorization.expires_at > datetime.now(UTC).replace(tzinfo=None)
                ]
            )
        for authorization in self.authorizations:
            if authorization.user_code and f"'{authorization.user_code}'" in compiled:
                return Result(authorization)
            if authorization.device_code and f"'{authorization.device_code}'" in compiled:
                return Result(authorization)
        return Result(None)

    async def get(self, model, row_id):
        assert model is Org
        return self.org if self.org and self.org.id == row_id else None

    async def commit(self):
        self.committed = True


def test_device_flow_returns_pending_until_browser_approval() -> None:
    db = Db()
    response = asyncio.run(
        device_flow.create_device_code(
            device_flow.DeviceCodeRequest(project_root="/repo", repo_full_name="acme/api"),
            request=SimpleNamespace(headers={}, client=SimpleNamespace(host="203.0.113.10")),
            db=db,
        )
    )

    assert response.user_code
    assert response.verification_uri_complete.endswith(response.user_code)
    pending = asyncio.run(device_flow.poll_device_token(device_flow.DeviceTokenRequest(device_code=response.device_code), db=db))
    assert pending.error == "authorization_pending"
    assert pending.interval == device_flow.DEVICE_POLL_INTERVAL_SECONDS


def test_device_flow_approval_returns_org_api_key() -> None:
    org = Org(id="org_1", github_org_id=1, login="acme", name="Acme", api_key="sk-existing")
    db = Db(org)
    code = asyncio.run(
        device_flow.create_device_code(
            device_flow.DeviceCodeRequest(repo_id="repo_1"),
            request=SimpleNamespace(headers={}, client=SimpleNamespace(host="203.0.113.20")),
            db=db,
        )
    )

    approved = asyncio.run(device_flow.approve_device_code(device_flow.DeviceApproveRequest(user_code=code.user_code), db=db, current_org_id="org_1"))
    token = asyncio.run(device_flow.poll_device_token(device_flow.DeviceTokenRequest(device_code=code.device_code), db=db))

    assert approved == {"ok": True, "status": "approved", "org_id": "org_1"}
    assert token.error is None
    assert token.access_token == "sk-existing"
    assert token.org_id == "org_1"
    assert token.repo_id == "repo_1"
    assert db.authorizations[0].status == "approved"


def test_device_flow_rate_limits_outstanding_codes_per_ip() -> None:
    db = Db()
    now = datetime.now(UTC).replace(tzinfo=None)
    for index in range(device_flow.DEVICE_CODE_IP_LIMIT):
        db.authorizations.append(
            DeviceAuthorization(
                device_code=f"device-{index}",
                user_code=f"USER-{index}",
                client_ip="203.0.113.30",
                status="pending",
                created_at=now - timedelta(minutes=1),
                expires_at=now + timedelta(minutes=10),
            )
        )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            device_flow.create_device_code(
                device_flow.DeviceCodeRequest(repo_id="repo_1"),
                request=SimpleNamespace(headers={}, client=SimpleNamespace(host="203.0.113.30")),
                db=db,
            )
        )

    assert exc.value.status_code == 429
    assert exc.value.detail["error"] == "slow_down"
