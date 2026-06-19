from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import AgentSession, Commit, PRAttribution, PullRequest


ERROR_SEVERITIES = {"error", "critical", "failure", "fatal"}
WARNING_SEVERITIES = {"warning", "warn", "suggestion"}


def risk_tier_for_score(score: int) -> str:
    if score >= 70:
        return "red"
    if score >= 30:
        return "yellow"
    return "green"


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def violation_signal(skills_violated: list[dict[str, Any]]) -> dict[str, Any]:
    error_count = 0
    warning_count = 0
    for item in skills_violated:
        severity = str(item.get("severity") or item.get("level") or "warning").lower()
        if severity in ERROR_SEVERITIES:
            error_count += 1
        else:
            warning_count += 1
    error_points = min(40, error_count * 10)
    warning_points = min(20, warning_count * 4)
    points = min(40, error_points + warning_points)
    return {
        "points": points,
        "error_count": error_count,
        "warning_count": warning_count,
        "explanation": (
            f"{error_count} error-severity and {warning_count} warning-severity skill findings"
            if error_count or warning_count
            else "No skill violations detected"
        ),
    }


def _file_paths_from_raw(raw: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    files = raw.get("files")
    if isinstance(files, list):
        for file_info in files:
            if not isinstance(file_info, dict):
                continue
            for key in ("filename", "file_path", "path", "previous_filename"):
                value = file_info.get(key)
                if value:
                    paths.add(str(value))
    for key in ("changed_files", "file_paths", "files_touched"):
        value = raw.get(key)
        if isinstance(value, list):
            paths.update(str(item) for item in value if item)
    for key in ("file_hashes", "produced_file_hashes"):
        value = raw.get(key)
        if isinstance(value, dict):
            paths.update(str(path) for path in value.keys() if path)
    return paths


def touched_paths(pr: PullRequest, commits: list[Commit]) -> set[str]:
    paths = _file_paths_from_raw(_as_dict(pr.raw))
    for commit in commits:
        paths.update(_file_paths_from_raw(_as_dict(commit.raw)))
    return paths


def incident_signal(touched: set[str], incident_sessions: list[AgentSession]) -> dict[str, Any]:
    if not touched:
        return {"points": 0, "incident_count": 0, "files": [], "explanation": "No changed files available for incident matching"}
    incident_files: set[str] = set()
    incident_count = 0
    for session in incident_sessions:
        session_files = {str(path) for path in _as_list(session.files_touched)}
        overlap = touched.intersection(session_files)
        if overlap:
            incident_count += 1
            incident_files.update(overlap)
    if incident_count >= 2:
        points = 25
    elif incident_count == 1:
        points = 12
    else:
        points = 0
    return {
        "points": points,
        "incident_count": incident_count,
        "files": sorted(incident_files),
        "explanation": (
            f"{incident_count} previous incident sessions touched the same files"
            if incident_count
            else "No incident history overlaps changed files"
        ),
    }


def _is_test_path(path: str) -> bool:
    lower = path.lower()
    return (
        "/test/" in lower
        or "/tests/" in lower
        or lower.startswith("test/")
        or lower.startswith("tests/")
        or lower.endswith("_test.py")
        or lower.endswith(".test.ts")
        or lower.endswith(".test.tsx")
        or lower.endswith(".spec.ts")
        or lower.endswith(".spec.tsx")
    )


def _coverage_drop_from_check_runs(raw: dict[str, Any]) -> float:
    runs = raw.get("check_runs") if isinstance(raw.get("check_runs"), list) else []
    drops: list[float] = []
    for run in runs:
        if not isinstance(run, dict):
            continue
        for key in ("coverage_delta", "coverage_percent_delta", "coverage_change"):
            value = run.get(key)
            if isinstance(value, (int, float)) and value < 0:
                drops.append(abs(float(value)))
        coverage = run.get("coverage")
        if isinstance(coverage, dict):
            value = coverage.get("delta") or coverage.get("percent_delta")
            if isinstance(value, (int, float)) and value < 0:
                drops.append(abs(float(value)))
    return max(drops) if drops else 0.0


def coverage_signal(pr: PullRequest, touched: set[str]) -> dict[str, Any]:
    raw = _as_dict(pr.raw)
    additions = int(pr.additions or raw.get("additions") or 0)
    has_test_change = any(_is_test_path(path) for path in touched)
    no_test_points = 15 if additions > 0 and touched and not has_test_change else 0
    coverage_drop = _coverage_drop_from_check_runs(raw)
    drop_points = min(20, int(coverage_drop * 5))
    points = min(20, no_test_points + drop_points)
    reasons: list[str] = []
    if no_test_points:
        reasons.append("production code changed without test files")
    if drop_points:
        reasons.append(f"coverage dropped {coverage_drop:g} percentage points")
    return {
        "points": points,
        "coverage_drop": coverage_drop,
        "test_files_changed": has_test_change,
        "explanation": "; ".join(reasons) if reasons else "No coverage risk detected",
    }


def ownership_signal(pr: PullRequest, touched: set[str]) -> dict[str, Any]:
    raw = _as_dict(pr.raw)
    ownership = raw.get("ownership") if isinstance(raw.get("ownership"), dict) else {}
    friction_files = ownership.get("friction_files") if isinstance(ownership.get("friction_files"), list) else []
    points = 15 if friction_files else 0
    return {
        "points": points,
        "files": [str(path) for path in friction_files],
        "explanation": "Changed files owned by another team" if friction_files else "No CODEOWNERS friction data available",
    }


async def compute_risk_score(pr_id: str, db: AsyncSession) -> dict[str, Any]:
    pr = await db.get(PullRequest, pr_id)
    if pr is None:
        raise ValueError("pull_request_not_found")

    attribution = (
        await db.execute(select(PRAttribution).where(PRAttribution.pr_id == pr_id))
    ).scalar_one_or_none()
    if attribution is None:
        attribution = PRAttribution(
            pr_id=pr_id,
            primary_agent="human",
            confidence=1.0,
            lines_by_agent={"human": int((pr.additions or 0) + (pr.deletions or 0))},
            lines_by_human=int((pr.additions or 0) + (pr.deletions or 0)),
            sessions=[],
            skills_loaded=[],
            skills_violated=[],
        )
        db.add(attribution)

    commits = list((await db.execute(select(Commit).where(Commit.pr_id == pr_id))).scalars().all())
    touched = touched_paths(pr, commits)
    incident_sessions = list(
        (
            await db.execute(
                select(AgentSession).where(
                    AgentSession.repo_id == pr.repo_id,
                    AgentSession.outcome == "incident",
                    AgentSession.created_at < pr.opened_at if pr.opened_at is not None else True,
                )
            )
        )
        .scalars()
        .all()
    )

    breakdown = {
        "violations": violation_signal(_as_list(attribution.skills_violated)),
        "incidents": incident_signal(touched, incident_sessions),
        "coverage": coverage_signal(pr, touched),
        "ownership": ownership_signal(pr, touched),
    }
    score = min(100, sum(int(section.get("points") or 0) for section in breakdown.values()))
    tier = risk_tier_for_score(score)
    attribution.risk_score = score
    attribution.risk_tier = tier
    attribution.risk_breakdown = breakdown
    await db.commit()
    return {"score": score, "tier": tier, "breakdown": breakdown}
