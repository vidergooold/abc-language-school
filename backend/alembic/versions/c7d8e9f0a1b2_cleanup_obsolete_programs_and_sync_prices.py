"""cleanup obsolete programs and sync prices

Revision ID: c7d8e9f0a1b2
Revises: b1c2d3e4f5a6
Create Date: 2026-05-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CANONICAL_COURSES = (
    ("Дошкольники", 2700, "Английский", "beginner", "children"),
    ("FH1, AS1", 3100, "Английский", "beginner", "school"),
    ("AS2, AS3, AS4", 3500, "Английский", "elementary", "school"),
    ("GWA1+, GWA2", 4250, "Английский", "pre_intermediate", "school"),
    ("GWB1, GWB1+, GWB2, GWB2+, GWC1", 4900, "Английский", "upper_intermediate", "school"),
    ("Взрослые групповые", 6500, "Английский", "intermediate", "adults"),
    ("Мини-группа (2 чел.)", 6600, "Английский", "intermediate", "adults"),
    ("Индивидуальные занятия", 1100, "Английский", "intermediate", "adults"),
    ("Китайский язык", 1200, "Китайский", "beginner", "adults"),
)

_CANONICAL_PROGRAM_NAMES = tuple(name for name, *_ in _CANONICAL_COURSES)
_PROGRAM_TARGET_GROUPS = {
    "Дошкольники": "дошкольники",
    "FH1, AS1": "школьники",
    "AS2, AS3, AS4": "школьники",
    "GWA1+, GWA2": "школьники",
    "GWB1, GWB1+, GWB2, GWB2+, GWC1": "школьники",
    "Взрослые групповые": "взрослые",
    "Мини-группа (2 чел.)": "взрослые",
    "Индивидуальные занятия": "взрослые",
    "Китайский язык": "взрослые",
}
_COURSE_REFERENCE_TABLES = ("groups", "enrollments", "materials", "reviews", "waitlist")

_PROGRAM_RENAME_MAP = {
    "English Start A1": "FH1, AS1",
    "English Progress A2": "AS2, AS3, AS4",
    "Английский для школьников": "AS2, AS3, AS4",
    "Разговорный английский для взрослых": "Взрослые групповые",
}


_COURSELEVEL_ENUM_VALUES = (
    "beginner",
    "elementary",
    "pre_intermediate",
    "intermediate",
    "upper_intermediate",
    "advanced",
    "proficiency",
)


def _ensure_enum_values() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    existing = {
        row
        for row in bind.execute(
            sa.text(
                "SELECT enumlabel FROM pg_enum e "
                "JOIN pg_type t ON e.enumtypid = t.oid "
                "WHERE t.typname = 'courselevel'"
            )
        )
    }
    missing = [v for v in _COURSELEVEL_ENUM_VALUES if v not in existing]
    if not missing:
        return
    raw_conn = bind.engine.raw_connection()
    try:
        raw_conn.set_isolation_level(0)  # AUTOCOMMIT
        with raw_conn.cursor() as cur:
            for value in missing:
                cur.execute(f"ALTER TYPE courselevel ADD VALUE IF NOT EXISTS '{value}'")
    finally:
        raw_conn.set_isolation_level(1)
        raw_conn.close()


def _table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(column["name"] == column_name for column in inspector.get_columns(table_name))


def _in_clause(statement: str, parameter_name: str) -> sa.sql.elements.TextClause:
    return sa.text(statement).bindparams(sa.bindparam(parameter_name, expanding=True))


def _cleanup_educational_programs() -> None:
    if not _table_exists("educational_programs"):
        return

    bind = op.get_bind()
    has_lessons = _column_exists("lessons", "program_id")

    for old_name, new_name in _PROGRAM_RENAME_MAP.items():
        bind.execute(
            sa.text(
                """
                UPDATE educational_programs
                SET name = :new_name
                WHERE name = :old_name
                """
            ),
            {"old_name": old_name, "new_name": new_name},
        )

    for name in _CANONICAL_PROGRAM_NAMES:
        existing_id = bind.execute(
            sa.text("SELECT id FROM educational_programs WHERE name = :name ORDER BY id LIMIT 1"),
            {"name": name},
        ).scalar()
        if existing_id is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO educational_programs
                        (name, code, language, target_group, is_active)
                    VALUES
                        (:name, :code, :language, :target_group, true)
                    """
                ),
                {
                    "name": name,
                    "code": None,
                    "language": "Китайский" if name == "Китайский язык" else "Английский",
                    "target_group": _PROGRAM_TARGET_GROUPS[name],
                },
            )

    if has_lessons:
        for name in _CANONICAL_PROGRAM_NAMES:
            duplicate_ids = [
                row[0]
                for row in bind.execute(
                    sa.text("SELECT id FROM educational_programs WHERE name = :name ORDER BY id"),
                    {"name": name},
                )
            ]
            if len(duplicate_ids) <= 1:
                continue
            primary_id = duplicate_ids[0]
            stale_ids = duplicate_ids[1:]
            bind.execute(
                _in_clause(
                    "UPDATE lessons SET program_id = :primary_id WHERE program_id IN :stale_ids",
                    "stale_ids",
                ),
                {"primary_id": primary_id, "stale_ids": stale_ids},
            )
            bind.execute(
                _in_clause("DELETE FROM educational_programs WHERE id IN :stale_ids", "stale_ids"),
                {"stale_ids": stale_ids},
            )

    obsolete_program_ids = [
        row[0]
        for row in bind.execute(
            _in_clause(
                "SELECT id FROM educational_programs WHERE name NOT IN :allowed_names",
                "allowed_names",
            ),
            {"allowed_names": _CANONICAL_PROGRAM_NAMES},
        )
    ]

    if obsolete_program_ids and has_lessons:
        bind.execute(
            _in_clause(
                "UPDATE lessons SET program_id = NULL WHERE program_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"obsolete_ids": obsolete_program_ids},
        )

    bind.execute(
        _in_clause(
            "DELETE FROM educational_programs WHERE name NOT IN :allowed_names",
            "allowed_names",
        ),
        {"allowed_names": _CANONICAL_PROGRAM_NAMES},
    )


def _cleanup_courses_and_prices() -> None:
    if not _table_exists("courses") or not _column_exists("courses", "price_per_month"):
        return

    bind = op.get_bind()
    canonical_names = tuple(name for name, *_ in _CANONICAL_COURSES)

    for name, price, language, level, category in _CANONICAL_COURSES:
        existing = bind.execute(
            sa.text("SELECT id FROM courses WHERE name = :name ORDER BY id LIMIT 1"),
            {"name": name},
        ).scalar()
        if existing is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO courses (
                        name, language, level, category, price_per_month, lessons_per_week, duration_months, max_students, is_active
                    )
                    VALUES (
                        :name, :language, :level, :category, :price_per_month, 2, 9, 8, true
                    )
                    """
                ),
                {
                    "name": name,
                    "language": language,
                    "level": level,
                    "category": category,
                    "price_per_month": price,
                },
            )
        else:
            bind.execute(
                sa.text(
                    """
                    UPDATE courses
                    SET price_per_month = :price_per_month,
                        language = :language,
                        level = :level,
                        category = :category,
                        is_active = true
                    WHERE name = :name
                    """
                ),
                {
                    "name": name,
                    "price_per_month": price,
                    "language": language,
                    "level": level,
                    "category": category,
                },
            )

    fallback_course_id = bind.execute(
        sa.text("SELECT id FROM courses WHERE name = :name ORDER BY id LIMIT 1"),
        {"name": "FH1, AS1"},
    ).scalar()

    if fallback_course_id is None:
        return

    for name in canonical_names:
        duplicate_ids = [
            row[0]
            for row in bind.execute(
                sa.text("SELECT id FROM courses WHERE name = :name ORDER BY id"),
                {"name": name},
            )
        ]
        if len(duplicate_ids) <= 1:
            continue
        primary_id = duplicate_ids[0]
        stale_ids = duplicate_ids[1:]
        for table_name in _COURSE_REFERENCE_TABLES:
            if not _column_exists(table_name, "course_id"):
                continue
            bind.execute(
                _in_clause(
                    f"UPDATE {table_name} SET course_id = :primary_id WHERE course_id IN :stale_ids",
                    "stale_ids",
                ),
                {"primary_id": primary_id, "stale_ids": stale_ids},
            )
        bind.execute(
            _in_clause("DELETE FROM courses WHERE id IN :stale_ids", "stale_ids"),
            {"stale_ids": stale_ids},
        )

    obsolete_course_ids = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT id FROM courses WHERE name NOT IN :allowed_names", "allowed_names"),
            {"allowed_names": canonical_names},
        )
    ]

    if obsolete_course_ids:
        for table_name in _COURSE_REFERENCE_TABLES:
            if not _column_exists(table_name, "course_id"):
                continue
            bind.execute(
                _in_clause(
                    f"UPDATE {table_name} SET course_id = :fallback_id WHERE course_id IN :obsolete_ids",
                    "obsolete_ids",
                ),
                {"fallback_id": fallback_course_id, "obsolete_ids": obsolete_course_ids},
            )
        bind.execute(
            _in_clause("DELETE FROM courses WHERE id IN :obsolete_ids", "obsolete_ids"),
            {"obsolete_ids": obsolete_course_ids},
        )


def upgrade() -> None:
    _ensure_enum_values()
    _cleanup_educational_programs()
    _cleanup_courses_and_prices()


def downgrade() -> None:
    pass
