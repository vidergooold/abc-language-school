import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.schedule import Classroom

BRANCHES = [
    {
        "name": "МАОУ Гимназия №11 «Гармония»",
        "address": "ул. Федосеева, 38",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт 9:50–18:30",
    },
    {
        "name": "МАОУ Гимназия №7 «Сибирская»",
        "address": "ул. Зорге, 42А",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Ср 9:30–15:30",
    },
    {
        "name": "МАОУ ЛИТ",
        "address": "ул. Римского-Корсакова, 13",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Вт/Чт 11:30–17:00",
    },
    {
        "name": "МАОУ НГПЛ",
        "address": "ул. Декабристов, 86",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 13:15–16:30",
    },
    {
        "name": "МАОУ НЭЛ",
        "address": "ул. Крылова, 44",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 12:00–14:00",
    },
    {
        "name": "МАОУ СОШ №216",
        "address": "ул. Виталия Потылицына, 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 9:30–19:30",
    },
    {
        "name": "МАОУ СОШ №217",
        "address": "ул. Виктора Шевелёва, 3",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт 9:00–19:00",
    },
    {
        "name": "МАОУ СОШ №218",
        "address": "Красный проспект, 320/1",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 10:30–16:00",
    },
    {
        "name": "МАОУ СОШ №222",
        "address": "ул. Кубовая, 100",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт 9:00–19:00",
    },
    {
        "name": "МБОУ Гимназия №5",
        "address": "Академическая ул., 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Ср 11:00–13:00",
    },
    {
        "name": "МБОУ Гимназия №9",
        "address": "ул. Калинина, 255",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 11:00–19:15",
    },
    {
        "name": "МБОУ СОШ №11",
        "address": "ул. Бориса Богаткова, 187",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Ср 11:00–12:30",
    },
    {
        "name": "МБОУ СОШ №121 «Академическая»",
        "address": "ул. Тружеников, 10",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Вт/Чт 12:00–15:00",
    },
    {
        "name": "МБОУ СОШ №155",
        "address": "ул. Ключ-Камышенское Плато, 1А",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Вт/Чт/Пт 10:00–20:00",
    },
    {
        "name": "МБОУ СОШ №186",
        "address": "ул. Бориса Богаткова, 189",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт 10:30–18:30",
    },
    {
        "name": "МБОУ СОШ №188",
        "address": "Курганская ул., 36А",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Пт 11:00–19:30",
    },
    {
        "name": "МБОУ СОШ №195",
        "address": "ул. В. Высоцкого, 1",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Чт 12:10–14:00",
    },
    {
        "name": "МБОУ СОШ №199",
        "address": "Лазурная ул., 27",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн-Чт 9:00–18:30",
    },
    {
        "name": "МБОУ СОШ №2",
        "address": "ул. Чехова, 271",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Вт/Чт/Пт 11:00–18:30",
    },
    {
        "name": "МБОУ СОШ №56",
        "address": "Планировочная ул., 7",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пн/Чт 11:30–15:30",
    },
    {
        "name": "МБОУ СОШ №61 им. Н.М.Иванова",
        "address": "ул. Иванова, 9",
        "phone": "+79139121809",
        "email": "info@abc-school.ru",
        "manager_name": "Андрюнина Марина Викторовна",
        "manager_position": "Директор",
        "working_hours": "Пт 14:00–16:00",
    },
]

# Classrooms linked to each branch (by branch name)
BRANCH_CLASSROOMS = {
    "МАОУ Гимназия №11 «Гармония»": ["каб. 113", "каб. 114"],
    "МАОУ Гимназия №7 «Сибирская»": ["каб. 119"],
    "МАОУ ЛИТ": ["каб. библ.", "каб. 116"],
    "МАОУ НГПЛ": ["каб. 205"],
    "МАОУ НЭЛ": ["каб. 312"],
    "МАОУ СОШ №216": ["каб. 317", "каб. 410"],
    "МАОУ СОШ №217": ["каб. 314А"],
    "МАОУ СОШ №218": ["каб. АВС"],
    "МАОУ СОШ №222": ["каб. 128", "каб. 311"],
    "МБОУ Гимназия №5": ["каб. 191"],
    "МБОУ Гимназия №9": ["каб. 37", "каб. 41"],
    "МБОУ СОШ №11": ["каб. 203"],
    "МБОУ СОШ №121 «Академическая»": ["каб. 214"],
    "МБОУ СОШ №155": ["каб. 426"],
    "МБОУ СОШ №186": ["каб. 211"],
    "МБОУ СОШ №188": ["каб. 409", "каб. АВС"],
    "МБОУ СОШ №195": ["каб. 415"],
    "МБОУ СОШ №199": ["каб. 218"],
    "МБОУ СОШ №2": ["каб. 307"],
    "МБОУ СОШ №56": ["каб. 3", "каб. 10"],
    "МБОУ СОШ №61 им. Н.М.Иванова": ["каб. 224"],
}


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
                branch.is_administrative = False
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
                    is_administrative=False,
                )
                session.add(branch)

            await session.flush()

            for classroom_name in BRANCH_CLASSROOMS.get(row["name"], []):
                existing_room = await session.execute(
                    select(Classroom).where(
                        Classroom.name == classroom_name,
                        Classroom.branch_id == branch.id,
                    )
                )
                if existing_room.scalar_one_or_none() is None:
                    session.add(
                        Classroom(
                            name=classroom_name,
                            branch_id=branch.id,
                            capacity=12,
                            is_active=True,
                        )
                    )

        await session.commit()
        print(f"Seeded {len(BRANCHES)} branches with classrooms")


if __name__ == "__main__":
    asyncio.run(seed_branches_22())
