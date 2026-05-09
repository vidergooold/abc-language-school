"""cleanup obsolete teachers

Revision ID: b1c2d3e4f5a6
Revises: a8b9c0d1e2f3
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a8b9c0d1e2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ALLOWED_TEACHER_NAMES = (
    "Белова Александра Анатольевна",
    "Григорьева Дарья Дмитриевна",
    "Данилова Мария Анатольевна",
    "Евдокимова Полина Евгеньевна",
    "Колесник Любовь Николаевна",
    "Куцых Марина Евгеньевна",
    "Кривилева Галина Александровна",
    "Лукьянова Светлана Ярославовна",
    "Митина Ольга Сергеевна",
    "Осинина Светлана Николаевна",
    "Пасикан Ангелина Сергеевна",
    "Переведенцева Александра Андреевна",
    "Позднякова Виктория Сергеевна",
    "Рубе Дарья Васильевна",
    "Стафеева Яна Викторовна",
    "Темлякова Анна Михайловна",
    "Федорова Анфиса Вячеславовна",
    "Фомина Снежанна Олеговна",
)


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _in_clause(statement: str, parameter_name: str) -> sa.sql.elements.TextClause:
    return sa.text(statement).bindparams(sa.bindparam(parameter_name, expanding=True))


def upgrade() -> None:
    if not _table_exists("teachers"):
        return

    bind = op.get_bind()

    obsolete_ids = [
        row[0]
        for row in bind.execute(
            _in_clause(
                "SELECT id FROM teachers WHERE full_name NOT IN :allowed_names",
                "allowed_names",
            ),
            {"allowed_names": _ALLOWED_TEACHER_NAMES},
        )
    ]

    if not obsolete_ids:
        return

    obsolete_emails = [
        row[0]
        for row in bind.execute(
            _in_clause(
                "SELECT email FROM teachers WHERE id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )
    ]

    # NULL out nullable foreign keys in related tables
    if _table_exists("attendance"):
        bind.execute(
            _in_clause(
                "UPDATE attendance SET teacher_id = NULL WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )
    if _table_exists("groups"):
        bind.execute(
            _in_clause(
                "UPDATE groups SET teacher_id = NULL WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )
    if _table_exists("room_bookings"):
        bind.execute(
            _in_clause(
                "UPDATE room_bookings SET teacher_id = NULL WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )

    # Delete records in tables where teacher_id is NOT NULL
    if _table_exists("homeworks"):
        bind.execute(
            _in_clause(
                "DELETE FROM homeworks WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )
    if _table_exists("lessons"):
        bind.execute(
            _in_clause(
                "DELETE FROM lessons WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_ids},
        )

    # Delete obsolete teachers (teacher_groups cascade-deleted automatically)
    bind.execute(
        _in_clause("DELETE FROM teachers WHERE id IN :obsolete_ids", "obsolete_ids"),
        {"obsolete_ids": obsolete_ids},
    )

    # Delete corresponding user accounts if they exist
    if _table_exists("users") and obsolete_emails:
        bind.execute(
            _in_clause("DELETE FROM users WHERE email IN :obsolete_emails", "obsolete_emails"),
            {"obsolete_emails": obsolete_emails},
        )


def downgrade() -> None:
    pass
