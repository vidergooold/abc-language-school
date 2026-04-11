"""add status, comment, created_at to forms; add is_read, created_at to feedback_forms

Revision ID: a1b2c3d4e5f6
Revises: 55deb8dbe4c5
Create Date: 2026-04-11 13:36:00
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '55deb8dbe4c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- child_forms ----
    op.add_column('child_forms', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('child_forms', sa.Column(
        'status', sa.String(), nullable=False,
        server_default='new'
    ))
    op.add_column('child_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))

    # ---- adult_forms ----
    op.add_column('adult_forms', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('adult_forms', sa.Column(
        'status', sa.String(), nullable=False,
        server_default='new'
    ))
    op.add_column('adult_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))

    # ---- preschool_forms ----
    op.add_column('preschool_forms', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('preschool_forms', sa.Column(
        'status', sa.String(), nullable=False,
        server_default='new'
    ))
    op.add_column('preschool_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))

    # ---- teacher_forms ----
    op.add_column('teacher_forms', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('teacher_forms', sa.Column(
        'status', sa.String(), nullable=False,
        server_default='new'
    ))
    op.add_column('teacher_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))

    # ---- testing_forms ----
    op.add_column('testing_forms', sa.Column('comment', sa.Text(), nullable=True))
    op.add_column('testing_forms', sa.Column(
        'status', sa.String(), nullable=False,
        server_default='new'
    ))
    op.add_column('testing_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))

    # ---- feedback_forms ----
    op.add_column('feedback_forms', sa.Column(
        'is_read', sa.Boolean(), nullable=False,
        server_default=sa.false()
    ))
    op.add_column('feedback_forms', sa.Column(
        'created_at', sa.DateTime(timezone=True),
        nullable=False, server_default=sa.func.now()
    ))


def downgrade() -> None:
    for table in [
        'child_forms', 'adult_forms', 'preschool_forms',
        'teacher_forms', 'testing_forms'
    ]:
        op.drop_column(table, 'created_at')
        op.drop_column(table, 'status')
        op.drop_column(table, 'comment')

    op.drop_column('feedback_forms', 'created_at')
    op.drop_column('feedback_forms', 'is_read')
