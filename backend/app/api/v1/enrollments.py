from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentOut,
)

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse)
async def create_enrollment(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = None,
):
    enrollment = Enrollment(**data.dict())

    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return enrollment


@router.get("/my", response_model=List[EnrollmentOut])
async def get_my_enrollments(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    user: User = await get_current_user(token=token, db=db)

    result = await db.execute(
        select(Enrollment).where(Enrollment.user_id == user.id)
    )
    return result.scalars().all()
