"""add language and program_name to groups

Revision ID: f8a9b0c1d2e3
Revises: c4d5e6f7a8b9
Create Date: 2026-05-12 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'f8a9b0c1d2e3'
down_revision = 'c4d5e6f7a8b9'
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [column['name'] for column in inspector.get_columns(table_name)]
    return column_name in columns


def upgrade() -> None:
    if not _has_column('groups', 'language'):
        op.add_column('groups', sa.Column('language', sa.String(50), nullable=True))
    if not _has_column('groups', 'program_name'):
        op.add_column('groups', sa.Column('program_name', sa.String(100), nullable=True))


def downgrade() -> None:
    if _has_column('groups', 'program_name'):
        op.drop_column('groups', 'program_name')
    if _has_column('groups', 'language'):
        op.drop_column('groups', 'language')
