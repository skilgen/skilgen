from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class SkillUsageEvent(Base):
    """Immutable skill-load event used for org analytics and agent breakdowns."""

    __tablename__ = "skill_usage_events"
    __table_args__ = (
        Index("ix_skill_usage_events_org_loaded_at", "org_id", "loaded_at"),
        Index("ix_skill_usage_events_skill_loaded_at", "skill_id", "loaded_at"),
        Index("ix_skill_usage_events_repo_loaded_at", "repo_id", "loaded_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(100), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    org: Mapped["Org"] = relationship()
    repo: Mapped["Repo"] = relationship()
    skill: Mapped["Skill"] = relationship()
