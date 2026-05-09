"""fix_news_status_history_id_sequence

Ensure news_status_history.id has a proper auto-increment sequence so that
INSERT statements without an explicit id value never raise an IntegrityError.

Root cause: migration c1d2e3f4a5b6 used ``CREATE TABLE IF NOT EXISTS`` with a
raw SERIAL keyword.  If the table already existed (e.g. from a prior
create_all() run that did not attach a sequence), the SERIAL clause was silently
skipped, leaving ``id`` as ``INTEGER NOT NULL`` with no DEFAULT – any INSERT
that omits ``id`` then raises
  "null value in column id of relation news_status_history violates not-null
   constraint".

This migration is idempotent: it creates the sequence only when missing and
renames ``changed_at`` → ``created_at`` only when the rename is needed.

Revision ID: d4e5f6a7b8c9
Revises: 9b1c_manual_messages_drop_unused
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = '9b1c_manual_messages_drop_unused'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Ensure the sequence exists ────────────────────────────────────────
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class
                WHERE relname = 'news_status_history_id_seq'
                  AND relkind = 'S'
            ) THEN
                CREATE SEQUENCE news_status_history_id_seq;
            END IF;
        END $$;
    """)

    # ── 2. Sync sequence value to the current max id (safe for empty table) ──
    op.execute("""
        SELECT setval(
            'news_status_history_id_seq',
            COALESCE((SELECT MAX(id) FROM news_status_history), 0) + 1,
            false
        );
    """)

    # ── 3. Attach the sequence as the column DEFAULT (idempotent) ─────────────
    op.execute("""
        ALTER TABLE news_status_history
            ALTER COLUMN id SET DEFAULT nextval('news_status_history_id_seq');
    """)

    # ── 4. Claim ownership so the sequence is dropped with the table ──────────
    op.execute("""
        ALTER SEQUENCE news_status_history_id_seq
            OWNED BY news_status_history.id;
    """)

    # ── 5. Rename changed_at → created_at if the migration column name was used
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
    # NOTE: we do not drop the sequence on downgrade because it may still be
    # needed by existing rows; dropping it would break the id default again.
