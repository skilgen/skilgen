"""add_enterprise_governance

Revision ID: 2f7b9d1c4a6e
Revises: 8e14c9a5d2b1
Create Date: 2026-04-24
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "2f7b9d1c4a6e"
down_revision = "8e14c9a5d2b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("actor_login", sa.String(length=128), nullable=True),
        sa.Column("actor_ip", sa.String(length=64), nullable=True),
        sa.Column("repo_id", sa.String(), nullable=True),
        sa.Column("repo_name", sa.String(length=128), nullable=True),
        sa.Column("skill_id", sa.String(), nullable=True),
        sa.Column("skill_domain", sa.String(length=256), nullable=True),
        sa.Column("resource_type", sa.String(length=64), nullable=True),
        sa.Column("resource_id", sa.String(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("summary", sa.String(length=512), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("severity", sa.String(length=16), server_default="info", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_events_org_created_at", "audit_events", ["org_id", "created_at"])
    op.create_index("ix_audit_events_org_event_type_created_at", "audit_events", ["org_id", "event_type", "created_at"])
    op.create_index("ix_audit_events_org_repo_created_at", "audit_events", ["org_id", "repo_id", "created_at"])

    op.create_table(
        "org_policies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("rule_type", sa.String(length=64), nullable=False),
        sa.Column("rule_config", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("severity", sa.String(length=16), server_default="error", nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "org_llm_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("provider", sa.String(length=64), server_default="skillayer", nullable=False),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("endpoint_url", sa.String(length=512), nullable=True),
        sa.Column("api_key_encrypted", sa.LargeBinary(), nullable=True),
        sa.Column("api_key_hint", sa.String(length=16), nullable=True),
        sa.Column("azure_deployment", sa.String(length=128), nullable=True),
        sa.Column("azure_api_version", sa.String(length=32), nullable=True),
        sa.Column("is_configured", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("last_tested_at", sa.DateTime(), nullable=True),
        sa.Column("last_test_ok", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("org_id"),
    )

    op.add_column("orgs", sa.Column("siem_webhook_url", sa.String(length=2048), nullable=True))
    op.add_column("orgs", sa.Column("siem_webhook_secret", sa.String(length=255), nullable=True))
    op.add_column("orgs", sa.Column("siem_webhook_enabled", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("orgs", sa.Column("siem_event_filter", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("orgs", "siem_event_filter")
    op.drop_column("orgs", "siem_webhook_enabled")
    op.drop_column("orgs", "siem_webhook_secret")
    op.drop_column("orgs", "siem_webhook_url")
    op.drop_table("org_llm_configs")
    op.drop_table("org_policies")
    op.drop_index("ix_audit_events_org_repo_created_at", table_name="audit_events")
    op.drop_index("ix_audit_events_org_event_type_created_at", table_name="audit_events")
    op.drop_index("ix_audit_events_org_created_at", table_name="audit_events")
    op.drop_table("audit_events")
