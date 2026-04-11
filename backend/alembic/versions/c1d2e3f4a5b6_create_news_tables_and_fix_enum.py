"""create_news_tables_and_fix_enum

Revision ID: c1d2e3f4a5b6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-12 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Добавить новые значения в ENUM newsstatus (review, scheduled)
    op.execute("ALTER TYPE newsstatus ADD VALUE IF NOT EXISTS 'review'")
    op.execute("ALTER TYPE newsstatus ADD VALUE IF NOT EXISTS 'scheduled'")

    # 2. Создать таблицу news_categories
    op.execute("""
        CREATE TABLE IF NOT EXISTS news_categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) NOT NULL UNIQUE,
            color VARCHAR(20),
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_news_categories_id ON news_categories (id)")

    # 3. Создать таблицу news_likes
    op.execute("""
        CREATE TABLE IF NOT EXISTS news_likes (
            id SERIAL PRIMARY KEY,
            news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT NOW(),
            UNIQUE (news_id, user_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_news_likes_id ON news_likes (id)")

    # 4. Создать таблицу news_status_history
    op.execute("""
        CREATE TABLE IF NOT EXISTS news_status_history (
            id SERIAL PRIMARY KEY,
            news_id INTEGER NOT NULL REFERENCES news(id) ON DELETE CASCADE,
            from_status newsstatus,
            to_status newsstatus NOT NULL,
            changed_by INTEGER REFERENCES users(id),
            comment TEXT,
            changed_at TIMESTAMP DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_news_status_history_id ON news_status_history (id)")

    # 5. Добавить колонку published_at в news если её нет
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='news' AND column_name='published_at'
            ) THEN
                ALTER TABLE news ADD COLUMN published_at TIMESTAMP;
            END IF;
        END $$;
    """)

    # 6. Добавить колонку image_url в news если её нет
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='news' AND column_name='image_url'
            ) THEN
                ALTER TABLE news ADD COLUMN image_url VARCHAR(500);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS news_status_history")
    op.execute("DROP TABLE IF EXISTS news_likes")
    op.execute("DROP TABLE IF EXISTS news_categories")
