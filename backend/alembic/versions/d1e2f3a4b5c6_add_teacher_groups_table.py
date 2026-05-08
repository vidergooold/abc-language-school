"""add_teacher_groups_table

Revision ID: d1e2f3a4b5c6
Revises: c4d5e6f7a8b9
Create Date: 2026-04-26 07:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if not _table_exists('teacher_groups'):
        op.create_table(
            'teacher_groups',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('teacher_id', sa.Integer(), nullable=False),
            sa.Column('group_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('teacher_id', 'group_id', name='uq_teacher_group'),
        )
        op.create_index(op.f('ix_teacher_groups_id'), 'teacher_groups', ['id'], unique=False)
        op.create_index(op.f('ix_teacher_groups_teacher_id'), 'teacher_groups', ['teacher_id'], unique=False)
        op.create_index(op.f('ix_teacher_groups_group_id'), 'teacher_groups', ['group_id'], unique=False)


def downgrade() -> None:
    if _table_exists('teacher_groups'):
        op.drop_index(op.f('ix_teacher_groups_group_id'), table_name='teacher_groups')
        op.drop_index(op.f('ix_teacher_groups_teacher_id'), table_name='teacher_groups')
        op.drop_index(op.f('ix_teacher_groups_id'), table_name='teacher_groups')
        op.drop_table('teacher_groups')
