"""add lesson_date to homeworks

Revision ID: a2b3c4d5e6f7
Revises: 321110387098
Create Date: 2026-04-21 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, Sequence[str], None] = '321110387098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    return sa.inspect(bind).has_table(table_name)


def upgrade() -> None:
    if _table_exists('homeworks'):
        # Таблица уже создана через create_all() — просто добавляем колонку
        col_names = [c['name'] for c in sa.inspect(op.get_bind()).get_columns('homeworks')]
        if 'lesson_date' not in col_names:
            op.add_column('homeworks', sa.Column('lesson_date', sa.DateTime(), nullable=True))
    else:
        # Таблица отсутствует (PostgreSQL в production) — создаём целиком
        op.create_table(
            'homeworks',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('lesson_date', sa.DateTime(), nullable=True),
            sa.Column('due_date', sa.DateTime(), nullable=False),
            sa.Column('status', sa.Enum(
                'assigned', 'in_progress', 'submitted', 'completed',
                name='homeworkstatus'
            ), nullable=False, server_default='assigned'),
            sa.Column('group_id', sa.Integer(), sa.ForeignKey('groups.id'), nullable=False),
            sa.Column('teacher_id', sa.Integer(), sa.ForeignKey('teachers.id'), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_homeworks_id', 'homeworks', ['id'])


def downgrade() -> None:
    if _table_exists('homeworks'):
        col_names = [c['name'] for c in sa.inspect(op.get_bind()).get_columns('homeworks')]
        if 'lesson_date' in col_names:
            op.drop_column('homeworks', 'lesson_date')
