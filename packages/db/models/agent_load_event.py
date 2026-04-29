from __future__ import annotations

from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class AgentLoadEvent(Base):
    __tablename__ = "agent_load_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(ForeignKey("orgs.id", ondelete="CASCADE"), nullable=False)
    agent_runtime: Mapped[str] = mapped_column(String(100), nullable=False)
    detected_runtime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    skill_path: Mapped[str] = mapped_column(String(512), nullable=False)
    loaded_at: Mapped[datetime] = mapped_column(default=utcnow, nullable=False)
    repo_id: Mapped[str | None] = mapped_column(ForeignKey("repos.id", ondelete="CASCADE"), nullable=True)
