"""backfill_null_news_slugs

Revision ID: e6f7a8b9c0d2
Revises: d4e5f6a7b8c9
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'e6f7a8b9c0d2'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        """
        UPDATE news
        SET slug = regexp_replace(
            regexp_replace(lower(trim(title)), '[^а-яёa-z0-9\\s-]', '', 'g'),
            '\\s+',
            '-',
            'g'
        ) || '-' || id::text
        WHERE slug IS NULL
        """
    )


def downgrade() -> None:
    pass
