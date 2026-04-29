from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import delete, desc, func, or_, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_admin_secret
from apps.api.api.services.commit_check import _severity_bucket
from packages.db.database import get_db
from packages.db.models import AgentSession, AnalysisRun, LoginEvent, Org, PRAttribution, PullRequest, Repo, Skill


router = APIRouter(prefix="/admin", tags=["admin"])


class SuspendOrgRequest(BaseModel):
    reason: str = ""


def _error(status_code: int, detail: str, code: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail, "code": code})


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _cursor_offset(cursor: str | None) -> int:
    if not cursor:
        return 0
    try:
        return max(0, int(cursor))
    except ValueError:
        return 0


def _next_cursor(offset: int, limit: int, total: int) -> str | None:
    next_offset = offset + limit
    return str(next_offset) if next_offset < total else None


def _count_severities(findings: list[dict[str, Any]] | None) -> tuple[int, int]:
    violations = 0
    warnings = 0
    for finding in findings or []:
        bucket = _severity_bucket(str(finding.get("severity") or ""))
        if bucket == "violation":
            violations += 1
        elif bucket == "warning":
            warnings += 1
    return violations, warnings


async def _repo_ids_for_org(db: AsyncSession, org_id: str) -> list[str]:
    rows = await db.execute(select(Repo.id).where(Repo.org_id == org_id))
    return [str(row) for row in rows.scalars().all()]


async def _org_summary(db: AsyncSession, org: Org) -> dict[str, Any]:
    repo_ids = await _repo_ids_for_org(db, org.id)
    last_session = (
        await db.execute(select(func.max(AgentSession.session_start)).where(AgentSession.org_id == org.id))
    ).scalar_one_or_none()
    last_run = None
    if repo_ids:
        last_run = (
            await db.execute(select(func.max(AnalysisRun.created_at)).where(AnalysisRun.repo_id.in_(repo_ids)))
        ).scalar_one_or_none()
    last_login = (
        await db.execute(select(func.max(LoginEvent.created_at)).where(LoginEvent.org_id == org.id))
    ).scalar_one_or_none()
    last_active = max([value for value in [last_session, last_run] if value is not None], default=None)
    skill_count = 0
    session_count = 0
    pr_count = 0
    analysis_run_count = 0
    if repo_ids:
        skill_count = int((await db.execute(select(func.count(Skill.id)).where(Skill.repo_id.in_(repo_ids)))).scalar_one() or 0)
        pr_count = int((await db.execute(select(func.count(PullRequest.id)).where(PullRequest.repo_id.in_(repo_ids)))).scalar_one() or 0)
        analysis_run_count = int((await db.execute(select(func.count(AnalysisRun.id)).where(AnalysisRun.repo_id.in_(repo_ids)))).scalar_one() or 0)
    session_count = int((await db.execute(select(func.count(AgentSession.id)).where(AgentSession.org_id == org.id))).scalar_one() or 0)
    user_count = int((await db.execute(select(func.count(func.distinct(LoginEvent.user_login))).where(LoginEvent.org_id == org.id))).scalar_one() or 0)
    login_count = int((await db.execute(select(func.count(LoginEvent.id)).where(LoginEvent.org_id == org.id))).scalar_one() or 0)
    return {
        "id": org.id,
        "name": org.name,
        "login": org.login,
        "plan": org.plan or "free",
        "is_suspended": bool(getattr(org, "is_suspended", False)),
        "suspended_at": _iso(getattr(org, "suspended_at", None)),
        "suspended_reason": getattr(org, "suspended_reason", None),
        "created_at": _iso(org.created_at),
        "last_active_at": _iso(last_active),
        "user_count": user_count,
        "login_count": login_count,
        "last_login_at": _iso(last_login),
        "skill_count": skill_count,
        "session_count": session_count,
        "pr_count": pr_count,
        "analysis_run_count": analysis_run_count,
        "repo_count": len(repo_ids),
        "api_key_hint": f"{org.api_key[:8]}..." if org.api_key else None,
    }


@router.post("/rollup-usage", response_model=None)
async def rollup_usage(
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, object] | JSONResponse:
    cutoff = datetime.utcnow() - timedelta(days=30)
    try:
        result = await db.execute(
            update(Skill)
            .where(Skill.load_count_30d > 0, Skill.last_loaded_at.is_not(None), Skill.last_loaded_at < cutoff)
            .values(load_count_30d=0)
        )
        await db.flush()
    except SQLAlchemyError:
        await db.rollback()
        return _error(400, "Unable to roll up usage counters", "ROLLUP_FAILED")
    return {"rolled_up": True, "reset_count": int(result.rowcount or 0)}


@router.get("/overview", response_model=None)
async def admin_overview(
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    now = datetime.utcnow()
    cutoff_7d = now - timedelta(days=7)
    cutoff_30d = now - timedelta(days=30)
    orgs = list((await db.execute(select(Org))).scalars().all())
    sessions = list((await db.execute(select(AgentSession))).scalars().all())
    runs = list((await db.execute(select(AnalysisRun))).scalars().all())
    prs = list((await db.execute(select(PullRequest))).scalars().all())
    logins = list((await db.execute(select(LoginEvent))).scalars().all())
    skills_total = int((await db.execute(select(func.count(Skill.id)))).scalar_one() or 0)
    repos_total = int((await db.execute(select(func.count(Repo.id)))).scalar_one() or 0)
    active_orgs = {session.org_id for session in sessions if session.session_start and session.session_start >= cutoff_30d}
    repo_org = dict((await db.execute(select(Repo.id, Repo.org_id))).all())
    active_orgs.update(repo_org.get(run.repo_id) for run in runs if run.created_at and run.created_at >= cutoff_30d and repo_org.get(run.repo_id))
    by_plan = Counter((org.plan or "free") for org in orgs)
    most_active = Counter(login.user_login for login in logins if login.user_login).most_common(5)
    return {
        "orgs": {
            "total": len(orgs),
            "active_30d": len(active_orgs),
            "suspended": sum(1 for org in orgs if getattr(org, "is_suspended", False)),
            "by_plan": {plan: int(by_plan.get(plan, 0)) for plan in ["free", "team", "business"]},
        },
        "users": {
            "total_unique": len({login.user_login for login in logins if login.user_login}),
            "logins_7d": sum(1 for login in logins if login.created_at and login.created_at >= cutoff_7d),
            "logins_30d": sum(1 for login in logins if login.created_at and login.created_at >= cutoff_30d),
            "most_active": [{"login": login, "count": count} for login, count in most_active],
        },
        "data": {
            "total_skills": skills_total,
            "total_agent_sessions": len(sessions),
            "total_prs": len(prs),
            "total_analysis_runs": len(runs),
            "total_repos": repos_total,
            "sessions_7d": sum(1 for session in sessions if session.session_start and session.session_start >= cutoff_7d),
            "sessions_30d": sum(1 for session in sessions if session.session_start and session.session_start >= cutoff_30d),
            "prs_7d": sum(1 for pr in prs if pr.opened_at and pr.opened_at >= cutoff_7d),
            "prs_30d": sum(1 for pr in prs if pr.opened_at and pr.opened_at >= cutoff_30d),
        },
        "generated_at": now.isoformat(),
    }


@router.get("/orgs", response_model=None)
async def admin_orgs(
    search: str | None = Query(default=None),
    plan: str | None = Query(default=None),
    is_suspended: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(Org)
    if search:
        needle = f"%{search.lower()}%"
        stmt = stmt.where(or_(func.lower(Org.name).like(needle), func.lower(Org.login).like(needle)))
    if plan:
        stmt = stmt.where(Org.plan == plan)
    if is_suspended is not None:
        stmt = stmt.where(Org.is_suspended == is_suspended)
    orgs = list((await db.execute(stmt)).scalars().all())
    summaries = [await _org_summary(db, org) for org in orgs]
    reverse = True
    key_map = {
        "created_at": lambda item: item.get("created_at") or "",
        "last_active": lambda item: item.get("last_active_at") or "",
        "skill_count": lambda item: item.get("skill_count") or 0,
        "session_count": lambda item: item.get("session_count") or 0,
    }
    summaries.sort(key=key_map.get(sort_by, key_map["created_at"]), reverse=reverse)
    offset = _cursor_offset(cursor)
    return {"orgs": summaries[offset : offset + limit], "next_cursor": _next_cursor(offset, limit, len(summaries)), "total": len(summaries)}


@router.get("/orgs/{org_id}", response_model=None)
async def admin_org_detail(
    org_id: str,
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    org = await db.get(Org, org_id)
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    repo_ids = await _repo_ids_for_org(db, org_id)
    summary = await _org_summary(db, org)
    repos = list((await db.execute(select(Repo).where(Repo.org_id == org_id).order_by(Repo.full_name))).scalars().all())
    skills = list((await db.execute(select(Skill).where(Skill.repo_id.in_(repo_ids))) if repo_ids else await db.execute(select(Skill).where(False))).scalars().all())
    sessions = list((await db.execute(select(AgentSession).where(AgentSession.org_id == org_id).order_by(desc(AgentSession.session_start)).limit(50))).scalars().all())
    logins = list((await db.execute(select(LoginEvent).where(LoginEvent.org_id == org_id).order_by(desc(LoginEvent.created_at)).limit(20))).scalars().all())
    attrs = []
    if repo_ids:
        attrs = list(
            (
                await db.execute(
                    select(PRAttribution)
                    .join(PullRequest, PullRequest.id == PRAttribution.pr_id)
                    .where(PullRequest.repo_id.in_(repo_ids), PullRequest.opened_at >= datetime.utcnow() - timedelta(days=30))
                )
            )
            .scalars()
            .all()
        )
    violations_30d = sum(_count_severities(attr.skills_violated)[0] for attr in attrs)
    risk_distribution = Counter(attr.risk_tier or "green" for attr in attrs)
    skill_counts = Counter((skill.skill_category or "codebase_architecture") for skill in skills)
    summary.update(
        {
            "repos": [
                {
                    "id": repo.id,
                    "full_name": repo.full_name,
                    "skill_count": sum(1 for skill in skills if skill.repo_id == repo.id),
                    "last_analysed_at": _iso(repo.last_analysed_at),
                    "is_active": bool(repo.is_active),
                }
                for repo in repos
            ],
            "recent_sessions": [
                {
                    "id": session.id,
                    "engineer_login": session.engineer_login,
                    "agent_runtime": session.agent_runtime,
                    "session_start": _iso(session.session_start),
                    "outcome": session.outcome,
                    "files_touched_count": len(session.files_touched or []),
                }
                for session in sessions[:10]
            ],
            "sessions": [
                {
                    "id": session.id,
                    "engineer_login": session.engineer_login,
                    "agent_runtime": session.agent_runtime,
                    "session_start": _iso(session.session_start),
                    "outcome": session.outcome,
                    "files_touched_count": len(session.files_touched or []),
                }
                for session in sessions
            ],
            "recent_logins": [
                {
                    "user_login": login.user_login,
                    "user_email": login.user_email,
                    "ip_address": login.ip_address,
                    "user_agent": login.user_agent,
                    "created_at": _iso(login.created_at),
                }
                for login in logins
            ],
            "skills_by_category": dict(skill_counts),
            "violations_30d": violations_30d,
            "risk_distribution": {tier: int(risk_distribution.get(tier, 0)) for tier in ["red", "yellow", "green"]},
        }
    )
    return summary


@router.get("/orgs/{org_id}/usage", response_model=None)
async def admin_org_usage(
    org_id: str,
    days: int = Query(default=30, ge=1, le=180),
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days - 1)
    repo_ids = await _repo_ids_for_org(db, org_id)
    series = {
        (start + timedelta(days=index)).isoformat(): {
            "date": (start + timedelta(days=index)).isoformat(),
            "agent_sessions": 0,
            "prs_opened": 0,
            "logins": 0,
            "analysis_runs": 0,
            "violations": 0,
        }
        for index in range(days)
    }
    sessions = (await db.execute(select(AgentSession).where(AgentSession.org_id == org_id, AgentSession.session_start >= datetime.combine(start, datetime.min.time())))).scalars().all()
    for session in sessions:
        key = session.session_start.date().isoformat()
        if key in series:
            series[key]["agent_sessions"] += 1
    logins = (await db.execute(select(LoginEvent).where(LoginEvent.org_id == org_id, LoginEvent.created_at >= datetime.combine(start, datetime.min.time())))).scalars().all()
    for login in logins:
        key = login.created_at.date().isoformat()
        if key in series:
            series[key]["logins"] += 1
    if repo_ids:
        runs = (await db.execute(select(AnalysisRun).where(AnalysisRun.repo_id.in_(repo_ids), AnalysisRun.created_at >= datetime.combine(start, datetime.min.time())))).scalars().all()
        prs = (await db.execute(select(PullRequest).where(PullRequest.repo_id.in_(repo_ids), PullRequest.opened_at >= datetime.combine(start, datetime.min.time())))).scalars().all()
        attrs = (
            await db.execute(
                select(PRAttribution, PullRequest.opened_at)
                .join(PullRequest, PullRequest.id == PRAttribution.pr_id)
                .where(PullRequest.repo_id.in_(repo_ids), PullRequest.opened_at >= datetime.combine(start, datetime.min.time()))
            )
        ).all()
        for run in runs:
            key = run.created_at.date().isoformat()
            if key in series:
                series[key]["analysis_runs"] += 1
        for pr in prs:
            if pr.opened_at:
                key = pr.opened_at.date().isoformat()
                if key in series:
                    series[key]["prs_opened"] += 1
        for attr, opened_at in attrs:
            if opened_at:
                key = opened_at.date().isoformat()
                if key in series:
                    series[key]["violations"] += _count_severities(attr.skills_violated)[0]
    return {"days": days, "series": list(series.values())}


@router.post("/orgs/{org_id}/suspend", response_model=None)
async def suspend_org(
    org_id: str,
    payload: SuspendOrgRequest,
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    org = await db.get(Org, org_id)
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    org.is_suspended = True
    org.suspended_at = datetime.utcnow()
    org.suspended_reason = payload.reason
    await db.commit()
    await db.refresh(org)
    return await _org_summary(db, org)


@router.post("/orgs/{org_id}/unsuspend", response_model=None)
async def unsuspend_org(
    org_id: str,
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any] | JSONResponse:
    org = await db.get(Org, org_id)
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    org.is_suspended = False
    org.suspended_at = None
    org.suspended_reason = None
    await db.commit()
    await db.refresh(org)
    return await _org_summary(db, org)


@router.delete("/orgs/{org_id}", response_model=None)
async def delete_org(
    org_id: str,
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str] | JSONResponse:
    org = await db.get(Org, org_id)
    if org is None:
        return _error(404, "Org not found", "ORG_NOT_FOUND")
    try:
        await db.delete(org)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        return _error(400, "Unable to delete org", "ORG_DELETE_FAILED")
    return {"ok": True, "deleted_org_id": org_id}


@router.get("/users", response_model=None)
async def admin_users(
    search: str | None = Query(default=None),
    org_id: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    login_stmt = select(LoginEvent)
    if org_id:
        login_stmt = login_stmt.where(LoginEvent.org_id == org_id)
    if search:
        needle = f"%{search.lower()}%"
        login_stmt = login_stmt.where(or_(func.lower(LoginEvent.user_login).like(needle), func.lower(LoginEvent.user_email).like(needle)))
    logins = list((await db.execute(login_stmt)).scalars().all())
    orgs = {org.id: org for org in (await db.execute(select(Org))).scalars().all()}
    sessions = list((await db.execute(select(AgentSession))).scalars().all())
    prs = list((await db.execute(select(PullRequest))).scalars().all())
    grouped: dict[str, dict[str, Any]] = {}
    for event in logins:
        if not event.user_login:
            continue
        item = grouped.setdefault(
            event.user_login,
            {
                "user_login": event.user_login,
                "user_email": event.user_email,
                "orgs": {},
                "login_count": 0,
                "last_login_at": None,
                "first_login_at": None,
                "sessions_count": 0,
                "prs_count": 0,
            },
        )
        if event.user_email:
            item["user_email"] = event.user_email
        if event.org_id and event.org_id in orgs:
            item["orgs"][event.org_id] = {"org_id": event.org_id, "org_name": orgs[event.org_id].name}
        item["login_count"] += 1
        if item["last_login_at"] is None or event.created_at > item["last_login_at"]:
            item["last_login_at"] = event.created_at
        if item["first_login_at"] is None or event.created_at < item["first_login_at"]:
            item["first_login_at"] = event.created_at
    for login, item in grouped.items():
        item["sessions_count"] = sum(1 for session in sessions if session.engineer_login == login)
        item["prs_count"] = sum(1 for pr in prs if pr.author_login == login)
    rows = [
        {
            **item,
            "orgs": list(item["orgs"].values()),
            "last_login_at": _iso(item["last_login_at"]),
            "first_login_at": _iso(item["first_login_at"]),
        }
        for item in grouped.values()
    ]
    rows.sort(key=lambda item: item.get("last_login_at") or "", reverse=True)
    offset = _cursor_offset(cursor)
    return {"users": rows[offset : offset + limit], "next_cursor": _next_cursor(offset, limit, len(rows)), "total": len(rows)}


@router.get("/logins", response_model=None)
async def admin_logins(
    org_id: str | None = Query(default=None),
    user_login: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(LoginEvent).order_by(desc(LoginEvent.created_at))
    if org_id:
        stmt = stmt.where(LoginEvent.org_id == org_id)
    if user_login:
        stmt = stmt.where(LoginEvent.user_login == user_login)
    if date_from:
        stmt = stmt.where(LoginEvent.created_at >= datetime.fromisoformat(date_from))
    if date_to:
        stmt = stmt.where(LoginEvent.created_at <= datetime.fromisoformat(date_to) + timedelta(days=1))
    rows = list((await db.execute(stmt)).scalars().all())
    orgs = {org.id: org.name for org in (await db.execute(select(Org))).scalars().all()}
    offset = _cursor_offset(cursor)
    page = rows[offset : offset + limit]
    return {
        "logins": [
            {
                "id": event.id,
                "org_id": event.org_id,
                "org_name": orgs.get(event.org_id or ""),
                "user_login": event.user_login,
                "user_email": event.user_email,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "created_at": _iso(event.created_at),
            }
            for event in page
        ],
        "next_cursor": _next_cursor(offset, limit, len(rows)),
        "total": len(rows),
    }


@router.get("/metrics/export", response_model=None)
async def export_admin_metrics(
    _: str = Depends(get_admin_secret),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    orgs = list((await db.execute(select(Org))).scalars().all())
    output = StringIO()
    fieldnames = [
        "id",
        "name",
        "plan",
        "is_suspended",
        "created_at",
        "last_active_at",
        "user_count",
        "login_count",
        "skill_count",
        "session_count",
        "pr_count",
        "analysis_run_count",
        "repo_count",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for org in orgs:
        row = await _org_summary(db, org)
        writer.writerow({key: row.get(key) for key in fieldnames})
    filename = f"skillayer-admin-{date.today().isoformat()}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
