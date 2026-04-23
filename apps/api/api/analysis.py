from __future__ import annotations

from datetime import datetime
import hashlib
import logging
from pathlib import Path
import shutil
import sys
import tempfile
import traceback
from typing import Any

import httpx
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.api.github import clone_repo
from apps.api.api.notifications import build_stale_skill_message, post_slack_message
from packages.db.models import AnalysisRun, Dependency, Org, Repo, ScoreHistory, Skill, SkillVersion
from skilgen.core.dependency_risk import analyze_dependency_risks
from skilgen.core.models import DependencyFinding, DependencyRiskReport


LOGGER = logging.getLogger("skillayer.analysis")
OSV_ENDPOINT = "https://api.osv.dev/v1/querybatch"
OSV_ECOSYSTEMS = {
    "pip": "PyPI",
    "npm": "npm",
    "cargo": "crates.io",
    "go": "Go",
}


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


def _osv_version(version: str | None) -> str | None:
    """Return a concrete version string acceptable to OSV, when one is available."""
    if not version:
        return None
    cleaned = version.strip()
    if cleaned.startswith("=="):
        return cleaned[2:].strip()
    if cleaned.startswith("="):
        return cleaned[1:].strip()
    if cleaned[:1].isdigit() or cleaned.startswith("v"):
        return cleaned
    return None


def _osv_key(finding: DependencyFinding) -> str:
    """Return the map key used to attach OSV vulnerabilities to dependency findings."""
    return f"{finding.ecosystem}:{finding.name.lower()}"


def _osv_queries(findings: list[DependencyFinding]) -> list[tuple[dict[str, object], str]]:
    """Build deduplicated OSV batch queries from dependency findings."""
    queries: list[tuple[dict[str, object], str]] = []
    seen: set[tuple[str, str, str | None]] = set()
    for finding in findings:
        ecosystem = OSV_ECOSYSTEMS.get(finding.ecosystem)
        if ecosystem is None:
            continue
        version = _osv_version(finding.version)
        key = (ecosystem, finding.name, version)
        if key in seen:
            continue
        seen.add(key)
        query: dict[str, object] = {"package": {"name": finding.name, "ecosystem": ecosystem}}
        if version:
            query["version"] = version
        queries.append((query, _osv_key(finding)))
    return queries


async def _fetch_osv_vulnerabilities(findings: list[DependencyFinding]) -> dict[str, list[dict[str, object]]]:
    """Fetch OSV vulnerabilities with bounded retries and per-request timeouts."""
    queries = _osv_queries(findings)
    if not queries:
        return {}

    vulnerabilities: dict[str, list[dict[str, object]]] = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for start in range(0, len(queries), 50):
            chunk_pairs = queries[start:start + 50]
            chunk = [item[0] for item in chunk_pairs]
            chunk_keys = [item[1] for item in chunk_pairs]
            for attempt in range(3):
                try:
                    response = await client.post(OSV_ENDPOINT, json={"queries": chunk})
                    response.raise_for_status()
                    results = response.json().get("results", [])
                    if not isinstance(results, list):
                        break
                    for key, result in zip(chunk_keys, results):
                        vulns = result.get("vulns", []) if isinstance(result, dict) else []
                        if isinstance(vulns, list):
                            vulnerabilities.setdefault(key, []).extend(
                                item for item in vulns if isinstance(item, dict)
                            )
                    break
                except (httpx.TimeoutException, httpx.HTTPError, ValueError) as exc:
                    LOGGER.warning("OSV dependency lookup failed", extra={"attempt": attempt + 1, "error": str(exc)})
                    if attempt == 2:
                        break
    return vulnerabilities


async def save_dependencies(
    db: AsyncSession,
    repo_id: str,
    run_id: str,
    report: DependencyRiskReport,
) -> list[Dependency]:
    """Persist dependency risk findings for a completed analysis run."""
    await db.execute(delete(Dependency).where(Dependency.run_id == run_id))
    saved: list[Dependency] = []
    for finding in report.dependencies:
        dependency = Dependency(
            repo_id=repo_id,
            run_id=run_id,
            name=finding.name,
            version=finding.version,
            ecosystem=finding.ecosystem,
            risk_level=finding.risk_level,
            cves=finding.cves,
            latest_version=finding.latest_version,
            license=finding.license,
        )
        db.add(dependency)
        saved.append(dependency)
    await db.flush()
    return saved


async def analyze_and_store_dependencies(db: AsyncSession, repo_id: str, run_id: str, project_root: Path) -> DependencyRiskReport:
    """Run dependency risk analysis, enrich with OSV data, and persist findings."""
    base_report = analyze_dependency_risks(project_root)
    vulnerabilities = await _fetch_osv_vulnerabilities(base_report.dependencies)
    report = analyze_dependency_risks(project_root, vulnerabilities)
    await save_dependencies(db, repo_id, run_id, report)
    return report


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


def _stale_high_usage_skills(skills: list[Skill]) -> list[Skill]:
    """Return skills that are stale enough and loaded often enough to alert."""
    return [
        skill
        for skill in skills
        if int(skill.score_freshness or 0) < 20 and int(skill.load_count_30d or 0) > 5
    ]


async def _notify_stale_skills(db: AsyncSession, repo_id: str, repo_full_name: str, skills: list[Skill]) -> None:
    """Send a non-blocking Slack alert for stale high-usage skills when enabled."""
    try:
        stale_skills = _stale_high_usage_skills(skills)
        if not stale_skills:
            return
        result = await db.execute(select(Org).join(Repo, Repo.org_id == Org.id).where(Repo.id == repo_id))
        org = result.scalar_one_or_none()
        if org is None or not org.slack_webhook_url or not org.notify_on_stale:
            return
        await post_slack_message(org.slack_webhook_url, build_stale_skill_message(org, repo_full_name, stale_skills))
        LOGGER.info(
            "Slack stale skill alert sent",
            extra={"org_id": org.id, "repo_id": repo_id, "stale_skill_count": len(stale_skills)},
        )
    except Exception as exc:
        LOGGER.warning(
            "Slack stale skill alert failed",
            extra={"repo_id": repo_id, "error": str(exc)},
        )


async def _score_threshold_for_repo(db: AsyncSession, repo_id: str) -> int:
    """Fetch the org-level score threshold for a repository."""
    result = await db.execute(
        select(Org.score_threshold)
        .join(Repo, Repo.org_id == Org.id)
        .where(Repo.id == repo_id)
    )
    try:
        return int(result.scalar_one_or_none() or 60)
    except (TypeError, ValueError):
        return 60


async def run_analysis(
    run_id: str,
    repo_id: str,
    installation_id: int,
    full_name: str,
    db: AsyncSession,
    pr_number: int | None = None,
    base_score: dict[str, Any] | None = None,
    head_sha: str | None = None,
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
        await analyze_and_store_dependencies(db, repo_id, run_id, tmpdir)

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
        await _notify_stale_skills(db, repo_id, full_name, saved_skills)

        if pr_number is not None:
            from apps.api.api.pr_comment import post_pr_comment

            try:
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
                    domains=list(analysis_result.get("domains") or []),
                    head_sha=head_sha,
                    score_threshold=await _score_threshold_for_repo(db, repo_id),
                )
            except Exception as exc:
                LOGGER.warning("PR feedback publication failed", extra={"run_id": run_id, "error": str(exc)})
    except Exception as exc:
        await db.rollback()
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
