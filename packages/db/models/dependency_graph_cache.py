from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class DependencyGraphCache(Base):
    __tablename__ = "dependency_graph_cache"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id"), index=True)
    scope: Mapped[str] = mapped_column(String(32), index=True)
    repo_id: Mapped[str | None] = mapped_column(ForeignKey("repos.id"), nullable=True, index=True)
    nodes_json: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    edges_json: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    opportunities_json: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    computed_at: Mapped[datetime] = mapped_column(default=utcnow)
