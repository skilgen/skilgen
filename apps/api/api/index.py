from __future__ import annotations

import logging
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.db.config import settings
from apps.api.api.routes import health, me, orgs, repos, skills, stripe, webhook, worker


LOGGER = logging.getLogger("skillayer.api")


def _configure_logging() -> None:
    logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)


def _run_migrations() -> None:
    try:
        from alembic import command
        from alembic.config import Config

        if not settings.DATABASE_URL:
            print("DATABASE_URL is not configured, skipping migrations")
            return

        local_root = Path(__file__).parent.parent
        root = next(
            (
                candidate
                for candidate in (local_root, local_root / "apps" / "api")
                if (candidate / "alembic.ini").exists()
            ),
            local_root,
        )
        alembic_ini = root / "alembic.ini"
        alembic_dir = root / "alembic"

        if not alembic_ini.exists():
            print(f"alembic.ini not found at {alembic_ini}, skipping migrations")
            return

        alembic_cfg = Config(str(alembic_ini))
        alembic_cfg.set_main_option("script_location", str(alembic_dir))
        command.upgrade(alembic_cfg, "head")
        print("Migrations completed successfully")
    except Exception as exc:
        print(f"Migration error: {exc}")
        # Don't crash the app if migrations fail. Tables may already exist.
        return


app = FastAPI(
    title="Skillayer API",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://skillayer.com", "https://app.skillayer.com", "http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        LOGGER.exception(
            "request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request_id})
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    LOGGER.info(
        "request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    response.headers["x-request-id"] = request_id
    return response


@app.on_event("startup")
async def startup() -> None:
    _configure_logging()
    try:
        _run_migrations()
    except Exception as exc:
        print(f"Migration warning: {exc}")


app.include_router(health.router)
app.include_router(webhook.router)
app.include_router(worker.router)
app.include_router(me.router)
app.include_router(orgs.router)
app.include_router(repos.router)
app.include_router(skills.router)
app.include_router(stripe.router)
