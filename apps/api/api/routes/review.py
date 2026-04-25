from __future__ import annotations

import re
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.auth import get_current_org_id
from packages.db.database import get_db
from packages.db.models import Repo, ReviewRun, Skill


router = APIRouter(prefix="/repos/{repo_id}/review", tags=["review"])


class ReviewBody(BaseModel):
    diff: str
    pr_url: str | None = None


def _patterns_from_content(content: str | None) -> list[str]:
    if not content:
        return []
    lines = content.splitlines()
    capture = False
    patterns: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## anti"):
            capture = True
            continue
        if capture and stripped.startswith("## "):
            break
        if capture and stripped.startswith("-"):
            cleaned = re.sub(r"^[-*]\s*", "", stripped)
            cleaned = re.sub(r"^\*\*(.*?)\*\*:\s*", r"\1 ", cleaned).strip()
            if cleaned:
                patterns.append(cleaned)
    return patterns[:8]


def _changed_lines(diff: str) -> list[dict[str, object]]:
    current_file = "unknown"
    line_number = 0
    rows: list[dict[str, object]] = []
    for raw in diff.splitlines():
        if raw.startswith("+++ b/"):
            current_file = raw.removeprefix("+++ b/")
            continue
        if raw.startswith("@@"):
            match = re.search(r"\+(\d+)", raw)
            line_number = int(match.group(1)) - 1 if match else line_number
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            line_number += 1
            rows.append({"file": current_file, "line": line_number, "text": raw[1:]})
        elif raw and not raw.startswith("-"):
            line_number += 1
    return rows


def _short_pattern(pattern: str) -> str:
    return pattern.split("—")[0].split("-")[0].strip().lower()


@router.post("")
async def review_diff(repo_id: str, body: ReviewBody, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    skills = (await db.execute(select(Skill).where(Skill.repo_id == repo_id))).scalars().all()
    lines = _changed_lines(body.diff)
    comments: list[dict[str, object]] = []
    for row in lines:
        text = str(row["text"]).lower()
        for skill in skills:
            patterns = list(skill.anti_patterns or []) + _patterns_from_content(skill.content)
            for pattern in patterns:
                needle = _short_pattern(str(pattern))
                if len(needle) >= 4 and needle in text:
                    comments.append(
                        {
                            "file": row["file"],
                            "line": row["line"],
                            "skill_name": skill.domain,
                            "anti_pattern": pattern,
                            "message": f"This line may violate the '{skill.domain}' skill anti-pattern: '{pattern}'",
                            "severity": "warning",
                        }
                    )
                    break
    db.add(ReviewRun(repo_id=repo_id, pr_url=body.pr_url, comment_count=len(comments), skills_checked=len(skills), lines_scanned=len(lines)))
    await db.commit()
    return {"comments": comments, "skills_checked": len(skills), "lines_scanned": len(lines), "repo_id": repo_id}


@router.get("/history")
async def review_history(repo_id: str, db: AsyncSession = Depends(get_db), current_org_id: str = Depends(get_current_org_id)) -> dict:
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if repo is None:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo.org_id != current_org_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    runs = (await db.execute(select(ReviewRun).where(ReviewRun.repo_id == repo_id).order_by(desc(ReviewRun.created_at)).limit(20))).scalars().all()
    return {
        "runs": [
            {
                "id": run.id,
                "repo_id": run.repo_id,
                "pr_url": run.pr_url,
                "comment_count": run.comment_count,
                "skills_checked": run.skills_checked,
                "lines_scanned": run.lines_scanned,
                "created_at": run.created_at.isoformat(),
            }
            for run in runs
        ]
    }
