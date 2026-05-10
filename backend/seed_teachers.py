"""
Seed преподавателей для ABC Language School
"""
import asyncio
from app.core.database import AsyncSessionLocal, init_db
from app.models.teacher import Teacher

TEACHERS_DATA = [
    {"full_name": "Арнгольд Валерия Евгеньевна", "email": "teacher01@abc-school.ru", "phone": "+79130001001", "subject": "Английский", "language_level": "C1", "experience_years": 10, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Белова Александра Анатольевна", "email": "teacher02@abc-school.ru", "phone": "+79130001002", "subject": "Английский", "language_level": "C1", "experience_years": 12, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Быковская Марина Эдуардовна", "email": "teacher03@abc-school.ru", "phone": "+79130001003", "subject": "Английский", "language_level": "C1", "experience_years": 9, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Винокурова Елена Александровна", "email": "teacher04@abc-school.ru", "phone": "+79130001004", "subject": "Английский", "language_level": "B2", "experience_years": 8, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Воронцова Анна Вадимовна", "email": "teacher05@abc-school.ru", "phone": "+79130001005", "subject": "Английский", "language_level": "C1", "experience_years": 7, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Данилова Мария Анатольевна", "email": "teacher06@abc-school.ru", "phone": "+79130001006", "subject": "Английский", "language_level": "B2", "experience_years": 10, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Евдокимова Полина Евгеньевна", "email": "teacher07@abc-school.ru", "phone": "+79130001007", "subject": "Английский", "language_level": "C2", "experience_years": 14, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Зудяева Надежда Андреевна", "email": "teacher08@abc-school.ru", "phone": "+79130001008", "subject": "Английский", "language_level": "C1", "experience_years": 11, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Иванова Мария Петровна", "email": "teacher09@abc-school.ru", "phone": "+79130001009", "subject": "Английский", "language_level": "C1", "experience_years": 9, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Караваева Алина Денисовна", "email": "teacher10@abc-school.ru", "phone": "+79130001010", "subject": "Английский", "language_level": "B2", "experience_years": 6, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Козлова Елена Геннадьевна", "email": "teacher11@abc-school.ru", "phone": "+79130001011", "subject": "Английский", "language_level": "C1", "experience_years": 12, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Колесник Любовь Николаевна", "email": "teacher12@abc-school.ru", "phone": "+79130001012", "subject": "Английский", "language_level": "C1", "experience_years": 11, "bio": "Старший преподаватель английского языка.", "is_active": True},
    {"full_name": "Куцых Марина Евгеньевна", "email": "teacher13@abc-school.ru", "phone": "+79130001013", "subject": "Английский", "language_level": "B2", "experience_years": 9, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Лукьянова Светлана Ярославовна", "email": "teacher14@abc-school.ru", "phone": "+79130001014", "subject": "Китайский", "language_level": "C2", "experience_years": 15, "bio": "Старший преподаватель китайского языка.", "is_active": True},
    {"full_name": "Митина Ольга Сергеевна", "email": "teacher15@abc-school.ru", "phone": "+79130001015", "subject": "Английский", "language_level": "C1", "experience_years": 10, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Осинина Светлана Николаевна", "email": "teacher16@abc-school.ru", "phone": "+79130001016", "subject": "Английский", "language_level": "B2", "experience_years": 7, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Пасикан Ангелина Сергеевна", "email": "teacher17@abc-school.ru", "phone": "+79130001017", "subject": "Английский", "language_level": "C1", "experience_years": 13, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Переведенцева Александра Андреевна", "email": "teacher18@abc-school.ru", "phone": "+79130001018", "subject": "Английский", "language_level": "C2", "experience_years": 16, "bio": "Старший преподаватель английского языка.", "is_active": True},
    {"full_name": "Позднякова Виктория Сергеевна", "email": "teacher19@abc-school.ru", "phone": "+79130001019", "subject": "Английский", "language_level": "C1", "experience_years": 10, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Походная Алёна Игоревна", "email": "teacher20@abc-school.ru", "phone": "+79130001020", "subject": "Английский", "language_level": "C1", "experience_years": 8, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Родина Татьяна Петровна", "email": "teacher21@abc-school.ru", "phone": "+79130001021", "subject": "Английский", "language_level": "B2", "experience_years": 9, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Рубе Дарья Васильевна", "email": "teacher22@abc-school.ru", "phone": "+79130001022", "subject": "Английский", "language_level": "B2", "experience_years": 8, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Темлякова Анна Михайловна", "email": "teacher23@abc-school.ru", "phone": "+79130001023", "subject": "Китайский", "language_level": "C2", "experience_years": 18, "bio": "Старший преподаватель китайского языка.", "is_active": True},
    {"full_name": "Тихвинская Виктория Олеговна", "email": "teacher24@abc-school.ru", "phone": "+79130001024", "subject": "Английский", "language_level": "C1", "experience_years": 8, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Турабова Диана Джейхуновна", "email": "teacher25@abc-school.ru", "phone": "+79130001025", "subject": "Английский", "language_level": "B2", "experience_years": 7, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Федорова Анфиса Вячеславовна", "email": "teacher26@abc-school.ru", "phone": "+79130001026", "subject": "Английский", "language_level": "C1", "experience_years": 9, "bio": "Преподаватель английского языка.", "is_active": True},
    {"full_name": "Фомина Снежанна Олеговна", "email": "teacher27@abc-school.ru", "phone": "+79130001027", "subject": "Китайский", "language_level": "B2", "experience_years": 10, "bio": "Преподаватель китайского языка.", "is_active": True},
]


async def seed_teachers():
    await init_db()
    async with AsyncSessionLocal() as db:
        for teacher_data in TEACHERS_DATA:
            existing = await db.execute(
                Teacher.__table__.select().where(Teacher.email == teacher_data["email"])
            )
            if existing.scalar_one_or_none():
                print(f"Преподаватель {teacher_data['full_name']} уже существует")
                continue

            teacher = Teacher(**teacher_data)
            db.add(teacher)
            print(f"Добавлен преподаватель: {teacher_data['full_name']}")

        await db.commit()
        print("✅ Seed преподавателей завершен")


if __name__ == "__main__":
    asyncio.run(seed_teachers())
