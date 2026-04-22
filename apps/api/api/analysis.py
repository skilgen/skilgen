from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.github import clone_repo
from packages.db.models import AnalysisRun, Repo, ScoreHistory, Skill, SkillVersion


def _score_value(score: dict[str, Any], key: str) -> int:
    if key == "total":
        value = score.get("total", score.get("score"))
    else:
        value = score.get(key)
        if value is None and isinstance(score.get("subscores"), dict):
            value = score["subscores"].get(key)
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


def _skill_directory_for_node(skills_dir: Path, skill_path: str | None, fallback_name: str) -> Path:
    if skill_path:
        relative = Path(skill_path)
        parts = list(relative.parts)
        if parts and parts[0] == "skills":
            parts = parts[1:]
        if parts and parts[-1] == "SKILL.md":
            parts = parts[:-1]
        if parts:
            return skills_dir.joinpath(*parts)
    slug = fallback_name.lower().replace(" ", "-").replace("_", "-").strip("-") or "domain"
    return skills_dir / slug


def _apply_skill_scores(skill: Skill, skill_data: dict[str, Any]) -> None:
    skill.score_total = int(skill_data.get("score_total", 0) or 0)
    skill.score_groundedness = int(skill_data.get("score_groundedness", 0) or 0)
    skill.score_coverage = int(skill_data.get("score_coverage", 0) or 0)
    skill.score_freshness = int(skill_data.get("score_freshness", 0) or 0)
    skill.score_structure = int(skill_data.get("score_structure", 0) or 0)


async def save_skills(
    db: AsyncSession,
    repo_id: str,
    run_id: str,
    skill_files: list[dict[str, Any]],
) -> list[Skill]:
    saved: list[Skill] = []

    for skill_data in skill_files:
        domain = str(skill_data["domain"])
        content = str(skill_data["content"])
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        existing = await db.execute(
            select(Skill)
            .where(Skill.repo_id == repo_id, Skill.domain == domain)
            .order_by(Skill.created_at.desc())
            .limit(1)
        )
        skill = existing.scalar_one_or_none()

        if skill is None:
            skill = Skill(
                repo_id=repo_id,
                run_id=run_id,
                domain=domain,
                skill_path=str(skill_data["skill_path"]),
                content=content,
                content_hash=content_hash,
                is_stale=False,
            )
            _apply_skill_scores(skill, skill_data)
            db.add(skill)
            await db.flush()
            version_number = 1
        else:
            _apply_skill_scores(skill, skill_data)
            if skill.content_hash == content_hash:
                skill.run_id = run_id
                skill.is_stale = False
                saved.append(skill)
                continue

            await db.execute(
                update(SkillVersion)
                .where(SkillVersion.skill_id == skill.id, SkillVersion.is_latest.is_(True))
                .values(is_latest=False)
            )
            count_result = await db.execute(
                select(func.count(SkillVersion.id)).where(SkillVersion.skill_id == skill.id)
            )
            version_number = int(count_result.scalar() or 0) + 1
            skill.content = content
            skill.content_hash = content_hash
            skill.run_id = run_id
            skill.skill_path = str(skill_data["skill_path"])
            skill.is_stale = False

        version = SkillVersion(
            skill_id=skill.id,
            run_id=run_id,
            repo_id=repo_id,
            domain=domain,
            content=content,
            content_hash=content_hash,
            version_number=version_number,
            is_latest=True,
        )
        db.add(version)
        saved.append(skill)

    return saved


async def run_skilgen_analysis(project_root: Path) -> dict[str, Any]:
    try:
        from skilgen.agents.domain_graph_planner import build_domain_graph_native
        from skilgen.agents.evidence_graph import build_evidence_graph
        from skilgen.agents.language_parsers import parse_language_evidence  # noqa: F401
        from skilgen.core.requirements import load_project_context

        # Step 1: Build requirements context from the repo shape only.
        requirements = load_project_context(project_root, None)

        # Step 2: Build AST-backed evidence graph. This is intentionally LLM-free.
        build_evidence_graph(project_root, requirements)

        # Step 3: Infer domains from static code/file evidence.
        domain_graph = build_domain_graph_native(project_root, requirements)

        # Step 4: Generate basic skill files for each inferred domain.
        skills_dir = project_root / ".skilgen" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        skill_count = 0
        domains: list[str] = []
        for node in domain_graph.nodes:
            domain_dir = _skill_directory_for_node(skills_dir, node.skill_path, node.name)
            domain_dir.mkdir(parents=True, exist_ok=True)
            skill_file = domain_dir / "SKILL.md"
            skill_content = f"""# {node.name}

## Domain summary
{node.summary}

## Key patterns
{chr(10).join(f"- {pattern}" for pattern in (node.key_patterns or [])[:5])}

## Related files
{chr(10).join(f"- {path}" for path in (node.key_files or [])[:10])}
"""
            skill_file.write_text(skill_content, encoding="utf-8")
            skill_count += 1
            domains.append(domain_dir.relative_to(skills_dir).as_posix())

        # Step 5: Compute score after materializing skills.
        score = _compute_score(project_root)
        skill_files: list[dict[str, Any]] = []
        if skills_dir.exists():
            for skill_file in skills_dir.rglob("SKILL.md"):
                content = skill_file.read_text(encoding="utf-8", errors="ignore")
                skill_files.append(
                    {
                        "domain": skill_file.parent.name,
                        "skill_path": str(skill_file.relative_to(project_root)),
                        "content": content,
                        "score_total": _score_value(score, "total"),
                        "score_groundedness": _score_value(score, "groundedness"),
                        "score_coverage": _score_value(score, "coverage"),
                        "score_freshness": _score_value(score, "freshness"),
                        "score_structure": _score_value(score, "structure"),
                    }
                )

        return {
            "skill_count": skill_count,
            "domain_count": len(set(domains)),
            "domains": domains,
            "score": score,
            "skill_files": skill_files,
        }

    except Exception as exc:
        print(f"Analysis error: {exc}")
        print(traceback.format_exc())
        raise


async def update_run_status(db: AsyncSession, run_id: str, status: str) -> None:
    run = await db.get(AnalysisRun, run_id)
    if run is None:
        raise RuntimeError(f"AnalysisRun not found: {run_id}")
    run.status = status
    if status == "running":
        run.started_at = datetime.utcnow()


async def update_run_failed(db: AsyncSession, run_id: str, error_message: str) -> None:
    run = await db.get(AnalysisRun, run_id)
    if run is None:
        return
    run.status = "failed"
    run.error_message = error_message[:4000]
    run.completed_at = datetime.utcnow()


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
    run.completed_at = datetime.utcnow()


async def update_repo_analysed(db: AsyncSession, repo_id: str) -> None:
    repo = await db.get(Repo, repo_id)
    if repo is not None:
        repo.last_analysed_at = datetime.utcnow()


async def run_analysis(
    run_id: str,
    repo_id: str,
    installation_id: int,
    full_name: str,
    db: AsyncSession,
    pr_number: int | None = None,
    base_score: dict[str, Any] | None = None,
) -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix=f"skillayer_{run_id[:8]}_"))
    try:
        await update_run_status(db, run_id, "running")
        await db.commit()

        await clone_repo(full_name, installation_id, tmpdir)

        skilgen_path = Path("/app/skilgen")
        if skilgen_path.exists() and "/app" not in sys.path:
            sys.path.insert(0, "/app")

        analysis_result = await run_skilgen_analysis(tmpdir)
        score = dict(analysis_result.get("score") or {})
        skill_files = list(analysis_result.get("skill_files") or [])
        saved_skills = await save_skills(db, repo_id, run_id, skill_files)

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
            domain_count=int(analysis_result.get("domain_count") or len({entry["domain"] for entry in skill_files})),
            skill_count=int(analysis_result.get("skill_count") or len(saved_skills)),
        )
        await update_repo_analysed(db, repo_id)
        await db.commit()

        if pr_number is not None:
            from apps.api.api.pr_comment import post_pr_comment

            await post_pr_comment(
                full_name=full_name,
                pr_number=pr_number,
                installation_id=installation_id,
                run_id=run_id,
                current_score={
                    "total": _score_value(score, "total"),
                    "groundedness": _score_value(score, "groundedness"),
                    "coverage": _score_value(score, "coverage"),
                    "freshness": _score_value(score, "freshness"),
                    "structure": _score_value(score, "structure"),
                },
                base_score=base_score,
            )
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
