"""ensure is_administrative column exists on branches

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-05-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    if not _table_exists("branches"):
        return

    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            sa.text(
                "ALTER TABLE branches ADD COLUMN IF NOT EXISTS "
                "is_administrative BOOLEAN DEFAULT FALSE NOT NULL;"
            )
        )
    elif not _column_exists("branches", "is_administrative"):
        op.add_column(
            "branches",
            sa.Column("is_administrative", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )


def downgrade() -> None:
    pass
