"""
Обновление существующих преподавателей: телефон, предмет, уровень языка,
и назначение в группы через teacher_groups.

Запуск:
    cd backend && python seed_teacher_details.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Group
from app.models.teacher import Teacher, TeacherGroup

TEACHER_DATA = [
    {"last_name": "Темлякова",    "phone": "+7-913-000-0101", "subject": "Английский", "language_level": "C2"},
    {"last_name": "Федорова",     "phone": "+7-913-000-0102", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Позднякова",   "phone": "+7-913-000-0103", "subject": "Английский", "language_level": "C2"},
    {"last_name": "Фомина",       "phone": "+7-913-000-0104", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Колесник",     "phone": "+7-913-000-0105", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Данилова",     "phone": "+7-913-000-0106", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Зудяева",      "phone": "+7-913-000-0107", "subject": "Английский", "language_level": "B2"},
    {"last_name": "Куцых",        "phone": "+7-913-000-0108", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Винокурова",   "phone": "+7-913-000-0109", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Евдокимова",   "phone": "+7-913-000-0110", "subject": "Английский", "language_level": "C2"},
    {"last_name": "Походная",     "phone": "+7-913-000-0111", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Митина",       "phone": "+7-913-000-0112", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Лукьянова",    "phone": "+7-913-000-0113", "subject": "Английский", "language_level": "C2"},
    {"last_name": "Пасикан",      "phone": "+7-913-000-0114", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Козлова",      "phone": "+7-913-000-0115", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Осинина",      "phone": "+7-913-000-0116", "subject": "Английский", "language_level": "B2"},
    {"last_name": "Турабова",     "phone": "+7-913-000-0117", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Белова",       "phone": "+7-913-000-0118", "subject": "Английский", "language_level": "C2"},
    {"last_name": "Родина",       "phone": "+7-913-000-0119", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Переведенцева","phone": "+7-913-000-0120", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Тихвинская",   "phone": "+7-913-000-0121", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Рубе",         "phone": "+7-913-000-0122", "subject": "Английский", "language_level": "B2"},
    {"last_name": "Арнгольд",     "phone": "+7-913-000-0123", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Быковская",    "phone": "+7-913-000-0124", "subject": "Немецкий",   "language_level": "C2"},
    {"last_name": "Воронцова",    "phone": "+7-913-000-0125", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Алексеева",    "phone": "+7-913-000-0126", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Калужина",     "phone": "+7-913-000-0127", "subject": "Китайский",  "language_level": "C2"},
    {"last_name": "Кривилева",    "phone": "+7-913-000-0128", "subject": "Английский", "language_level": "C1"},
    {"last_name": "Иванова",      "phone": "+7-913-000-0129", "subject": "Английский", "language_level": "C1"},
]


async def seed_teacher_details() -> None:
    await init_db()

    updated_teachers = 0
    skipped_teachers = 0
    not_found = []
    total_groups_assigned = 0

    async with AsyncSessionLocal() as session:
        for entry in TEACHER_DATA:
            last_name = entry["last_name"]

            result = await session.execute(
                select(Teacher).where(
                    Teacher.full_name.ilike(f"%{last_name}%")
                )
            )
            teachers = result.scalars().all()

            if not teachers:
                not_found.append(last_name)
                continue

            if len(teachers) > 1:
                names = ", ".join(t.full_name for t in teachers)
                print(f"  [WARNING] Multiple matches for '{last_name}': {names} — updating all")

            for teacher in teachers:
                changed = False

                if not teacher.phone:
                    teacher.phone = entry["phone"]
                    changed = True

                if not teacher.subject:
                    teacher.subject = entry["subject"]
                    changed = True

                if not teacher.language_level:
                    teacher.language_level = entry["language_level"]
                    changed = True

                if changed:
                    session.add(teacher)
                    updated_teachers += 1
                else:
                    skipped_teachers += 1

                # Assign teacher to groups where groups.teacher_id = teacher.id
                # Uses INSERT ... ON CONFLICT DO NOTHING for idempotency
                groups_result = await session.execute(
                    select(Group.id).where(Group.teacher_id == teacher.id)
                )
                group_ids = groups_result.scalars().all()

                if group_ids:
                    stmt = pg_insert(TeacherGroup).values(
                        [{"teacher_id": teacher.id, "group_id": gid} for gid in group_ids]
                    ).on_conflict_do_nothing(constraint="uq_teacher_group")
                    result_proxy = await session.execute(stmt)
                    total_groups_assigned += result_proxy.rowcount

        await session.commit()

    print("\n===== seed_teacher_details: Summary =====")
    print(f"  Teachers updated:        {updated_teachers}")
    print(f"  Teachers already filled: {skipped_teachers}")
    print(f"  Teacher-group links added: {total_groups_assigned}")
    if not_found:
        print(f"  Not found ({len(not_found)}): {', '.join(not_found)}")
    print("=========================================\n")


if __name__ == "__main__":
    asyncio.run(seed_teacher_details())
