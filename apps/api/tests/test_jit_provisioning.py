from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest
from fastapi import HTTPException

from apps.api.api.services import jit_provisioning
from packages.db.models import Org, Role, RoleBinding, User
from packages.db.models.base import new_uuid


class Result:
    def __init__(self, rows: list[object]) -> None:
        self._rows = rows

    def scalar_one_or_none(self) -> object | None:
        if not self._rows:
            return None
        return self._rows[0]


@dataclass
class FakeAsyncSession:
    orgs: list[Org] = field(default_factory=list)
    users: list[User] = field(default_factory=list)
    roles: list[Role] = field(default_factory=list)
    bindings: list[RoleBinding] = field(default_factory=list)
    added: list[object] = field(default_factory=list)

    def add(self, item: object) -> None:
        self.added.append(item)

    async def flush(self) -> None:
        for item in list(self.added):
            if hasattr(item, "id") and (getattr(item, "id", None) is None):
                setattr(item, "id", new_uuid())
            if isinstance(item, Org):
                self.orgs.append(item)
            elif isinstance(item, User):
                self.users.append(item)
            elif isinstance(item, Role):
                self.roles.append(item)
            elif isinstance(item, RoleBinding):
                self.bindings.append(item)
        self.added.clear()

    async def get(self, model: object, row_id: str) -> object | None:
        if model is Org:
            return next((org for org in self.orgs if str(org.id) == str(row_id)), None)
        return None

    async def execute(self, stmt: Any) -> Result:
        compiled = str(stmt.compile(compile_kwargs={"literal_binds": True}))

        def extract_equals(token: str) -> str | None:
            if token not in compiled:
                return None
            tail = compiled.split(token, 1)[-1].lstrip()
            if not tail.startswith("'"):
                return None
            tail = tail[1:]
            return tail.split("'", 1)[0]

        if "FROM users" in compiled:
            email = extract_equals("users.email = ")
            if email is not None:
                return Result([user for user in self.users if user.email == email])
            return Result(list(self.users))

        if "FROM orgs" in compiled:
            login = extract_equals("orgs.login = ")
            if login is not None:
                return Result([org for org in self.orgs if org.login == login])
            org_id = extract_equals("orgs.id = ")
            if org_id is not None:
                return Result([org for org in self.orgs if str(org.id) == org_id])
            return Result(list(self.orgs))

        if "FROM roles" in compiled:
            rows = list(self.roles)
            org_id = extract_equals("roles.org_id = ")
            if org_id is not None:
                rows = [role for role in rows if str(role.org_id) == org_id]
            name = extract_equals("roles.name = ")
            if name is not None:
                rows = [role for role in rows if role.name == name]
            return Result(rows)

        if "FROM role_bindings" in compiled:
            rows = list(self.bindings)
            for field_name in ("org_id", "role_id", "principal_id", "principal_type"):
                value = extract_equals(f"role_bindings.{field_name} = ")
                if value is not None:
                    rows = [binding for binding in rows if str(getattr(binding, field_name)) == value]
            # ensure scalar_one_or_none returns something truthy when a row exists
            return Result([binding.id for binding in rows if getattr(binding, "id", None)])

        return Result([])


@pytest.fixture(autouse=True)
def _disable_audit_emit(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _noop(*_args: Any, **_kwargs: Any) -> None:  # noqa: ANN401
        return None

    monkeypatch.setattr(jit_provisioning.audit, "emit", _noop)


def test_jit_provisioning_creates_org_and_owner_user() -> None:
    db = FakeAsyncSession()
    org, user, created_org = asyncio.run(jit_provisioning.ensure_from_login(db, email="dev@acme.test", name="Dev", source="magic_link"))

    assert created_org is True
    assert org.login == "acme.test"
    assert user.email == "dev@acme.test"
    assert user.role == "owner"


def test_jit_provisioning_reuses_existing_user() -> None:
    db = FakeAsyncSession()
    first_org, first_user, first_created = asyncio.run(
        jit_provisioning.ensure_from_login(db, email="dev@acme.test", name="Dev", source="magic_link")
    )
    second_org, second_user, second_created = asyncio.run(
        jit_provisioning.ensure_from_login(db, email="dev@acme.test", name="Dev", source="workos")
    )

    assert first_created is True
    assert second_created is False
    assert second_org.id == first_org.id
    assert second_user.id == first_user.id


def test_jit_provisioning_blocks_suspended_org() -> None:
    db = FakeAsyncSession()
    org, user, _ = asyncio.run(jit_provisioning.ensure_from_login(db, email="dev@acme.test", name="Dev", source="magic_link"))
    org.is_suspended = True

    with pytest.raises(HTTPException) as exc:
        asyncio.run(jit_provisioning.ensure_from_login(db, email=user.email, name="Dev", source="workos"))

    assert exc.value.status_code == 403


def test_jit_provisioning_respects_auto_join_domain_toggle() -> None:
    db = FakeAsyncSession()
    org, _, _ = asyncio.run(jit_provisioning.ensure_from_login(db, email="owner@acme.test", name="Owner", source="workos"))
    org.auto_join_domain = False

    joined_org, joined_user, created_org = asyncio.run(
        jit_provisioning.ensure_from_login(db, email="dev2@acme.test", name="Dev Two", source="workos")
    )

    assert created_org is True
    assert joined_org.id != org.id
    assert joined_user.role == "owner"


def test_jit_provisioning_never_auto_joins_personal_email_domains() -> None:
    db = FakeAsyncSession()
    first_org, _, first_created = asyncio.run(
        jit_provisioning.ensure_from_login(db, email="owner@gmail.com", name="Owner", source="magic_link")
    )
    second_org, second_user, second_created = asyncio.run(
        jit_provisioning.ensure_from_login(db, email="dev@gmail.com", name="Dev", source="magic_link")
    )

    assert first_created is True
    assert second_created is True
    assert first_org.id != second_org.id
    assert second_user.role == "owner"
