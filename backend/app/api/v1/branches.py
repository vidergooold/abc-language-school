from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.branch import Branch
from app.schemas.branch import BranchCreate, BranchUpdate, BranchOut

router = APIRouter(prefix="/branches", tags=["Branches"])


@router.get("/", response_model=List[BranchOut])
async def get_branches(db: AsyncSession = Depends(get_db)):
    """Публичный список активных филиалов"""
    result = await db.execute(
        select(Branch).where(Branch.is_active == True).order_by(Branch.name)
    )
    return result.scalars().all()


@router.get("/all", response_model=List[BranchOut])
async def get_all_branches(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Все филиалы включая неактивные — для сотрудников"""
    result = await db.execute(select(Branch).order_by(Branch.name))
    return result.scalars().all()


@router.get("/{branch_id}", response_model=BranchOut)
async def get_branch(branch_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    return branch


@router.post("/", response_model=BranchOut)
async def create_branch(
    data: BranchCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    branch = Branch(**data.model_dump())
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch


@router.put("/{branch_id}", response_model=BranchOut)
async def update_branch(
    branch_id: int,
    data: BranchUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(branch, field, value)
    await db.commit()
    await db.refresh(branch)
    return branch


@router.delete("/{branch_id}")
async def delete_branch(
    branch_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(Branch).where(Branch.id == branch_id))
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Филиал не найден")
    branch.is_active = False
    await db.commit()
    return {"ok": True, "message": "Филиал деактивирован"}
