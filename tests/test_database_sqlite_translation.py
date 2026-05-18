from __future__ import annotations

from packages.db import database as db_module


def _resolve(url: str) -> tuple[str, dict[str, object]]:
    """Invoke the private URL translator with the given DATABASE_URL.

    Restores the original settings after the call so other tests are not affected.
    """
    settings = db_module.settings
    original_url = settings.DATABASE_URL
    original_unpooled = settings.DATABASE_URL_UNPOOLED
    settings.DATABASE_URL = url
    settings.DATABASE_URL_UNPOOLED = ""
    try:
        return db_module._database_url_and_connect_args()
    finally:
        settings.DATABASE_URL = original_url
        settings.DATABASE_URL_UNPOOLED = original_unpooled


def test_sqlite_url_translation() -> None:
    """Plain sqlite:// URLs should be rewritten to sqlite+aiosqlite:// for async use."""
    translated_url, _ = _resolve("sqlite:///./local.db")

    assert translated_url.startswith("sqlite+aiosqlite:")
    assert translated_url == "sqlite+aiosqlite:///./local.db"


def test_sqlite_url_translation_is_idempotent() -> None:
    """An already-aiosqlite URL should pass through unchanged."""
    translated_url, _ = _resolve("sqlite+aiosqlite:///./local.db")

    assert translated_url == "sqlite+aiosqlite:///./local.db"


def test_sqlite_thread_safety() -> None:
    """Async engine connect_args must include check_same_thread=False for sqlite URLs."""
    _, connect_args = _resolve("sqlite:///./local.db")

    assert connect_args.get("check_same_thread") is False


def test_postgres_url_translation_to_asyncpg() -> None:
    """postgres:// and postgresql:// URLs should be rewritten to use asyncpg."""
    translated_url, connect_args = _resolve("postgresql://user:pass@localhost:5432/db")

    assert translated_url.startswith("postgresql+asyncpg://")
    # No sqlite-specific thread arg for postgres URLs.
    assert "check_same_thread" not in connect_args
