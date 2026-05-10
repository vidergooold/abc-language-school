import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch

BRANCHES = [
    {
        "name": "Офис",
        "address": "г. Новосибирск, ул. Бориса Богаткова, 208/2, офис 4, 5",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.00 до 20.00 без обеда",
        "is_administrative": True,
    },
    {
        "name": "Филиал в МАОУ Гимназия 11 «Гармония»",
        "address": "г. Новосибирск, ул. Федосеева, д. 38",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №56",
        "address": "г. Новосибирск, ул. Планировочная, д. 7",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Чт с 11.30 до 15.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №188",
        "address": "г. Новосибирск, ул. Курганская, д. 36а",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ СОШ №218",
        "address": "г. Новосибирск, Красный проспект, д. 320/1",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ «Гимназия №7 «Сибирская»",
        "address": "г. Новосибирск, ул. Зорге, д. 42а",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №186",
        "address": "г. Новосибирск, ул. Бориса Богаткова, д. 189",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №11",
        "address": "г. Новосибирск, ул. Бориса Богаткова, д. 187",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №2",
        "address": "г. Новосибирск, ул. Чехова, д. 271",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №199",
        "address": "г. Новосибирск, ул. Лазурная, д. 27",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ №155",
        "address": "г. Новосибирск, Ключ-Камышенское Плато, д. 1А",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ ЛИТ",
        "address": "г. Новосибирск, ул. Римского-Корсакова, д. 13",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ НГПЛ",
        "address": "г. Новосибирск, ул. Декабристов, д. 86",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ Гимназия №9",
        "address": "г. Новосибирск, ул. Калинина, д. 255",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ НЭЛ",
        "address": "г. Новосибирск, ул. Крылова, д. 44",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ СОШ №216",
        "address": "г. Новосибирск, ул. Виталия Потылицына, д. 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ СОШ №217",
        "address": "г. Новосибирск, ул. Виктора Шевелева, д. 3",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ гимназия №5",
        "address": "г. Новосибирск, ул. Академическая, д. 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ № 121 «Академическая»",
        "address": "г. Новосибирск, ул. Тружеников, д. 10",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МБОУ СОШ № 61 им. Н.М.Иванова",
        "address": "г. Новосибирск, ул. Иванова, д. 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
    },
    {
        "name": "Филиал в МАОУ «СОШ №222»",
        "address": "г. Новосибирск, ул. Кубовая, д. 100",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт с 9.50 до 18.30 без обеда",
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
                branch.is_administrative = row.get("is_administrative", False)
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
                    is_administrative=row.get("is_administrative", False),
                )
                session.add(branch)

        await session.commit()
        print(f"Seeded branches: {len(BRANCHES)}")


if __name__ == "__main__":
    asyncio.run(seed_branches_22())
