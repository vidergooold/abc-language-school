"""normalize canonical branch teacher classroom data

Revision ID: e1f2a3b4c5d6
Revises: d1f2a3b4c5e6
Create Date: 2026-05-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d1f2a3b4c5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ALLOWED_BRANCHES = (
    "МАОУ Гимназия №11 «Гармония»",
    "МАОУ Гимназия №7 «Сибирская»",
    "МАОУ ЛИТ",
    "МАОУ НГПЛ",
    "МАОУ НЭЛ",
    "МАОУ СОШ №216",
    "МАОУ СОШ №217",
    "МАОУ СОШ №218",
    "МАОУ СОШ №222",
    "МБОУ Гимназия №5",
    "МБОУ Гимназия №9",
    "МБОУ СОШ №11",
    "МБОУ СОШ №121 «Академическая»",
    "МБОУ СОШ №155",
    "МБОУ СОШ №186",
    "МБОУ СОШ №188",
    "МБОУ СОШ №195",
    "МБОУ СОШ №199",
    "МБОУ СОШ №2",
    "МБОУ СОШ №56",
    "МБОУ СОШ №61 им. Н.М.Иванова",
)

_BRANCH_RENAME_MAP = {
    "Филиал в МАОУ Гимназия 11 «Гармония»": "Гимназия 11 «Гармония»",
    "Филиал в МАОУ «Гимназия №7 «Сибирская»": "Гимназия №7 «Сибирская»",
    "Филиал в МАОУ ЛИТ": "МАОУ ЛИТ",
    "Филиал в МАОУ НГПЛ": "МАОУ НГПЛ",
    "Филиал в МАОУ НЭЛ": "МАОУ НЭЛ",
    "Филиал в МАОУ СОШ №216": "МАОУ СОШ №216",
    "Филиал в МАОУ СОШ №217": "МАОУ СОШ №217",
    "Филиал в МАОУ СОШ №218": "МАОУ СОШ №218",
    "Филиал в МАОУ «СОШ №222»": "МАОУ СОШ №222",
    "Филиал в МАОУ СОШ №222": "МАОУ СОШ №222",
    "Филиал в МБОУ Гимназия №5": "МБОУ Гимназия №5",
    "Филиал в МБОУ гимназия №5": "МБОУ Гимназия №5",
    "Филиал в МБОУ Гимназия №9": "МБОУ Гимназия №9",
    "Филиал в МБОУ СОШ №11": "МБОУ СОШ №11",
    "Филиал в МБОУ СОШ № 121 «Академическая»": "МБОУ СОШ №121 «Академическая»",
    "Филиал в МБОУ СОШ №121 «Академическая»": "МБОУ СОШ №121 «Академическая»",
    "Филиал в МБОУ СОШ №155": "МБОУ СОШ №155",
    "Филиал в МБОУ СОШ №186": "МБОУ СОШ №186",
    "Филиал в МБОУ СОШ №188": "МБОУ СОШ №188",
    "Филиал в МБОУ СОШ №56": "МБОУ СОШ №56",
}

_ALLOWED_TEACHER_NAMES = (
    "Арнгольд Валерия Евгеньевна",
    "Белова Александра Анатольевна",
    "Быковская Марина Эдуардовна",
    "Винокурова Елена Александровна",
    "Воронцова Анна Вадимовна",
    "Данилова Мария Анатольевна",
    "Евдокимова Полина Евгеньевна",
    "Зудяева Надежда Андреевна",
    "Иванова Мария Петровна",
    "Караваева Алина Денисовна",
    "Козлова Елена Геннадьевна",
    "Колесник Любовь Николаевна",
    "Куцых Марина Евгеньевна",
    "Лукьянова Светлана Ярославовна",
    "Митина Ольга Сергеевна",
    "Осинина Светлана Николаевна",
    "Пасикан Ангелина Сергеевна",
    "Переведенцева Александра Андреевна",
    "Позднякова Виктория Сергеевна",
    "Походная Алёна Игоревна",
    "Родина Татьяна Петровна",
    "Рубе Дарья Васильевна",
    "Темлякова Анна Михайловна",
    "Тихвинская Виктория Олеговна",
    "Турабова Диана Джейхуновна",
    "Федорова Анфиса Вячеславовна",
    "Фомина Снежанна Олеговна",
)

_CHINESE_TEACHERS = {
    "Лукьянова Светлана Ярославовна",
    "Темлякова Анна Михайловна",
    "Фомина Снежанна Олеговна",
}

_BRANCH_CLASSROOMS = {
    "МАОУ Гимназия №11 «Гармония»": ("каб. 113", "каб. 114"),
    "МАОУ Гимназия №7 «Сибирская»": ("каб. 119",),
    "МАОУ ЛИТ": ("каб. библ.", "каб. 116"),
    "МАОУ НГПЛ": ("каб. 205",),
    "МАОУ НЭЛ": ("каб. 312",),
    "МАОУ СОШ №216": ("каб. 317", "каб. 410"),
    "МАОУ СОШ №217": ("каб. 314А",),
    "МАОУ СОШ №218": ("каб. АВС",),
    "МАОУ СОШ №222": ("каб. 128", "каб. 311"),
    "МБОУ Гимназия №5": ("каб. 191",),
    "МБОУ Гимназия №9": ("каб. 37", "каб. 41"),
    "МБОУ СОШ №11": ("каб. 203",),
    "МБОУ СОШ №121 «Академическая»": ("каб. 214",),
    "МБОУ СОШ №155": ("каб. 426",),
    "МБОУ СОШ №186": ("каб. 211",),
    "МБОУ СОШ №188": ("каб. 409", "каб. АВС"),
    "МБОУ СОШ №195": ("каб. 415",),
    "МБОУ СОШ №199": ("каб. 218",),
    "МБОУ СОШ №2": ("каб. 307",),
    "МБОУ СОШ №56": ("каб. 3", "каб. 10"),
    "МБОУ СОШ №61 им. Н.М.Иванова": ("каб. 224",),
}

_ALLOWED_CLASSROOMS = tuple(sorted({room for rooms in _BRANCH_CLASSROOMS.values() for room in rooms}))


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


def _cleanup_branches() -> None:
    if not _table_exists("branches"):
        return

    bind = op.get_bind()

    for old_name, new_name in _BRANCH_RENAME_MAP.items():
        bind.execute(
            sa.text("UPDATE branches SET name = :new_name WHERE name = :old_name"),
            {"old_name": old_name, "new_name": new_name},
        )

    for index, branch_name in enumerate(_ALLOWED_BRANCHES, start=1):
        existing_id = bind.execute(
            sa.text("SELECT id FROM branches WHERE name = :name ORDER BY id LIMIT 1"),
            {"name": branch_name},
        ).scalar()
        if existing_id is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO branches (
                        name, address, phone, email, manager_name, manager_position,
                        working_hours, is_active, is_administrative
                    ) VALUES (
                        :name, :address, :phone, :email, :manager_name, :manager_position,
                        :working_hours, true, false
                    )
                    """
                ),
                {
                    "name": branch_name,
                    "address": "г. Новосибирск, адрес уточняется",
                    "phone": "+79139121809",
                    "email": "info@abc-school.ru",
                    "manager_name": "Андрюнина Марина Викторовна",
                    "manager_position": "Директор",
                    "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
                },
            )

    if _table_exists("lessons") and _column_exists("lessons", "branch_id"):
        for branch_name in _ALLOWED_BRANCHES:
            branch_ids = [
                row[0]
                for row in bind.execute(
                    sa.text("SELECT id FROM branches WHERE name = :name ORDER BY id"),
                    {"name": branch_name},
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

    if _column_exists("branches", "is_administrative"):
        bind.execute(
            _in_clause(
                "UPDATE branches SET is_administrative = false WHERE name IN :allowed_names",
                "allowed_names",
            ),
            {"allowed_names": _ALLOWED_BRANCHES},
        )

    obsolete_branch_ids = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT id FROM branches WHERE name NOT IN :allowed_names", "allowed_names"),
            {"allowed_names": _ALLOWED_BRANCHES},
        )
    ]

    if obsolete_branch_ids and _table_exists("lessons") and _column_exists("lessons", "branch_id"):
        bind.execute(
            _in_clause("UPDATE lessons SET branch_id = NULL WHERE branch_id IN :obsolete_ids", "obsolete_ids"),
            {"obsolete_ids": obsolete_branch_ids},
        )

    bind.execute(
        _in_clause("DELETE FROM branches WHERE name NOT IN :allowed_names", "allowed_names"),
        {"allowed_names": _ALLOWED_BRANCHES},
    )


def _cleanup_teachers() -> None:
    if not _table_exists("teachers"):
        return

    bind = op.get_bind()

    for index, full_name in enumerate(_ALLOWED_TEACHER_NAMES, start=1):
        existing_id = bind.execute(
            sa.text("SELECT id FROM teachers WHERE full_name = :full_name ORDER BY id LIMIT 1"),
            {"full_name": full_name},
        ).scalar()
        if existing_id is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO teachers (
                        full_name, email, phone, subject, language_level,
                        experience_years, bio, is_active
                    ) VALUES (
                        :full_name, :email, :phone, :subject, :language_level,
                        :experience_years, :bio, true
                    )
                    """
                ),
                {
                    "full_name": full_name,
                    "email": f"teacher{index:02d}@abc-school.ru",
                    "phone": "+79130000000",
                    "subject": "Китайский" if full_name in _CHINESE_TEACHERS else "Английский",
                    "language_level": "C1",
                    "experience_years": 5,
                    "bio": "Канонический преподаватель.",
                },
            )

    bind.execute(
        _in_clause("UPDATE teachers SET is_active = true WHERE full_name IN :allowed_names", "allowed_names"),
        {"allowed_names": _ALLOWED_TEACHER_NAMES},
    )

    fallback_teacher_id = bind.execute(
        sa.text("SELECT id FROM teachers WHERE full_name = :name ORDER BY id LIMIT 1"),
        {"name": _ALLOWED_TEACHER_NAMES[0]},
    ).scalar()

    obsolete_ids = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT id FROM teachers WHERE full_name NOT IN :allowed_names", "allowed_names"),
            {"allowed_names": _ALLOWED_TEACHER_NAMES},
        )
    ]

    if not obsolete_ids or fallback_teacher_id is None:
        return

    if _table_exists("attendance") and _column_exists("attendance", "teacher_id"):
        bind.execute(
            _in_clause(
                "UPDATE attendance SET teacher_id = :fallback_id WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"fallback_id": fallback_teacher_id, "obsolete_ids": obsolete_ids},
        )
    if _table_exists("groups") and _column_exists("groups", "teacher_id"):
        bind.execute(
            _in_clause(
                "UPDATE groups SET teacher_id = :fallback_id WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"fallback_id": fallback_teacher_id, "obsolete_ids": obsolete_ids},
        )
    if _table_exists("room_bookings") and _column_exists("room_bookings", "teacher_id"):
        bind.execute(
            _in_clause(
                "UPDATE room_bookings SET teacher_id = :fallback_id WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"fallback_id": fallback_teacher_id, "obsolete_ids": obsolete_ids},
        )
    if _table_exists("homeworks") and _column_exists("homeworks", "teacher_id"):
        bind.execute(
            _in_clause(
                "UPDATE homeworks SET teacher_id = :fallback_id WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"fallback_id": fallback_teacher_id, "obsolete_ids": obsolete_ids},
        )
    if _table_exists("lessons") and _column_exists("lessons", "teacher_id"):
        bind.execute(
            _in_clause(
                "UPDATE lessons SET teacher_id = :fallback_id WHERE teacher_id IN :obsolete_ids",
                "obsolete_ids",
            ),
            {"fallback_id": fallback_teacher_id, "obsolete_ids": obsolete_ids},
        )

    obsolete_emails = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT email FROM teachers WHERE id IN :obsolete_ids", "obsolete_ids"),
            {"obsolete_ids": obsolete_ids},
        )
    ]

    bind.execute(
        _in_clause("DELETE FROM teachers WHERE id IN :obsolete_ids", "obsolete_ids"),
        {"obsolete_ids": obsolete_ids},
    )

    if _table_exists("users") and obsolete_emails:
        bind.execute(
            _in_clause("DELETE FROM users WHERE email IN :obsolete_emails", "obsolete_emails"),
            {"obsolete_emails": obsolete_emails},
        )


def _cleanup_classrooms() -> None:
    if not _table_exists("classrooms"):
        return

    bind = op.get_bind()

    for room_name in _ALLOWED_CLASSROOMS:
        existing_id = bind.execute(
            sa.text("SELECT id FROM classrooms WHERE name = :name ORDER BY id LIMIT 1"),
            {"name": room_name},
        ).scalar()
        if existing_id is None:
            bind.execute(
                sa.text(
                    """
                    INSERT INTO classrooms (
                        name, capacity, floor, has_projector, has_whiteboard, is_active
                    ) VALUES (
                        :name, 12, NULL, false, true, true
                    )
                    """
                ),
                {"name": room_name},
            )

    fallback_classroom_id = bind.execute(
        sa.text("SELECT id FROM classrooms WHERE name = :name ORDER BY id LIMIT 1"),
        {"name": _ALLOWED_CLASSROOMS[0]},
    ).scalar()

    obsolete_classroom_ids = [
        row[0]
        for row in bind.execute(
            _in_clause("SELECT id FROM classrooms WHERE name NOT IN :allowed_names", "allowed_names"),
            {"allowed_names": _ALLOWED_CLASSROOMS},
        )
    ]

    if obsolete_classroom_ids and fallback_classroom_id is not None:
        if _table_exists("lessons") and _column_exists("lessons", "classroom_id"):
            bind.execute(
                _in_clause(
                    "UPDATE lessons SET classroom_id = :fallback_id WHERE classroom_id IN :obsolete_ids",
                    "obsolete_ids",
                ),
                {"fallback_id": fallback_classroom_id, "obsolete_ids": obsolete_classroom_ids},
            )
        if _table_exists("room_bookings") and _column_exists("room_bookings", "classroom_id"):
            bind.execute(
                _in_clause(
                    "UPDATE room_bookings SET classroom_id = :fallback_id WHERE classroom_id IN :obsolete_ids",
                    "obsolete_ids",
                ),
                {"fallback_id": fallback_classroom_id, "obsolete_ids": obsolete_classroom_ids},
            )

    bind.execute(
        _in_clause("DELETE FROM classrooms WHERE name NOT IN :allowed_names", "allowed_names"),
        {"allowed_names": _ALLOWED_CLASSROOMS},
    )


def _normalize_lesson_branch_classroom_links() -> None:
    if not _table_exists("lessons") or not _column_exists("lessons", "classroom_id") or not _column_exists("lessons", "branch_id"):
        return

    bind = op.get_bind()

    for branch_name, classrooms in _BRANCH_CLASSROOMS.items():
        branch_id = bind.execute(
            sa.text("SELECT id FROM branches WHERE name = :name ORDER BY id LIMIT 1"),
            {"name": branch_name},
        ).scalar()
        if branch_id is None:
            continue

        classroom_ids = [
            row[0]
            for row in bind.execute(
                _in_clause("SELECT id FROM classrooms WHERE name IN :room_names ORDER BY id", "room_names"),
                {"room_names": classrooms},
            )
        ]
        if not classroom_ids:
            continue

        primary_classroom_id = classroom_ids[0]
        bind.execute(
            _in_clause(
                """
                UPDATE lessons
                SET classroom_id = :primary_classroom_id
                WHERE branch_id = :branch_id
                  AND classroom_id NOT IN :allowed_classroom_ids
                """,
                "allowed_classroom_ids",
            ),
            {
                "primary_classroom_id": primary_classroom_id,
                "branch_id": branch_id,
                "allowed_classroom_ids": classroom_ids,
            },
        )


def upgrade() -> None:
    _cleanup_branches()
    _cleanup_teachers()
    _cleanup_classrooms()
    _normalize_lesson_branch_classroom_links()


def downgrade() -> None:
    # Irreversible data-normalization migration: deleted/rewired rows cannot be restored safely.
    pass
