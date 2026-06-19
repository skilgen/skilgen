"""add skill snapshots

Revision ID: 20260430_0004
Revises: 20260430_0003
Create Date: 2026-04-30
"""

from __future__ import annotations

from alembic import op


revision = "20260430_0004"
down_revision = "20260430_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS skill_snapshots (
            id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
            skill_id TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            repo_id TEXT NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
            snapshot_type TEXT NOT NULL DEFAULT 'auto',
            label TEXT,
            content TEXT NOT NULL,
            score_total INT,
            score_groundedness INT,
            score_coverage INT,
            score_freshness INT,
            score_structure INT,
            created_by TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_skill_snapshots_skill_id ON skill_snapshots (skill_id, created_at DESC)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_skill_snapshots_repo_id ON skill_snapshots (repo_id, created_at DESC)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_skill_snapshots_repo_id")
    op.execute("DROP INDEX IF EXISTS ix_skill_snapshots_skill_id")
    op.execute("DROP TABLE IF EXISTS skill_snapshots")
