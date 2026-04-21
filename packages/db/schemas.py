from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScoreResponse(BaseModel):
    total: int
    groundedness: int
    coverage: int
    freshness: int
    structure: int


class OrgResponse(BaseModel):
    id: str
    login: str
    name: str
    plan: str
    repo_count: int
    avg_score: float | None


class RepoResponse(BaseModel):
    id: str
    full_name: str
    name: str
    language: str | None
    is_monorepo: bool
    last_analysed_at: datetime | None
    score: ScoreResponse | None
    score_delta: int | None
    skill_count: int


class SkillResponse(BaseModel):
    id: str
    domain: str
    skill_path: str
    score: ScoreResponse
    is_stale: bool
    load_count_30d: int
    last_loaded_at: datetime | None


class AnalysisRunResponse(BaseModel):
    id: str
    status: str
    trigger: str
    commit_sha: str | None
    score: ScoreResponse | None
    domain_count: int | None
    skill_count: int | None
    started_at: datetime | None
    completed_at: datetime | None


class WebhookPayload(BaseModel):
    action: str | None = None
    ref: str | None = None
    repository: dict[str, Any]
    installation: dict[str, Any] | None = None
    sender: dict[str, Any]
