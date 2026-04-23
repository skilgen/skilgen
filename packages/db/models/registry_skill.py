from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.org import Org
    from packages.db.models.repo import Repo
    from packages.db.models.skill import Skill


class RegistrySkill(Base):
    """Public registry listing for a generated Skillayer skill."""

    __tablename__ = "registry_skills"
    __table_args__ = (
        Index("ix_registry_skills_is_public", "is_public"),
        Index("ix_registry_skills_org_id", "org_id"),
        Index("ix_registry_skills_repo_id", "repo_id"),
        Index("ix_registry_skills_skill_id", "skill_id"),
        Index("ix_registry_skills_import_count", "import_count"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), nullable=False)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_official: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    import_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=utcnow)

    org: Mapped["Org"] = relationship()
    repo: Mapped["Repo"] = relationship()
    skill: Mapped["Skill"] = relationship()
