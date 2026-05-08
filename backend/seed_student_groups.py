"""seed_student_groups.py

Наполняет таблицу student_groups для КАЖДОЙ группы из таблицы groups.
После запуска матрица посещаемости перестаёт показывать
«В выбранной группе пока нет активных студентов».

Запуск:
    cd backend
    python seed_student_groups.py
"""

import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Group, StudentGroup, CourseCategory
from app.models.student import Student, StudentType


# Сколько студентов добавлять в одну группу
MIN_STUDENTS_PER_GROUP = 4
MAX_STUDENTS_PER_GROUP = 8


def _preferred_student_type(category: str) -> list[str]:
    """Возвращает предпочтительные типы студентов для категории курса."""
    if category in (CourseCategory.children.value, CourseCategory.school.value,
                    "children", "school"):
        return [StudentType.child.value, StudentType.preschool.value, StudentType.adult.value]
    elif category in (CourseCategory.corporate.value, CourseCategory.adults.value,
                      CourseCategory.exam_prep.value,
                      "corporate", "adults", "exam_prep"):
        return [StudentType.adult.value, StudentType.child.value, StudentType.preschool.value]
    # fallback — любой порядок
    return [StudentType.adult.value, StudentType.child.value, StudentType.preschool.value]


async def seed_student_groups() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Загружаем все группы вместе с курсами
        groups_result = await session.execute(
            select(Group)
        )
        groups = groups_result.scalars().all()

        if not groups:
            print("⚠️  Таблица groups пуста. Сначала запустите seed_demo.py или seed_real_schedule.py.")
            return

        # Загружаем всех активных студентов
        students_result = await session.execute(
            select(Student).where(Student.is_active == True)
        )
        all_students = students_result.scalars().all()

        if not all_students:
            print("⚠️  Таблица students пуста. Сначала запустите seed_demo.py.")
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
            # Получаем курс группы для определения категории
            from app.models.group import Course
            course_result = await session.execute(
                select(Course).where(Course.id == group.course_id)
            )
            course = course_result.scalar_one_or_none()
            category = course.category.value if course and course.category else "adults"

            # Определяем порядок предпочтения типов студентов
            type_order = _preferred_student_type(category)

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

            # Сколько нужно добавить
            already_count = len(existing_names)
            need = max(0, MIN_STUDENTS_PER_GROUP - already_count)
            want = random.randint(MIN_STUDENTS_PER_GROUP, MAX_STUDENTS_PER_GROUP)
            to_add_count = max(need, min(want - already_count, len(candidates)))

            if to_add_count <= 0:
                total_skipped += len(candidates) + already_count - to_add_count
                groups_processed += 1
                continue

            selected = random.sample(candidates, min(to_add_count, len(candidates)))

            for student in selected:
                s_type = student.student_type.value if hasattr(student.student_type, "value") else str(student.student_type)
                enrolled_at = datetime.utcnow() - timedelta(days=random.randint(14, 60))

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
