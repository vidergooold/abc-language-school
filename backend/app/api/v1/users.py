"""
Модуль пользователей (staff: admin, teacher).

Публичное/авторизованное API:
  GET   /users/me          — свой профиль
  PATCH /users/me          — обновить имя / сменить пароль

Административное API:
  GET    /admin/users              — список всех пользователей
  POST   /admin/users              — создать пользователя
  GET    /admin/users/{id}         — профиль пользователя
  PATCH  /admin/users/{id}/role    — сменить роль
  PATCH  /admin/users/{id}/deactivate — заблокировать / разблокировать
  DELETE /admin/users/{id}         — удалить пользователя
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr, Field

from app.core.database import get_db
from app.core.security import get_current_user, require_admin, get_password_hash, verify_password
from app.models.user import User, UserRole
from app.models.teacher import Teacher

router = APIRouter(tags=["Users"])


# ═══════════════════════════════════════════════════════════════════════
# PYDANTIC СХЕМЫ
# ═══════════════════════════════════════════════════════════════════════

class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True

    class Config:
        from_attributes = True


class UserMeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    current_password: Optional[str] = Field(None, description="Текущий пароль (для смены пароля)")
    new_password: Optional[str] = Field(None, min_length=8, description="Новый пароль (мин. 8 символов)")


class UserAdminCreate(BaseModel):
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.teacher


class UserRoleUpdate(BaseModel):
    role: UserRole


# ═══════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ═══════════════════════════════════════════════════════════════════════

async def _get_user_or_404(user_id: int, db: AsyncSession) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


# ═══════════════════════════════════════════════════════════════════════
# ЛИЧНЫЙ КАБИНЕТ (авторизованный пользователь)
# ═══════════════════════════════════════════════════════════════════════

@router.get("/users/me", response_model=UserOut, summary="Мой профиль")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """Возвращает профиль текущего авторизованного пользователя."""
    return current_user


@router.patch("/users/me", response_model=UserOut, summary="Обновить свой профиль")
async def update_me(
    data: UserMeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Пользователь может:
    - Изменить своё имя (full_name)
    - Сменить пароль (обязательно указать current_password + new_password)
    """
    if data.full_name is not None:
        current_user.full_name = data.full_name

    # Смена пароля — только если переданы оба поля
    if data.new_password is not None:
        if not data.current_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Для смены пароля необходимо указать текущий пароль (current_password)"
            )
        if not verify_password(data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Текущий пароль указан неверно"
            )
        current_user.hashed_password = get_password_hash(data.new_password)

    await db.commit()
    await db.refresh(current_user)
    return current_user


# ═══════════════════════════════════════════════════════════════════════
# АДМИНИСТРАТИВНОЕ API
# ═══════════════════════════════════════════════════════════════════════

@router.get("/admin/users", response_model=List[UserOut], summary="[Админ] Список пользователей")
async def admin_list_users(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Список всех зарегистрированных пользователей (staff)."""
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


@router.get("/admin/users/{user_id}", response_model=UserOut, summary="[Админ] Профиль пользователя")
async def admin_get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    return await _get_user_or_404(user_id, db)


@router.post("/admin/users", response_model=UserOut, status_code=201,
             summary="[Админ] Создать пользователя")
async def admin_create_user(
    data: UserAdminCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """
    Создать нового сотрудника (admin или teacher).
    Email должен быть уникальным.
    """
    # Проверяем уникальность email
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с email '{data.email}' уже существует"
        )
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/admin/users/{user_id}/role", response_model=UserOut,
              summary="[Админ] Сменить роль пользователя")
async def admin_update_role(
    user_id: int,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Изменить роль: teacher ↔ admin.
    Администратор не может понизить сам себя.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя изменить собственную роль"
        )
    user = await _get_user_or_404(user_id, db)
    user.role = data.role

    # При назначении роли преподавателя автоматически создаём профиль в teachers,
    # чтобы пользователь появился в разделе "Преподаватели".
    if data.role == UserRole.teacher:
        teacher_result = await db.execute(select(Teacher).where(Teacher.email == user.email))
        teacher = teacher_result.scalar_one_or_none()
        if teacher is None:
            teacher = Teacher(
                full_name=user.full_name or user.email,
                email=user.email,
                is_active=True,
            )
            db.add(teacher)
        elif not teacher.is_active:
            teacher.is_active = True

    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/admin/users/{user_id}/deactivate", response_model=UserOut,
              summary="[Админ] Заблокировать / разблокировать")
async def admin_toggle_active(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Переключает is_active. Заблокированный пользователь получает 403
    при попытке авторизации (проверяется в security.py).
    Администратор не может заблокировать сам себя.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя заблокировать собственную учётную запись"
        )
    user = await _get_user_or_404(user_id, db)
    user.is_active = not user.is_active
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/admin/users/{user_id}", status_code=204,
               summary="[Админ] Удалить пользователя")
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Удалить учётную запись сотрудника.
    Администратор не может удалить самого себя.
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нельзя удалить собственную учётную запись"
        )
    user = await _get_user_or_404(user_id, db)
    await db.delete(user)
    await db.commit()
