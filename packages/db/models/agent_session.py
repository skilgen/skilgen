from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.repo import Repo
    from packages.db.models.skill_memory_stub import SkillMemoryStub


class AgentSession(Base):
    __tablename__ = "agent_sessions"
    __table_args__ = (
        UniqueConstraint("repo_id", "session_id", name="uq_agent_sessions_repo_session"),
        Index("ix_agent_sessions_org_created_at", "org_id", "created_at"),
        Index("ix_agent_sessions_repo_created_at", "repo_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=False)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(64), nullable=False)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), default="unknown", nullable=False)
    compliance_status: Mapped[str] = mapped_column(String(16), default="unknown", nullable=False)
    permission_profile: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approval_policy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sandbox_policy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    access_scope: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_access: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    external_api_call_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    command_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mcp_tools_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_targets_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    policy_violations: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    engineer_login: Mapped[str | None] = mapped_column(String(128), nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    files_touched: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    skill_paths_loaded: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    transcript_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_message_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    discoveries_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    session_start: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    session_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    skills_loaded: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    code_produced: Mapped[str | None] = mapped_column(Text, nullable=True)
    produced_artifacts: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)
    produced_file_hashes: Mapped[dict[str, str]] = mapped_column(JSONB, default=dict, nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    inactivity_timeout_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    last_artifact_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    repo: Mapped["Repo"] = relationship()
    memory_stubs: Mapped[list["SkillMemoryStub"]] = relationship(back_populates="session")
