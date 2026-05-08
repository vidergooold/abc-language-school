from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentListOut

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=List[EnrollmentListOut])
async def list_applications(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Админский список заявок (алиас для enrollment-заявок)."""
    result = await db.execute(select(Enrollment).order_by(Enrollment.created_at.desc()))
    return result.scalars().all()
