from typing import Optional
"""Seed data for account pages: teachers, students, groups, lessons, and linked users."""

import asyncio
from datetime import datetime, timedelta, time

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import (
    Course,
    CourseCategory,
    CourseLevel,
    Group,
    GroupStatus,
    StudentGroup,
)
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.student import Student, StudentStatus, StudentType
from app.models.teacher import Teacher
from app.models.user import User, UserRole


async def _get_or_create(session, model, lookup: dict, defaults: Optional[dict] = None):
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalar_one_or_none()
    if instance:
        return instance, False
    payload = {**lookup, **(defaults or {})}
    instance = model(**payload)
    session.add(instance)
    await session.flush()
    return instance, True


async def seed_account_data():
    await init_db()

    async with AsyncSessionLocal() as session:
        branch, _ = await _get_or_create(
            session,
            Branch,
            {"name": "Офис (главный)"},
            {
                "address": "г. Новосибирск, ул. Бориса Богаткова, 208/2",
                "phone": "+79139121809",
                "email": "info@abc-school.ru",
                "manager_name": "Андрюнина Марина Викторовна",
                "manager_position": "Директор",
                "working_hours": "Пн-Пт с 09:00 до 20:00",
                "is_active": True,
            },
        )

        program_a1, _ = await _get_or_create(
            session,
            EducationalProgram,
            {"name": "English Start A1"},
            {
                "code": "ENG-A1",
                "language": "Английский",
                "level": "A1",
                "target_group": "школьники",
                "duration_months": 9,
                "description": "Базовая программа английского языка для школьников.",
                "is_active": True,
            },
        )
        program_a2, _ = await _get_or_create(
            session,
            EducationalProgram,
            {"name": "English Progress A2"},
            {
                "code": "ENG-A2",
                "language": "Английский",
                "level": "A2",
                "target_group": "взрослые",
                "duration_months": 9,
                "description": "Продолжающая программа английского языка.",
                "is_active": True,
            },
        )

        course_school, _ = await _get_or_create(
            session,
            Course,
            {"name": "Английский для школьников A1"},
            {
                "description": "Группа начального уровня для школьников.",
                "language": "Английский",
                "level": CourseLevel.beginner,
                "category": CourseCategory.school,
                "duration_months": 9,
                "lessons_per_week": 2,
                "price_per_month": 5400,
                "max_students": 10,
                "is_active": True,
            },
        )
        course_adult, _ = await _get_or_create(
            session,
            Course,
            {"name": "Английский для взрослых A2"},
            {
                "description": "Группа продолжающего уровня для взрослых.",
                "language": "Английский",
                "level": CourseLevel.elementary,
                "category": CourseCategory.adults,
                "duration_months": 9,
                "lessons_per_week": 2,
                "price_per_month": 6200,
                "max_students": 8,
                "is_active": True,
            },
        )

        group_school, _ = await _get_or_create(
            session,
            Group,
            {"name": "School A1 Morning"},
            {
                "course_id": course_school.id,
                "status": GroupStatus.active,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=180),
            },
        )
        group_adult, _ = await _get_or_create(
            session,
            Group,
            {"name": "Adult A2 Evening"},
            {
                "course_id": course_adult.id,
                "status": GroupStatus.active,
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=180),
            },
        )

        classroom_1, _ = await _get_or_create(
            session,
            Classroom,
            {"name": "Кабинет 101"},
            {"capacity": 12, "floor": 1, "has_projector": True, "has_whiteboard": True, "is_active": True},
        )
        classroom_2, _ = await _get_or_create(
            session,
            Classroom,
            {"name": "Кабинет 202"},
            {"capacity": 10, "floor": 2, "has_projector": True, "has_whiteboard": True, "is_active": True},
        )

        teachers_data = [
            {
                "full_name": "Иванова Анна Сергеевна",
                "email": "anna.ivanova@abc-school.ru",
                "phone": "+79131234567",
                "subject": "Английский",
                "language_level": "C2",
                "experience_years": 5,
                "bio": "Опытный преподаватель английского языка.",
            },
            {
                "full_name": "Петров Михаил Андреевич",
                "email": "mikhail.petrov@abc-school.ru",
                "phone": "+79139876543",
                "subject": "Английский",
                "language_level": "C1",
                "experience_years": 4,
                "bio": "Ведёт группы школьников и взрослых.",
            },
        ]

        teacher_records = []
        for teacher_data in teachers_data:
            teacher, _ = await _get_or_create(
                session,
                Teacher,
                {"email": teacher_data["email"]},
                {**teacher_data, "is_active": True},
            )
            teacher_records.append(teacher)
            await _get_or_create(
                session,
                User,
                {"email": teacher.email},
                {
                    "hashed_password": hash_password("teacher123"),
                    "full_name": teacher.full_name,
                    "role": UserRole.teacher,
                    "is_active": True,
                },
            )

        students_data = [
            {
                "full_name": "Смирнов Кирилл Олегович",
                "email": "kirill.smirnov@abc-school.ru",
                "phone": "+79001112233",
                "student_type": StudentType.child,
                "status": StudentStatus.active,
                "language_level": "A1",
            },
            {
                "full_name": "Козлова Мария Игоревна",
                "email": "maria.kozlova@abc-school.ru",
                "phone": "+79004445566",
                "student_type": StudentType.child,
                "status": StudentStatus.active,
                "language_level": "A1",
            },
            {
                "full_name": "Орлова Елена Павловна",
                "email": "elena.orlova@abc-school.ru",
                "phone": "+79007778899",
                "student_type": StudentType.adult,
                "status": StudentStatus.active,
                "language_level": "A2",
            },
        ]

        student_records = []
        for student_data in students_data:
            student, _ = await _get_or_create(
                session,
                Student,
                {"email": student_data["email"]},
                {**student_data, "is_active": True},
            )
            student_records.append(student)

        await _get_or_create(
            session,
            User,
            {"email": students_data[0]["email"]},
            {
                "hashed_password": hash_password("student123"),
                "full_name": students_data[0]["full_name"],
                "role": UserRole.student,
                "is_active": True,
            },
        )

        student_groups = [
            (group_school.id, student_records[0]),
            (group_school.id, student_records[1]),
            (group_adult.id, student_records[2]),
        ]
        for group_id, student in student_groups:
            await _get_or_create(
                session,
                StudentGroup,
                {"group_id": group_id, "student_email": student.email},
                {
                    "student_name": student.full_name,
                    "student_phone": student.phone,
                    "student_type": student.student_type.value,
                    "is_active": True,
                },
            )

        lessons_data = [
            {
                "group_id": group_school.id,
                "teacher_id": teacher_records[0].id,
                "classroom_id": classroom_1.id,
                "branch_id": branch.id,
                "program_id": program_a1.id,
                "day_of_week": DayOfWeek.monday,
                "time_start": time(10, 0),
                "time_end": time(11, 0),
                "topic": "Present Simple",
                "status": LessonStatus.scheduled,
                "is_recurring": True,
            },
            {
                "group_id": group_school.id,
                "teacher_id": teacher_records[0].id,
                "classroom_id": classroom_1.id,
                "branch_id": branch.id,
                "program_id": program_a1.id,
                "day_of_week": DayOfWeek.wednesday,
                "time_start": time(10, 0),
                "time_end": time(11, 0),
                "topic": "Reading Practice",
                "status": LessonStatus.scheduled,
                "is_recurring": True,
            },
            {
                "group_id": group_adult.id,
                "teacher_id": teacher_records[1].id,
                "classroom_id": classroom_2.id,
                "branch_id": branch.id,
                "program_id": program_a2.id,
                "day_of_week": DayOfWeek.tuesday,
                "time_start": time(18, 30),
                "time_end": time(20, 0),
                "topic": "Speaking Club",
                "status": LessonStatus.scheduled,
                "is_recurring": True,
            },
            {
                "group_id": group_adult.id,
                "teacher_id": teacher_records[1].id,
                "classroom_id": classroom_2.id,
                "branch_id": branch.id,
                "program_id": program_a2.id,
                "day_of_week": DayOfWeek.thursday,
                "time_start": time(18, 30),
                "time_end": time(20, 0),
                "topic": "Grammar Workshop",
                "status": LessonStatus.scheduled,
                "is_recurring": True,
            },
        ]

        for lesson_data in lessons_data:
            await _get_or_create(
                session,
                Lesson,
                {
                    "group_id": lesson_data["group_id"],
                    "teacher_id": lesson_data["teacher_id"],
                    "day_of_week": lesson_data["day_of_week"],
                    "time_start": lesson_data["time_start"],
                },
                lesson_data,
            )

        await session.commit()
        print("✅ Данные для личного кабинета загружены в БД")
        print("   Преподаватели: 2")
        print("   Студенты: 3")
        print("   Группы: 2")
        print("   Занятия: 4")
        print("   Тестовые логины: teacher123 / student123")


if __name__ == "__main__":
    asyncio.run(seed_account_data())