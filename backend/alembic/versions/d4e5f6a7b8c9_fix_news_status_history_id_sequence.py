"""fix_news_status_history_id_sequence

Ensure that news_status_history, news_categories, and news_likes all have a
proper auto-increment sequence on their ``id`` column so that INSERT statements
without an explicit id value never raise an IntegrityError.

Root cause: migration c1d2e3f4a5b6 used ``CREATE TABLE IF NOT EXISTS`` with a
raw SERIAL keyword for three tables.  If any of those tables already existed
(e.g. from a prior create_all() run that did not attach a sequence), the SERIAL
clause was silently skipped, leaving ``id`` as ``INTEGER NOT NULL`` with no
DEFAULT – any INSERT that omits ``id`` then raises
  "null value in column id of relation <table> violates not-null constraint".

This migration is fully idempotent: each sequence is created only when missing,
the DEFAULT is set unconditionally (SET DEFAULT is a no-op if already correct),
and the ``changed_at`` → ``created_at`` rename is performed only when needed.

Revision ID: d4e5f6a7b8c9
Revises: 9b1c_manual_messages_drop_unused
Create Date: 2026-05-09
"""
import re
from typing import Sequence, Union

from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = '9b1c_manual_messages_drop_unused'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SAFE_IDENTIFIER = re.compile(r'^[a-z][a-z0-9_]*$')


def _fix_id_sequence(table: str) -> None:
    """Idempotently attach an auto-increment sequence to <table>.id.

    Mirrors what PostgreSQL's SERIAL shorthand does:
      1. Create the sequence if it doesn't exist.
      2. Advance the sequence past the current MAX(id) so there are no clashes.
      3. Set the column DEFAULT to nextval(<seq>).
      4. Transfer ownership so the sequence is dropped with the table.
    """
    if not _SAFE_IDENTIFIER.match(table):
        raise ValueError(f"Unsafe table name: {table!r}")
    seq = f"{table}_id_seq"
    op.execute(f"""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class
                WHERE relname = '{seq}' AND relkind = 'S'
            ) THEN
                CREATE SEQUENCE {seq};
            END IF;
        END $$;
    """)
    op.execute(f"""
        SELECT setval(
            '{seq}',
            COALESCE((SELECT MAX(id) FROM {table}), 0) + 1,
            false
        );
    """)
    op.execute(f"""
        ALTER TABLE {table}
            ALTER COLUMN id SET DEFAULT nextval('{seq}');
    """)
    op.execute(f"""
        ALTER SEQUENCE {seq} OWNED BY {table}.id;
    """)


def upgrade() -> None:
    # ── Fix all three tables created via CREATE TABLE IF NOT EXISTS in c1d2e3f4a5b6
    _fix_id_sequence("news_status_history")
    _fix_id_sequence("news_categories")
    _fix_id_sequence("news_likes")

    # ── Rename changed_at → created_at if the old column name was used ────────
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name  = 'news_status_history'
                  AND column_name = 'changed_at'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name  = 'news_status_history'
                  AND column_name = 'created_at'
            ) THEN
                ALTER TABLE news_status_history
                    RENAME COLUMN changed_at TO created_at;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Restore changed_at name if it was renamed (best-effort)
    op.execute("""
        DO $$ BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name  = 'news_status_history'
                  AND column_name = 'created_at'
            ) AND NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name  = 'news_status_history'
                  AND column_name = 'changed_at'
            ) THEN
                ALTER TABLE news_status_history
                    RENAME COLUMN created_at TO changed_at;
            END IF;
        END $$;
    """)
    # NOTE: sequences are intentionally not dropped on downgrade — removing them
    # would break the id DEFAULT for any rows already present.
