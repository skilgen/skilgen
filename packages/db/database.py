from __future__ import annotations

from collections.abc import AsyncGenerator
import ssl

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from packages.db.config import settings


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _database_url_and_connect_args() -> tuple[str, dict[str, object]]:
    database_url = settings.DATABASE_URL
    connect_args: dict[str, object] = {}
    if "neon.tech" in database_url or "ssl" in database_url:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connect_args = {"ssl": ssl_context}
        database_url = database_url.split("?")[0]
    return database_url, connect_args


def get_engine() -> AsyncEngine:
    global _engine
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    if _engine is None:
        database_url, connect_args = _database_url_and_connect_args()
        _engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            connect_args=connect_args,
        )
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False, class_=AsyncSession)
    return _sessionmaker


class _SessionLocalProxy:
    def __call__(self, *args: object, **kwargs: object) -> AsyncSession:
        return get_sessionmaker()(*args, **kwargs)


AsyncSessionLocal = _SessionLocalProxy()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
