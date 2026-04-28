"""
Seed реального расписания ABC Language School.

Учителя ищутся по фамилии через ILIKE-матч на поле full_name,
потому что в БД email хранится в формате «temlyakova@abc-school.ru»,
а не «anna.temlyakova@abc-school.ru».
"""
import asyncio
from datetime import time

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.teacher import Teacher

# ---------------------------------------------------------------------------
# Расписание групп
# Поле teacher_lastname — фамилия преподавателя (первое слово full_name в БД).
# Если преподаватель не найден — урок пропускается с предупреждением.
# ---------------------------------------------------------------------------
GROUPS_SCHEDULE = [
    # ── Понедельник ─────────────────────────────────────────────────────────
    {
        "group_name": "Английский A1 — Пн/Ср 09:00",
        "teacher_lastname": "Темлякова",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 101",
    },
    {
        "group_name": "Английский A2 — Пн/Ср 11:00",
        "teacher_lastname": "Федорова",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский B1 — Пн/Ср 13:00",
        "teacher_lastname": "Позднякова",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B2 — Пн/Ср 15:00",
        "teacher_lastname": "Фомина",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский C1 — Пн/Ср 17:00",
        "teacher_lastname": "Колесник",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    {
        "group_name": "Английский Kids A1 — Пн/Ср 16:00",
        "teacher_lastname": "Данилова",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(16, 0),
        "time_end": time(17, 30),
        "classroom": "Кабинет 203",
    },
    # ── Вторник ──────────────────────────────────────────────────────────────
    {
        "group_name": "Английский Pre-A1 — Вт/Чт 09:00",
        "teacher_lastname": "Зудяева",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 101",
    },
    {
        "group_name": "Английский A1.2 — Вт/Чт 11:00",
        "teacher_lastname": "Куцых",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский A2.1 — Вт/Чт 13:00",
        "teacher_lastname": "Винокурова",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B1.2 — Вт/Чт 15:00",
        "teacher_lastname": "Евдокимова",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский B2.1 — Вт/Чт 17:00",
        "teacher_lastname": "Походная",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    # ── Среда ────────────────────────────────────────────────────────────────
    {
        "group_name": "Английский A1 — Пн/Ср 09:00",
        "teacher_lastname": "Темлякова",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 101",
    },
    {
        "group_name": "Английский A2 — Пн/Ср 11:00",
        "teacher_lastname": "Федорова",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский B1 — Пн/Ср 13:00",
        "teacher_lastname": "Позднякова",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B2 — Пн/Ср 15:00",
        "teacher_lastname": "Фомина",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский C1 — Пн/Ср 17:00",
        "teacher_lastname": "Колесник",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    {
        "group_name": "Английский Kids A1 — Пн/Ср 16:00",
        "teacher_lastname": "Данилова",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(16, 0),
        "time_end": time(17, 30),
        "classroom": "Кабинет 203",
    },
    # ── Четверг ──────────────────────────────────────────────────────────────
    {
        "group_name": "Английский Pre-A1 — Вт/Чт 09:00",
        "teacher_lastname": "Зудяева",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 101",
    },
    {
        "group_name": "Английский A1.2 — Вт/Чт 11:00",
        "teacher_lastname": "Куцых",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский A2.1 — Вт/Чт 13:00",
        "teacher_lastname": "Винокурова",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B1.2 — Вт/Чт 15:00",
        "teacher_lastname": "Евдокимова",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский B2.1 — Вт/Чт 17:00",
        "teacher_lastname": "Походная",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    # ── Пятница ──────────────────────────────────────────────────────────────
    {
        "group_name": "Английский A2.2 — Пт 11:00",
        "teacher_lastname": "Митина",
        "day_of_week": DayOfWeek.friday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский B1.3 — Пт 13:00",
        "teacher_lastname": "Лукьянова",
        "day_of_week": DayOfWeek.friday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B2.2 — Пт 15:00",
        "teacher_lastname": "Пасикан",
        "day_of_week": DayOfWeek.friday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский C1.2 — Пт 17:00",
        "teacher_lastname": "Козлова",
        "day_of_week": DayOfWeek.friday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    # ── Суббота ──────────────────────────────────────────────────────────────
    {
        "group_name": "Английский A1 Сб 09:00",
        "teacher_lastname": "Осинина",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 101",
    },
    {
        "group_name": "Английский A2 Сб 11:00",
        "teacher_lastname": "Турабова",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(11, 0),
        "time_end": time(12, 30),
        "classroom": "Кабинет 102",
    },
    {
        "group_name": "Английский B1 Сб 13:00",
        "teacher_lastname": "Белова",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(13, 0),
        "time_end": time(14, 30),
        "classroom": "Кабинет 103",
    },
    {
        "group_name": "Английский B2 Сб 15:00",
        "teacher_lastname": "Родина",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(15, 0),
        "time_end": time(16, 30),
        "classroom": "Кабинет 201",
    },
    {
        "group_name": "Английский C1 Сб 17:00",
        "teacher_lastname": "Переведенцева",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(17, 0),
        "time_end": time(18, 30),
        "classroom": "Кабинет 202",
    },
    # Необязательные преподаватели (пропускаются если не найдены)
    {
        "group_name": "Немецкий A1 — Пн/Ср 19:00",
        "teacher_lastname": "Тихвинская",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 203",
    },
    {
        "group_name": "Немецкий A2 — Вт/Чт 19:00",
        "teacher_lastname": "Рубе",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 203",
    },
    {
        "group_name": "Немецкий B1 — Пт 19:00",
        "teacher_lastname": "Арнгольд",
        "day_of_week": DayOfWeek.friday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 203",
    },
    {
        "group_name": "Немецкий B2 — Сб 09:00",
        "teacher_lastname": "Быковская",
        "day_of_week": DayOfWeek.saturday,
        "time_start": time(9, 0),
        "time_end": time(10, 30),
        "classroom": "Кабинет 204",
    },
    {
        "group_name": "Французский A1 — Пн/Ср 19:00",
        "teacher_lastname": "Воронцова",
        "day_of_week": DayOfWeek.wednesday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 204",
    },
    # Возможно отсутствующие в БД — пропускаются
    {
        "group_name": "Английский A1 доп. — Пн 19:00",
        "teacher_lastname": "Алексеева",
        "day_of_week": DayOfWeek.monday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 204",
    },
    {
        "group_name": "Английский A2 доп. — Вт 19:00",
        "teacher_lastname": "Калужина",
        "day_of_week": DayOfWeek.tuesday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 204",
    },
    {
        "group_name": "Английский B1 доп. — Чт 19:00",
        "teacher_lastname": "Кривилева",
        "day_of_week": DayOfWeek.thursday,
        "time_start": time(19, 0),
        "time_end": time(20, 30),
        "classroom": "Кабинет 204",
    },
]


async def _find_teacher_by_lastname(db: AsyncSession, lastname: str) -> Teacher | None:
    """Ищет преподавателя по фамилии (ILIKE, совпадение с начала full_name)."""
    # Экранируем специальные символы LIKE, чтобы избежать случайных совпадений
    escaped = lastname.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await db.execute(
        select(Teacher)
        .where(Teacher.full_name.ilike(f"{escaped}%"))
        .where(Teacher.is_active)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_or_create_group(
    db: AsyncSession, name: str, course_id: int, teacher_id: int
) -> Group:
    result = await db.execute(select(Group).where(Group.name == name))
    group = result.scalar_one_or_none()
    if group:
        return group
    group = Group(
        name=name,
        course_id=course_id,
        teacher_id=teacher_id,
        status=GroupStatus.active,
    )
    db.add(group)
    await db.flush()
    return group


async def _get_or_create_classroom(db: AsyncSession, name: str) -> Classroom:
    result = await db.execute(select(Classroom).where(Classroom.name == name))
    classroom = result.scalar_one_or_none()
    if classroom:
        return classroom
    classroom = Classroom(name=name, capacity=12, is_active=True)
    db.add(classroom)
    await db.flush()
    return classroom


async def _get_or_create_course(db: AsyncSession) -> Course:
    """Возвращает первый активный курс или создаёт заглушку."""
    result = await db.execute(select(Course).limit(1))
    course = result.scalar_one_or_none()
    if course:
        return course
    course = Course(
        name="Английский язык",
        language="Английский",
        level=CourseLevel.beginner,
        category=CourseCategory.adults,
        price_per_month=5000,
    )
    db.add(course)
    await db.flush()
    return course


async def seed_real_schedule() -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        course = await _get_or_create_course(db)

        created_lessons = 0
        skipped_no_teacher = 0
        skipped_exists = 0

        for entry in GROUPS_SCHEDULE:
            lastname = entry["teacher_lastname"]
            teacher = await _find_teacher_by_lastname(db, lastname)

            if teacher is None:
                print(f"⚠️  Преподаватель '{lastname}' не найден — строка пропущена")
                skipped_no_teacher += 1
                continue

            classroom = await _get_or_create_classroom(db, entry["classroom"])
            group = await _get_or_create_group(
                db, entry["group_name"], course.id, teacher.id
            )

            # Проверяем дубликат по (group, teacher, day, time_start)
            existing = await db.execute(
                select(Lesson).where(
                    Lesson.group_id == group.id,
                    Lesson.teacher_id == teacher.id,
                    Lesson.day_of_week == entry["day_of_week"],
                    Lesson.time_start == entry["time_start"],
                )
            )
            if existing.scalar_one_or_none():
                skipped_exists += 1
                continue

            lesson = Lesson(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                day_of_week=entry["day_of_week"],
                time_start=entry["time_start"],
                time_end=entry["time_end"],
                status=LessonStatus.scheduled,
                is_recurring=True,
            )
            db.add(lesson)
            created_lessons += 1

        await db.commit()

    print(
        f"✅ Расписание загружено: создано {created_lessons} уроков, "
        f"пропущено (нет учителя) {skipped_no_teacher}, "
        f"уже существовало {skipped_exists}"
    )


if __name__ == "__main__":
    asyncio.run(seed_real_schedule())
