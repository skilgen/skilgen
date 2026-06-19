"""add pr attributions

Revision ID: 20260428_0002
Revises: 20260428_0001
Create Date: 2026-04-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260428_0002"
down_revision = "20260428_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    json_type = postgresql.JSONB(astext_type=sa.Text()) if bind.dialect.name == "postgresql" else sa.JSON()
    empty_object_default = sa.text("'{}'::jsonb") if bind.dialect.name == "postgresql" else sa.text("'{}'")
    empty_array_default = sa.text("'[]'::jsonb") if bind.dialect.name == "postgresql" else sa.text("'[]'")

    if "pr_attributions" not in tables:
        op.create_table(
            "pr_attributions",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("pr_id", sa.String(), nullable=False),
            sa.Column("primary_agent", sa.String(length=32), nullable=False),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("lines_by_agent", json_type, nullable=False, server_default=empty_object_default),
            sa.Column("lines_by_human", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("sessions", json_type, nullable=False, server_default=empty_array_default),
            sa.Column("skills_loaded", json_type, nullable=False, server_default=empty_array_default),
            sa.Column("skills_violated", json_type, nullable=False, server_default=empty_array_default),
            sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.ForeignKeyConstraint(["pr_id"], ["pull_requests.id"], ondelete="CASCADE"),
            sa.CheckConstraint(
                "primary_agent IN ('claude_code', 'codex', 'cursor', 'copilot', 'devin', 'human', 'mixed')",
                name="ck_pr_attributions_primary_agent",
            ),
        )
        op.create_index("ix_pr_attributions_pr_id", "pr_attributions", ["pr_id"], unique=True)
        op.create_index("ix_pr_attributions_primary_agent", "pr_attributions", ["primary_agent"])
        if bind.dialect.name == "postgresql":
            op.execute("CREATE INDEX ix_pr_attributions_computed_at ON pr_attributions (computed_at DESC)")
        else:
            op.create_index("ix_pr_attributions_computed_at", "pr_attributions", ["computed_at"])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if "pr_attributions" in tables:
        op.drop_index("ix_pr_attributions_computed_at", table_name="pr_attributions")
        op.drop_index("ix_pr_attributions_primary_agent", table_name="pr_attributions")
        op.drop_index("ix_pr_attributions_pr_id", table_name="pr_attributions")
        op.drop_table("pr_attributions")
