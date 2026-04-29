from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.repo import Repo
    from packages.db.models.skill_version import SkillVersion


SOURCE_TYPE_TO_CATEGORY: dict[str, str] = {
    "code": "codebase_architecture",
    "openapi": "internal_tools",
    "graphql": "internal_tools",
    "postman": "internal_tools",
    "terraform": "codebase_architecture",
    "kubernetes": "codebase_architecture",
    "helm": "codebase_architecture",
    "dbt": "data_schema",
    "sql_schema": "data_schema",
    "kafka": "data_schema",
    "sarif": "security_compliance",
    "sbom": "security_compliance",
    "security_policy": "security_compliance",
    "runbook": "operational_knowledge",
    "runbooks": "operational_knowledge",
    "confluence": "operational_knowledge",
    "notion": "operational_knowledge",
    "incident": "operational_knowledge",
    "incidents": "operational_knowledge",
    "pagerduty": "operational_knowledge",
}


def skill_category_for_source_type(source_type: str | None) -> str:
    """Return the dashboard taxonomy category for a persisted skill source."""
    return SOURCE_TYPE_TO_CATEGORY.get(source_type or "code", "codebase_architecture")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"))
    run_id: Mapped[str] = mapped_column(ForeignKey("analysis_runs.id"))
    domain: Mapped[str] = mapped_column(String(255))
    skill_path: Mapped[str] = mapped_column(String(512))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True, default="code")
    skill_category: Mapped[str | None] = mapped_column(String(50), nullable=True, default="codebase_architecture")
    score_total: Mapped[int] = mapped_column(default=0)
    score_groundedness: Mapped[int] = mapped_column(default=0)
    score_coverage: Mapped[int] = mapped_column(default=0)
    score_freshness: Mapped[int] = mapped_column(default=0)
    score_structure: Mapped[int] = mapped_column(default=0)
    is_stale: Mapped[bool] = mapped_column(default=False)
    is_enterprise: Mapped[bool] = mapped_column(Boolean, default=False)
    anti_patterns: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    load_count_30d: Mapped[int] = mapped_column(default=0)
    last_loaded_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    repo: Mapped["Repo"] = relationship(back_populates="skills")
    versions: Mapped[list["SkillVersion"]] = relationship(
        back_populates="skill",
        order_by="SkillVersion.version_number",
    )
