"""
seed_real_schedule.py
---------------------
Seeds a realistic lesson schedule for ABC Language School.

Each group definition includes a ``branch_name`` that determines which
branch the lessons belong to.  The branch is looked up by name before any
lesson is inserted, and ``branch_id`` is set on every ``Lesson`` row.

Also provides ``fix_existing_lessons_branch()`` to backfill ``branch_id``
for any existing lessons whose ``branch_id`` is currently NULL.

Run from the backend/ directory:
    cd backend
    python seed_real_schedule.py
"""

import asyncio
import os
import sys
from datetime import time
from typing import Optional

from sqlalchemy import select

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.teacher import Teacher

# ---------------------------------------------------------------------------
# Seed data — groups with their branch assignments
# ---------------------------------------------------------------------------
# Each entry defines a group and the branch it belongs to.  The branch_name
# is used to look up Branch.id so every lesson created for this group
# carries the correct branch_id.

GROUPS_SCHEDULE = [
    {
        "group_name": "A2 Подростки Вт/Чт 17:00",
        "branch_name": "Филиал №1 — Центральный",
        "teacher_email": "anna.ivanova@abc-school.ru",
        "classroom_name": "Кабинет 301",
        "program_code": "ENG-SCHOOL",
        "lessons": [
            (DayOfWeek.tuesday,  time(17, 0), time(18, 30), "Present Simple vs Present Continuous"),
            (DayOfWeek.thursday, time(17, 0), time(18, 30), "Travel vocabulary and airport situations"),
        ],
    },
    {
        "group_name": "A2 Подростки Сб 11:00",
        "branch_name": "Филиал №1 — Центральный",
        "teacher_email": "anna.ivanova@abc-school.ru",
        "classroom_name": "Кабинет 204",
        "program_code": "ENG-SCHOOL",
        "lessons": [
            (DayOfWeek.saturday, time(11, 0), time(12, 30), "Reading club: short stories discussion"),
        ],
    },
    {
        "group_name": "A2 Взрослые Пн/Ср 19:00",
        "branch_name": "Филиал №2 — Октябрьский",
        "teacher_email": "olga.morozova@abc-school.ru",
        "classroom_name": "Кабинет 102",
        "program_code": "ENG-ADULT",
        "lessons": [
            (DayOfWeek.monday,    time(19, 0), time(20, 30), "Listening practice: everyday conversations"),
            (DayOfWeek.wednesday, time(19, 0), time(20, 30), "Speaking drills and role-play"),
        ],
    },
    {
        "group_name": "School A1 Morning",
        "branch_name": "Офис (главный)",
        "teacher_email": "anna.ivanova@abc-school.ru",
        "classroom_name": "Кабинет 101",
        "program_code": "ENG-A1",
        "lessons": [
            (DayOfWeek.monday,    time(10, 0), time(11, 0), "Present Simple"),
            (DayOfWeek.wednesday, time(10, 0), time(11, 0), "Past Simple"),
        ],
    },
    {
        "group_name": "Adult A2 Evening",
        "branch_name": "Офис (главный)",
        "teacher_email": "olga.morozova@abc-school.ru",
        "classroom_name": "Кабинет 202",
        "program_code": "ENG-A2",
        "lessons": [
            (DayOfWeek.tuesday,  time(19, 0), time(20, 0), "Conditionals"),
            (DayOfWeek.thursday, time(19, 0), time(20, 0), "Business vocabulary"),
        ],
    },
    {
        "group_name": "B1 Взрослые Пн/Чт 18:00",
        "branch_name": "Филиал №3 — Академгородок",
        "teacher_email": "mikhail.petrov@abc-school.ru",
        "classroom_name": "Кабинет 303",
        "program_code": "ENG-B1",
        "lessons": [
            (DayOfWeek.monday,   time(18, 0), time(19, 30), "Intermediate grammar review"),
            (DayOfWeek.thursday, time(18, 0), time(19, 30), "Reading and comprehension"),
        ],
    },
    {
        "group_name": "Дошкольники Вт/Пт 10:00",
        "branch_name": "Филиал №4 — Ленинский",
        "teacher_email": "elena.sidorova@abc-school.ru",
        "classroom_name": "Кабинет 105",
        "program_code": "ENG-PRE",
        "lessons": [
            (DayOfWeek.tuesday, time(10, 0), time(10, 45), "Alphabet and phonics"),
            (DayOfWeek.friday,  time(10, 0), time(10, 45), "Numbers and colours"),
        ],
    },
]

# Branch used as a fallback when a lesson's group is not listed in GROUPS_SCHEDULE
FALLBACK_BRANCH_NAME = "Филиал №1 — Центральный"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

async def _get_or_create(
    session,
    model,
    lookup: dict,
    defaults: Optional[dict] = None,
):
    stmt = select(model).filter_by(**lookup)
    result = await session.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance:
        return instance, False
    params = {**lookup, **(defaults or {})}
    instance = model(**params)
    session.add(instance)
    await session.flush()
    return instance, True


# ---------------------------------------------------------------------------
# Fix function — backfills branch_id for all existing NULL lessons
# ---------------------------------------------------------------------------

async def fix_existing_lessons_branch() -> None:
    """
    One-time fix: update all existing lessons with branch_id = NULL.

    Strategy:
      1. Build a mapping  group_name → branch_id  from GROUPS_SCHEDULE.
      2. For each lesson where branch_id IS NULL, look up its group name
         in the mapping and apply the correct branch_id.
      3. Lessons whose group is not in the mapping receive the fallback
         branch_id (FALLBACK_BRANCH_NAME, or the first branch in the DB).
    """
    await init_db()
    async with AsyncSessionLocal() as session:
        # --- build branch_name → branch_id cache ---
        branch_cache: dict[str, int] = {}
        branch_names = {entry["branch_name"] for entry in GROUPS_SCHEDULE}
        branch_names.add(FALLBACK_BRANCH_NAME)
        for bname in branch_names:
            result = await session.execute(
                select(Branch).where(Branch.name == bname)
            )
            branch = result.scalar_one_or_none()
            if branch:
                branch_cache[bname] = branch.id

        # --- resolve fallback branch id ---
        fallback_id = branch_cache.get(FALLBACK_BRANCH_NAME)
        if fallback_id is None:
            result = await session.execute(select(Branch).limit(1))
            first_branch = result.scalar_one_or_none()
            fallback_id = first_branch.id if first_branch else None

        # --- build group_name → branch_id mapping ---
        group_to_branch: dict[str, int] = {}
        for entry in GROUPS_SCHEDULE:
            bid = branch_cache.get(entry["branch_name"], fallback_id)
            if bid is not None:
                group_to_branch[entry["group_name"]] = bid

        # --- fetch all lessons with branch_id IS NULL ---
        null_lessons_result = await session.execute(
            select(Lesson).where(Lesson.branch_id.is_(None))
        )
        null_lessons = null_lessons_result.scalars().all()

        if not null_lessons:
            print("✅ fix_existing_lessons_branch: no lessons with NULL branch_id found")
            return

        # --- fetch group names for those lessons ---
        group_ids = {lesson.group_id for lesson in null_lessons}
        groups_result = await session.execute(
            select(Group).where(Group.id.in_(group_ids))
        )
        groups_by_id: dict[int, str] = {g.id: g.name for g in groups_result.scalars().all()}

        # --- apply updates ---
        updated = 0
        for lesson in null_lessons:
            group_name = groups_by_id.get(lesson.group_id, "")
            branch_id = group_to_branch.get(group_name, fallback_id)
            if branch_id is not None:
                lesson.branch_id = branch_id
                updated += 1

        await session.commit()
        print(f"✅ fix_existing_lessons_branch: updated {updated} lessons")


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

async def seed_real_schedule() -> None:
    """Create groups and lessons, setting branch_id on every lesson."""
    await init_db()
    async with AsyncSessionLocal() as session:
        # Ensure a base course exists for groups that don't specify one
        course, _ = await _get_or_create(
            session,
            Course,
            {"name": "English A2.1"},
            {
                "description": "Базовый разговорный курс",
                "language": "Английский",
                "level": CourseLevel.elementary,
                "category": CourseCategory.school,
                "duration_months": 9,
                "lessons_per_week": 2,
                "price_per_month": 5200,
                "max_students": 10,
                "is_active": True,
            },
        )

        lessons_created = 0

        for entry in GROUPS_SCHEDULE:
            # 1. Look up the branch by name — branch_id is required for lessons
            branch_result = await session.execute(
                select(Branch).where(Branch.name == entry["branch_name"])
            )
            branch = branch_result.scalar_one_or_none()
            if branch is None:
                print(
                    f"⚠️  Branch '{entry['branch_name']}' not found, "
                    f"skipping group '{entry['group_name']}'"
                )
                continue
            branch_id = branch.id

            # 2. Get or create the group
            group, _ = await _get_or_create(
                session,
                Group,
                {"name": entry["group_name"]},
                {"course_id": course.id, "status": GroupStatus.active},
            )

            # 3. Look up the teacher by email; fall back to any active teacher
            teacher_result = await session.execute(
                select(Teacher).where(Teacher.email == entry["teacher_email"])
            )
            teacher = teacher_result.scalar_one_or_none()
            if teacher is None:
                teacher_result2 = await session.execute(
                    select(Teacher).where(Teacher.is_active.is_(True)).limit(1)
                )
                teacher = teacher_result2.scalar_one_or_none()
            if teacher is None:
                print(
                    f"⚠️  No teacher found for group '{entry['group_name']}', skipping"
                )
                continue

            # 4. Get or create the classroom
            classroom, _ = await _get_or_create(
                session,
                Classroom,
                {"name": entry["classroom_name"]},
                {
                    "capacity": 12,
                    "has_projector": True,
                    "has_whiteboard": True,
                    "is_active": True,
                },
            )

            # 5. Look up the educational program (optional)
            program_result = await session.execute(
                select(EducationalProgram).where(
                    EducationalProgram.code == entry["program_code"]
                )
            )
            program = program_result.scalar_one_or_none()

            # 6. Create lessons — branch_id is set from the branch looked up above
            for dow, t_start, t_end, topic in entry["lessons"]:
                _, created = await _get_or_create(
                    session,
                    Lesson,
                    {
                        "group_id": group.id,
                        "teacher_id": teacher.id,
                        "classroom_id": classroom.id,
                        "day_of_week": dow,
                        "time_start": t_start,
                    },
                    {
                        "time_end": t_end,
                        "topic": topic,
                        "status": LessonStatus.scheduled,
                        "branch_id": branch_id,
                        "program_id": program.id if program else None,
                        "is_recurring": True,
                    },
                )
                if created:
                    lessons_created += 1

        await session.commit()
        print(
            f"✅ seed_real_schedule: created {lessons_created} new lessons with branch_id set"
        )


if __name__ == "__main__":
    asyncio.run(fix_existing_lessons_branch())
    asyncio.run(seed_real_schedule())
