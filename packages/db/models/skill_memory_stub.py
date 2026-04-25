from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.agent_session import AgentSession
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class SkillMemoryStub(Base):
    __tablename__ = "skill_memory_stubs"
    __table_args__ = (
        Index("ix_skill_memory_stubs_org_status_created_at", "org_id", "status", "created_at"),
        Index("ix_skill_memory_stubs_repo_created_at", "repo_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)
    domain: Mapped[str] = mapped_column(String(256), nullable=False)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    discovery_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    proposed_content: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(64), nullable=False)
    engineer_login: Mapped[str | None] = mapped_column(String(128), nullable=True)
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    merged_version_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    repo: Mapped["Repo"] = relationship()
    session: Mapped["AgentSession"] = relationship(back_populates="memory_stubs")
    skill: Mapped["Skill | None"] = relationship()
