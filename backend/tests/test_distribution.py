import asyncio
from collections import defaultdict

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import Course, Group, StudentGroup
from app.models.schedule import Classroom, Lesson
from app.models.student import Student, StudentStatus, StudentType
from app.models.teacher import Teacher
from seed_branches_22 import BRANCHES
from seed_distribution import seed_distribution
from seed_teachers import TEACHERS_DATA
from seeds.seed_all import COURSES_DATA


async def _prepare_data() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        await session.execute(delete(StudentGroup))
        await session.execute(delete(Lesson))
        await session.execute(delete(Group))
        await session.execute(delete(Student))
        await session.execute(delete(Teacher))
        await session.execute(delete(Classroom))
        await session.execute(delete(EducationalProgram))
        await session.execute(delete(Course))
        await session.execute(delete(Branch))

        for branch_data in BRANCHES:
            session.add(Branch(**branch_data, is_active=True))

        for teacher_data in TEACHERS_DATA:
            session.add(Teacher(**teacher_data))

        for course_data in COURSES_DATA:
            session.add(
                Course(
                    name=course_data["name"],
                    language=course_data["language"],
                    level=course_data["level"],
                    category=course_data["category"],
                    price_per_month=course_data["price_per_month"],
                    lessons_per_week=course_data["lessons_per_week"],
                    duration_months=9,
                    max_students=12,
                    is_active=True,
                )
            )
            session.add(
                EducationalProgram(
                    name=course_data["name"],
                    code=course_data["name"],
                    language=course_data["language"],
                    level=None,
                    target_group="тест",
                    duration_months=9,
                    description="Тестовая программа",
                    is_active=True,
                )
            )

        for index in range(1, 127):
            session.add(
                Student(
                    full_name=f"Тестовый Ученик {index}",
                    student_type=StudentType.adult,
                    status=StudentStatus.active,
                    email=f"student{index}@example.com",
                    phone=f"+7900{index:07d}",
                    language_level="A1",
                    is_active=True,
                )
            )

        room_capacities = [12, 12, 10, 8, 6]
        for index, capacity in enumerate(room_capacities, start=1):
            session.add(
                Classroom(
                    name=f"Кабинет {index}",
                    capacity=capacity,
                    floor=1,
                    has_projector=True,
                    has_whiteboard=True,
                    is_active=True,
                )
            )

        await session.commit()


async def _run_distribution_and_fetch():
    await _prepare_data()
    await seed_distribution()

    async with AsyncSessionLocal() as session:
        branches = (await session.execute(select(Branch))).scalars().all()
        teachers = (await session.execute(select(Teacher))).scalars().all()
        programs = (await session.execute(select(EducationalProgram))).scalars().all()
        groups = (await session.execute(select(Group))).scalars().all()
        lessons = (await session.execute(select(Lesson))).scalars().all()

        return branches, teachers, programs, groups, lessons


def test_distribution_constraints() -> None:
    branches, teachers, programs, groups, lessons = asyncio.run(_run_distribution_and_fetch())

    teacher_by_id = {teacher.id: teacher for teacher in teachers}
    program_by_id = {program.id: program for program in programs}

    admin_branch_ids = {branch.id for branch in branches if getattr(branch, "is_administrative", False)}
    assert all(lesson.branch_id not in admin_branch_ids for lesson in lessons)

    teachers_by_branch = defaultdict(set)
    for lesson in lessons:
        teachers_by_branch[lesson.branch_id].add(lesson.teacher_id)

    for branch in branches:
        assert len(teachers_by_branch[branch.id]) >= 2

    teachers_by_program = defaultdict(set)
    for lesson in lessons:
        program = program_by_id[lesson.program_id]
        if program.name == "Китайский язык":
            continue
        teachers_by_program[program.id].add(lesson.teacher_id)

    english_programs = [program for program in programs if program.name != "Китайский язык"]
    for program in english_programs:
        assert len(teachers_by_program[program.id]) >= 2

    assert all(group.teacher_id is not None for group in groups)
    assert all(lesson.teacher_id and lesson.branch_id and lesson.classroom_id for lesson in lessons)

    occupied_slots = set()
    for lesson in lessons:
        slot = (lesson.classroom_id, lesson.day_of_week, lesson.time_start, lesson.time_end)
        assert slot not in occupied_slots
        occupied_slots.add(slot)

    for lesson in lessons:
        teacher = teacher_by_id[lesson.teacher_id]
        program = program_by_id[lesson.program_id]
        is_chinese_teacher = "китай" in (teacher.subject or "").lower()
        if is_chinese_teacher:
            assert program.name == "Китайский язык"
        else:
            assert program.name != "Китайский язык"
