from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.db.models.base import Base, new_uuid, utcnow

if TYPE_CHECKING:
    from packages.db.models.digest_config import DigestConfig
    from packages.db.models.repo import Repo
    from packages.db.models.rbac import Role, RoleBinding
    from packages.db.models.source_connection import SourceConnection


class Org(Base):
    __tablename__ = "orgs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    github_org_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    login: Mapped[str] = mapped_column(String(255), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    plan: Mapped[str] = mapped_column(String(50), default="free")
    seat_count: Mapped[int] = mapped_column(default=0)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    plan_seat_limit: Mapped[int] = mapped_column(default=3)
    score_threshold: Mapped[int] = mapped_column(default=60)
    slack_webhook_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    slack_signing_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    slack_team_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    slack_standup_enabled: Mapped[bool] = mapped_column(default=False)
    slack_standup_hour: Mapped[int] = mapped_column(default=9)
    digest_email: Mapped[str | None] = mapped_column(Text, nullable=True)
    digest_enabled: Mapped[bool] = mapped_column(default=False)
    digest_day: Mapped[int] = mapped_column(default=1)
    digest_hour: Mapped[int] = mapped_column(default=8)
    is_suspended: Mapped[bool] = mapped_column(default=False)
    suspended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    suspended_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    notify_on_pr: Mapped[bool] = mapped_column(default=True)
    notify_on_stale: Mapped[bool] = mapped_column(default=True)
    notification_settings: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)
    settings: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True, default=dict)
    siem_webhook_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    siem_webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    siem_webhook_enabled: Mapped[bool] = mapped_column(default=False)
    siem_event_filter: Mapped[str | None] = mapped_column(String(32), nullable=True)
    auto_join_domain: Mapped[bool] = mapped_column(default=True)
    workos_org_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github_installation_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(255), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

    repos: Mapped[list["Repo"]] = relationship(back_populates="org")
    source_connections: Mapped[list["SourceConnection"]] = relationship(back_populates="org")
    digest_config: Mapped["DigestConfig | None"] = relationship(back_populates="org")
    roles: Mapped[list["Role"]] = relationship(back_populates="org")
    role_bindings: Mapped[list["RoleBinding"]] = relationship(back_populates="org")
