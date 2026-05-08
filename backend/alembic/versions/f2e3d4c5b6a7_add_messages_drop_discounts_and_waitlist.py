"""add messages, drop discounts and waitlist

Revision ID: f2e3d4c5b6a7
Revises: e2f3a4b5c6d7
Create Date: 2026-05-07 06:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f2e3d4c5b6a7'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # CREATE TABLE messages
    if not _table_exists('messages'):
        op.create_table(
            'messages',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('sender_id', sa.Integer(), nullable=False),
            sa.Column('recipient_id', sa.Integer(), nullable=False),
            sa.Column('body', sa.Text(), nullable=False),
            sa.Column('is_read', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['recipient_id'], ['users.id']),
            sa.ForeignKeyConstraint(['sender_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    # DROP TABLE discounts
    if _table_exists('discounts'):
        op.drop_table('discounts')

    # DROP TABLE waitlist
    if _table_exists('waitlist'):
        op.drop_table('waitlist')


def downgrade() -> None:
    # Recreate waitlist
    if not _table_exists('waitlist'):
        op.create_table(
            'waitlist',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('course_id', sa.Integer(), nullable=False),
            sa.Column('group_id', sa.Integer(), nullable=True),
            sa.Column('student_name', sa.String(length=255), nullable=False),
            sa.Column('student_phone', sa.String(length=50), nullable=True),
            sa.Column('student_email', sa.String(length=255), nullable=True),
            sa.Column('student_type', sa.String(length=50), nullable=False),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('position', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('notified_at', sa.DateTime(), nullable=True),
            sa.Column('enrolled_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['course_id'], ['courses.id']),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    # Recreate discounts
    if not _table_exists('discounts'):
        op.create_table(
            'discounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('student_group_id', sa.Integer(), nullable=True),
            sa.Column('group_id', sa.Integer(), nullable=True),
            sa.Column('reason', sa.String(length=50), nullable=False),
            sa.Column('discount_type', sa.String(length=50), nullable=False),
            sa.Column('value', sa.Numeric(10, 2), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('promo_code', sa.String(length=50), nullable=True),
            sa.Column('valid_from', sa.DateTime(), nullable=True),
            sa.Column('valid_until', sa.DateTime(), nullable=True),
            sa.Column('max_uses', sa.Integer(), nullable=True),
            sa.Column('used_count', sa.Integer(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.id']),
            sa.ForeignKeyConstraint(['student_group_id'], ['student_groups.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    # Drop messages table
    if _table_exists('messages'):
        op.drop_index(op.f('ix_messages_id'), table_name='messages')
        op.drop_table('messages')
