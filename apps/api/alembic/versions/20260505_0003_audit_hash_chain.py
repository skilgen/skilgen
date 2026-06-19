"""add audit hash chain and report view

Revision ID: 20260505_0003
Revises: 20260505_0002
Create Date: 2026-05-05
"""

from __future__ import annotations

from alembic import context, op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260505_0003"
down_revision = "20260505_0002"
branch_labels = None
depends_on = None


REPORT_VIEW_SQL = """
CREATE OR REPLACE VIEW v8_audit_report_events AS
SELECT
    id,
    org_id,
    event_type,
    action,
    actor_login,
    repo_id,
    repo_name,
    skill_id,
    skill_domain,
    resource_type,
    resource_id,
    severity,
    summary,
    metadata,
    created_at,
    metadata ->> 'commit_sha' AS commit_sha,
    metadata ->> 'policy_id' AS policy_id,
    metadata ->> 'policy_decision' AS policy_decision,
    metadata ->> 'control' AS control_mapping,
    metadata ->> 'agent_runtime' AS agent_runtime,
    metadata ->> 'sensitivity_tier' AS sensitivity_tier
FROM audit_events
"""


def _has_table(table_name: str) -> bool:
    if context.is_offline_mode():
        return False
    return table_name in set(sa.inspect(op.get_bind()).get_table_names())


def _has_index(table_name: str, index_name: str) -> bool:
    if context.is_offline_mode():
        return False
    if not _has_table(table_name):
        return False
    return index_name in {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table_name)}


def upgrade() -> None:
    if not _has_table("audit_hash_chain"):
        op.create_table(
            "audit_hash_chain",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("event_id", sa.String(), nullable=False),
            sa.Column("sequence", sa.Integer(), nullable=False),
            sa.Column("event_hash", sa.String(length=64), nullable=False),
            sa.Column("previous_hash", sa.String(length=64), nullable=False),
            sa.Column("root_hash", sa.String(length=64), nullable=False),
            sa.Column("merkle_proof", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "event_id", name="uq_audit_hash_chain_org_event"),
            sa.UniqueConstraint("org_id", "sequence", name="uq_audit_hash_chain_org_sequence"),
        )
    if not _has_index("audit_hash_chain", "ix_audit_hash_chain_org_sequence"):
        op.create_index("ix_audit_hash_chain_org_sequence", "audit_hash_chain", ["org_id", "sequence"])
    if not _has_index("audit_hash_chain", "ix_audit_hash_chain_org_root"):
        op.create_index("ix_audit_hash_chain_org_root", "audit_hash_chain", ["org_id", "root_hash"])

    if not _has_table("audit_worm_roots"):
        op.create_table(
            "audit_worm_roots",
            sa.Column("id", sa.String(), nullable=False),
            sa.Column("org_id", sa.String(), nullable=False),
            sa.Column("root_hash", sa.String(length=64), nullable=False),
            sa.Column("start_sequence", sa.Integer(), nullable=False),
            sa.Column("end_sequence", sa.Integer(), nullable=False),
            sa.Column("event_count", sa.Integer(), nullable=False),
            sa.Column("storage_provider", sa.String(length=32), nullable=False, server_default="s3_object_lock"),
            sa.Column("object_key", sa.String(length=1024), nullable=True),
            sa.Column("cadence", sa.String(length=32), nullable=False, server_default="daily"),
            sa.Column("merkle_proof", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
            sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("org_id", "root_hash", name="uq_audit_worm_roots_org_root"),
        )
    if not _has_index("audit_worm_roots", "ix_audit_worm_roots_org_created_at"):
        op.create_index("ix_audit_worm_roots_org_created_at", "audit_worm_roots", ["org_id", "created_at"])

    op.execute(REPORT_VIEW_SQL)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v8_audit_report_events")
    if context.is_offline_mode() or _has_index("audit_worm_roots", "ix_audit_worm_roots_org_created_at"):
        op.drop_index("ix_audit_worm_roots_org_created_at", table_name="audit_worm_roots")
    if context.is_offline_mode() or _has_table("audit_worm_roots"):
        op.drop_table("audit_worm_roots")
    if context.is_offline_mode() or _has_index("audit_hash_chain", "ix_audit_hash_chain_org_root"):
        op.drop_index("ix_audit_hash_chain_org_root", table_name="audit_hash_chain")
    if context.is_offline_mode() or _has_index("audit_hash_chain", "ix_audit_hash_chain_org_sequence"):
        op.drop_index("ix_audit_hash_chain_org_sequence", table_name="audit_hash_chain")
    if context.is_offline_mode() or _has_table("audit_hash_chain"):
        op.drop_table("audit_hash_chain")
