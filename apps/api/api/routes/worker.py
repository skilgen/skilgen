from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.analysis import run_analysis
from packages.db.config import settings
from packages.db.database import get_db


router = APIRouter(tags=["worker"])


class AnalysisJobPayload(BaseModel):
    run_id: str
    repo_id: str
    installation_id: int
    full_name: str
    ref: str | None = None
    pr_number: int | None = None
    base_score: dict[str, int] | None = None


def _verify_qstash_signature(signature: str | None) -> None:
    if settings.DEPLOYMENT_MODE != "saas":
        return
    if not settings.QSTASH_CURRENT_SIGNING_KEY and not settings.QSTASH_NEXT_SIGNING_KEY:
        raise HTTPException(status_code=500, detail="QStash signing keys are not configured")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing QStash signature")
    keys = [key for key in [settings.QSTASH_CURRENT_SIGNING_KEY, settings.QSTASH_NEXT_SIGNING_KEY] if key]
    for key in keys:
        try:
            jwt.decode(signature, key, algorithms=["HS256"], options={"verify_aud": False})
            return
        except JWTError:
            continue
    raise HTTPException(status_code=401, detail="Invalid QStash signature")


@router.post("/worker/analyse", name="worker_analyse")
async def worker_analyse(
    payload: AnalysisJobPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    upstash_signature: str | None = Header(default=None, alias="Upstash-Signature"),
) -> dict[str, Any]:
    _verify_qstash_signature(upstash_signature or request.headers.get("upstash-signature"))
    await run_analysis(
        payload.run_id,
        payload.repo_id,
        payload.installation_id,
        payload.full_name,
        db,
        pr_number=payload.pr_number,
        base_score=payload.base_score,
    )
    return {"ok": True, "run_id": payload.run_id}
