#!/usr/bin/env python3
"""
Диагностический скрипт для проверки работы аутентификации администратора
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password
from sqlalchemy import select


async def test_admin():
    print("=" * 60)
    print("Диагностика администратора")
    print("=" * 60)
    
    # Инициализируем БД
    print("\n1️⃣  Инициализирую БД...")
    try:
        await init_db()
        print("   ✅ БД инициализирована")
    except Exception as e:
        print(f"   ❌ Ошибка инициализации: {e}")
        return
    
    # Проверяем есть ли администратор
    print("\n2️⃣  Ищу администратора в БД...")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@abc-school.ru")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == admin_email))
        admin = result.scalar_one_or_none()
        
        if admin:
            print(f"   ✅ Администратор найден: {admin.email}")
            print(f"      - ID: {admin.id}")
            print(f"      - Роль: {admin.role.value}")
            print(f"      - Активен: {admin.is_active}")
            print(f"      - Имя: {admin.full_name}")
        else:
            print(f"   ⚠️  Администратор {admin_email} НЕ найден в БД!")
            print(f"   💡 Решение: запустите python create_admin.py")
    
    # Тестируем функции хеширования
    print("\n3️⃣  Тестирую функции хеширования...")
    test_password = "testpass123"
    try:
        hashed = hash_password(test_password)
        print(f"   ✅ hash_password() работает")
        print(f"      Хеш: {hashed[:30]}... (длина: {len(hashed)})")
        
        # Проверяем правильный пароль
        if verify_password(test_password, hashed):
            print(f"   ✅ verify_password() работает с правильным паролем")
        else:
            print(f"   ❌ verify_password() НЕ подтвердил правильный пароль!")
        
        # Проверяем неправильный пароль
        if not verify_password("wrongpassword", hashed):
            print(f"   ✅ verify_password() отклоняет неправильный пароль")
        else:
            print(f"   ❌ verify_password() принял неправильный пароль!")
    except Exception as e:
        print(f"   ❌ Ошибка в функциях хеширования: {e}")
    
    # Если админ найден, тестируем его пароль
    print("\n4️⃣  Тестирую пароль администратора...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == admin_email))
        admin = result.scalar_one_or_none()
        
        if admin:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            
            # Попытаемся проверить пароль
            try:
                if verify_password(admin_password, admin.hashed_password):
                    print(f"   ✅ Пароль '{admin_password}' ВЕРЕН для администратора!")
                else:
                    print(f"   ❌ Пароль '{admin_password}' НЕВЕРЕН для администратора")
                    print(f"      (Это может быть правильно, если админ был создан с другим паролем)")
            except Exception as e:
                print(f"   ❌ Ошибка при проверке пароля: {e}")
    
    print("\n" + "=" * 60)
    print("Диагностика завершена")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_admin())
