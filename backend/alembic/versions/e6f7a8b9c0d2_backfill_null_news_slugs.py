"""backfill_null_news_slugs

Revision ID: e6f7a8b9c0d2
Revises: d4e5f6a7b8c9
Create Date: 2026-05-09
"""
import re
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'e6f7a8b9c0d2'
down_revision: Union[str, Sequence[str], None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slugify(value: str) -> str:
    slug = (value or "").lower().strip()
    slug = re.sub(r'[^а-яёa-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    return slug


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, title FROM news WHERE slug IS NULL")).mappings().all()
    payload = [{"id": row["id"], "slug": f"{_slugify(row['title'])}-{row['id']}"} for row in rows]
    if payload:
        bind.execute(
            sa.text("UPDATE news SET slug = :slug WHERE id = :id AND slug IS NULL"),
            payload,
        )


def downgrade() -> None:
    pass
