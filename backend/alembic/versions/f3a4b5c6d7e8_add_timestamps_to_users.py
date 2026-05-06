"""add created_at and updated_at to users

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-05-06 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add created_at and updated_at columns to the users table.

    Existing rows are backfilled with NOW() before the columns are set
    NOT NULL so that the migration is safe on a live database.
    """
    # Add columns as nullable first so existing rows are not rejected.
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # Backfill existing rows.
    op.execute("UPDATE users SET created_at = NOW(), updated_at = NOW() WHERE created_at IS NULL")

    # Enforce NOT NULL and set server defaults.
    op.alter_column('users', 'created_at',
                    nullable=False,
                    server_default=sa.text('NOW()'))
    op.alter_column('users', 'updated_at',
                    nullable=False,
                    server_default=sa.text('NOW()'))


def downgrade() -> None:
    """Remove created_at and updated_at columns from users."""
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
