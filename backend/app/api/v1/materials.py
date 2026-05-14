"""Top-level materials endpoint that reuses attendance materials query logic."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.api.v1.attendance import get_materials_by_group
from app.core.database import get_db
from app.core.security import require_staff, require_student
from app.models.group import StudentGroup
from app.models.user import User

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get("")
@router.get("/")
async def list_materials(
    group_id: int = Query(...),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_staff),
):
    return await get_materials_by_group(
        group_id=group_id,
        date_from=date_from,
        date_to=date_to,
        db=db,
    )


@router.get("/my")
async def list_my_materials(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    groups_result = await db.execute(
        select(StudentGroup.group_id).where(
            and_(
                StudentGroup.student_email == current_user.email,
                StudentGroup.is_active == True,
            )
        )
    )
    group_ids = groups_result.scalars().all()
    if not group_ids:
        return []

    materials = []
    for group_id in group_ids:
        rows = await get_materials_by_group(
            group_id=group_id,
            date_from=date_from,
            date_to=date_to,
            db=db,
        )
        materials.extend(rows)
    return materials
