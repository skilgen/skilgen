"""add_pr_number_to_analysis_runs

Revision ID: 7b68f2d4c9a1
Revises: 1d9eedf285e5
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b68f2d4c9a1"
down_revision: Union[str, Sequence[str], None] = "1d9eedf285e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "analysis_runs",
        sa.Column("pr_number", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("analysis_runs", "pr_number")
