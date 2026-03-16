"""
Скрипт для создания администратора.
Запуск: python create_admin.py

Можно передать email, пароль и имя через переменные окружения:
  ADMIN_EMAIL=admin@abc-school.ru ADMIN_PASSWORD=secret123 python create_admin.py
"""
import asyncio
import os
from sqlalchemy import select
from app.core.database import async_session
from app.core.security import hash_password
from app.models.user import User, UserRole


async def create_admin():
    email = os.getenv("ADMIN_EMAIL", "admin@abc-school.ru")
    password = os.getenv("ADMIN_PASSWORD", "admin123")
    full_name = os.getenv("ADMIN_NAME", "Администратор")

    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            print(f"ℹ️  Пользователь {email} уже существует.")
            return

        admin = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=UserRole.admin,
        )
        db.add(admin)
        await db.commit()
        print(f"✅  Администратор создан.")
        print(f"   Email:    {email}")
        print(f"   Пароль:   {password}")
        print(f"⚠️  Не забудьте сменить пароль после первого входа!")


asyncio.run(create_admin())
