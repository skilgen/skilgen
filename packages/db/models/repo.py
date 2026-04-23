from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.analysis_run import AnalysisRun
    from packages.db.models.dependency import Dependency
    from packages.db.models.org import Org
    from packages.db.models.skill import Skill


class Repo(Base):
    __tablename__ = "repos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"))
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    github_installation_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    full_name: Mapped[str] = mapped_column(String(512), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    default_branch: Mapped[str] = mapped_column(String(255), default="main")
    language: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_monorepo: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_analysed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    org: Mapped["Org"] = relationship(back_populates="repos")
    runs: Mapped[list["AnalysisRun"]] = relationship(back_populates="repo")
    skills: Mapped[list["Skill"]] = relationship(back_populates="repo")
    dependencies: Mapped[list["Dependency"]] = relationship(back_populates="repo")
