from __future__ import annotations

from datetime import datetime

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class AgentTask(Base):
    """One unit of agent work attempted by an agent in a repo."""

    __tablename__ = "agent_tasks"
    __table_args__ = (
        Index("ix_agent_tasks_org_repo_started", "org_id", "repo_id", "started_at"),
        Index("ix_agent_tasks_org_outcome_started", "org_id", "outcome", "started_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(64), nullable=False)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    outcome: Mapped[str] = mapped_column(String(32), nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_loaded: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    skill_domains_loaded: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skill_score_at_task: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)


class EvalSession(Base):
    """A batch of tasks run as part of an A/B test or benchmark."""

    __tablename__ = "eval_sessions"
    __table_args__ = (Index("ix_eval_sessions_org_repo_created", "org_id", "repo_id", "created_at"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str | None] = mapped_column(ForeignKey("repos.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    eval_type: Mapped[str] = mapped_column(String(32), nullable=False)
    skill_version_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(64), nullable=False)
    task_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    partial_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_token_count: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    started_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)


class ABTest(Base):
    """Compares two skill versions against real agent tasks."""

    __tablename__ = "ab_tests"
    __table_args__ = (Index("ix_ab_tests_org_status_created", "org_id", "status", "created_at"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="running", nullable=False)
    control_version_id: Mapped[str] = mapped_column(ForeignKey("skill_versions.id"), nullable=False)
    treatment_version_id: Mapped[str] = mapped_column(ForeignKey("skill_versions.id"), nullable=False)
    control_session_id: Mapped[str | None] = mapped_column(ForeignKey("eval_sessions.id"), nullable=True)
    treatment_session_id: Mapped[str | None] = mapped_column(ForeignKey("eval_sessions.id"), nullable=True)
    winner: Mapped[str | None] = mapped_column(String(32), nullable=True)
    control_success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    treatment_success_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    improvement_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(32), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class SkillGap(Base):
    """Auto-detected gap: agents failing on a domain repeatedly."""

    __tablename__ = "skill_gaps"
    __table_args__ = (
        Index("ix_skill_gaps_org_repo_status", "org_id", "repo_id", "status"),
        Index("ix_skill_gaps_org_domain_status", "org_id", "domain", "status"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    failure_count: Mapped[int] = mapped_column(Integer, nullable=False)
    task_ids: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    existing_skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id", ondelete="SET NULL"), nullable=True)
    existing_skill_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gap_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="open", nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    resolution_note: Mapped[str | None] = mapped_column(Text, nullable=True)
