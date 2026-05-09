"""cleanup obsolete branches

Revision ID: a8b9c0d1e2f3
Revises: f7a8b9c0d1e2
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8b9c0d1e2f3"
down_revision: Union[str, Sequence[str], None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ALLOWED_BRANCHES = (
    "Офис",
    "Филиал в МАОУ Гимназия 11 «Гармония»",
    "Филиал в МБОУ СОШ №56",
    "Филиал в МБОУ СОШ №188",
    "Филиал в МАОУ СОШ №218",
    "Филиал в МАОУ «Гимназия №7 «Сибирская»",
    "Филиал в МБОУ СОШ №186",
    "Филиал в МБОУ СОШ №11",
    "Филиал в МБОУ СОШ №2",
    "Филиал в МБОУ СОШ №199",
    "Филиал в МБОУ СОШ №155",
    "Филиал в МАОУ ЛИТ",
    "Филиал в МАОУ НГПЛ",
    "Филиал в МБОУ Гимназия №9",
    "Филиал в МАОУ НЭЛ",
    "Филиал в МАОУ СОШ №216",
    "Филиал в МАОУ СОШ №217",
    "Филиал в МБОУ гимназия №5",
    "Филиал в МБОУ СОШ № 121 «Академическая»",
    "Филиал в МБОУ СОШ № 61 им. Н.М.Иванова",
    "Филиал в МАОУ «СОШ №222»",
)

_RENAME_MAP = {
    "Офис (главный)": "Офис",
    "Филиал в МБОУ Гимназия №5": "Филиал в МБОУ гимназия №5",
    "Филиал в МБОУ СОШ №121 «Академическая»": "Филиал в МБОУ СОШ № 121 «Академическая»",
    "Филиал в МБОУ СОШ №61 им. Н.М. Иванова": "Филиал в МБОУ СОШ № 61 им. Н.М.Иванова",
    "Филиал в МАОУ СОШ №222": "Филиал в МАОУ «СОШ №222»",
}


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _in_clause(statement: str, parameter_name: str) -> sa.sql.elements.TextClause:
    return sa.text(statement).bindparams(sa.bindparam(parameter_name, expanding=True))


def upgrade() -> None:
    if not _table_exists("branches"):
        return

    bind = op.get_bind()
    has_lessons = _table_exists("lessons")

    for old_name, new_name in _RENAME_MAP.items():
        bind.execute(
            sa.text("UPDATE branches SET name = :new_name WHERE name = :old_name"),
            {"old_name": old_name, "new_name": new_name},
        )

    if has_lessons:
        for branch_name in _ALLOWED_BRANCHES:
            branch_ids = [
                row[0]
                for row in bind.execute(
                    sa.text("SELECT id FROM branches WHERE name = :branch_name ORDER BY id"),
                    {"branch_name": branch_name},
                )
            ]
            if len(branch_ids) <= 1:
                continue

            primary_id = branch_ids[0]
            duplicate_ids = branch_ids[1:]
            bind.execute(
                _in_clause(
                    "UPDATE lessons SET branch_id = :primary_id WHERE branch_id IN :duplicate_ids",
                    "duplicate_ids",
                ),
                {"primary_id": primary_id, "duplicate_ids": duplicate_ids},
            )
            bind.execute(
                _in_clause("DELETE FROM branches WHERE id IN :duplicate_ids", "duplicate_ids"),
                {"duplicate_ids": duplicate_ids},
            )

    bind.execute(
        _in_clause("UPDATE branches SET is_active = true WHERE name IN :allowed_names", "allowed_names"),
        {"allowed_names": _ALLOWED_BRANCHES},
    )

    obsolete_branch_ids = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT id FROM branches WHERE name NOT IN :allowed_names", "allowed_names"),
            {"allowed_names": _ALLOWED_BRANCHES},
        )
    ]

    if obsolete_branch_ids and has_lessons:
        bind.execute(
            _in_clause("UPDATE lessons SET branch_id = NULL WHERE branch_id IN :obsolete_ids", "obsolete_ids"),
            {"obsolete_ids": obsolete_branch_ids},
        )

    bind.execute(
        _in_clause("DELETE FROM branches WHERE name NOT IN :allowed_names", "allowed_names"),
        {"allowed_names": _ALLOWED_BRANCHES},
    )


def downgrade() -> None:
    pass
