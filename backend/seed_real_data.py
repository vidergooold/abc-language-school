"""Seed с реальными данными школы (ON0002-2025.xlsx)."""
import asyncio
from app.core.database import init_db, AsyncSessionLocal
from app.models.group import Course, Group, CourseLevel, CourseCategory
from app.models.teacher import Teacher
from app.models.schedule import Classroom, Lesson, DayOfWeek
from datetime import time

async def seed_real_data():
    await init_db()
    async with AsyncSessionLocal() as db:
        # Курсы на основе разделов 1.1—1.15 из Excel
        courses_data = [
            {"name": "Английский — базовый уровень", "language": "Английский", "level": CourseLevel.beginner, "category": CourseCategory.school, "price_per_month": 5400, "lessons_per_week": 2},
            {"name": "Немецкий — средний", "language": "Немецкий", "level": CourseLevel.intermediate, "category": CourseCategory.school, "price_per_month": 5600, "lessons_per_week": 2},
            {"name": "Французский — продвинутый", "language": "Французский", "level": CourseLevel.advanced, "category": CourseCategory.adults, "price_per_month": 6200, "lessons_per_week": 3},
            {"name": "Испанский — A1", "language": "Испанский", "level": CourseLevel.beginner, "category": CourseCategory.adults, "price_per_month": 5200, "lessons_per_week": 2},
            {"name": "Подготовка к IELTS", "language": "Английский", "level": CourseLevel.upper_intermediate, "category": CourseCategory.exam_prep, "price_per_month": 7800, "lessons_per_week": 3},
            {"name": "Дошкольный английский 4–6 лет", "language": "Английский", "level": CourseLevel.beginner, "category": CourseCategory.children, "price_per_month": 4800, "lessons_per_week": 2},
        ]
        for c in courses_data:
            course = Course(**c)
            db.add(course)
        await db.commit()
        print("✅ Загружено курсов:", len(courses_data))

if __name__ == "__main__":
    asyncio.run(seed_real_data())
