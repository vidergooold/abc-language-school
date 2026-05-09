import asyncio
from collections import defaultdict
from datetime import datetime, time

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import Group, GroupStatus, StudentGroup, Course
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.student import Student
from app.models.teacher import Teacher

OFFICE_BRANCH_NAME = "Офис"
CHINESE_PROGRAM_NAME = "Китайский язык"
MIN_TEACHERS_PER_BRANCH = 2
GROUP_SIZE_REGULAR = 6
GROUP_SIZE_MINI = 2
GROUP_SIZE_INDIVIDUAL = 1

TEACHER_SUBJECTS = {
    "Лукьянова Светлана Ярославовна": "chinese",
    "Темлякова Анна Михайловна": "chinese",
    "Фомина Снежанна Олеговна": "chinese",
}

DAY_SEQUENCE = [
    DayOfWeek.monday,
    DayOfWeek.tuesday,
    DayOfWeek.wednesday,
    DayOfWeek.thursday,
    DayOfWeek.friday,
    DayOfWeek.saturday,
]
TIME_SEQUENCE = [
    (time(9, 0), time(10, 30)),
    (time(10, 40), time(12, 10)),
    (time(12, 20), time(13, 50)),
    (time(14, 0), time(15, 30)),
    (time(15, 40), time(17, 10)),
    (time(17, 20), time(18, 50)),
    (time(19, 0), time(20, 30)),
]


def _teacher_language(teacher: Teacher) -> str:
    explicit = TEACHER_SUBJECTS.get(teacher.full_name)
    if explicit in {"english", "chinese"}:
        return explicit

    normalized = (teacher.subject or "").strip().lower()
    if "китай" in normalized:
        return "chinese"
    return "english"


def _program_group_size(program_name: str) -> int:
    if program_name == "Мини-группа (2 чел.)":
        return GROUP_SIZE_MINI
    if program_name == "Индивидуальные занятия":
        return GROUP_SIZE_INDIVIDUAL
    return GROUP_SIZE_REGULAR


async def seed_distribution() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        branches = (await session.execute(select(Branch).where(Branch.is_active == True).order_by(Branch.id))).scalars().all()
        teachers = (await session.execute(select(Teacher).where(Teacher.is_active == True).order_by(Teacher.id))).scalars().all()
        programs = (await session.execute(select(EducationalProgram).where(EducationalProgram.is_active == True).order_by(EducationalProgram.id))).scalars().all()
        courses = (await session.execute(select(Course).where(Course.is_active == True).order_by(Course.id))).scalars().all()
        students = (await session.execute(select(Student).where(Student.is_active == True).order_by(Student.id))).scalars().all()
        rooms = (await session.execute(select(Classroom).where(Classroom.is_active == True).order_by(Classroom.capacity, Classroom.id))).scalars().all()

        if not branches or not teachers or not programs or not courses:
            print("⚠️ Недостаточно исходных данных для распределения")
            return

        non_office_branches = [branch for branch in branches if branch.name != OFFICE_BRANCH_NAME]
        if not non_office_branches:
            print("⚠️ Нет учебных филиалов (кроме Офиса)")
            return

        for teacher in teachers:
            teacher.subject = "Китайский" if _teacher_language(teacher) == "chinese" else "Английский"

        english_teachers = [teacher for teacher in teachers if _teacher_language(teacher) == "english"]
        chinese_teachers = [teacher for teacher in teachers if _teacher_language(teacher) == "chinese"]

        english_programs = [program for program in programs if program.name != CHINESE_PROGRAM_NAME]
        chinese_program = next((program for program in programs if program.name == CHINESE_PROGRAM_NAME), None)

        if len(english_teachers) < 2 or chinese_program is None or not chinese_teachers:
            print("⚠️ Недостаточно преподавателей/программ для корректного распределения")
            await session.rollback()
            return

        teacher_programs: dict[int, list[EducationalProgram]] = {teacher.id: [] for teacher in teachers}

        for index, program in enumerate(english_programs):
            first = english_teachers[index % len(english_teachers)]
            second = english_teachers[(index + max(1, len(english_teachers) // 2)) % len(english_teachers)]
            for teacher in (first, second):
                if program not in teacher_programs[teacher.id]:
                    teacher_programs[teacher.id].append(program)

        for index, teacher in enumerate(english_teachers):
            if teacher_programs[teacher.id]:
                continue
            teacher_programs[teacher.id].append(english_programs[index % len(english_programs)])

        for teacher in english_teachers:
            teacher_programs[teacher.id] = teacher_programs[teacher.id][:3]

        for teacher in chinese_teachers:
            teacher_programs[teacher.id] = [chinese_program]

        teacher_branches: dict[int, list[Branch]] = {teacher.id: [] for teacher in teachers}
        branch_teachers: dict[int, list[Teacher]] = defaultdict(list)

        for index, branch in enumerate(non_office_branches):
            first = teachers[index % len(teachers)]
            second = teachers[(index + max(1, len(teachers) // 2)) % len(teachers)]
            for teacher in (first, second):
                if branch not in teacher_branches[teacher.id] and len(teacher_branches[teacher.id]) < 4:
                    teacher_branches[teacher.id].append(branch)
                if teacher not in branch_teachers[branch.id]:
                    branch_teachers[branch.id].append(teacher)

        for branch in non_office_branches:
            if len(branch_teachers[branch.id]) >= MIN_TEACHERS_PER_BRANCH:
                continue
            for teacher in sorted(teachers, key=lambda t: len(teacher_branches[t.id])):
                if branch in teacher_branches[teacher.id]:
                    continue
                if len(teacher_branches[teacher.id]) >= 4:
                    continue
                teacher_branches[teacher.id].append(branch)
                branch_teachers[branch.id].append(teacher)
                if len(branch_teachers[branch.id]) >= MIN_TEACHERS_PER_BRANCH:
                    break

        for teacher in teachers:
            if teacher_branches[teacher.id]:
                continue
            teacher_branches[teacher.id].append(non_office_branches[teacher.id % len(non_office_branches)])

        course_by_name = {course.name: course for course in courses}
        course_by_language = defaultdict(list)
        for course in courses:
            course_by_language[(course.language or "").lower()].append(course)

        async def resolve_course(program: EducationalProgram) -> Course | None:
            exact = course_by_name.get(program.name)
            if exact:
                return exact
            language_key = (program.language or "").lower()
            if language_key in course_by_language and course_by_language[language_key]:
                return course_by_language[language_key][0]
            return courses[0] if courses else None

        planned_groups: list[tuple[Branch, Teacher, EducationalProgram]] = []
        for program in english_programs:
            covering_teachers = [teacher for teacher in english_teachers if program in teacher_programs[teacher.id]]
            for offset, teacher in enumerate(covering_teachers[:2]):
                assigned_branches = teacher_branches[teacher.id]
                branch = assigned_branches[offset % len(assigned_branches)]
                planned_groups.append((branch, teacher, program))

        for teacher in chinese_teachers:
            branch = teacher_branches[teacher.id][0]
            planned_groups.append((branch, teacher, chinese_program))

        for branch in non_office_branches:
            represented = {teacher.id for (b, teacher, _) in planned_groups if b.id == branch.id}
            for teacher in branch_teachers[branch.id]:
                if len(represented) >= MIN_TEACHERS_PER_BRANCH:
                    break
                if teacher.id in represented:
                    continue
                individual_program = next((program for program in teacher_programs[teacher.id] if program.name == "Индивидуальные занятия"), None)
                if individual_program is None:
                    fallback_program = teacher_programs[teacher.id][0]
                else:
                    fallback_program = individual_program
                planned_groups.append((branch, teacher, fallback_program))
                represented.add(teacher.id)

        # Полностью пересобираем распределение групп и расписания
        await session.execute(delete(StudentGroup))
        await session.execute(delete(Lesson))
        await session.execute(delete(Group))
        await session.flush()

        if not rooms:
            print("⚠️ Нет доступных кабинетов. Все группы пропущены.")
            await session.commit()
            return

        used_slots: set[tuple[int, DayOfWeek, time, time]] = set()
        groups_created_by_branch: dict[str, int] = defaultdict(int)
        skipped_by_branch_program: dict[tuple[str, str], int] = defaultdict(int)
        created_groups: list[tuple[Group, Branch, EducationalProgram, int]] = []

        slot_index = 0

        for branch, teacher, program in planned_groups:
            course = await resolve_course(program)
            if course is None:
                skipped_by_branch_program[(branch.name, program.name)] += 1
                continue

            group_size = _program_group_size(program.name)
            suitable_rooms = [room for room in rooms if room.capacity >= group_size]
            if not suitable_rooms:
                skipped_by_branch_program[(branch.name, program.name)] += 1
                continue

            assigned = None
            for _ in range(len(DAY_SEQUENCE) * len(TIME_SEQUENCE)):
                day = DAY_SEQUENCE[slot_index % len(DAY_SEQUENCE)]
                start, end = TIME_SEQUENCE[(slot_index // len(DAY_SEQUENCE)) % len(TIME_SEQUENCE)]
                slot_index += 1
                for room in suitable_rooms:
                    slot = (room.id, day, start, end)
                    if slot in used_slots:
                        continue
                    assigned = (room, day, start, end)
                    used_slots.add(slot)
                    break
                if assigned:
                    break

            if assigned is None:
                skipped_by_branch_program[(branch.name, program.name)] += 1
                continue

            room, day, start, end = assigned
            group = Group(
                name=f"{branch.name} | {program.name} | гр.{teacher.id}",
                course_id=course.id,
                teacher_id=teacher.id,
                status=GroupStatus.active,
                start_date=datetime.utcnow(),
                end_date=None,
            )
            session.add(group)
            await session.flush()

            lesson = Lesson(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=room.id,
                branch_id=branch.id,
                program_id=program.id,
                day_of_week=day,
                time_start=start,
                time_end=end,
                topic=f"{program.name} — основное занятие",
                status=LessonStatus.scheduled,
                is_recurring=True,
            )
            session.add(lesson)

            created_groups.append((group, branch, program, group_size))
            groups_created_by_branch[branch.name] += 1

        if students and created_groups:
            groups_by_branch: dict[int, list[tuple[Group, Branch, EducationalProgram, int]]] = defaultdict(list)
            for payload in created_groups:
                groups_by_branch[payload[1].id].append(payload)

            branch_ids = [branch.id for branch in non_office_branches]
            assigned_student_ids = set()
            group_remaining: dict[int, int] = {group.id: size for group, _, _, size in created_groups}

            for index, student in enumerate(students):
                branch_id = branch_ids[index % len(branch_ids)]
                branch_groups = groups_by_branch.get(branch_id, [])
                target_group = next((g for g in branch_groups if group_remaining[g[0].id] > 0), None)
                if target_group is None:
                    target_group = next((g for g in created_groups if group_remaining[g[0].id] > 0), None)
                if target_group is None:
                    break

                group = target_group[0]
                session.add(
                    StudentGroup(
                        group_id=group.id,
                        student_name=student.full_name,
                        student_phone=student.phone,
                        student_email=student.email,
                        student_type=str(student.student_type.value) if hasattr(student.student_type, "value") else str(student.student_type),
                        form_id=student.source_form_id,
                        is_active=True,
                    )
                )
                group_remaining[group.id] -= 1
                assigned_student_ids.add(student.id)

            if students:
                cycle_students = students if students else []
                cycle_index = 0
                for group, _, _, _ in created_groups:
                    while group_remaining[group.id] > 0 and cycle_students:
                        student = cycle_students[cycle_index % len(cycle_students)]
                        cycle_index += 1
                        session.add(
                            StudentGroup(
                                group_id=group.id,
                                student_name=student.full_name,
                                student_phone=student.phone,
                                student_email=student.email,
                                student_type=str(student.student_type.value) if hasattr(student.student_type, "value") else str(student.student_type),
                                form_id=student.source_form_id,
                                is_active=True,
                            )
                        )
                        group_remaining[group.id] -= 1

        await session.commit()

        print("\n📊 Отчёт распределения групп:")
        for branch in sorted(non_office_branches, key=lambda b: b.name):
            print(f"- {branch.name}: создано групп {groups_created_by_branch.get(branch.name, 0)}")

        skipped_total = sum(skipped_by_branch_program.values())
        print(f"\nПропущено групп из-за нехватки кабинетов: {skipped_total}")
        if skipped_total:
            for (branch_name, program_name), count in sorted(skipped_by_branch_program.items()):
                print(f"  * {branch_name} — {program_name}: {count}")


if __name__ == "__main__":
    asyncio.run(seed_distribution())
