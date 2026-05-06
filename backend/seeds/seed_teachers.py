"""
Seed преподавателей для ABC Language School
"""
import asyncio
from app.core.database import AsyncSessionLocal, init_db
from app.models.teacher import Teacher

TEACHERS_DATA = [
    {
        "full_name": "Иванова Анна Сергеевна",
        "email": "anna.ivanova@abc-school.ru",
        "phone": "+79131234567",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 5,
        "bio": "Опытный преподаватель английского языка с 5-летним стажем.",
        "is_active": True,
    },
    {
        "full_name": "Петров Михаил Андреевич",
        "email": "mikhail.petrov@abc-school.ru",
        "phone": "+79139876543",
        "subject": "Немецкий",
        "language_level": "C1",
        "experience_years": 3,
        "bio": "Специалист по немецкому языку, носитель языка.",
        "is_active": True,
    },
    {
        "full_name": "Сидорова Елена Викторовна",
        "email": "elena.sidorova@abc-school.ru",
        "phone": "+79135678901",
        "subject": "Французский",
        "language_level": "C2",
        "experience_years": 7,
        "bio": "Преподаватель французского языка с международным опытом.",
        "is_active": True,
    },
    {
        "full_name": "Кузнецов Дмитрий Олегович",
        "email": "dmitry.kuznetsov@abc-school.ru",
        "phone": "+79134567890",
        "subject": "Испанский",
        "language_level": "C1",
        "experience_years": 4,
        "bio": "Преподаватель испанского языка, выпускник МГУ.",
        "is_active": True,
    },
    {
        "full_name": "Морозова Ольга Ивановна",
        "email": "olga.morozova@abc-school.ru",
        "phone": "+79132345678",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 10,
        "bio": "Ведущий преподаватель английского, методист.",
        "is_active": True,
    },
    {
        "full_name": "Белова Александра Анатольевна",
        "email": "alexandra.belova@abc-school.ru",
        "phone": "+79130001001",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 12,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Григорьева Дарья Дмитриевна",
        "email": "daria.grigorieva@abc-school.ru",
        "phone": "+79130001002",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 8,
        "bio": "Преподаватель английского языка и методист.",
        "is_active": True,
    },
    {
        "full_name": "Данилова Мария Анатольевна",
        "email": "maria.danilova@abc-school.ru",
        "phone": "+79130001003",
        "subject": "Английский",
        "language_level": "B2",
        "experience_years": 10,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Евдокимова Полина Евгеньевна",
        "email": "polina.evdokimova@abc-school.ru",
        "phone": "+79130001004",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 14,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Колесник Любовь Николаевна",
        "email": "lyubov.kolesnik@abc-school.ru",
        "phone": "+79130001005",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 11,
        "bio": "Старший преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Куцых Марина Евгеньевна",
        "email": "marina.kutsykh@abc-school.ru",
        "phone": "+79130001006",
        "subject": "Английский",
        "language_level": "B2",
        "experience_years": 9,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Кривилева Галина Александровна",
        "email": "galina.krivileva@abc-school.ru",
        "phone": "+79130001007",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 13,
        "bio": "Преподаватель и методист.",
        "is_active": True,
    },
    {
        "full_name": "Лукьянова Светлана Ярославовна",
        "email": "svetlana.lukyanova@abc-school.ru",
        "phone": "+79130001008",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 15,
        "bio": "Старший преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Митина Ольга Сергеевна",
        "email": "olga.mitina@abc-school.ru",
        "phone": "+79130001009",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 10,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Осинина Светлана Николаевна",
        "email": "svetlana.osinina@abc-school.ru",
        "phone": "+79130001010",
        "subject": "Английский",
        "language_level": "B2",
        "experience_years": 7,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Пасикан Ангелина Сергеевна",
        "email": "angelina.pasikan@abc-school.ru",
        "phone": "+79130001011",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 13,
        "bio": "Преподаватель английского языка, методист.",
        "is_active": True,
    },
    {
        "full_name": "Переведенцева Александра Андреевна",
        "email": "alexandra.perevedentseva@abc-school.ru",
        "phone": "+79130001012",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 16,
        "bio": "Старший преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Позднякова Виктория Сергеевна",
        "email": "victoria.pozdnyakova@abc-school.ru",
        "phone": "+79130001013",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 10,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Рубе Дарья Васильевна",
        "email": "daria.rube@abc-school.ru",
        "phone": "+79130001014",
        "subject": "Английский",
        "language_level": "B2",
        "experience_years": 8,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Стафеева Яна Викторовна",
        "email": "yana.stafeeva@abc-school.ru",
        "phone": "+79130001015",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 12,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Темлякова Анна Михайловна",
        "email": "anna.temlyakova@abc-school.ru",
        "phone": "+79130001016",
        "subject": "Английский",
        "language_level": "C2",
        "experience_years": 18,
        "bio": "Старший преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Федорова Анфиса Вячеславовна",
        "email": "anfisa.fedorova@abc-school.ru",
        "phone": "+79130001017",
        "subject": "Английский",
        "language_level": "C1",
        "experience_years": 9,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
    {
        "full_name": "Фомина Снежанна Олеговна",
        "email": "snezhanna.fomina@abc-school.ru",
        "phone": "+79130001018",
        "subject": "Английский",
        "language_level": "B2",
        "experience_years": 10,
        "bio": "Преподаватель английского языка.",
        "is_active": True,
    },
]

async def seed_teachers():
    await init_db()
    async with AsyncSessionLocal() as db:
        for teacher_data in TEACHERS_DATA:
            # Проверяем, существует ли уже
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