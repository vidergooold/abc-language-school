"""drop_unused_tables

Drops tables that have no SQLAlchemy model and are not referenced
in any active router or service file:
  - expenses
  - revenue_analytics
  - rooms
  - materials
  - reviews

Kept tables (have FK dependencies or active code references):
  - All other tables referenced in app/models/ and app/api/

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-04-26 07:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_UNUSED_TABLES = [
    'expenses',
    'revenue_analytics',
    'rooms',
    'materials',
    'reviews',
]


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    """
    Drop unused tables.

    Dropped tables   : expenses, revenue_analytics, rooms, materials, reviews
    Dropped columns  : (none — all active columns are used in current models)
    Kept (FK dep)    : (none of the above has FK references from other tables)
    """
    for table in _UNUSED_TABLES:
        if _table_exists(table):
            op.drop_table(table)


def downgrade() -> None:
    # Recreate dropped tables in reverse order (simplified schema — no data recovery)
    if not _table_exists('reviews'):
        op.create_table(
            'reviews',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('is_published', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
            sa.ForeignKeyConstraint(['student_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    if not _table_exists('materials'):
        op.create_table(
            'materials',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('file_url', sa.String(), nullable=False),
            sa.Column('file_type', sa.String(), nullable=True),
            sa.Column('uploaded_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    if not _table_exists('rooms'):
        op.create_table(
            'rooms',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('capacity', sa.Integer(), nullable=False),
            sa.Column('equipment', sa.Text(), nullable=True),
            sa.Column('is_available', sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )

    if not _table_exists('revenue_analytics'):
        op.create_table(
            'revenue_analytics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('period_start', sa.Date(), nullable=False),
            sa.Column('period_end', sa.Date(), nullable=False),
            sa.Column('total_revenue', sa.Float(), nullable=True),
            sa.Column('total_expenses', sa.Float(), nullable=True),
            sa.Column('net_profit', sa.Float(), nullable=True),
            sa.Column('student_count', sa.Integer(), nullable=True),
            sa.Column('course_count', sa.Integer(), nullable=True),
            sa.Column('average_revenue_per_student', sa.Float(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )

    if not _table_exists('expenses'):
        op.create_table(
            'expenses',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('category', sa.String(), nullable=False),
            sa.Column('amount', sa.Float(), nullable=False),
            sa.Column('currency', sa.String(), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('date', sa.Date(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
