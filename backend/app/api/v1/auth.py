from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserCreate

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, нет ли уже пользователя с таким email
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.name,
    )
    db.add(user)
    await db.commit()
    return {"status": "registered"}


@router.post("/login")
async def login(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }
    }
