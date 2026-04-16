from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin, require_staff
from app.models.educational_program import EducationalProgram
from app.schemas.educational_program import ProgramCreate, ProgramUpdate, ProgramOut

router = APIRouter(prefix="/programs", tags=["Educational Programs"])


@router.get("/", response_model=List[ProgramOut])
async def get_programs(db: AsyncSession = Depends(get_db)):
    """Публичный список активных образовательных программ"""
    result = await db.execute(
        select(EducationalProgram).where(EducationalProgram.is_active == True).order_by(EducationalProgram.name)
    )
    return result.scalars().all()


@router.get("/all", response_model=List[ProgramOut])
async def get_all_programs(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_staff),
):
    """Все программы включая неактивные — для сотрудников"""
    result = await db.execute(select(EducationalProgram).order_by(EducationalProgram.name))
    return result.scalars().all()


@router.get("/{program_id}", response_model=ProgramOut)
async def get_program(program_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EducationalProgram).where(EducationalProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    return program


@router.post("/", response_model=ProgramOut)
async def create_program(
    data: ProgramCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    program = EducationalProgram(**data.model_dump())
    db.add(program)
    await db.commit()
    await db.refresh(program)
    return program


@router.put("/{program_id}", response_model=ProgramOut)
async def update_program(
    program_id: int,
    data: ProgramUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(EducationalProgram).where(EducationalProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(program, field, value)
    await db.commit()
    await db.refresh(program)
    return program


@router.delete("/{program_id}")
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(EducationalProgram).where(EducationalProgram.id == program_id))
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Программа не найдена")
    program.is_active = False
    await db.commit()
    return {"ok": True, "message": "Программа деактивирована"}
