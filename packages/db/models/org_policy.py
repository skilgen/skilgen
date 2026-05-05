from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from packages.db.models.base import Base, new_uuid, utcnow


class OrgPolicy(Base):
    __tablename__ = "org_policies"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    org_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(64), nullable=False)
    rule_config: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    decision: Mapped[str] = mapped_column(String(32), nullable=False, default="log_only")
    deprecated_decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dsl_yaml: Mapped[str | None] = mapped_column(Text, nullable=True)
    dsl_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    policy_pack: Mapped[str | None] = mapped_column(String(64), nullable=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="error")
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
