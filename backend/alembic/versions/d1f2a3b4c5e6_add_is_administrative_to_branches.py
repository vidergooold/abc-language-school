"""add is_administrative to branches

Revision ID: d1f2a3b4c5e6
Revises: c7d8e9f0a1b2, b9c8d7e6f5a4
Create Date: 2026-05-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1f2a3b4c5e6"
down_revision: Union[str, Sequence[str], None] = "c7d8e9f0a1b2"
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

    if not _column_exists("branches", "is_administrative"):
        op.add_column(
            "branches",
            sa.Column("is_administrative", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )

    # Пометить Офис как административный — занятий там не проводится
    bind = op.get_bind()
    bind.execute(
        sa.text("UPDATE branches SET is_administrative = true WHERE name = 'Офис'")
    )


def downgrade() -> None:
    if _table_exists("branches") and _column_exists("branches", "is_administrative"):
        op.drop_column("branches", "is_administrative")
