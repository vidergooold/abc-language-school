"""seed_student_groups.py

Наполняет таблицу student_groups для КАЖДОЙ группы из таблицы groups.
После запуска матрица посещаемости перестаёт показывать
«В выбранной группе пока нет активных студентов».

Запуск:
    cd backend
    python seed_student_groups.py
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Group, StudentGroup
from app.models.student import Student, StudentType


PRESCHOOL_AND_JUNIOR_GROUPS = {"Дошкольники", "FH1", "AS1", "AS2"}
TEEN_GROUPS = {"AS3", "AS4", "GWA1+", "GWA2"}
ADULT_GROUPS = {
    "GWA1+",
    "GWA2",
    "GWB1",
    "GWB1+",
    "GWB2",
    "GWB2+",
    "GWC1",
    "Взрослые групповые",
    "Китайский",
}


def _preferred_student_type(group_name: str) -> list[str]:
    if group_name in PRESCHOOL_AND_JUNIOR_GROUPS:
        return [StudentType.preschool.value, StudentType.child.value, StudentType.adult.value]
    if group_name in TEEN_GROUPS:
        return [StudentType.child.value, StudentType.adult.value, StudentType.preschool.value]
    if group_name in ADULT_GROUPS or group_name in {"Мини-группа (2 чел.)", "Индивидуальные занятия"}:
        return [StudentType.adult.value, StudentType.child.value, StudentType.preschool.value]
    return [StudentType.adult.value, StudentType.child.value, StudentType.preschool.value]


def _target_students_per_group(group_name: str) -> int:
    if group_name == "Мини-группа (2 чел.)":
        return 2
    if group_name == "Индивидуальные занятия":
        return 1
    if group_name in PRESCHOOL_AND_JUNIOR_GROUPS:
        return 6
    if group_name in TEEN_GROUPS:
        return 7
    return 8


async def seed_student_groups() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Загружаем все группы вместе с курсами
        groups_result = await session.execute(
            select(Group)
        )
        groups = groups_result.scalars().all()

        if not groups:
            print("⚠️  Таблица groups пуста. Запустите канонический seed: python seeds/seed_all.py")
            return

        # Загружаем всех активных студентов
        students_result = await session.execute(
            select(Student).where(Student.is_active == True)
        )
        all_students = students_result.scalars().all()

        if not all_students:
            print("⚠️  Таблица students пуста. Запустите канонический seed: python seeds/seed_all.py")
            return

        # Группируем студентов по типу для быстрого доступа
        students_by_type: dict[str, list[Student]] = {}
        for s in all_students:
            t = s.student_type.value if hasattr(s.student_type, "value") else str(s.student_type)
            students_by_type.setdefault(t, []).append(s)

        total_created = 0
        total_skipped = 0
        groups_processed = 0

        for group in groups:
            type_order = _preferred_student_type(group.name)
            target_count = _target_students_per_group(group.name)

            # Собираем пул студентов по приоритету
            student_pool: list[Student] = []
            for t in type_order:
                student_pool.extend(students_by_type.get(t, []))

            # Убираем дубли (если студент встречается в нескольких типах — маловероятно, но на всякий)
            seen_ids = set()
            unique_pool = []
            for s in student_pool:
                if s.id not in seen_ids:
                    seen_ids.add(s.id)
                    unique_pool.append(s)

            # Проверяем, какие студенты уже есть в этой группе
            existing_result = await session.execute(
                select(StudentGroup.student_name).where(
                    StudentGroup.group_id == group.id
                )
            )
            existing_names = {row[0] for row in existing_result.fetchall()}

            # Фильтруем — только те, кого ещё нет в группе
            candidates = [s for s in unique_pool if s.full_name not in existing_names]

            already_count = len(existing_names)
            to_add_count = max(0, min(target_count - already_count, len(candidates)))

            if to_add_count <= 0:
                total_skipped += len(candidates) + already_count - to_add_count
                groups_processed += 1
                continue

            selected = candidates[:to_add_count]

            for student in selected:
                s_type = student.student_type.value if hasattr(student.student_type, "value") else str(student.student_type)
                enrolled_at = datetime.utcnow() - timedelta(days=14 + (student.id % 45))

                sg = StudentGroup(
                    group_id=group.id,
                    student_name=student.full_name,
                    student_phone=student.phone,
                    student_email=student.email,
                    student_type=s_type,
                    form_id=student.source_form_id,
                    enrolled_at=enrolled_at,
                    is_active=True,
                )
                session.add(sg)
                total_created += 1

            skipped_here = len(existing_names)
            total_skipped += skipped_here
            groups_processed += 1

        await session.commit()

    print("\n✅ seed_student_groups завершён:")
    print(f"   Групп обработано:              {groups_processed}")
    print(f"   Записей student_groups создано: {total_created}")
    print(f"   Пропущено (уже существуют):    {total_skipped}")


if __name__ == "__main__":
    asyncio.run(seed_student_groups())
