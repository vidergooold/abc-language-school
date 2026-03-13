from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def get_me(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    user: User = await get_current_user(token=token, db=db)
    return user
