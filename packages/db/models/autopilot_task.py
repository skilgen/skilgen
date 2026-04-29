from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class AutopilotTask(Base):
    __tablename__ = "autopilot_tasks"
    __table_args__ = (
        UniqueConstraint("org_id", "repo_id", "skill_id", "task_type", "status", name="uq_autopilot_pending_task"),
        Index("ix_autopilot_tasks_org_status_created_at", "org_id", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    trigger_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    freshness_at_trigger: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    improvement_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    original_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    pr_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    org: Mapped["Org"] = relationship()
    repo: Mapped["Repo"] = relationship()
    skill: Mapped["Skill | None"] = relationship()
