"""
Скрипт для создания админа в базе данных

Использование:
    cd backend
    python create_admin.py
Или с параметрами:
    ADMIN_EMAIL=my@mail.ru ADMIN_PASSWORD=mypass python create_admin.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@abc-school.ru")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"ℹ️  Админ {ADMIN_EMAIL} уже существует")
            return
        admin = User(
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            full_name="Администратор",
            role=UserRole.admin,
        )
        db.add(admin)
        await db.commit()
        print(f"✅ Админ создан: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
