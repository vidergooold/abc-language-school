"""Единый seed-скрипт для заполнения базовых данных."""

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

COURSES_DATA = [
    {
        "name": "Английский — базовый уровень",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.school,
        "price_per_month": 5400,
        "lessons_per_week": 2,
    },
    {
        "name": "Немецкий — средний",
        "language": "Немецкий",
        "level": CourseLevel.intermediate,
        "category": CourseCategory.school,
        "price_per_month": 5600,
        "lessons_per_week": 2,
    },
    {
        "name": "Французский — продвинутый",
        "language": "Французский",
        "level": CourseLevel.advanced,
        "category": CourseCategory.adults,
        "price_per_month": 6200,
        "lessons_per_week": 3,
    },
    {
        "name": "Испанский — A1",
        "language": "Испанский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.adults,
        "price_per_month": 5200,
        "lessons_per_week": 2,
    },
    {
        "name": "Подготовка к IELTS",
        "language": "Английский",
        "level": CourseLevel.upper_intermediate,
        "category": CourseCategory.exam_prep,
        "price_per_month": 7800,
        "lessons_per_week": 3,
    },
    {
        "name": "Дошкольный английский 4–6 лет",
        "language": "Английский",
        "level": CourseLevel.beginner,
        "category": CourseCategory.children,
        "price_per_month": 4800,
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


if __name__ == "__main__":
    asyncio.run(seed_all())
