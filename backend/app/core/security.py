"""JWT-аутентификация и зависимости (Депенденсы) для FastAPI.

Матрица доступа:
  get_current_user   — любой авторизованный пользователь
  require_student    — student | teacher | admin  (свои данные)
  require_staff      — teacher | admin             (расписание, группы, посещаемость)
  require_admin      — admin only                  (финансы, аналитика, управление)
Правило по пульчам:
  - GET публичных списков (курсы, новости) — без токена (для сайта)
  - GET внутренних данных (расписание, аудитории) — require_staff
  - POST/PUT/DELETE объектов школы — require_admin¹
  - POST/PUT своей посещаемости, заявок — require_student
  - Финансы, аналитика, аудит — require_admin
¹ Смену посещаемости может делать учитель через require_staff.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, UserRole

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 часов

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ─── Утилиты ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# Псевдонимы для совместимости с FastAPI-конвенцией
get_password_hash = hash_password


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создаёт JWT. В payload включает 'sub' (user_id), 'email', 'role'."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─── Депенденсы ───────────────────────────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Декодирует JWT и возвращает пользователя из DB."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен аутентификации",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            raise exc
        user_id = int(sub)
    except (JWTError, ValueError):
        raise exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise exc
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись заблокирована",
        )
    return user


async def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Любой аутентифицированный пользователь (student | teacher | admin)."""
    return current_user


async def require_staff(current_user: User = Depends(get_current_user)) -> User:
    """Только teacher или admin. Для внутренних данных школы."""
    if current_user.role not in (UserRole.admin, UserRole.teacher):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для сотрудников школы",
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Только admin. Для финансов, аналитики, управления структурой школы."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администратора",
        )
    return current_user
