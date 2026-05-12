"""add branch_id to classrooms

Revision ID: h3i4j5k6l7m8
Revises: f8a9b0c1d2e3, g1h2i3j4k5l6
Create Date: 2026-05-12 15:40:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "h3i4j5k6l7m8"
down_revision: Union[str, Sequence[str], None] = ("f8a9b0c1d2e3", "g1h2i3j4k5l6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(op.get_bind())
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _has_fk(table_name: str, constrained_columns: list[str]) -> bool:
    inspector = sa.inspect(op.get_bind())
    for fk in inspector.get_foreign_keys(table_name):
        if fk.get("constrained_columns") == constrained_columns:
            return True
    return False


def upgrade() -> None:
    if not _has_column("classrooms", "branch_id"):
        op.add_column("classrooms", sa.Column("branch_id", sa.Integer(), nullable=True))
    if not _has_fk("classrooms", ["branch_id"]):
        op.create_foreign_key(
            "fk_classrooms_branch_id_branches",
            "classrooms",
            "branches",
            ["branch_id"],
            ["id"],
        )


def downgrade() -> None:
    if _has_fk("classrooms", ["branch_id"]):
        op.drop_constraint("fk_classrooms_branch_id_branches", "classrooms", type_="foreignkey")
    if _has_column("classrooms", "branch_id"):
        op.drop_column("classrooms", "branch_id")
