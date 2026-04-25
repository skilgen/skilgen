"""add_skill_registry_and_half_life

Revision ID: 4b8a21f0c3d9
Revises: 2f7b9d1c4a6e
Create Date: 2026-04-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "4b8a21f0c3d9"
down_revision = "2f7b9d1c4a6e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "skill_registry_entries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=True),
        sa.Column("skill_id", sa.String(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=64), server_default="1.0.0", nullable=False),
        sa.Column("publisher_org_id", sa.String(), nullable=False),
        sa.Column("publisher_login", sa.String(length=255), nullable=False),
        sa.Column("visibility", sa.String(length=32), server_default="private", nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("compatible_runtimes", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'[]'::jsonb"), nullable=False),
        sa.Column("install_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("score_groundedness", sa.Float(), server_default="0", nullable=False),
        sa.Column("score_coverage", sa.Float(), server_default="0", nullable=False),
        sa.Column("score_freshness", sa.Float(), server_default="0", nullable=False),
        sa.Column("score_structure", sa.Float(), server_default="0", nullable=False),
        sa.Column("score_total", sa.Float(), server_default="0", nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("is_deprecated", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("deprecation_message", sa.Text(), nullable=True),
        sa.Column("successor_entry_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["orgs.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.ForeignKeyConstraint(["successor_entry_id"], ["skill_registry_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skill_dependencies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("source_skill_id", sa.String(), nullable=False),
        sa.Column("target_registry_entry_id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("detected_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_skill_id"], ["skills.id"]),
        sa.ForeignKeyConstraint(["target_registry_entry_id"], ["skill_registry_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "marketplace_installs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("registry_entry_id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=True),
        sa.Column("installed_by", sa.String(length=255), nullable=False),
        sa.Column("installed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["registry_entry_id"], ["skill_registry_entries.id"]),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "skill_half_lives",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("skill_id", sa.String(), nullable=False),
        sa.Column("org_id", sa.String(), nullable=False),
        sa.Column("repo_id", sa.String(), nullable=False),
        sa.Column("commits_30d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("commits_60d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("commits_90d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("file_churn_30d", sa.Integer(), server_default="0", nullable=False),
        sa.Column("predicted_decay_days", sa.Float(), server_default="90", nullable=False),
        sa.Column("predicted_decay_date", sa.DateTime(), nullable=True),
        sa.Column("decay_confidence", sa.Float(), server_default="0.3", nullable=False),
        sa.Column("last_actual_decay_date", sa.DateTime(), nullable=True),
        sa.Column("prediction_error_days", sa.Float(), nullable=True),
        sa.Column("regeneration_buffer_hours", sa.Integer(), server_default="24", nullable=False),
        sa.Column("regen_queued", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("regen_queued_at", sa.DateTime(), nullable=True),
        sa.Column("computed_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("skill_id"),
    )


def downgrade() -> None:
    op.drop_table("skill_half_lives")
    op.drop_table("marketplace_installs")
    op.drop_table("skill_dependencies")
    op.drop_table("skill_registry_entries")
