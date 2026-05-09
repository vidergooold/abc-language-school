"""ensure_news_status_history_id_default

Revision ID: f7a8b9c0d1e2
Revises: e6f7a8b9c0d2
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op

revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, Sequence[str], None] = "e6f7a8b9c0d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = 'news_status_history'
            ) THEN
                CREATE SEQUENCE IF NOT EXISTS news_status_history_id_seq;

                PERFORM setval(
                    'news_status_history_id_seq',
                    COALESCE((SELECT MAX(id) FROM news_status_history), 0) + 1,
                    false
                );

                ALTER TABLE news_status_history
                    ALTER COLUMN id SET DEFAULT nextval('news_status_history_id_seq'::regclass);

                ALTER SEQUENCE news_status_history_id_seq
                    OWNED BY news_status_history.id;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    # Keep sequence/default intact to avoid breaking inserts on rollback.
    pass
