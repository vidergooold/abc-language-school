"""fix_news_null_defaults

Backfill NULL values in news.is_pinned, news.views_count, news.likes_count
and set server-side defaults so Pydantic validation never receives None.

Revision ID: f1e2d3c4b5a6
Revises: 55deb8dbe4c5
Create Date: 2026-04-12
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, Sequence[str], None] = '55deb8dbe4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Backfill existing NULL rows
    op.execute("UPDATE news SET is_pinned   = FALSE WHERE is_pinned   IS NULL")
    op.execute("UPDATE news SET views_count = 0     WHERE views_count IS NULL")
    op.execute("UPDATE news SET likes_count = 0     WHERE likes_count IS NULL")

    # 2. Set server defaults and NOT NULL constraints
    op.alter_column(
        'news', 'is_pinned',
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text('false'),
    )
    op.alter_column(
        'news', 'views_count',
        existing_type=sa.Integer(),
        nullable=False,
        server_default=sa.text('0'),
    )
    op.alter_column(
        'news', 'likes_count',
        existing_type=sa.Integer(),
        nullable=False,
        server_default=sa.text('0'),
    )


def downgrade() -> None:
    op.alter_column('news', 'is_pinned',   existing_type=sa.Boolean(),  nullable=True, server_default=None)
    op.alter_column('news', 'views_count', existing_type=sa.Integer(),  nullable=True, server_default=None)
    op.alter_column('news', 'likes_count', existing_type=sa.Integer(),  nullable=True, server_default=None)
