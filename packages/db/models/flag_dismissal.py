from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class FlagDismissal(Base):
    __tablename__ = "flag_dismissals"
    __table_args__ = (
        UniqueConstraint("org_id", "flag_type", "repo_id", "skill_id", name="uq_flag_dismissals_scope"),
        Index("ix_flag_dismissals_org_dismissed_at", "org_id", "dismissed_at"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), nullable=False)
    flag_type: Mapped[str] = mapped_column(String(100), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    dismissed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), default="not_a_risk", nullable=False)
    dismissed_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)

    org: Mapped["Org"] = relationship()
    repo: Mapped["Repo"] = relationship()
    skill: Mapped["Skill | None"] = relationship()
