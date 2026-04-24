"""add github_installation_id to orgs

Revision ID: f1b2c3d4e5f6
Revises: 9a7c3e4d1b20
Create Date: 2026-04-24 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9a7c3e4d1b20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("orgs", sa.Column("github_installation_id", sa.BigInteger(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orgs", "github_installation_id")
