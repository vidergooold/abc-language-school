"""
Seed реального расписания ABC Language School.

Учителя ищутся по фамилии через ILIKE-матч на поле full_name.
"""
from typing import Optional
import asyncio
from datetime import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.teacher import Teacher
from app.schedule_rules import canonical_program_duration_minutes, derive_time_end

BRANCH_CLASSROOMS = {
    "Гимназия 11 «Гармония»": ("каб. 113", "каб. 114"),
    "Гимназия №7 «Сибирская»": ("каб. 119",),
    "МАОУ ЛИТ": ("каб. библиотека", "каб. 116"),
    "МАОУ НГПЛ": ("каб. 115",),
    "МАОУ НЭЛ": ("каб. 205",),
    "МАОУ СОШ №216": ("каб. 317", "каб. 410"),
    "МАОУ СОШ №217": ("каб. 314А",),
    "МАОУ СОШ №218": ("каб. АВС",),
    "МАОУ СОШ №221": ("каб. 128", "каб. 311"),
    "МАОУ СОШ №222": ("каб. 128", "каб. 311"),
    "МБОУ Гимназия №5": ("каб. 191",),
    "МБОУ Гимназия №9": ("каб. 37", "каб. 41"),
    "МБОУ СОШ №11": ("каб. 203",),
    "МБОУ СОШ №121 «Академическая»": ("каб. 214",),
    "МБОУ СОШ №13": ("каб. 18",),
    "МБОУ СОШ №155": ("каб. 426",),
    "МБОУ СОШ №167": ("каб. 211",),
    "МБОУ СОШ №186": ("каб. 211",),
    "МБОУ СОШ №188": ("каб. 409", "каб. АВС"),
    "МБОУ СОШ №195": ("каб. 229",),
    "МБОУ СОШ №56": ("каб. 3", "каб. 10"),
}

TEACHER_LANGUAGE_BY_LASTNAME = {
    "Арнгольд": "Английский",
    "Белова": "Английский",
    "Быковская": "Английский",
    "Винокурова": "Китайский",
    "Воронцова": "Китайский",
    "Данилова": "Английский",
    "Евдокимова": "Английский",
    "Зудяева": "Английский",
    "Иванова": "Английский",
    "Караваева": "Английский",
    "Козлова": "Английский",
    "Колесник": "Английский",
    "Куцых": "Английский",
    "Лукьянова": "Английский",
    "Митина": "Английский",
    "Осинина": "Английский",
    "Пасикан": "Английский",
    "Переведенцева": "Английский",
    "Позднякова": "Английский",
    "Походная": "Английский",
    "Родина": "Английский",
    "Рубе": "Английский",
    "Темлякова": "Английский",
    "Тихвинская": "Английский",
    "Турабова": "Английский",
    "Федорова": "Английский",
    "Фомина": "Английский",
}
ALLOWED_TEACHER_LASTNAMES = set(TEACHER_LANGUAGE_BY_LASTNAME.keys())

GROUPS_SCHEDULE = [
    {"group_name": "Дошкольники", "teacher_lastname": "Данилова", "branch_name": "МАОУ СОШ №221", "day_of_week": DayOfWeek.monday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 311"},
    {"group_name": "Дошкольники", "teacher_lastname": "Зудяева", "branch_name": "МБОУ Гимназия №9", "day_of_week": DayOfWeek.thursday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 37"},
    {"group_name": "FH1", "teacher_lastname": "Данилова", "branch_name": "Гимназия 11 «Гармония»", "day_of_week": DayOfWeek.tuesday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 113"},
    {"group_name": "FH1", "teacher_lastname": "Зудяева", "branch_name": "МБОУ СОШ №56", "day_of_week": DayOfWeek.friday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 3"},
    {"group_name": "AS1", "teacher_lastname": "Федорова", "branch_name": "Гимназия 11 «Гармония»", "day_of_week": DayOfWeek.wednesday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 114"},
    {"group_name": "AS1", "teacher_lastname": "Темлякова", "branch_name": "МБОУ СОШ №167", "day_of_week": DayOfWeek.saturday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 211"},
    {"group_name": "AS2", "teacher_lastname": "Федорова", "branch_name": "Гимназия №7 «Сибирская»", "day_of_week": DayOfWeek.tuesday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 119"},
    {"group_name": "AS2", "teacher_lastname": "Темлякова", "branch_name": "МАОУ ЛИТ", "day_of_week": DayOfWeek.thursday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 116"},
    {"group_name": "AS3", "teacher_lastname": "Евдокимова", "branch_name": "МАОУ ЛИТ", "day_of_week": DayOfWeek.monday, "time_start": time(13, 0), "time_end": time(14, 30), "classroom": "каб. библиотека"},
    {"group_name": "AS3", "teacher_lastname": "Походная", "branch_name": "МБОУ СОШ №121 «Академическая»", "day_of_week": DayOfWeek.tuesday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 214"},
    {"group_name": "AS4", "teacher_lastname": "Евдокимова", "branch_name": "МБОУ СОШ №11", "day_of_week": DayOfWeek.monday, "time_start": time(19, 0), "time_end": time(20, 30), "classroom": "каб. 203"},
    {"group_name": "AS4", "teacher_lastname": "Походная", "branch_name": "МБОУ СОШ №13", "day_of_week": DayOfWeek.wednesday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 18"},
    {"group_name": "GWA1+", "teacher_lastname": "Зудяева", "branch_name": "МАОУ НГПЛ", "day_of_week": DayOfWeek.tuesday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 115"},
    {"group_name": "GWA1+", "teacher_lastname": "Куцых", "branch_name": "МБОУ СОШ №155", "day_of_week": DayOfWeek.friday, "time_start": time(13, 0), "time_end": time(14, 30), "classroom": "каб. 426"},
    {"group_name": "GWA2", "teacher_lastname": "Зудяева", "branch_name": "МАОУ НЭЛ", "day_of_week": DayOfWeek.wednesday, "time_start": time(13, 0), "time_end": time(14, 30), "classroom": "каб. 205"},
    {"group_name": "GWA2", "teacher_lastname": "Куцых", "branch_name": "МБОУ СОШ №186", "day_of_week": DayOfWeek.saturday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 211"},
    {"group_name": "GWB1", "teacher_lastname": "Позднякова", "branch_name": "МАОУ СОШ №216", "day_of_week": DayOfWeek.monday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 317"},
    {"group_name": "GWB1", "teacher_lastname": "Фомина", "branch_name": "МБОУ СОШ №188", "day_of_week": DayOfWeek.wednesday, "time_start": time(19, 0), "time_end": time(20, 30), "classroom": "каб. АВС"},
    {"group_name": "GWB1+", "teacher_lastname": "Позднякова", "branch_name": "МАОУ СОШ №216", "day_of_week": DayOfWeek.thursday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 410"},
    {"group_name": "GWB1+", "teacher_lastname": "Фомина", "branch_name": "МБОУ СОШ №195", "day_of_week": DayOfWeek.thursday, "time_start": time(13, 0), "time_end": time(14, 30), "classroom": "каб. 229"},
    {"group_name": "GWB2", "teacher_lastname": "Колесник", "branch_name": "МАОУ СОШ №217", "day_of_week": DayOfWeek.friday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 314А"},
    {"group_name": "GWB2", "teacher_lastname": "Митина", "branch_name": "МБОУ СОШ №56", "day_of_week": DayOfWeek.friday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 10"},
    {"group_name": "GWB2+", "teacher_lastname": "Колесник", "branch_name": "МАОУ СОШ №218", "day_of_week": DayOfWeek.tuesday, "time_start": time(13, 0), "time_end": time(14, 30), "classroom": "каб. АВС"},
    {"group_name": "GWB2+", "teacher_lastname": "Митина", "branch_name": "МБОУ СОШ №188", "day_of_week": DayOfWeek.monday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 409"},
    {"group_name": "GWC1", "teacher_lastname": "Козлова", "branch_name": "МАОУ СОШ №221", "day_of_week": DayOfWeek.monday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 128"},
    {"group_name": "GWC1", "teacher_lastname": "Арнгольд", "branch_name": "МАОУ СОШ №222", "day_of_week": DayOfWeek.tuesday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 128"},
    {"group_name": "Взрослые групповые", "teacher_lastname": "Родина", "branch_name": "МАОУ СОШ №222", "day_of_week": DayOfWeek.friday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 311"},
    {"group_name": "Взрослые групповые", "teacher_lastname": "Лукьянова", "branch_name": "МАОУ СОШ №221", "day_of_week": DayOfWeek.wednesday, "time_start": time(15, 0), "time_end": time(16, 30), "classroom": "каб. 311"},
    {"group_name": "Мини-группа (2 чел.)", "teacher_lastname": "Осинина", "branch_name": "МБОУ Гимназия №5", "day_of_week": DayOfWeek.wednesday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 191"},
    {"group_name": "Мини-группа (2 чел.)", "teacher_lastname": "Караваева", "branch_name": "МБОУ Гимназия №9", "day_of_week": DayOfWeek.thursday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 41"},
    {"group_name": "Индивидуальные занятия", "teacher_lastname": "Иванова", "branch_name": "МБОУ СОШ №56", "day_of_week": DayOfWeek.tuesday, "time_start": time(19, 0), "time_end": time(20, 30), "classroom": "каб. 3"},
    {"group_name": "Индивидуальные занятия", "teacher_lastname": "Рубе", "branch_name": "МБОУ СОШ №167", "day_of_week": DayOfWeek.saturday, "time_start": time(9, 0), "time_end": time(10, 30), "classroom": "каб. 211"},
    {"group_name": "Китайский", "language": "Китайский", "teacher_lastname": "Винокурова", "branch_name": "МАОУ СОШ №222", "day_of_week": DayOfWeek.thursday, "time_start": time(17, 0), "time_end": time(18, 30), "classroom": "каб. 311"},
    {"group_name": "Китайский", "language": "Китайский", "teacher_lastname": "Воронцова", "branch_name": "МБОУ СОШ №186", "day_of_week": DayOfWeek.saturday, "time_start": time(11, 0), "time_end": time(12, 30), "classroom": "каб. 211"},
]


async def _find_teacher_by_lastname(db: AsyncSession, lastname: str) -> Optional[Teacher]:
    escaped = lastname.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await db.execute(
        select(Teacher)
        .where(Teacher.full_name.ilike(f"{escaped}%"))
        .where(Teacher.is_active)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _find_branch_by_name(db: AsyncSession, branch_name: str) -> Optional[Branch]:
    result = await db.execute(
        select(Branch)
        .where(Branch.name == branch_name)
        .where(Branch.is_active == True)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_or_create_group(
    db: AsyncSession, name: str, course_id: int, teacher_id: int
) -> Group:
    result = await db.execute(
        select(Group).where(
            Group.name == name,
            Group.course_id == course_id,
            Group.teacher_id == teacher_id,
        )
    )
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


def _lesson_duration_minutes(group_name: str) -> Optional[int]:
    return canonical_program_duration_minutes(group_name)


async def _get_or_create_classroom(db: AsyncSession, name: str, branch_id: int) -> Classroom:
    if branch_id is None:
        raise ValueError("branch_id is required for classroom binding")
    result = await db.execute(
        select(Classroom).where(
            Classroom.name == name,
            Classroom.branch_id == branch_id,
        )
    )
    classroom = result.scalar_one_or_none()
    if classroom:
        return classroom
    classroom = Classroom(name=name, capacity=12, branch_id=branch_id, is_active=True)
    db.add(classroom)
    await db.flush()
    return classroom


async def _get_or_create_courses(db: AsyncSession) -> dict[str, Course]:
    course_configs = {
        "Английский": {
            "name": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
            "level": CourseLevel.upper_intermediate,
            "category": CourseCategory.adults,
            "price_per_month": 4900,
        },
        "Китайский": {
            "name": "Китайский язык",
            "level": CourseLevel.beginner,
            "category": CourseCategory.adults,
            "price_per_month": 1200,
        },
    }
    courses: dict[str, Course] = {}
    for language, config in course_configs.items():
        result = await db.execute(select(Course).where(Course.name == config["name"]).limit(1))
        course = result.scalar_one_or_none()
        if course is None:
            course = Course(
                name=config["name"],
                language=language,
                level=config["level"],
                category=config["category"],
                price_per_month=config["price_per_month"],
            )
            db.add(course)
            await db.flush()
        courses[language] = course
    return courses


async def seed_real_schedule() -> None:
    await init_db()

    async with AsyncSessionLocal() as db:
        courses = await _get_or_create_courses(db)

        created_lessons = 0
        skipped_no_teacher = 0
        skipped_invalid_data = 0
        skipped_exists = 0

        for entry in GROUPS_SCHEDULE:
            lastname = entry["teacher_lastname"]
            branch_name = entry["branch_name"]
            classroom_name = entry["classroom"]

            if lastname not in ALLOWED_TEACHER_LASTNAMES:
                print(f"⚠️  Преподаватель '{lastname}' вне канонического списка — строка пропущена")
                skipped_invalid_data += 1
                continue

            allowed_classrooms = BRANCH_CLASSROOMS.get(branch_name)
            if not allowed_classrooms or classroom_name not in allowed_classrooms:
                print(
                    f"⚠️  Кабинет '{classroom_name}' не соответствует филиалу '{branch_name}' — строка пропущена"
                )
                skipped_invalid_data += 1
                continue

            teacher = await _find_teacher_by_lastname(db, lastname)
            if teacher is None:
                print(f"⚠️  Преподаватель '{lastname}' не найден — строка пропущена")
                skipped_no_teacher += 1
                continue

            branch = await _find_branch_by_name(db, branch_name)
            if branch is None:
                print(f"⚠️  Филиал '{branch_name}' не найден — строка пропущена")
                skipped_invalid_data += 1
                continue

            classroom = await _get_or_create_classroom(db, classroom_name, branch.id)
            expected_language = TEACHER_LANGUAGE_BY_LASTNAME.get(lastname)
            if expected_language is None:
                print(f"⚠️  Для преподавателя '{lastname}' не найден язык обучения — строка пропущена")
                skipped_invalid_data += 1
                continue
            explicit_language = entry.get("language")
            if explicit_language and explicit_language != expected_language:
                print(
                    f"⚠️  Для преподавателя '{lastname}' указан язык '{explicit_language}', "
                    f"ожидался '{expected_language}' — строка пропущена"
                )
                skipped_invalid_data += 1
                continue

            course_language = expected_language
            group = await _get_or_create_group(db, entry["group_name"], courses[course_language].id, teacher.id)

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

            duration_minutes = _lesson_duration_minutes(entry["group_name"])
            if duration_minutes is None:
                print(
                    f"⚠️  Не удалось определить длительность программы для группы '{entry['group_name']}' — строка пропущена"
                )
                skipped_invalid_data += 1
                continue

            lesson = Lesson(
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                branch_id=branch.id,
                day_of_week=entry["day_of_week"],
                time_start=entry["time_start"],
                time_end=derive_time_end(entry["time_start"], duration_minutes),
                status=LessonStatus.scheduled,
                is_recurring=True,
            )
            db.add(lesson)
            created_lessons += 1

        await db.commit()

    print(
        f"✅ Расписание загружено: создано {created_lessons} уроков, "
        f"пропущено (нет учителя) {skipped_no_teacher}, "
        f"пропущено (некорректные данные) {skipped_invalid_data}, "
        f"уже существовало {skipped_exists}"
    )


if __name__ == "__main__":
    asyncio.run(seed_real_schedule())
