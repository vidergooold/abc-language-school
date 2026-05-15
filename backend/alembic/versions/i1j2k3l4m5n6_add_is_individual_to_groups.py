"""add is_individual to groups

Revision ID: i1j2k3l4m5n6
Revises: h3i4j5k6l7m8, b9c8d7e6f5a4
Create Date: 2026-05-15 07:20:00.000000

Adds is_individual boolean column to the groups table with a safe default
of FALSE so that all existing group rows keep their current meaning (group
lessons) without any data loss.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "i1j2k3l4m5n6"
down_revision: Union[str, Sequence[str], None] = ("h3i4j5k6l7m8", "b9c8d7e6f5a4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(col["name"] == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    if not _has_column("groups", "is_individual"):
        op.add_column(
            "groups",
            sa.Column(
                "is_individual",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
        )


def downgrade() -> None:
    if _has_column("groups", "is_individual"):
        op.drop_column("groups", "is_individual")
