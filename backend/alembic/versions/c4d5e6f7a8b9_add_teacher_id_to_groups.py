"""add teacher_id to groups

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-04-21 18:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'c4d5e6f7a8b9'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [column['name'] for column in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _has_column('groups', 'teacher_id'):
        op.add_column('groups', sa.Column('teacher_id', sa.Integer(), nullable=True))
        op.create_foreign_key('fk_groups_teacher_id_teachers', 'groups', 'teachers', ['teacher_id'], ['id'])
    op.execute(
        sa.text(
            """
            UPDATE groups
            SET teacher_id = source.teacher_id
            FROM (
                SELECT group_id, MIN(teacher_id) AS teacher_id
                FROM lessons
                WHERE teacher_id IS NOT NULL
                GROUP BY group_id
            ) AS source
            WHERE groups.id = source.group_id
              AND groups.teacher_id IS NULL
            """
        )
    )


def downgrade() -> None:
    if _has_column('groups', 'teacher_id'):
        op.drop_constraint('fk_groups_teacher_id_teachers', 'groups', type_='foreignkey')
        op.drop_column('groups', 'teacher_id')