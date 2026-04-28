"""Seed real timetable from school schedule (ON0002-2025.xlsx)."""

from typing import Optional

import asyncio
import sys
import os
from datetime import datetime, time

from sqlalchemy import select, update

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import (
    Course,
    CourseLevel,
    CourseCategory,
    Group,
    GroupStatus,
)
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.teacher import Teacher


# ─────────────────────────── schedule data ───────────────────────

GROUPS_SCHEDULE = [
    {
        "name": "Школьники A1-1",
        "teacher_email": "anna.ivanova@abc-school.ru",
        "course": "Английский для школьников A1",
        "classroom": "Кабинет 101",
        "slots": [
            (DayOfWeek.monday, time(15, 0), time(16, 30), "Введение в язык"),
            (DayOfWeek.wednesday, time(15, 0), time(16, 30), "Алфавит и звуки"),
        ],
    },
    {
        "name": "Школьники A1-2",
        "teacher_email": "olga.morozova@abc-school.ru",
        "course": "Английский для школьников A1",
        "classroom": "Кабинет 102",
        "slots": [
            (DayOfWeek.tuesday, time(15, 0), time(16, 30), "Цвета и цифры"),
            (DayOfWeek.thursday, time(15, 0), time(16, 30), "Приветствия"),
        ],
    },
    {
        "name": "Взрослые A2-1",
        "teacher_email": "mikhail.petrov@abc-school.ru",
        "course": "Английский для взрослых A2",
        "classroom": "Кабинет 201",
        "slots": [
            (DayOfWeek.monday, time(18, 30), time(20, 0), "Present Simple"),
            (DayOfWeek.wednesday, time(18, 30), time(20, 0), "Past Simple"),
        ],
    },
    {
        "name": "Взрослые A2-2",
        "teacher_email": "anna.temlyakova@abc-school.ru",
        "course": "Английский для взрослых A2",
        "classroom": "Кабинет 202",
        "slots": [
            (DayOfWeek.tuesday, time(18, 30), time(20, 0), "Future Simple"),
            (DayOfWeek.thursday, time(18, 30), time(20, 0), "Present Continuous"),
        ],
    },
    {
        "name": "Дошкольники 4-6 лет",
        "teacher_email": "polina.evdokimova@abc-school.ru",
        "course": "Дошкольный английский 4–6 лет",
        "classroom": "Кабинет 103",
        "slots": [
            (DayOfWeek.tuesday, time(10, 0), time(11, 0), "Животные"),
            (DayOfWeek.friday, time(10, 0), time(11, 0), "Игры и песни"),
        ],
    },
    {
        "name": "IELTS Prep-1",
        "teacher_email": "svetlana.lukyanova@abc-school.ru",
        "course": "Подготовка к IELTS",
        "classroom": "Кабинет 204",
        "slots": [
            (DayOfWeek.monday, time(10, 0), time(11, 30), "Reading Skills"),
            (DayOfWeek.wednesday, time(10, 0), time(11, 30), "Writing Task 1"),
            (DayOfWeek.friday, time(10, 0), time(11, 30), "Speaking Practice"),
        ],
    },
]

COURSES_DATA = [
    {
        "name": "Английский для школьников A1",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 5400,
        "lessons_per_week": 2,
        "max_students": 10,
        "is_active": True,
    },
    {
        "name": "Английский для взрослых A2",
        "language": "Английский",
        "level": CourseLevel.elementary,
        "category": CourseCategory.adults,
        "price_per_month": 6200,
        "lessons_per_week": 2,
        "max_students": 8,
        "is_active": True,
    },
    {
        "name": "Дошкольный английский 4–6 лет",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.children,
        "price_per_month": 4800,
        "lessons_per_week": 2,
        "max_students": 6,
        "is_active": True,
    },
    {
        "name": "Подготовка к IELTS",
        "language": "Английский",
        "level": CourseLevel.upper_intermediate,
        "category": CourseCategory.exam_prep,
        "price_per_month": 7800,
        "lessons_per_week": 3,
        "max_students": 8,
        "is_active": True,
    },
]

ACADEMIC_YEAR_START = datetime(2025, 9, 1)
ACADEMIC_YEAR_END = datetime(2026, 5, 31)

CLASSROOMS_DATA = [
    {"name": "Кабинет 101", "capacity": 10, "floor": 1, "has_projector": True, "has_whiteboard": True, "is_active": True},
    {"name": "Кабинет 102", "capacity": 10, "floor": 1, "has_projector": False, "has_whiteboard": True, "is_active": True},
    {"name": "Кабинет 103", "capacity": 8, "floor": 1, "has_projector": True, "has_whiteboard": True, "is_active": True},
    {"name": "Кабинет 201", "capacity": 8, "floor": 2, "has_projector": True, "has_whiteboard": True, "is_active": True},
    {"name": "Кабинет 202", "capacity": 8, "floor": 2, "has_projector": True, "has_whiteboard": True, "is_active": True},
    {"name": "Кабинет 204", "capacity": 10, "floor": 2, "has_projector": True, "has_whiteboard": True, "is_active": True},
]


# ─────────────────────────── helpers ─────────────────────────────

async def _get_or_create(session, model, lookup: dict, defaults: Optional[dict] = None):
    """Retrieve an existing row matching *lookup* or create a new one.

    Args:
        session: The active SQLAlchemy async session.
        model: The ORM model class to query.
        lookup: Column/value pairs used to filter the query.
        defaults: Extra column/value pairs only applied when creating a new row.

    Returns:
        A ``(instance, created)`` tuple where *created* is ``True`` when a new
        row was inserted and ``False`` when an existing row was returned.
    """
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalars().first()
    if instance:
        return instance, False
    payload = {**lookup, **(defaults or {})}
    instance = model(**payload)
    session.add(instance)
    await session.flush()
    return instance, True


# ─────────────────────────── fix helper ──────────────────────────

async def fix_existing_lessons_branch() -> None:
    """Back-fill branch_id on lessons that were created without it."""
    await init_db()
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Branch).limit(1))
        branch = result.scalars().first()
        if branch is None:
            print("⚠️  No branches found — skipping fix_existing_lessons_branch")
            return

        stmt = (
            update(Lesson)
            .where(Lesson.branch_id.is_(None))
            .values(branch_id=branch.id)
        )
        result = await session.execute(stmt)
        updated = result.rowcount
        await session.commit()
        print(f"✅  fix_existing_lessons_branch: updated {updated} lessons")


# ──────────────────────── main seeder ────────────────────────────

async def seed_real_schedule() -> None:
    """Seed the real school timetable: courses, classrooms, groups, and lessons."""
    await init_db()

    async with AsyncSessionLocal() as session:

        # ── 0. Branch ────────────────────────────────────────────
        branch, _ = await _get_or_create(
            session,
            Branch,
            {"name": "Офис (главный)"},
            {
                "address": "г. Новосибирск, ул. Бориса Богаткова, 208/2",
                "phone": "+79139121809",
                "email": "info@abc-school.ru",
                "is_active": True,
            },
        )

        # ── 1. Educational program ───────────────────────────────
        program, _ = await _get_or_create(
            session,
            EducationalProgram,
            {"name": "English General"},
            {
                "code": "ENG-GEN",
                "language": "Английский",
                "level": "A1-B2",
                "target_group": "все",
                "duration_months": 9,
                "description": "Общий курс английского языка для всех возрастов и уровней.",
                "is_active": True,
            },
        )

        # ── 2. Courses ───────────────────────────────────────────
        course_map: dict[str, Course] = {}
        for c in COURSES_DATA:
            course, _ = await _get_or_create(
                session,
                Course,
                {"name": c["name"]},
                c,
            )
            course_map[c["name"]] = course

        # ── 3. Classrooms ────────────────────────────────────────
        classroom_map: dict[str, Classroom] = {}
        for cl in CLASSROOMS_DATA:
            classroom, _ = await _get_or_create(
                session,
                Classroom,
                {"name": cl["name"]},
                cl,
            )
            classroom_map[cl["name"]] = classroom

        # ── 4. Groups + lessons ──────────────────────────────────
        groups_created = 0
        lessons_created = 0

        for entry in GROUPS_SCHEDULE:
            # Resolve teacher by email
            teacher_result = await session.execute(
                select(Teacher).where(Teacher.email == entry["teacher_email"])
            )
            teacher = teacher_result.scalars().first()
            if teacher is None:
                print(f"⚠️  Teacher {entry['teacher_email']} not found — skipping group {entry['name']}")
                continue

            course = course_map.get(entry["course"])
            if course is None:
                print(f"⚠️  Course '{entry['course']}' not found — skipping group {entry['name']}")
                continue

            classroom = classroom_map.get(entry["classroom"])
            if classroom is None:
                print(f"⚠️  Classroom '{entry['classroom']}' not found — skipping group {entry['name']}")
                continue

            group, created = await _get_or_create(
                session,
                Group,
                {"name": entry["name"]},
                {
                    "course_id": course.id,
                    "teacher_id": teacher.id,
                    "status": GroupStatus.active,
                    "start_date": ACADEMIC_YEAR_START,
                    "end_date": ACADEMIC_YEAR_END,
                },
            )
            if created:
                groups_created += 1

            for day_of_week, t_start, t_end, topic in entry["slots"]:
                _, created = await _get_or_create(
                    session,
                    Lesson,
                    {
                        "group_id": group.id,
                        "teacher_id": teacher.id,
                        "day_of_week": day_of_week,
                        "time_start": t_start,
                    },
                    {
                        "classroom_id": classroom.id,
                        "branch_id": branch.id,
                        "program_id": program.id,
                        "time_end": t_end,
                        "topic": topic,
                        "status": LessonStatus.scheduled,
                        "is_recurring": True,
                    },
                )
                if created:
                    lessons_created += 1

        await session.commit()

        print("✅  seed_real_schedule завершён")
        print(f"   Группы созданы:  {groups_created}")
        print(f"   Занятия созданы: {lessons_created}")


if __name__ == "__main__":
    async def _main() -> None:
        await fix_existing_lessons_branch()
        await seed_real_schedule()

    asyncio.run(_main())
