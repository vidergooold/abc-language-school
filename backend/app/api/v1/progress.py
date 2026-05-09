from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.attendance import get_group_grades
from app.core.database import get_db
from app.core.security import require_staff

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("")
@router.get("/")
async def get_progress(
    group_id: int = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_staff),
):
    return await get_group_grades(
        group_id=group_id,
        date_from=date_from,
        date_to=date_to,
        db=db,
        _=current_user,
    )
