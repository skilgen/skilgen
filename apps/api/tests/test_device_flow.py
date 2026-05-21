from __future__ import annotations

import asyncio
from types import SimpleNamespace

from apps.api.api.routes import device_flow
from packages.db.models import DeviceAuthorization, Org


class Result:
    def __init__(self, value=None) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value


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
    code = asyncio.run(device_flow.create_device_code(device_flow.DeviceCodeRequest(repo_id="repo_1"), db=db))

    approved = asyncio.run(device_flow.approve_device_code(device_flow.DeviceApproveRequest(user_code=code.user_code), db=db, current_org_id="org_1"))
    token = asyncio.run(device_flow.poll_device_token(device_flow.DeviceTokenRequest(device_code=code.device_code), db=db))

    assert approved == {"ok": True, "status": "approved", "org_id": "org_1"}
    assert token.error is None
    assert token.access_token == "sk-existing"
    assert token.org_id == "org_1"
    assert token.repo_id == "repo_1"
    assert db.authorizations[0].status == "approved"
