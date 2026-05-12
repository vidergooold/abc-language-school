"""add teacher role and student age fields

Revision ID: g1h2i3j4k5l6
Revises: f2a3b4c5d6e7, 476b21780d50
Create Date: 2026-05-12 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "g1h2i3j4k5l6"
down_revision: Union[str, Sequence[str], None] = ("f2a3b4c5d6e7", "476b21780d50")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols


def upgrade() -> None:
    # Add role column to teachers (if not exists)
    if not _column_exists("teachers", "role"):
        op.add_column("teachers", sa.Column("role", sa.String(50), nullable=True))
        op.execute("UPDATE teachers SET role = 'teacher' WHERE role IS NULL")

    # Make email nullable in teachers (if it isn't already).
    # We guard with column inspection to ensure idempotency.
    bind = op.get_bind()
    insp = sa.inspect(bind)
    teacher_cols = {c["name"]: c for c in insp.get_columns("teachers")}
    if "email" in teacher_cols and not teacher_cols["email"]["nullable"]:
        with op.batch_alter_table("teachers") as batch_op:
            batch_op.alter_column(
                "email",
                existing_type=sa.String(255),
                nullable=True,
            )

    # Add age column to students (if not exists)
    if not _column_exists("students", "age"):
        op.add_column("students", sa.Column("age", sa.Integer(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    student_cols = [c["name"] for c in insp.get_columns("students")]
    if "age" in student_cols:
        op.drop_column("students", "age")

    teacher_cols = [c["name"] for c in insp.get_columns("teachers")]
    if "role" in teacher_cols:
        op.drop_column("teachers", "role")
