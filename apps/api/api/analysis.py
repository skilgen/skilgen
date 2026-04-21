from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.github import clone_repo
from packages.db.models import AnalysisRun, Repo, ScoreHistory, Skill


def _score_value(score: dict[str, Any], key: str) -> int:
    value = score.get(key)
    if isinstance(value, dict):
        value = value.get("score")
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _compute_score(project_root: Path) -> dict[str, Any]:
    try:
        from skilgen.core.score import compute_score

        return dict(compute_score(project_root))
    except ImportError:
        from skilgen.core.score import compute_skillgen_score

        raw = dict(compute_skillgen_score(project_root))
        if "score" in raw and isinstance(raw["score"], dict):
            return dict(raw["score"])
        return raw


def _run_delivery(project_root: Path, output_dir: Path) -> list[Path]:
    try:
        from skilgen.delivery import deliver

        result = deliver(project_root=project_root, output_dir=output_dir, llm_enabled=False, silent=True)
        return list(result or [])
    except ImportError:
        from skilgen.delivery import run_delivery

        return list(run_delivery(None, project_root, targets=("docs", "skills"), skip_index=False))


async def update_run_status(db: AsyncSession, run_id: str, status: str) -> None:
    run = await db.get(AnalysisRun, run_id)
    if run is None:
        raise RuntimeError(f"AnalysisRun not found: {run_id}")
    run.status = status
    if status == "running":
        run.started_at = datetime.now(timezone.utc)


async def update_run_failed(db: AsyncSession, run_id: str, error_message: str) -> None:
    run = await db.get(AnalysisRun, run_id)
    if run is None:
        return
    run.status = "failed"
    run.error_message = error_message[:4000]
    run.completed_at = datetime.now(timezone.utc)


async def update_run_complete(
    db: AsyncSession,
    run_id: str,
    *,
    score: dict[str, Any],
    domain_count: int,
    skill_count: int,
) -> None:
    run = await db.get(AnalysisRun, run_id)
    if run is None:
        raise RuntimeError(f"AnalysisRun not found: {run_id}")
    run.status = "complete"
    run.score_total = _score_value(score, "total")
    run.score_groundedness = _score_value(score, "groundedness")
    run.score_coverage = _score_value(score, "coverage")
    run.score_freshness = _score_value(score, "freshness")
    run.score_structure = _score_value(score, "structure")
    run.domain_count = domain_count
    run.skill_count = skill_count
    run.completed_at = datetime.now(timezone.utc)


async def update_repo_analysed(db: AsyncSession, repo_id: str) -> None:
    repo = await db.get(Repo, repo_id)
    if repo is not None:
        repo.last_analysed_at = datetime.now(timezone.utc)


async def run_analysis(
    run_id: str,
    repo_id: str,
    installation_id: int,
    full_name: str,
    db: AsyncSession,
) -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix=f"skillayer_{run_id[:8]}_"))
    try:
        await update_run_status(db, run_id, "running")
        await db.commit()

        await clone_repo(full_name, installation_id, tmpdir)

        skilgen_path = Path("/app/skilgen")
        if skilgen_path.exists() and "/app" not in sys.path:
            sys.path.insert(0, "/app")

        skills_dir = tmpdir / ".skilgen" / "skills"
        _run_delivery(tmpdir, skills_dir)
        score = _compute_score(tmpdir)

        skill_records: list[dict[str, str]] = []
        if skills_dir.exists():
            for skill_file in skills_dir.rglob("SKILL.md"):
                skill_records.append(
                    {
                        "domain": skill_file.parent.name,
                        "skill_path": str(skill_file.relative_to(tmpdir)),
                    }
                )

        await db.execute(delete(Skill).where(Skill.run_id == run_id))
        for skill_data in skill_records:
            db.add(
                Skill(
                    repo_id=repo_id,
                    run_id=run_id,
                    domain=skill_data["domain"],
                    skill_path=skill_data["skill_path"],
                    score_total=_score_value(score, "total"),
                    score_groundedness=_score_value(score, "groundedness"),
                    score_coverage=_score_value(score, "coverage"),
                    score_freshness=_score_value(score, "freshness"),
                    score_structure=_score_value(score, "structure"),
                )
            )

        db.add(
            ScoreHistory(
                repo_id=repo_id,
                run_id=run_id,
                score_total=_score_value(score, "total"),
                score_groundedness=_score_value(score, "groundedness"),
                score_coverage=_score_value(score, "coverage"),
                score_freshness=_score_value(score, "freshness"),
                score_structure=_score_value(score, "structure"),
            )
        )

        await update_run_complete(
            db,
            run_id,
            score=score,
            domain_count=len({entry["domain"] for entry in skill_records}),
            skill_count=len(skill_records),
        )
        await update_repo_analysed(db, repo_id)
        await db.commit()
    except Exception as exc:
        await update_run_failed(db, run_id, str(exc))
        await db.commit()
        raise
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


async def run_analysis_for_id(run_id: str, db: AsyncSession) -> None:
    result = await db.execute(select(AnalysisRun, Repo).join(Repo, AnalysisRun.repo_id == Repo.id).where(AnalysisRun.id == run_id))
    row = result.first()
    if row is None:
        raise RuntimeError(f"AnalysisRun not found: {run_id}")
    run, repo = row
    installation_id = 0
    await run_analysis(run.id, repo.id, installation_id, repo.full_name, db)
