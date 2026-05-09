"""fix_forms_id_sequences

Revision ID: ea21b92c0a50
Revises: f7a8b9c0d1e2
Create Date: 2026-05-09 10:16:50.646462
"""
import re
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ea21b92c0a50'
down_revision: Union[str, Sequence[str], None] = 'f7a8b9c0d1e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_SAFE_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")
_FORM_TABLES = (
    "adult_forms",
    "child_forms",
    "preschool_forms",
    "teacher_forms",
    "testing_forms",
    "feedback_forms",
    "tax_forms",
)


def _fix_id_sequence(table: str) -> None:
    if not _SAFE_IDENTIFIER.match(table):
        raise ValueError(f"Unsafe table name: {table!r}")
    seq = f"{table}_id_seq"
    op.execute(
        f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = current_schema()
                  AND table_name = '{table}'
            ) THEN
                CREATE SEQUENCE IF NOT EXISTS {seq};

                PERFORM setval(
                    '{seq}',
                    COALESCE((SELECT MAX(id) FROM {table}), 0) + 1,
                    false
                );

                ALTER TABLE {table}
                    ALTER COLUMN id SET DEFAULT nextval('{seq}');

                ALTER SEQUENCE {seq}
                    OWNED BY {table}.id;
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    for table in _FORM_TABLES:
        _fix_id_sequence(table)


def downgrade() -> None:
    # Keep sequence/default intact to avoid breaking inserts on rollback.
    pass
