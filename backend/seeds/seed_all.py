"""Единый (канонический) seed-скрипт для демо-данных.

Заполняет базовые справочники и запускает demo/schedule seed-поток,
после чего гарантированно дополняет student_groups для всех групп.
"""

import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Course, CourseCategory, CourseLevel
from app.models.news import News
from seed_demo import seed as seed_demo
from seed_branches_22 import seed_branches_22
from seed_distribution import seed_distribution
from seed_real_schedule import seed_real_schedule
from seed_student_groups import seed_student_groups
from seed_requirements import seed_requirements

COURSES_DATA = [
    {
        "name": "Дошкольники",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.children,
        "price_per_month": 2700,
        "lessons_per_week": 2,
    },
    {
        "name": "FH1, AS1",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 3100,
        "lessons_per_week": 2,
    },
    {
        "name": "AS2, AS3, AS4",
        "language": "Английский",
        "level": CourseLevel.elementary,
        "category": CourseCategory.school,
        "price_per_month": 3500,
        "lessons_per_week": 2,
    },
    {
        "name": "GWA1+, GWA2",
        "language": "Английский",
        "level": CourseLevel.pre_intermediate,
        "category": CourseCategory.school,
        "price_per_month": 4250,
        "lessons_per_week": 2,
    },
    {
        "name": "GWB1, GWB1+, GWB2, GWB2+, GWC1",
        "language": "Английский",
        "level": CourseLevel.upper_intermediate,
        "category": CourseCategory.school,
        "price_per_month": 4900,
        "lessons_per_week": 2,
    },
    {
        "name": "Взрослые групповые",
        "language": "Английский",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.adults,
        "price_per_month": 6500,
        "lessons_per_week": 2,
    },
    {
        "name": "Мини-группа (2 чел.)",
        "language": "Английский",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.adults,
        "price_per_month": 6600,
        "lessons_per_week": 2,
    },
    {
        "name": "Индивидуальные занятия",
        "language": "Английский",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.adults,
        "price_per_month": 1100,
        "lessons_per_week": 2,
    },
    {
        "name": "Китайский язык",
        "language": "Китайский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 1200,
        "lessons_per_week": 2,
    },
]

NEWS_DATA = [
    {
        "title": "График работы офиса в Новогодние праздники",
        "tag": "Объявление",
        "date": "25.12.2023",
        "body": "Уважаемые родители и обучающиеся! Поздравляем Вас С Наступающим Новым 2024 годом! Желаем Вам успехов и всего самого наилучшего!",
    },
    {
        "title": "График работы Лингвоцентра в праздничные дни",
        "date": "30.12.2023",
        "tag": "Объявление",
        "body": "30.12.2023 – 07.01.2024 — занятия проводиться не будут, офис закрыт. Занятия продолжатся с 08.01.2024 (понедельник) по расписанию. Для приема оплат офис работает 25.12.2023 – 29.12.2023 с 09:00 до 20:00. С уважением, Администрация Лингвоцентра",
    },
    {
        "title": "Приятных летних каникул!!!",
        "tag": "Каникулы",
        "date": "01.06.2022",
        "body": "Дорогие наши учащиеся! Уважаемые родители! Мы с радостью поздравляем Вас всех с долгожданными летними каникулами! У вас столько впереди интересного! Пусть каникулы принесут вам наслаждение, пусть новые знакомства придадут надежных друзей. Отдыхайте и набирайтесь новых сил на новый учебный год.",
    },
    {
        "title": "До встречи в Новом 2022-2023 учебном году!",
        "date": "15.08.2022",
        "tag": "Объявление",
        "body": "Напоминаем Вам, что в период с 01.06.22 по 15.08.2022 года Лингвоцентр не работает. Вопросы по телефону: 214-18-09 (Марина Викторовна)",
    },
    {
        "title": "График работы офиса",
        "tag": "Объявление",
        "date": "03.11.2021",
        "body": "Уважаемые родители и обучающиеся! 04.11.2021 офис Лингвоцентра не работает.",
    },
    {
        "title": "Поздравляем с Днем народного единства!",
        "date": "04.11.2021",
        "tag": "Праздник",
        "body": "Желаем крепкого здоровья, счастья, благополучия, мира и процветания!",
    },
]


async def seed_courses(db: AsyncSession) -> None:
    existing_course = await db.scalar(select(Course.id).limit(1))
    if existing_course is not None:
        print("В базе уже есть курсы. Пропускаем заполнение курсов.")
        return

    for course_data in COURSES_DATA:
        db.add(Course(**course_data))

    await db.commit()
    print(f"✅ Загружено курсов: {len(COURSES_DATA)}")


async def seed_news(db: AsyncSession) -> None:
    existing_news = await db.scalar(select(News.id).limit(1))
    if existing_news is not None:
        print("В базе уже есть новости. Пропускаем заполнение новостей.")
        return

    for news_data in NEWS_DATA:
        db.add(News(**news_data))

    await db.commit()
    print(f"✅ Загружено новостей: {len(NEWS_DATA)}")


async def seed_all() -> None:
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_courses(db)
        await seed_news(db)
    # Seed all real branches with classrooms first
    await seed_branches_22()
    # Канонический поток демо-данных для матрицы посещаемости.
    await seed_demo()
    await seed_real_schedule()
    await seed_student_groups()
    await seed_distribution()
    # Финальный шаг: обеспечивает выполнение всех требований валидации
    await seed_requirements()


if __name__ == "__main__":
    asyncio.run(seed_all())
