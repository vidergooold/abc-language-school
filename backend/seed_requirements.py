"""seed_requirements.py

Финальный seed-скрипт, обеспечивающий выполнение всех требований валидации:

1. Все 9 видов образовательных программ существуют и используются в расписании.
2. Каждый преподаватель имеет ≥ 5 занятий в расписании (is_recurring=True).
3. Каждый преподаватель привязан к группам по языку через TeacherGroup.
4. Каждый активный студент привязан хотя бы к одной группе через StudentGroup.
5. У каждой группы установлен язык (из связанного курса).

Запуск (из директории backend):
    python seed_requirements.py

Обычно вызывается автоматически из seeds/seed_all.py как последний шаг.
"""

import asyncio
import sys
from collections import defaultdict
from datetime import time
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import Course, Group, GroupStatus, StudentGroup
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.student import Student
from app.models.teacher import Teacher, TeacherGroup
from app.schedule_rules import canonical_program_duration_minutes, derive_time_end

# ─── Константы ───────────────────────────────────────────────────────────────

TARGET_LESSONS_PER_TEACHER = 5

# Все виды программ, которые должны существовать в системе
PROGRAMS_DATA = [
    {
        "name": "Дошкольники",
        "code": "PRESCHOOL",
        "language": "Английский",
        "level": "A0",
        "target_group": "дошкольники",
        "duration_months": 9,
        "description": "Программа раннего развития на английском языке для дошкольников.",
    },
    {
        "name": "FH1, AS1",
        "code": "FH1-AS1",
        "language": "Английский",
        "level": "A1",
        "target_group": "школьники",
        "duration_months": 9,
        "description": "Базовый курс английского языка для младших школьников.",
    },
    {
        "name": "AS2, AS3, AS4",
        "code": "AS2-AS4",
        "language": "Английский",
        "level": "A2",
        "target_group": "школьники",
        "duration_months": 9,
        "description": "Программа для школьников среднего уровня.",
    },
    {
        "name": "GWA1+, GWA2",
        "code": "GWA1-GWA2",
        "language": "Английский",
        "level": "B1",
        "target_group": "школьники",
        "duration_months": 9,
        "description": "Программа для школьников уровня pre-intermediate.",
    },
    {
        "name": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
        "code": "GWB-GWC",
        "language": "Английский",
        "level": "B2",
        "target_group": "школьники",
        "duration_months": 9,
        "description": "Программа для школьников уровня upper-intermediate.",
    },
    {
        "name": "Взрослые групповые",
        "code": "ADULT-GROUP",
        "language": "Английский",
        "level": "B1",
        "target_group": "взрослые",
        "duration_months": 6,
        "description": "Групповая программа английского языка для взрослых.",
    },
    {
        "name": "Мини-группа (2 чел.)",
        "code": "MINI-GROUP",
        "language": "Английский",
        "level": "B1",
        "target_group": "взрослые",
        "duration_months": 6,
        "description": "Мини-группа (2 человека) английского языка.",
    },
    {
        "name": "Индивидуальные занятия",
        "code": "INDIVIDUAL",
        "language": "Английский",
        "level": "A1",
        "target_group": "все",
        "duration_months": 6,
        "description": "Индивидуальные занятия английским языком.",
    },
    {
        "name": "Китайский язык",
        "code": "CHINESE",
        "language": "Китайский",
        "level": "A1",
        "target_group": "все",
        "duration_months": 9,
        "description": "Программа изучения китайского языка.",
    },
]

# Слоты времени для расширения расписания
DAILY_SLOTS: list[tuple[time, time]] = [
    (time(9, 0), time(10, 30)),
    (time(10, 45), time(12, 15)),
    (time(13, 0), time(14, 30)),
    (time(15, 0), time(16, 30)),
    (time(17, 0), time(18, 30)),
    (time(19, 0), time(20, 30)),
]

DAYS_ORDER = [
    DayOfWeek.monday,
    DayOfWeek.tuesday,
    DayOfWeek.wednesday,
    DayOfWeek.thursday,
    DayOfWeek.friday,
    DayOfWeek.saturday,
]

# Соответствие названий групп → названиям программ (для определения program_id)
GROUP_NAME_TO_PROGRAM: dict[str, str] = {
    "Дошкольники": "Дошкольники",
    "FH1": "FH1, AS1",
    "AS1": "FH1, AS1",
    "AS2": "AS2, AS3, AS4",
    "AS3": "AS2, AS3, AS4",
    "AS4": "AS2, AS3, AS4",
    "GWA1+": "GWA1+, GWA2",
    "GWA2": "GWA1+, GWA2",
    "GWB1": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
    "GWB1+": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
    "GWB2": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
    "GWB2+": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
    "GWC1": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
    "Взрослые групповые": "Взрослые групповые",
    "Мини-группа (2 чел.)": "Мини-группа (2 чел.)",
    "Индивидуальные занятия": "Индивидуальные занятия",
    "Китайский": "Китайский язык",
}


# ─── Вспомогательные функции ──────────────────────────────────────────────────


def _teacher_language(teacher: Teacher) -> str:
    s = (teacher.subject or "").strip().lower()
    if "китай" in s:
        return "Китайский"
    return "Английский"


def _program_duration_minutes(program_name: str) -> int:
    return canonical_program_duration_minutes(program_name) or 90


def _derive_time_end(time_start: time, duration_minutes: int) -> time:
    return derive_time_end(time_start, duration_minutes)


# ─── Шаги seed ───────────────────────────────────────────────────────────────


async def _ensure_programs(session: AsyncSession) -> dict[str, EducationalProgram]:
    """Создаёт все образовательные программы, если они отсутствуют."""
    programs: dict[str, EducationalProgram] = {}
    created = 0

    for p_data in PROGRAMS_DATA:
        result = await session.execute(
            select(EducationalProgram).where(EducationalProgram.name == p_data["name"])
        )
        program = result.scalar_one_or_none()
        if not program:
            program = EducationalProgram(
                name=p_data["name"],
                code=p_data["code"],
                language=p_data["language"],
                level=p_data["level"],
                target_group=p_data["target_group"],
                duration_months=p_data["duration_months"],
                description=p_data.get("description"),
                is_active=True,
            )
            session.add(program)
            await session.flush()
            created += 1
        programs[program.name] = program

    if created:
        print(f"  ✅ Создано программ: {created}")
    else:
        print(f"  ✓  Все {len(PROGRAMS_DATA)} программ уже существуют")
    return programs


async def _ensure_group_languages(session: AsyncSession) -> None:
    """Обновляет поле language у групп, которым оно не задано."""
    result = await session.execute(
        select(Group, Course.language.label("course_lang"))
        .join(Course, Course.id == Group.course_id)
        .where(Group.language.is_(None))
    )
    rows = result.all()
    for row in rows:
        row.Group.language = row.course_lang
    if rows:
        print(f"  ✅ Обновлено групп с полем language: {len(rows)}")
    else:
        print("  ✓  У всех групп уже задан язык")


async def _ensure_groups_for_programs(
    session: AsyncSession,
    programs: dict[str, EducationalProgram],
) -> None:
    """Создаёт хотя бы одну группу для программ, у которых её нет."""
    # Получаем все курсы по языку
    courses_result = await session.execute(
        select(Course).where(Course.is_active == True)
    )
    courses = courses_result.scalars().all()
    course_by_lang: dict[str, Course] = {}
    for c in courses:
        if c.language not in course_by_lang:
            course_by_lang[c.language] = c

    # Получаем преподавателей по языку
    teachers_result = await session.execute(
        select(Teacher).where(Teacher.is_active == True).order_by(Teacher.id)
    )
    teachers = teachers_result.scalars().all()
    teachers_by_lang: dict[str, list[Teacher]] = defaultdict(list)
    for t in teachers:
        teachers_by_lang[_teacher_language(t)].append(t)

    # Для каждой программы нужно убедиться, что существует хотя бы одна группа с этим названием
    program_to_canonical_group_name = {
        "Дошкольники": "Дошкольники",
        "FH1, AS1": "FH1",
        "AS2, AS3, AS4": "AS2",
        "GWA1+, GWA2": "GWA1+",
        "GWB1, GWB1+, GWB2, GWB2+, GWC1": "GWB1",
        "Взрослые групповые": "Взрослые групповые",
        "Мини-группа (2 чел.)": "Мини-группа (2 чел.)",
        "Индивидуальные занятия": "Индивидуальные занятия",
        "Китайский язык": "Китайский",
    }

    created = 0
    for prog_name, group_name in program_to_canonical_group_name.items():
        program = programs.get(prog_name)
        if not program:
            continue

        # Check if group exists
        result = await session.execute(
            select(Group).where(Group.name == group_name).limit(1)
        )
        existing_group = result.scalar_one_or_none()
        if existing_group:
            continue

        # Find appropriate course
        lang = program.language
        course = course_by_lang.get(lang)
        if not course:
            # Pick any course
            course = courses[0] if courses else None
        if not course:
            print(f"  ⚠️  Нет курса для программы '{prog_name}' — группа не создана")
            continue

        # Find appropriate teacher
        t_list = teachers_by_lang.get(lang, [])
        teacher = t_list[0] if t_list else (teachers[0] if teachers else None)

        group = Group(
            name=group_name,
            course_id=course.id,
            teacher_id=teacher.id if teacher else None,
            language=lang,
            status=GroupStatus.active,
        )
        session.add(group)
        await session.flush()
        created += 1

    if created:
        await session.flush()
        print(f"  ✅ Создано групп для программ: {created}")
    else:
        print("  ✓  Группы для всех программ уже существуют")


async def _extend_teacher_schedules(
    session: AsyncSession,
    programs: dict[str, EducationalProgram],
) -> None:
    """Дополняет расписание так, чтобы каждый учитель имел ≥ TARGET_LESSONS уроков."""

    # Получаем всех активных преподавателей
    teachers_result = await session.execute(
        select(Teacher).where(Teacher.is_active == True).order_by(Teacher.id)
    )
    teachers = teachers_result.scalars().all()

    # Считаем текущее количество уроков на учителя
    counts_result = await session.execute(
        select(Lesson.teacher_id, func.count(Lesson.id).label("cnt"))
        .where(Lesson.status == LessonStatus.scheduled)
        .group_by(Lesson.teacher_id)
    )
    teacher_lesson_counts: dict[int, int] = {
        row.teacher_id: row.cnt for row in counts_result
    }

    # Загружаем все группы с языком курса
    groups_result = await session.execute(
        select(Group, Course.language.label("lang"))
        .join(Course, Course.id == Group.course_id)
        .where(Group.status.in_([GroupStatus.active, GroupStatus.recruiting]))
    )
    all_groups_with_lang: list[tuple[Group, str]] = [
        (row.Group, row.lang) for row in groups_result
    ]

    # Получаем аудитории
    classrooms_result = await session.execute(
        select(Classroom).where(Classroom.is_active == True).order_by(Classroom.id)
    )
    classrooms = classrooms_result.scalars().all()
    if not classrooms:
        # Создаём запасную аудиторию
        fallback = Classroom(name="каб. 001", capacity=20, is_active=True)
        session.add(fallback)
        await session.flush()
        classrooms = [fallback]

    # Получаем учебные филиалы
    branches_result = await session.execute(
        select(Branch)
        .where(Branch.is_active == True, Branch.is_administrative.is_(False))
        .order_by(Branch.id)
    )
    branches = branches_result.scalars().all()
    if not branches:
        # Попробуем взять любые филиалы
        branches_result2 = await session.execute(
            select(Branch).where(Branch.is_active == True).order_by(Branch.id)
        )
        branches = branches_result2.scalars().all()
    if not branches:
        print("  ⚠️  Нет филиалов — расширение расписания пропущено")
        return

    # Строим набор занятых слотов из ВСЕХ (scheduled) уроков
    all_lessons_result = await session.execute(
        select(Lesson).where(Lesson.status == LessonStatus.scheduled)
    )
    all_lessons = all_lessons_result.scalars().all()

    teacher_slots: set[tuple] = set()   # (teacher_id, day, time_start)
    group_slots: set[tuple] = set()     # (group_id, day, time_start)
    room_slots: set[tuple] = set()      # (classroom_id, day, time_start)
    used_program_ids: set[int] = set()

    for les in all_lessons:
        teacher_slots.add((les.teacher_id, les.day_of_week, les.time_start))
        group_slots.add((les.group_id, les.day_of_week, les.time_start))
        room_slots.add((les.classroom_id, les.day_of_week, les.time_start))
        if les.program_id:
            used_program_ids.add(les.program_id)

    # Разбиваем программы по языку
    english_programs = [p for p in programs.values() if p.language == "Английский"]
    chinese_programs = [p for p in programs.values() if p.language == "Китайский"]

    added_total = 0

    for teacher in teachers:
        current_count = teacher_lesson_counts.get(teacher.id, 0)
        needed = max(0, TARGET_LESSONS_PER_TEACHER - current_count)
        if needed == 0:
            continue

        t_lang = _teacher_language(teacher)
        t_groups = [g for g, lang in all_groups_with_lang if lang == t_lang]
        t_programs = english_programs if t_lang == "Английский" else chinese_programs

        if not t_groups:
            print(f"  ⚠️  Нет групп ({t_lang}) для {teacher.full_name}")
            continue
        if not t_programs:
            print(f"  ⚠️  Нет программ ({t_lang}) для {teacher.full_name}")
            continue

        added = 0
        slot_iter = (
            (day, t_start)
            for day in DAYS_ORDER
            for t_start, _ in DAILY_SLOTS
        )

        for day, t_start in slot_iter:
            if added >= needed:
                break

            # Проверяем, свободен ли учитель
            if (teacher.id, day, t_start) in teacher_slots:
                continue

            # Ищем свободную группу
            group: Group | None = None
            for g in t_groups:
                if (g.id, day, t_start) not in group_slots:
                    group = g
                    break
            if group is None:
                continue

            # Ищем свободную аудиторию
            classroom: Classroom | None = None
            for c in classrooms:
                if (c.id, day, t_start) not in room_slots:
                    classroom = c
                    break
            if classroom is None:
                continue

            # Выбираем программу — предпочитаем ещё не использованные
            program: EducationalProgram | None = None
            for p in t_programs:
                if p.id not in used_program_ids:
                    program = p
                    break
            if program is None:
                program = t_programs[added % len(t_programs)]
            duration_minutes = _program_duration_minutes(program.name)
            t_end = _derive_time_end(t_start, duration_minutes)

            # Выбираем филиал (round-robin по счётчику добавленных уроков)
            branch = branches[added % len(branches)]

            lesson = Lesson(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                branch_id=branch.id,
                program_id=program.id,
                day_of_week=day,
                time_start=t_start,
                time_end=t_end,
                topic=f"{program.name} — занятие",
                status=LessonStatus.scheduled,
                is_recurring=True,
            )
            session.add(lesson)

            # Обновляем отслеживание занятых слотов
            teacher_slots.add((teacher.id, day, t_start))
            group_slots.add((group.id, day, t_start))
            room_slots.add((classroom.id, day, t_start))
            used_program_ids.add(program.id)

            added += 1
            added_total += 1

        if added < needed:
            current_after = current_count + added
            print(
                f"  ⚠️  {teacher.full_name}: добавлено {added}/{needed} "
                f"(итого: {current_after})"
            )

    await session.flush()

    # Проверяем, все ли программы использованы
    unused = [
        p for p in programs.values() if p.id not in used_program_ids
    ]
    if unused:
        print(
            f"  ⚠️  Программы ещё не использованы в расписании: "
            + ", ".join(p.name for p in unused)
        )

    print(f"  ✅ Добавлено уроков: {added_total}")


async def _link_teacher_groups(session: AsyncSession) -> None:
    """Привязывает каждого преподавателя к группам по его языку через TeacherGroup."""

    teachers_result = await session.execute(
        select(Teacher).where(Teacher.is_active == True).order_by(Teacher.id)
    )
    teachers = teachers_result.scalars().all()

    # Все существующие TeacherGroup
    existing_tg_result = await session.execute(select(TeacherGroup))
    existing_pairs: set[tuple[int, int]] = {
        (tg.teacher_id, tg.group_id) for tg in existing_tg_result.scalars().all()
    }

    # Загружаем группы с языком курса
    groups_result = await session.execute(
        select(Group, Course.language.label("lang"))
        .join(Course, Course.id == Group.course_id)
        .where(Group.status.in_([GroupStatus.active, GroupStatus.recruiting]))
    )
    groups_by_lang: dict[str, list[Group]] = defaultdict(list)
    for row in groups_result:
        groups_by_lang[row.lang].append(row.Group)

    created = 0
    for teacher in teachers:
        t_lang = _teacher_language(teacher)
        matching_groups = groups_by_lang.get(t_lang, [])

        for group in matching_groups:
            if (teacher.id, group.id) not in existing_pairs:
                tg = TeacherGroup(teacher_id=teacher.id, group_id=group.id)
                session.add(tg)
                existing_pairs.add((teacher.id, group.id))
                created += 1

    await session.flush()
    print(f"  ✅ Создано привязок преподаватель–группа: {created}")


async def _ensure_student_groups(session: AsyncSession) -> None:
    """Гарантирует, что каждый активный студент привязан хотя бы к одной группе."""

    students_result = await session.execute(
        select(Student).where(Student.is_active == True).order_by(Student.id)
    )
    students = students_result.scalars().all()

    # Имена студентов, у которых есть активная запись StudentGroup
    sg_result = await session.execute(
        select(StudentGroup.student_name).where(StudentGroup.is_active == True)
    )
    students_with_groups: set[str] = {row[0] for row in sg_result.fetchall()}

    # Загружаем все активные группы для распределения
    groups_result = await session.execute(
        select(Group)
        .where(Group.status.in_([GroupStatus.active, GroupStatus.recruiting]))
        .order_by(Group.id)
    )
    all_groups = groups_result.scalars().all()

    if not all_groups:
        print("  ⚠️  Нет групп для привязки студентов")
        return

    added = 0
    for student in students:
        if student.full_name in students_with_groups:
            continue

        # Назначаем группу по счётчику (round-robin по порядку итерации)
        target_group = all_groups[added % len(all_groups)]
        s_type = (
            student.student_type.value
            if hasattr(student.student_type, "value")
            else str(student.student_type)
        )

        sg = StudentGroup(
            group_id=target_group.id,
            student_name=student.full_name,
            student_phone=student.phone,
            student_email=student.email,
            student_type=s_type,
            form_id=student.source_form_id,
            is_active=True,
        )
        session.add(sg)
        students_with_groups.add(student.full_name)
        added += 1

    await session.flush()
    if added:
        print(f"  ✅ Студентов привязано к группам: {added}")
    else:
        print("  ✓  Все студенты уже привязаны к группам")


# ─── Главная функция ──────────────────────────────────────────────────────────


async def seed_requirements() -> None:
    await init_db()

    print("\n🔧 seed_requirements: запуск...")

    async with AsyncSessionLocal() as session:
        print("\n1. Образовательные программы...")
        programs = await _ensure_programs(session)
        await session.commit()

        print("\n2. Языки групп...")
        async with AsyncSessionLocal() as s2:
            await _ensure_group_languages(s2)
            await s2.commit()

        print("\n3. Группы для каждой программы...")
        async with AsyncSessionLocal() as s3:
            await _ensure_groups_for_programs(s3, programs)
            await s3.commit()

        # Перезагружаем программы после commit, чтобы получить актуальные id
        async with AsyncSessionLocal() as s4:
            prog_result = await s4.execute(
                select(EducationalProgram).where(EducationalProgram.is_active == True)
            )
            programs = {p.name: p for p in prog_result.scalars().all()}

            print("\n4. Расширение расписания (≥ 5 уроков на учителя)...")
            await _extend_teacher_schedules(s4, programs)
            await s4.commit()

        print("\n5. Привязка преподавателей к группам по языку...")
        async with AsyncSessionLocal() as s5:
            await _link_teacher_groups(s5)
            await s5.commit()

        print("\n6. Привязка студентов к группам...")
        async with AsyncSessionLocal() as s6:
            await _ensure_student_groups(s6)
            await s6.commit()

    print("\n✅ seed_requirements завершён!")


if __name__ == "__main__":
    asyncio.run(seed_requirements())
