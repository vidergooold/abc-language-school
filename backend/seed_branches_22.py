import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch

BRANCHES = [
    {
        "name": "Филиал №1 — Центральный",
        "address": "г. Новосибирск, ул. Ленина, 12",
        "phone": "+73832090001",
        "email": "branch1@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00, Сб 10:00-16:00",
    },
    {
        "name": "Филиал №2 — Октябрьский",
        "address": "г. Новосибирск, ул. Кирова, 44",
        "phone": "+73832090002",
        "email": "branch2@abc-school.ru",
        "manager_name": "Шевченко Елена Викторовна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-20:00",
    },
    {
        "name": "Филиал №3 — Академгородок",
        "address": "г. Новосибирск, пр. Лаврентьева, 6",
        "phone": "+73832090003",
        "email": "branch3@abc-school.ru",
        "manager_name": "Алексеева Марина Владимировна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 08:30-20:30",
    },
    {
        "name": "Филиал №4 — Ленинский",
        "address": "г. Новосибирск, ул. Станиславского, 21",
        "phone": "+73832090004",
        "email": "branch4@abc-school.ru",
        "manager_name": "Сушкова Ольга Игоревна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №5 — Заельцовский",
        "address": "г. Новосибирск, Красный проспект, 167",
        "phone": "+73832090005",
        "email": "branch5@abc-school.ru",
        "manager_name": "Кривилева Галина Александровна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Вс 10:00-20:00",
    },
    {
        "name": "Филиал №6 — Калининский",
        "address": "г. Новосибирск, ул. Богдана Хмельницкого, 38",
        "phone": "+73832090006",
        "email": "branch6@abc-school.ru",
        "manager_name": "Куцых Марина Евгеньевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-19:30",
    },
    {
        "name": "Филиал №7 — Дзержинский",
        "address": "г. Новосибирск, пр. Дзержинского, 57",
        "phone": "+73832090007",
        "email": "branch7@abc-school.ru",
        "manager_name": "Колесник Любовь Николаевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №8 — Первомайский",
        "address": "г. Новосибирск, ул. Героев Революции, 18",
        "phone": "+73832090008",
        "email": "branch8@abc-school.ru",
        "manager_name": "Митина Ольга Сергеевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 10:00-20:00",
    },
    {
        "name": "Филиал №9 — Кировский",
        "address": "г. Новосибирск, ул. Петухова, 74",
        "phone": "+73832090009",
        "email": "branch9@abc-school.ru",
        "manager_name": "Осинина Светлана Николаевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №10 — Советский",
        "address": "г. Новосибирск, Морской проспект, 14",
        "phone": "+73832090010",
        "email": "branch10@abc-school.ru",
        "manager_name": "Пасикан Ангелина Сергеевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00, Сб 10:00-16:00",
    },
    {
        "name": "Филиал №11 — Бердск",
        "address": "г. Бердск, ул. Ленина, 35",
        "phone": "+73832090011",
        "email": "branch11@abc-school.ru",
        "manager_name": "Позднякова Виктория Сергеевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-19:00",
    },
    {
        "name": "Филиал №12 — Обь",
        "address": "г. Обь, ул. ЖКО Аэропорта, 22",
        "phone": "+73832090012",
        "email": "branch12@abc-school.ru",
        "manager_name": "Рубе Дарья Васильевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №13 — Кольцово",
        "address": "р.п. Кольцово, пр. Академика Сандахчиева, 9",
        "phone": "+73832090013",
        "email": "branch13@abc-school.ru",
        "manager_name": "Стафеева Яна Викторовна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-20:00",
    },
    {
        "name": "Филиал №14 — Краснообск",
        "address": "р.п. Краснообск, 2-й микрорайон, 25",
        "phone": "+73832090014",
        "email": "branch14@abc-school.ru",
        "manager_name": "Темлякова Анна Михайловна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №15 — Пашино",
        "address": "г. Новосибирск, ул. Солидарности, 66",
        "phone": "+73832090015",
        "email": "branch15@abc-school.ru",
        "manager_name": "Федорова Анфиса Вячеславовна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 10:00-19:00",
    },
    {
        "name": "Филиал №16 — Родники",
        "address": "г. Новосибирск, ул. Краузе, 17",
        "phone": "+73832090016",
        "email": "branch16@abc-school.ru",
        "manager_name": "Фомина Снежанна Олеговна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00",
    },
    {
        "name": "Филиал №17 — Золотая Нива",
        "address": "г. Новосибирск, ул. Бориса Богаткова, 250",
        "phone": "+73832090017",
        "email": "branch17@abc-school.ru",
        "manager_name": "Белова Александра Анатольевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-20:00",
    },
    {
        "name": "Филиал №18 — Площадь Маркса",
        "address": "г. Новосибирск, ул. Ватутина, 28А",
        "phone": "+73832090018",
        "email": "branch18@abc-school.ru",
        "manager_name": "Григорьева Дарья Дмитриевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-21:00",
    },
    {
        "name": "Филиал №19 — Речной вокзал",
        "address": "г. Новосибирск, ул. Большевистская, 101",
        "phone": "+73832090019",
        "email": "branch19@abc-school.ru",
        "manager_name": "Данилова Мария Анатольевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 10:00-20:00",
    },
    {
        "name": "Филиал №20 — Студенческая",
        "address": "г. Новосибирск, пр. Карла Маркса, 30",
        "phone": "+73832090020",
        "email": "branch20@abc-school.ru",
        "manager_name": "Евдокимова Полина Евгеньевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:30",
    },
    {
        "name": "Филиал №21 — Сибирская",
        "address": "г. Новосибирск, ул. Гоголя, 37",
        "phone": "+73832090021",
        "email": "branch21@abc-school.ru",
        "manager_name": "Лукьянова Светлана Ярославовна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Сб 09:00-20:00",
    },
    {
        "name": "Филиал №22 — Площадь Ленина",
        "address": "г. Новосибирск, ул. Советская, 23",
        "phone": "+73832090022",
        "email": "branch22@abc-school.ru",
        "manager_name": "Переведенцева Александра Андреевна",
        "manager_position": "Руководитель филиала",
        "working_hours": "Пн-Пт 09:00-20:00, Сб 10:00-16:00",
    },
]


async def seed_branches_22() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        target_names = {row["name"] for row in BRANCHES}

        all_existing = await session.execute(select(Branch))
        for existing_branch in all_existing.scalars().all():
            if existing_branch.name not in target_names:
                existing_branch.is_active = False

        for row in BRANCHES:
            existing = await session.execute(select(Branch).where(Branch.name == row["name"]))
            branch = existing.scalar_one_or_none()
            if branch:
                branch.address = row["address"]
                branch.phone = row["phone"]
                branch.email = row["email"]
                branch.manager_name = row["manager_name"]
                branch.manager_position = row["manager_position"]
                branch.working_hours = row["working_hours"]
                branch.is_active = True
            else:
                branch = Branch(
                    name=row["name"],
                    address=row["address"],
                    phone=row["phone"],
                    email=row["email"],
                    manager_name=row["manager_name"],
                    manager_position=row["manager_position"],
                    working_hours=row["working_hours"],
                    is_active=True,
                )
                session.add(branch)

        await session.commit()
        print(f"Seeded branches: {len(BRANCHES)}")


if __name__ == "__main__":
    asyncio.run(seed_branches_22())
