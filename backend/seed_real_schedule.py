"""Seed script for real school schedule data.

Usage:
    cd backend && python seed_real_schedule.py
"""

import asyncio
import os
import sys
from datetime import date, datetime, time, timedelta
from typing import Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _t(h: int, m: int) -> time:
    return time(h, m)


def _end(start: time, minutes: int) -> time:
    dt = datetime.combine(date.today(), start) + timedelta(minutes=minutes)
    return dt.time()


async def _get_or_create(
    session, model, lookup: dict, defaults: Optional[dict] = None
) -> Tuple[object, bool]:
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalar_one_or_none()
    if instance:
        return instance, False
    payload = {**lookup, **(defaults or {})}
    instance = model(**payload)
    session.add(instance)
    await session.flush()
    return instance, True


# ---------------------------------------------------------------------------
# Static data
# ---------------------------------------------------------------------------

TEACHER_NAMES = [
    "Анна Михайловна Темлякова",          # 1
    "Анфиса Вячеславовна Федорова",        # 2
    "Виктория Сергеевна Позднякова",       # 3
    "Алина Денисовна Караваева",           # 4
    "Мария Анатольевна Данилова",          # 5
    "Ольга Сергеевна Митина",              # 6
    "Светлана Ярославовна Лукьянова",      # 7
    "Ангелина Сергеевна Пасикан",          # 8
    "Елена Геннадьевна Козлова",           # 9
    "Любовь Николаевна Колесник",          # 10
    "Светлана Николаевна Осинина",         # 11
    "Диана Джейхуновна Турабова",          # 12
    "Александра Анатольевна Белова",       # 13
    "Алена Игоревна Походная",             # 14
    "Полина Евгеньевна Евдокимова",        # 15
    "Татьяна Петровна Родина",             # 16
    "Надежда Андреевна Зудяева",           # 17
    "Александра Переведенцева",            # 18
    "Виктория Олеговна Тихвинская",        # 19
    "Дарья Васильевна Рубе",               # 20
    "Марина Евгеньевна Куцых",             # 21
    "Снежанна Олеговна Фомина",            # 22
    "Елена Александровна Винокурова",      # 23
    "Марина Эдуардовна Быковская",         # 24
    "Анна Вадимовна Воронцова",            # 25
    "Марина Владимировна Алексеева",       # 26
    "Валерия Евгеньевна Арнгольд",         # 27
    "Дарья Дмитриевна Калужина",           # 28
]

BRANCH_NAMES = [
    "Школа №216",
    "Школа №11",
    "Школа №188",
    "Офис",
    "Школа №121",
    "Гимназия №5",
    "Гимназия №11",
    "Школа №221",
    "Гимназия №9",
    "Школа №218",
    "НГПЛ",
    "Школа №2",
    "Гимназия №7",
    "НЭЛ",
    "Школа №56",
    "Школа №155",
    "ЛИТ",
    "Школа №186",
    "Школа №199",
    "Школа №217",
    "Школа №195",
    "Школа №13",
    "Школа №167",
    "Школа №222",
]

COURSES_DEF = [
    {
        "name": "GateWay B1+",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.school,
        "price_per_month": 5250,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "GateWay A2",
        "level": CourseLevel.elementary,
        "category": CourseCategory.school,
        "price_per_month": 4500,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "GateWay A1+",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 4500,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "GateWay B1",
        "level": CourseLevel.pre_intermediate,
        "category": CourseCategory.school,
        "price_per_month": 5250,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Academy Stars 1",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 3400,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Academy Stars 2",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 3800,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Academy Stars 3",
        "level": CourseLevel.elementary,
        "category": CourseCategory.school,
        "price_per_month": 3800,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Fly High 1",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 3400,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Индивидуальные занятия (45 мин)",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 1200,
        "duration_months": 12,
        "lessons_per_week": 1,
    },
    {
        "name": "Индивидуальные занятия (30 мин)",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 800,
        "duration_months": 12,
        "lessons_per_week": 1,
    },
    {
        "name": "Индивидуальные занятия (60 мин)",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 1600,
        "duration_months": 12,
        "lessons_per_week": 1,
    },
    {
        "name": "Индивидуальные занятия (90 мин)",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 2400,
        "duration_months": 12,
        "lessons_per_week": 1,
    },
    {
        "name": "Мини-группа Academy Stars 3 (45 мин)",
        "level": CourseLevel.elementary,
        "category": CourseCategory.school,
        "price_per_month": 3500,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
    {
        "name": "Мини-группа GateWay B1+ (45 мин)",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.school,
        "price_per_month": 7000,
        "duration_months": 9,
        "lessons_per_week": 2,
    },
]

STUDENTS_DEF = [
    {"full_name": "Кружкова Ульяна", "student_type": StudentType.child},
    {"full_name": "Мухарев Максим", "student_type": StudentType.child},
    {"full_name": "Мусорбаев Артем", "student_type": StudentType.child},
    {"full_name": "Димитров Антон", "student_type": StudentType.child},
    {"full_name": "Агапкин Вячеслав", "student_type": StudentType.adult},
    {"full_name": "Масенкова Аэлита", "student_type": StudentType.adult},
]

# Each entry describes one group and its recurring lessons.
# Fields:
#   name        – group name (unique key)
#   course      – course name
#   teacher     – teacher full_name
#   branch      – branch name (used for each lesson)
#   duration_min – lesson length in minutes
#   schedule    – list of (DayOfWeek, time_start)
#   student     – full_name of individual student (or None)
GROUPS_DEF = [
    # =========================================================
    # Темлякова А.М. — Школа №216
    # =========================================================
    {
        "name": "GateWay B1+ (1)",
        "course": "GateWay B1+",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.monday, _t(9, 30)),
            (DayOfWeek.wednesday, _t(9, 30)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (1)",
        "course": "GateWay A2",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(11, 10)),
            (DayOfWeek.wednesday, _t(11, 10)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (1)",
        "course": "Academy Stars 1",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(12, 30)),
            (DayOfWeek.wednesday, _t(12, 30)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (1)",
        "course": "Academy Stars 3",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(13, 50)),
            (DayOfWeek.wednesday, _t(13, 50)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (1)",
        "course": "GateWay A1+",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(15, 0)),
            (DayOfWeek.wednesday, _t(15, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (2)",
        "course": "Academy Stars 3",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(16, 20)),
            (DayOfWeek.wednesday, _t(16, 20)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (1)",
        "course": "Academy Stars 2",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(17, 20)),
            (DayOfWeek.wednesday, _t(17, 20)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (2)",
        "course": "GateWay A2",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(9, 50)),
            (DayOfWeek.thursday, _t(9, 50)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (2)",
        "course": "Academy Stars 2",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(11, 10)),
            (DayOfWeek.thursday, _t(11, 10)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (2)",
        "course": "Academy Stars 1",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.tuesday, _t(12, 20)),
            (DayOfWeek.thursday, _t(12, 20)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (3)",
        "course": "Academy Stars 3",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(13, 20)),
            (DayOfWeek.thursday, _t(13, 20)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (4)",
        "course": "Academy Stars 3",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(14, 30)),
            (DayOfWeek.thursday, _t(14, 30)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (2)",
        "course": "GateWay A1+",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(15, 40)),
            (DayOfWeek.thursday, _t(15, 40)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (3)",
        "course": "GateWay A2",
        "teacher": "Анна Михайловна Темлякова",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(17, 0)),
            (DayOfWeek.thursday, _t(17, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Федорова А.В. — Школа №11
    # =========================================================
    {
        "name": "Fly High 1 (1)",
        "course": "Fly High 1",
        "teacher": "Анфиса Вячеславовна Федорова",
        "branch": "Школа №11",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(11, 35)),
            (DayOfWeek.wednesday, _t(11, 35)),
        ],
        "student": None,
    },
    {
        "name": "Fly High 1 (2)",
        "course": "Fly High 1",
        "teacher": "Анфиса Вячеславовна Федорова",
        "branch": "Школа №11",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.tuesday, _t(11, 35)),
            (DayOfWeek.thursday, _t(11, 35)),
        ],
        "student": None,
    },
    # =========================================================
    # Федорова А.В. — НГПЛ (individual)
    # =========================================================
    {
        "name": "Агапкин Вячеслав (инд.)",
        "course": "Индивидуальные занятия (60 мин)",
        "teacher": "Анфиса Вячеславовна Федорова",
        "branch": "НГПЛ",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(15, 15)),
            (DayOfWeek.thursday, _t(15, 15)),
        ],
        "student": "Агапкин Вячеслав",
    },
    # =========================================================
    # Позднякова В.С. — Школа №188
    # =========================================================
    {
        "name": "Fly High 1 (3)",
        "course": "Fly High 1",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(11, 50)),
            (DayOfWeek.friday, _t(11, 15)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (3)",
        "course": "Academy Stars 1",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(12, 50)),
            (DayOfWeek.friday, _t(12, 50)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (3)",
        "course": "Academy Stars 2",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(13, 45)),
            (DayOfWeek.friday, _t(13, 45)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (3)",
        "course": "GateWay A1+",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(14, 50)),
            (DayOfWeek.friday, _t(14, 50)),
        ],
        "student": None,
    },
    {
        "name": "GateWay B1 (1)",
        "course": "GateWay B1",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.monday, _t(16, 5)),
            (DayOfWeek.friday, _t(16, 5)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (5)",
        "course": "Academy Stars 3",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(17, 40)),
            (DayOfWeek.friday, _t(17, 40)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (6)",
        "course": "Academy Stars 3",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(15, 45)),
            (DayOfWeek.thursday, _t(15, 45)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (4)",
        "course": "GateWay A1+",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(16, 45)),
            (DayOfWeek.thursday, _t(16, 45)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (4)",
        "course": "GateWay A2",
        "teacher": "Виктория Сергеевна Позднякова",
        "branch": "Школа №188",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(18, 0)),
            (DayOfWeek.thursday, _t(18, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Фомина С.О. — Школа №217 (individual)
    # =========================================================
    {
        "name": "Кружкова Ульяна (инд.)",
        "course": "Индивидуальные занятия (45 мин)",
        "teacher": "Снежанна Олеговна Фомина",
        "branch": "Школа №217",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.monday, _t(9, 0)),
            (DayOfWeek.friday, _t(9, 0)),
        ],
        "student": "Кружкова Ульяна",
    },
    # =========================================================
    # Колесник Л.Н. — Школа №218
    # Note: group name is taken from the real schedule as-is;
    # the course used is the closest matching mini-group format.
    # =========================================================
    {
        "name": "Academy Stars 1 мини (1)",
        "course": "Мини-группа Academy Stars 3 (45 мин)",
        "teacher": "Любовь Николаевна Колесник",
        "branch": "Школа №218",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.monday, _t(9, 30)),
        ],
        "student": None,
    },
    # =========================================================
    # Данилова М.А. — Школа №221 (individual)
    # =========================================================
    {
        "name": "Мухарев Максим (инд.)",
        "course": "Индивидуальные занятия (45 мин)",
        "teacher": "Мария Анатольевна Данилова",
        "branch": "Школа №221",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
        ],
        "student": "Мухарев Максим",
    },
    # =========================================================
    # Зудяева Н.А. — Школа №56 (individual)
    # =========================================================
    {
        "name": "Мусорбаев Артем (инд.)",
        "course": "Индивидуальные занятия (30 мин)",
        "teacher": "Надежда Андреевна Зудяева",
        "branch": "Школа №56",
        "duration_min": 30,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": "Мусорбаев Артем",
    },
    # =========================================================
    # Куцых М.Е. — Школа №199
    # =========================================================
    {
        "name": "Academy Stars 3 мини (1)",
        "course": "Мини-группа Academy Stars 3 (45 мин)",
        "teacher": "Марина Евгеньевна Куцых",
        "branch": "Школа №199",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.monday, _t(10, 15)),
        ],
        "student": None,
    },
    # =========================================================
    # Винокурова Е.А. — Школа №195 (individual)
    # =========================================================
    {
        "name": "Димитров Антон (инд.)",
        "course": "Индивидуальные занятия (45 мин)",
        "teacher": "Елена Александровна Винокурова",
        "branch": "Школа №195",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.monday, _t(10, 45)),
        ],
        "student": "Димитров Антон",
    },
    # =========================================================
    # Караваева А.Д. — Офис
    # =========================================================
    {
        "name": "GateWay B1+ мини (1)",
        "course": "Мини-группа GateWay B1+ (45 мин)",
        "teacher": "Алина Денисовна Караваева",
        "branch": "Офис",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 30)),
            (DayOfWeek.thursday, _t(10, 30)),
        ],
        "student": None,
    },
    # =========================================================
    # Походная А.И. — НЭЛ (individual)
    # =========================================================
    {
        "name": "Масенкова Аэлита (инд.)",
        "course": "Индивидуальные занятия (90 мин)",
        "teacher": "Алена Игоревна Походная",
        "branch": "НЭЛ",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.wednesday, _t(13, 45)),
        ],
        "student": "Масенкова Аэлита",
    },
    # =========================================================
    # Евдокимова П.Е. — Офис
    # =========================================================
    {
        "name": "AS3 мини (Офис)",
        "course": "Мини-группа Academy Stars 3 (45 мин)",
        "teacher": "Полина Евгеньевна Евдокимова",
        "branch": "Офис",
        "duration_min": 45,
        "schedule": [
            (DayOfWeek.friday, _t(11, 15)),
        ],
        "student": None,
    },
    # =========================================================
    # Митина О.С. — Офис
    # =========================================================
    {
        "name": "GateWay A1+ (5)",
        "course": "GateWay A1+",
        "teacher": "Ольга Сергеевна Митина",
        "branch": "Офис",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (4)",
        "course": "Academy Stars 2",
        "teacher": "Ольга Сергеевна Митина",
        "branch": "Офис",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (5)",
        "course": "GateWay A2",
        "teacher": "Ольга Сергеевна Митина",
        "branch": "Офис",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Лукьянова С.Я. — Школа №121, Гимназия №5
    # =========================================================
    {
        "name": "Academy Stars 1 (4)",
        "course": "Academy Stars 1",
        "teacher": "Светлана Ярославовна Лукьянова",
        "branch": "Школа №121",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(10, 30)),
            (DayOfWeek.wednesday, _t(10, 30)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (7)",
        "course": "Academy Stars 3",
        "teacher": "Светлана Ярославовна Лукьянова",
        "branch": "Школа №121",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (6)",
        "course": "GateWay A2",
        "teacher": "Светлана Ярославовна Лукьянова",
        "branch": "Гимназия №5",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(11, 0)),
            (DayOfWeek.thursday, _t(11, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay B1 (2)",
        "course": "GateWay B1",
        "teacher": "Светлана Ярославовна Лукьянова",
        "branch": "Гимназия №5",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.tuesday, _t(14, 0)),
            (DayOfWeek.thursday, _t(14, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Пасикан А.С. — Гимназия №11, Офис
    # =========================================================
    {
        "name": "Fly High 1 (4)",
        "course": "Fly High 1",
        "teacher": "Ангелина Сергеевна Пасикан",
        "branch": "Гимназия №11",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (6)",
        "course": "GateWay A1+",
        "teacher": "Ангелина Сергеевна Пасикан",
        "branch": "Гимназия №11",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (8)",
        "course": "Academy Stars 3",
        "teacher": "Ангелина Сергеевна Пасикан",
        "branch": "Офис",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Козлова Е.Г. — Гимназия №9
    # =========================================================
    {
        "name": "GateWay B1+ (2)",
        "course": "GateWay B1+",
        "teacher": "Елена Геннадьевна Козлова",
        "branch": "Гимназия №9",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (5)",
        "course": "Academy Stars 2",
        "teacher": "Елена Геннадьевна Козлова",
        "branch": "Гимназия №9",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (5)",
        "course": "Academy Stars 1",
        "teacher": "Елена Геннадьевна Козлова",
        "branch": "Гимназия №9",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Осинина С.Н. — Гимназия №11
    # =========================================================
    {
        "name": "GateWay A2 (7)",
        "course": "GateWay A2",
        "teacher": "Светлана Николаевна Осинина",
        "branch": "Гимназия №11",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (9)",
        "course": "Academy Stars 3",
        "teacher": "Светлана Николаевна Осинина",
        "branch": "Гимназия №11",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (7)",
        "course": "GateWay A1+",
        "teacher": "Светлана Николаевна Осинина",
        "branch": "Гимназия №11",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(11, 0)),
            (DayOfWeek.thursday, _t(11, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Турабова Д.Д. — Школа №2, Школа №222
    # =========================================================
    {
        "name": "Academy Stars 1 (6)",
        "course": "Academy Stars 1",
        "teacher": "Диана Джейхуновна Турабова",
        "branch": "Школа №2",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (6)",
        "course": "Academy Stars 2",
        "teacher": "Диана Джейхуновна Турабова",
        "branch": "Школа №2",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (8)",
        "course": "GateWay A2",
        "teacher": "Диана Джейхуновна Турабова",
        "branch": "Школа №222",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Белова А.А. — Гимназия №7, ЛИТ
    # =========================================================
    {
        "name": "Fly High 1 (5)",
        "course": "Fly High 1",
        "teacher": "Александра Анатольевна Белова",
        "branch": "Гимназия №7",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (10)",
        "course": "Academy Stars 3",
        "teacher": "Александра Анатольевна Белова",
        "branch": "ЛИТ",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay B1 (3)",
        "course": "GateWay B1",
        "teacher": "Александра Анатольевна Белова",
        "branch": "ЛИТ",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Родина Т.П. — Гимназия №9
    # (time slots chosen to avoid overlap with Козлова Е.Г.)
    # =========================================================
    {
        "name": "GateWay A1+ (8)",
        "course": "GateWay A1+",
        "teacher": "Татьяна Петровна Родина",
        "branch": "Гимназия №9",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(12, 0)),
            (DayOfWeek.wednesday, _t(12, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (7)",
        "course": "Academy Stars 2",
        "teacher": "Татьяна Петровна Родина",
        "branch": "Гимназия №9",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(15, 0)),
            (DayOfWeek.wednesday, _t(15, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (11)",
        "course": "Academy Stars 3",
        "teacher": "Татьяна Петровна Родина",
        "branch": "Гимназия №9",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(14, 0)),
            (DayOfWeek.thursday, _t(14, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Переведенцева А.А. — Школа №155
    # =========================================================
    {
        "name": "Academy Stars 1 (7)",
        "course": "Academy Stars 1",
        "teacher": "Александра Переведенцева",
        "branch": "Школа №155",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (9)",
        "course": "GateWay A2",
        "teacher": "Александра Переведенцева",
        "branch": "Школа №155",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (12)",
        "course": "Academy Stars 3",
        "teacher": "Александра Переведенцева",
        "branch": "Школа №155",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Тихвинская В.О. — НЭЛ
    # =========================================================
    {
        "name": "GateWay B1+ (3)",
        "course": "GateWay B1+",
        "teacher": "Виктория Олеговна Тихвинская",
        "branch": "НЭЛ",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (10)",
        "course": "GateWay A2",
        "teacher": "Виктория Олеговна Тихвинская",
        "branch": "НЭЛ",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (8)",
        "course": "Academy Stars 2",
        "teacher": "Виктория Олеговна Тихвинская",
        "branch": "НЭЛ",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.tuesday, _t(11, 0)),
            (DayOfWeek.thursday, _t(11, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Рубе Д.В. — Школа №186, Офис
    # =========================================================
    {
        "name": "Fly High 1 (6)",
        "course": "Fly High 1",
        "teacher": "Дарья Васильевна Рубе",
        "branch": "Школа №186",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(11, 0)),
            (DayOfWeek.wednesday, _t(11, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (13)",
        "course": "Academy Stars 3",
        "teacher": "Дарья Васильевна Рубе",
        "branch": "Офис",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A1+ (9)",
        "course": "GateWay A1+",
        "teacher": "Дарья Васильевна Рубе",
        "branch": "Школа №186",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Арнгольд В.Е. — Школа №216
    # =========================================================
    {
        "name": "GateWay A2 (11)",
        "course": "GateWay A2",
        "teacher": "Валерия Евгеньевна Арнгольд",
        "branch": "Школа №216",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.friday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (8)",
        "course": "Academy Stars 1",
        "teacher": "Валерия Евгеньевна Арнгольд",
        "branch": "Школа №216",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.friday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay B1 (4)",
        "course": "GateWay B1",
        "teacher": "Валерия Евгеньевна Арнгольд",
        "branch": "Школа №216",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Калужина Д.Д. — Школа №13
    # =========================================================
    {
        "name": "GateWay A1+ (10)",
        "course": "GateWay A1+",
        "teacher": "Дарья Дмитриевна Калужина",
        "branch": "Школа №13",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (9)",
        "course": "Academy Stars 2",
        "teacher": "Дарья Дмитриевна Калужина",
        "branch": "Школа №13",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "Fly High 1 (7)",
        "course": "Fly High 1",
        "teacher": "Дарья Дмитриевна Калужина",
        "branch": "Школа №13",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Алексеева М.В. — Школа №2
    # =========================================================
    {
        "name": "Academy Stars 3 (14)",
        "course": "Academy Stars 3",
        "teacher": "Марина Владимировна Алексеева",
        "branch": "Школа №2",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (12)",
        "course": "GateWay A2",
        "teacher": "Марина Владимировна Алексеева",
        "branch": "Школа №2",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 1 (9)",
        "course": "Academy Stars 1",
        "teacher": "Марина Владимировна Алексеева",
        "branch": "Школа №2",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Быковская М.Э. — Школа №13
    # (offset times to avoid classroom slot duplicates with Калужина)
    # =========================================================
    {
        "name": "GateWay B1+ (4)",
        "course": "GateWay B1+",
        "teacher": "Марина Эдуардовна Быковская",
        "branch": "Школа №13",
        "duration_min": 90,
        "schedule": [
            (DayOfWeek.monday, _t(9, 0)),
            (DayOfWeek.wednesday, _t(9, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 2 (10)",
        "course": "Academy Stars 2",
        "teacher": "Марина Эдуардовна Быковская",
        "branch": "Школа №13",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(13, 0)),
            (DayOfWeek.wednesday, _t(13, 0)),
        ],
        "student": None,
    },
    {
        "name": "Fly High 1 (8)",
        "course": "Fly High 1",
        "teacher": "Марина Эдуардовна Быковская",
        "branch": "Школа №13",
        "duration_min": 50,
        "schedule": [
            (DayOfWeek.tuesday, _t(9, 0)),
            (DayOfWeek.thursday, _t(9, 0)),
        ],
        "student": None,
    },
    # =========================================================
    # Воронцова А.В. — Школа №167
    # =========================================================
    {
        "name": "GateWay A1+ (11)",
        "course": "GateWay A1+",
        "teacher": "Анна Вадимовна Воронцова",
        "branch": "Школа №167",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.monday, _t(10, 0)),
            (DayOfWeek.wednesday, _t(10, 0)),
        ],
        "student": None,
    },
    {
        "name": "Academy Stars 3 (15)",
        "course": "Academy Stars 3",
        "teacher": "Анна Вадимовна Воронцова",
        "branch": "Школа №167",
        "duration_min": 60,
        "schedule": [
            (DayOfWeek.monday, _t(14, 0)),
            (DayOfWeek.wednesday, _t(14, 0)),
        ],
        "student": None,
    },
    {
        "name": "GateWay A2 (13)",
        "course": "GateWay A2",
        "teacher": "Анна Вадимовна Воронцова",
        "branch": "Школа №167",
        "duration_min": 75,
        "schedule": [
            (DayOfWeek.tuesday, _t(10, 0)),
            (DayOfWeek.thursday, _t(10, 0)),
        ],
        "student": None,
    },
]


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

async def seed_real_schedule() -> None:
    await init_db()

    counts = {
        "teachers": 0,
        "branches": 0,
        "courses": 0,
        "groups": 0,
        "lessons": 0,
        "students": 0,
        "student_groups": 0,
    }

    async with AsyncSessionLocal() as session:
        # ------------------------------------------------------------------
        # 1. Teachers
        # ------------------------------------------------------------------
        teacher_map: dict[str, Teacher] = {}
        for idx, full_name in enumerate(TEACHER_NAMES, start=1):
            # Generate a stable email from teacher index to satisfy NOT NULL
            email = f"real_teacher_{idx:02d}@abc-school.ru"
            teacher, created = await _get_or_create(
                session,
                Teacher,
                {"full_name": full_name},
                {
                    "email": email,
                    "subject": "Английский",
                    "is_active": True,
                },
            )
            # If the teacher already exists but was created without this email,
            # keep it as-is (idempotent by full_name).
            teacher_map[full_name] = teacher
            if created:
                counts["teachers"] += 1

        # ------------------------------------------------------------------
        # 2. Branches
        # ------------------------------------------------------------------
        branch_map: dict[str, Branch] = {}
        for idx, name in enumerate(BRANCH_NAMES, start=1):
            branch, created = await _get_or_create(
                session,
                Branch,
                {"name": name},
                {
                    "address": f"г. Новосибирск, филиал «{name}»",
                    "is_active": True,
                },
            )
            branch_map[name] = branch
            if created:
                counts["branches"] += 1

        # ------------------------------------------------------------------
        # 3. Courses
        # ------------------------------------------------------------------
        course_map: dict[str, Course] = {}
        for cdef in COURSES_DEF:
            course, created = await _get_or_create(
                session,
                Course,
                {"name": cdef["name"]},
                {
                    "language": "Английский",
                    "level": cdef["level"],
                    "category": cdef["category"],
                    "price_per_month": cdef["price_per_month"],
                    "duration_months": cdef["duration_months"],
                    "lessons_per_week": cdef["lessons_per_week"],
                    "is_active": True,
                },
            )
            course_map[cdef["name"]] = course
            if created:
                counts["courses"] += 1

        # ------------------------------------------------------------------
        # 4. Default classroom (required FK on Lesson)
        # ------------------------------------------------------------------
        default_classroom, _ = await _get_or_create(
            session,
            Classroom,
            {"name": "Класс (по умолчанию)"},
            {
                "capacity": 15,
                "has_whiteboard": True,
                "is_active": True,
            },
        )

        # ------------------------------------------------------------------
        # 5. Students
        # ------------------------------------------------------------------
        student_map: dict[str, Student] = {}
        for sdef in STUDENTS_DEF:
            student, created = await _get_or_create(
                session,
                Student,
                {"full_name": sdef["full_name"]},
                {
                    "student_type": sdef["student_type"],
                    "status": StudentStatus.active,
                    "is_active": True,
                },
            )
            student_map[sdef["full_name"]] = student
            if created:
                counts["students"] += 1

        # ------------------------------------------------------------------
        # 6. Groups, Lessons, and StudentGroup links
        # ------------------------------------------------------------------
        for gdef in GROUPS_DEF:
            teacher = teacher_map[gdef["teacher"]]
            branch = branch_map[gdef["branch"]]
            course = course_map[gdef["course"]]

            group, g_created = await _get_or_create(
                session,
                Group,
                {"name": gdef["name"]},
                {
                    "course_id": course.id,
                    "teacher_id": teacher.id,
                    "status": GroupStatus.active,
                    "start_date": datetime(2024, 9, 1),
                    "end_date": datetime(2025, 6, 30),
                },
            )
            if g_created:
                counts["groups"] += 1

            for day, time_start in gdef["schedule"]:
                time_end = _end(time_start, gdef["duration_min"])
                _, l_created = await _get_or_create(
                    session,
                    Lesson,
                    {
                        "group_id": group.id,
                        "day_of_week": day,
                        "time_start": time_start,
                    },
                    {
                        "teacher_id": teacher.id,
                        "classroom_id": default_classroom.id,
                        "branch_id": branch.id,
                        "time_end": time_end,
                        "is_recurring": True,
                        "status": LessonStatus.scheduled,
                    },
                )
                if l_created:
                    counts["lessons"] += 1

            # StudentGroup link for individual-lesson groups
            if gdef["student"]:
                student = student_map[gdef["student"]]
                _, sg_created = await _get_or_create(
                    session,
                    StudentGroup,
                    {
                        "group_id": group.id,
                        "student_name": student.full_name,
                    },
                    {
                        "student_type": student.student_type.value,
                        "is_active": True,
                    },
                )
                if sg_created:
                    counts["student_groups"] += 1

        await session.commit()

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("✅ Реальное расписание загружено в БД")
    print(f"   Преподаватели (новые):    {counts['teachers']}")
    print(f"   Филиалы (новые):          {counts['branches']}")
    print(f"   Курсы (новые):            {counts['courses']}")
    print(f"   Группы (новые):           {counts['groups']}")
    print(f"   Занятия (новые):          {counts['lessons']}")
    print(f"   Студенты (новые):         {counts['students']}")
    print(f"   Связи студент-группа:     {counts['student_groups']}")


if __name__ == "__main__":
    asyncio.run(seed_real_schedule())
