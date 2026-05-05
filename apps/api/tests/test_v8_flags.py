from __future__ import annotations

import asyncio
import importlib
from types import SimpleNamespace

from apps.api.api.index import app
from apps.api.api.v8 import flags


ia_v8_migration = importlib.import_module("apps.api.alembic.versions.20260504_0001_ia_v8_tenant_override")


class Db:
    def __init__(self, org: object | None) -> None:
        self.org = org
        self.get_count = 0

    async def get(self, model: object, key: str) -> object | None:
        self.get_count += 1
        return self.org


def _reset_cache() -> None:
    flags._request_cache.set({})  # pyright: ignore[reportPrivateUsage]


def test_v8_flags_router_is_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/v8/orgs/{org_id}/flags/ia-v8" in paths


def test_ia_v8_migration_upgrade_and_downgrade_are_safe_noops() -> None:
    ia_v8_migration.upgrade()
    ia_v8_migration.downgrade()


def test_is_v8_defaults_false_without_env_or_override(monkeypatch) -> None:
    monkeypatch.delenv("IA_V8_DEFAULT", raising=False)
    _reset_cache()

    value = asyncio.run(flags.is_v8("org_1", Db(SimpleNamespace(settings={}))))

    assert value is False


def test_is_v8_uses_env_default_when_override_missing(monkeypatch) -> None:
    monkeypatch.setenv("IA_V8_DEFAULT", "true")
    _reset_cache()

    value = asyncio.run(flags.is_v8("org_1", Db(SimpleNamespace(settings={}))))

    assert value is True


def test_is_v8_tenant_override_beats_env_default(monkeypatch) -> None:
    monkeypatch.setenv("IA_V8_DEFAULT", "false")
    _reset_cache()
    db = Db(SimpleNamespace(settings={"feature_flags": {"IA_V8": True}}))

    value = asyncio.run(flags.is_v8("org_1", db))

    assert value is True


def test_is_v8_false_tenant_override_beats_true_env_default(monkeypatch) -> None:
    monkeypatch.setenv("IA_V8_DEFAULT", "true")
    _reset_cache()
    db = Db(SimpleNamespace(settings={"feature_flags": {"IA_V8": False}}))

    value = asyncio.run(flags.is_v8("org_1", db))

    assert value is False


def test_is_v8_uses_request_cache(monkeypatch) -> None:
    monkeypatch.setenv("IA_V8_DEFAULT", "true")
    _reset_cache()
    db = Db(SimpleNamespace(settings={}))

    first = asyncio.run(flags.is_v8("org_1", db))
    second = asyncio.run(flags.is_v8("org_1", db))

    assert first is True
    assert second is True
    assert db.get_count == 1
