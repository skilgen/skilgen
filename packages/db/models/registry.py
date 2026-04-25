from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class SkillRegistryEntry(Base):
    __tablename__ = "skill_registry_entries"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str | None] = mapped_column(ForeignKey("orgs.id"), nullable=True)
    skill_id: Mapped[str | None] = mapped_column(ForeignKey("skills.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False, default="1.0.0")
    publisher_org_id: Mapped[str] = mapped_column(String, nullable=False)
    publisher_login: Mapped[str] = mapped_column(String(255), nullable=False)
    visibility: Mapped[str] = mapped_column(String(32), nullable=False, default="private")
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    compatible_runtimes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    install_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score_groundedness: Mapped[float] = mapped_column(default=0.0)
    score_coverage: Mapped[float] = mapped_column(default=0.0)
    score_freshness: Mapped[float] = mapped_column(default=0.0)
    score_structure: Mapped[float] = mapped_column(default=0.0)
    score_total: Mapped[float] = mapped_column(default=0.0)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_deprecated: Mapped[bool] = mapped_column(default=False)
    deprecation_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    successor_entry_id: Mapped[str | None] = mapped_column(ForeignKey("skill_registry_entries.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)


class SkillDependency(Base):
    __tablename__ = "skill_dependencies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    source_skill_id: Mapped[str] = mapped_column(ForeignKey("skills.id"), nullable=False)
    target_registry_entry_id: Mapped[str] = mapped_column(ForeignKey("skill_registry_entries.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(default=utcnow)


class MarketplaceInstall(Base):
    __tablename__ = "marketplace_installs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    registry_entry_id: Mapped[str] = mapped_column(ForeignKey("skill_registry_entries.id"), nullable=False)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    repo_id: Mapped[str | None] = mapped_column(ForeignKey("repos.id"), nullable=True)
    installed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    installed_at: Mapped[datetime] = mapped_column(default=utcnow)
