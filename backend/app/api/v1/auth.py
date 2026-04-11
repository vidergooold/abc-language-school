"""Auth router — регистрация и вход в систему.

Публичные эндпоинты (без токена):
  POST  /auth/register   — регистрация нового пользователя
  POST  /auth/login      — получение JWT-токена (принимает JSON)
  GET   /auth/me         — данные текущего пользователя
  PATCH /auth/me         — обновление профиля (full_name, password)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, create_access_token,
    require_student,
)
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=UserRole.student,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user: User | None = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Учётная запись заблокирована",
        )
    token = create_access_token({
        "sub":   str(user.id),
        "email": user.email,
        "role":  user.role.value,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id":        user.id,
            "email":     user.email,
            "full_name": user.full_name,
            "role":      user.role.value,
        },
    }


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(require_student)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: ProfileUpdate,
    current_user: User = Depends(require_student),
    db: AsyncSession = Depends(get_db),
):
    """Update full_name and/or password of the current user."""
    if data.full_name is not None:
        current_user.full_name = data.full_name

    if data.new_password:
        if not data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Укажите текущий пароль",
            )
        if not verify_password(data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный текущий пароль",
            )
        current_user.hashed_password = hash_password(data.new_password)

    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
