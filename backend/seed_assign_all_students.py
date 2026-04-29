"""seed_assign_all_students.py

Убеждается, что КАЖДЫЙ студент из таблицы `students`
привязан хотя бы к одной группе через `student_groups`.

Логика:
  1. Загружает всех активных студентов (is_active=True).
  2. Загружает все группы вместе с курсами (join Course).
  3. Для каждого студента проверяет наличие записи в student_groups
     (по student_name = student.full_name). Если есть — пропускает.
  4. Если студент ещё не в группе — назначает наиболее подходящую:
     - child / preschool  → предпочтительны курсы children / school
     - adult              → предпочтительны курсы adults / corporate / exam_prep
     - Среди подходящих — группа с наименьшим числом активных студентов.
     - Лимит: не более 10 студентов на группу.
     - Fallback: любая группа с местом, если подходящих нет.
  5. Вставляет StudentGroup с enrolled_at = utcnow() − random(14..60) дней.
  6. Идемпотентен: второй запуск не создаёт новых записей.

Запуск:
    cd backend
    python seed_assign_all_students.py
"""

import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import func, select

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Course, CourseCategory, Group, StudentGroup
from app.models.student import Student, StudentType

MAX_STUDENTS_PER_GROUP = 10


def _is_preferred(student_type: str, course_category: str) -> bool:
    """Возвращает True, если категория курса подходит для данного типа студента."""
    preferred_for_child = {CourseCategory.children.value, CourseCategory.school.value}
    preferred_for_adult = {
        CourseCategory.adults.value,
        CourseCategory.corporate.value,
        CourseCategory.exam_prep.value,
    }

    if student_type in (StudentType.child.value, StudentType.preschool.value):
        return course_category in preferred_for_child
    if student_type == StudentType.adult.value:
        return course_category in preferred_for_adult
    return False


async def seed_assign_all_students() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Все активные студенты
        students_result = await session.execute(
            select(Student).where(Student.is_active == True)
        )
        students = students_result.scalars().all()

        if not students:
            print("⚠️  Таблица students пуста. Сначала запустите seed_demo.py.")
            return

        # 2. Все группы с курсами
        groups_result = await session.execute(
            select(Group, Course).join(Course, Group.course_id == Course.id)
        )
        groups_with_courses = groups_result.all()

        if not groups_with_courses:
            print(
                "⚠️  Таблица groups пуста. Сначала запустите seed_demo.py или "
                "seed_real_schedule.py."
            )
            return

        # 3. Подсчитываем текущий размер каждой группы (только активные записи)
        counts_result = await session.execute(
            select(StudentGroup.group_id, func.count(StudentGroup.id).label("cnt"))
            .where(StudentGroup.is_active == True)
            .group_by(StudentGroup.group_id)
        )
        group_sizes: dict[int, int] = {row.group_id: row.cnt for row in counts_result}

        # 4. Имена студентов, уже присутствующих хотя бы в одной группе
        existing_result = await session.execute(
            select(StudentGroup.student_name).distinct()
        )
        already_assigned: set[str] = {row[0] for row in existing_result}

        checked = 0
        attached = 0
        skipped = 0
        no_space = 0

        for student in students:
            checked += 1
            s_type = (
                student.student_type.value
                if hasattr(student.student_type, "value")
                else str(student.student_type)
            )

            # Шаг 3: уже в группе?
            if student.full_name in already_assigned:
                skipped += 1
                continue

            # Шаг 4: разбиваем группы на предпочтительные и остальные
            preferred: list[tuple[Group, int]] = []
            fallback: list[tuple[Group, int]] = []

            for grp, course in groups_with_courses:
                size = group_sizes.get(grp.id, 0)
                if size >= MAX_STUDENTS_PER_GROUP:
                    continue
                cat = (
                    course.category.value
                    if hasattr(course.category, "value")
                    else str(course.category)
                )
                if _is_preferred(s_type, cat):
                    preferred.append((grp, size))
                else:
                    fallback.append((grp, size))

            # Выбираем группу с наименьшим числом студентов
            candidates = preferred if preferred else fallback

            if not candidates:
                print(
                    f"⚠️  Нет свободных групп для студента «{student.full_name}» "
                    f"(тип: {s_type}). Пропускаем."
                )
                no_space += 1
                continue

            chosen_grp, _ = min(candidates, key=lambda x: x[1])

            # Шаг 5: вставляем StudentGroup
            enrolled_at = datetime.utcnow() - timedelta(days=random.randint(14, 60))
            sg = StudentGroup(
                group_id=chosen_grp.id,
                student_name=student.full_name,
                student_phone=student.phone,
                student_email=student.email,
                student_type=s_type,
                form_id=student.source_form_id,
                enrolled_at=enrolled_at,
                is_active=True,
            )
            session.add(sg)

            # Обновляем локальный счётчик, чтобы не превысить лимит в рамках текущего запуска
            group_sizes[chosen_grp.id] = group_sizes.get(chosen_grp.id, 0) + 1
            # Добавляем в множество уже назначенных, чтобы гарантировать идемпотентность
            # при повторном прохождении по студентам в этом же запуске
            already_assigned.add(student.full_name)
            attached += 1

        await session.commit()

    print("\n✅ seed_assign_all_students завершён:")
    print(f"   Студентов проверено:              {checked}")
    print(f"   Прикреплено к группам:            {attached}")
    print(f"   Уже были в группе (пропущено):    {skipped}")
    print(f"   Не удалось прикрепить (нет места): {no_space}")


if __name__ == "__main__":
    asyncio.run(seed_assign_all_students())
