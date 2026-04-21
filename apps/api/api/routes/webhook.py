from __future__ import annotations

import hashlib
import hmac
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.analysis import run_analysis
from packages.db.config import settings
from packages.db.database import AsyncSessionLocal, get_db
from packages.db.models import AnalysisRun, Org, Repo


router = APIRouter(tags=["webhook"])


def _verify_github_signature(body: bytes, signature: str | None) -> None:
    if not settings.GITHUB_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="GITHUB_WEBHOOK_SECRET is not configured")
    if not signature or not signature.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")
    expected = hmac.new(settings.GITHUB_WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, f"sha256={expected}"):
        raise HTTPException(status_code=401, detail="Invalid GitHub signature")


def _account_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    installation = payload.get("installation") or {}
    account = installation.get("account") or payload.get("organization") or payload.get("sender") or {}
    return dict(account)


async def _upsert_org(db: AsyncSession, payload: dict[str, Any]) -> Org:
    account = _account_from_payload(payload)
    github_org_id = int(account.get("id") or 0)
    login = str(account.get("login") or f"github-{github_org_id}")
    result = await db.execute(select(Org).where(Org.github_org_id == github_org_id))
    org = result.scalar_one_or_none()
    if org is None:
        org = Org(github_org_id=github_org_id, login=login, name=str(account.get("name") or login))
        db.add(org)
        await db.flush()
    else:
        org.login = login
        org.name = str(account.get("name") or login)
    return org


async def _upsert_repo(db: AsyncSession, org: Org, repo_payload: dict[str, Any], installation_id: int | None) -> Repo:
    github_repo_id = int(repo_payload.get("id") or 0)
    result = await db.execute(select(Repo).where(Repo.github_repo_id == github_repo_id))
    repo = result.scalar_one_or_none()
    if repo is None:
        repo = Repo(
            org_id=org.id,
            github_repo_id=github_repo_id,
            github_installation_id=installation_id,
            full_name=str(repo_payload.get("full_name")),
            name=str(repo_payload.get("name")),
            default_branch=str(repo_payload.get("default_branch") or "main"),
            language=repo_payload.get("language"),
            is_active=True,
        )
        db.add(repo)
        await db.flush()
    else:
        repo.org_id = org.id
        repo.github_installation_id = installation_id or repo.github_installation_id
        repo.full_name = str(repo_payload.get("full_name"))
        repo.name = str(repo_payload.get("name"))
        repo.default_branch = str(repo_payload.get("default_branch") or repo.default_branch or "main")
        repo.language = repo_payload.get("language") or repo.language
        repo.is_active = True
    return repo


async def _queue_qstash(request: Request, payload: dict[str, Any]) -> None:
    if not settings.QSTASH_TOKEN:
        raise HTTPException(status_code=503, detail="QSTASH_TOKEN is not configured")
    worker_url = str(request.url_for("worker_analyse"))
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            f"https://qstash.upstash.io/v2/publish/{worker_url}",
            headers={"Authorization": f"Bearer {settings.QSTASH_TOKEN}", "Content-Type": "application/json"},
            json=payload,
        )
    response.raise_for_status()


async def _run_development_job(payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as db:
        await run_analysis(
            str(payload["run_id"]),
            str(payload["repo_id"]),
            int(payload["installation_id"]),
            str(payload["full_name"]),
            db,
        )


async def _queue_analysis(request: Request, background_tasks: BackgroundTasks, payload: dict[str, Any]) -> None:
    if settings.DEPLOYMENT_MODE == "saas":
        await _queue_qstash(request, payload)
    elif settings.DEPLOYMENT_MODE == "selfhosted":
        from apps.worker.worker import run_analysis_task

        run_analysis_task.delay(payload["run_id"], payload["repo_id"], payload["installation_id"], payload["full_name"])
    elif settings.DEPLOYMENT_MODE == "development":
        background_tasks.add_task(_run_development_job, payload)
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported DEPLOYMENT_MODE: {settings.DEPLOYMENT_MODE}")


@router.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
) -> dict[str, Any]:
    body = await request.body()
    _verify_github_signature(body, x_hub_signature_256)
    payload = await request.json()
    action = payload.get("action")

    if x_github_event == "installation":
        org = await _upsert_org(db, payload)
        installation_id = int((payload.get("installation") or {}).get("id") or 0) or None
        if action == "created":
            for repo_payload in payload.get("repositories", []):
                await _upsert_repo(db, org, repo_payload, installation_id)
        elif action == "deleted":
            await db.execute(update(Repo).where(Repo.org_id == org.id).values(is_active=False))
        return {"ok": True}

    if x_github_event == "installation_repositories":
        org = await _upsert_org(db, payload)
        installation_id = int((payload.get("installation") or {}).get("id") or 0) or None
        if action == "added":
            for repo_payload in payload.get("repositories_added", []):
                await _upsert_repo(db, org, repo_payload, installation_id)
        elif action == "removed":
            removed_ids = [int(repo.get("id")) for repo in payload.get("repositories_removed", []) if repo.get("id")]
            if removed_ids:
                await db.execute(update(Repo).where(Repo.github_repo_id.in_(removed_ids)).values(is_active=False))
        return {"ok": True}

    if x_github_event == "push":
        repo_payload = payload.get("repository") or {}
        full_name = str(repo_payload.get("full_name") or "")
        result = await db.execute(select(Repo).where(Repo.full_name == full_name))
        repo = result.scalar_one_or_none()
        if repo is None or not repo.is_active:
            return {"ignored": True}
        run = AnalysisRun(
            repo_id=repo.id,
            trigger="push",
            status="queued",
            commit_sha=payload.get("after"),
            branch=str(payload.get("ref") or "").replace("refs/heads/", ""),
            created_at=datetime.now(timezone.utc),
        )
        db.add(run)
        await db.flush()
        installation_id = int((payload.get("installation") or {}).get("id") or 0)
        repo.github_installation_id = installation_id or repo.github_installation_id
        await _queue_analysis(
            request,
            background_tasks,
            {
                "run_id": run.id,
                "repo_id": repo.id,
                "installation_id": installation_id,
                "full_name": repo.full_name,
            },
        )
        return {"queued": run.id}

    return {"ignored": True}
