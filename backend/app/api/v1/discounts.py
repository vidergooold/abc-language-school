from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from decimal import Decimal

from app.core.database import get_db
from app.core.security import require_admin
from app.models.discount import Discount, DiscountType, DiscountReason

router = APIRouter(prefix="/discounts", tags=["Discounts"])


# ─── Pydantic схемы ──────────────────────────────────────────────

class DiscountCreate(BaseModel):
    student_group_id: Optional[int] = None
    group_id: Optional[int] = None
    reason: DiscountReason
    discount_type: DiscountType
    value: Decimal
    description: Optional[str] = None
    promo_code: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    is_active: bool = True


class DiscountOut(BaseModel):
    id: int
    student_group_id: Optional[int]
    group_id: Optional[int]
    reason: DiscountReason
    discount_type: DiscountType
    value: Decimal
    description: Optional[str]
    promo_code: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    max_uses: Optional[int]
    used_count: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApplyDiscountRequest(BaseModel):
    amount: float
    promo_code: Optional[str] = None
    student_group_id: Optional[int] = None


class ApplyDiscountResponse(BaseModel):
    original_amount: float
    discounted_amount: float
    saved: float
    discount_id: Optional[int]
    discount_description: Optional[str]


# ─── CRUD ────────────────────────────────────────────────────────

@router.get("", response_model=List[DiscountOut])
async def list_discounts(
    is_active: Optional[bool] = Query(None),
    reason: Optional[DiscountReason] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Список всех скидок. Фильтрация по активности и типу."""
    query = select(Discount).order_by(Discount.created_at.desc())
    if is_active is not None:
        query = query.where(Discount.is_active == is_active)
    if reason:
        query = query.where(Discount.reason == reason)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=DiscountOut, status_code=201)
async def create_discount(
    data: DiscountCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Создать скидку. Промокод проверяется на уникальность."""
    if data.promo_code:
        existing = await db.execute(
            select(Discount).where(
                Discount.promo_code == data.promo_code,
                Discount.is_active == True
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(400, detail=f"Промокод '{data.promo_code}' уже существует")
    discount = Discount(**data.model_dump())
    db.add(discount)
    await db.commit()
    await db.refresh(discount)
    return discount


@router.get("/promo/{code}", response_model=DiscountOut)
async def get_discount_by_promo(
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Получить скидку по промокоду (доступно любому пользователю)."""
    result = await db.execute(
        select(Discount).where(Discount.promo_code == code)
    )
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(404, detail="Промокод не найден")
    return discount


@router.post("/apply", response_model=ApplyDiscountResponse)
async def apply_discount(
    data: ApplyDiscountRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Применить скидку и вернуть новую сумму.

    Логика:
    1. Если передан promo_code — ищем скидку по нему
    2. Иначе ищем скидку привязанную к student_group_id
    3. Иначе возвращаем оригинальную сумму
    """
    discount = None

    if data.promo_code:
        result = await db.execute(
            select(Discount).where(
                Discount.promo_code == data.promo_code,
                Discount.is_active == True
            )
        )
        discount = result.scalar_one_or_none()
    elif data.student_group_id:
        result = await db.execute(
            select(Discount).where(
                Discount.student_group_id == data.student_group_id,
                Discount.is_active == True
            ).order_by(Discount.value.desc())
        )
        discount = result.scalars().first()

    if not discount or not discount.is_valid():
        return ApplyDiscountResponse(
            original_amount=data.amount,
            discounted_amount=data.amount,
            saved=0.0,
            discount_id=None,
            discount_description=None,
        )

    new_amount = discount.apply(data.amount)
    discount.used_count += 1
    await db.commit()

    return ApplyDiscountResponse(
        original_amount=data.amount,
        discounted_amount=new_amount,
        saved=round(data.amount - new_amount, 2),
        discount_id=discount.id,
        discount_description=discount.description,
    )


@router.patch("/{discount_id}/deactivate", response_model=DiscountOut)
async def deactivate_discount(
    discount_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Деактивировать скидку без удаления."""
    result = await db.execute(select(Discount).where(Discount.id == discount_id))
    discount = result.scalar_one_or_none()
    if not discount:
        raise HTTPException(404, detail="Скидка не найдена")
    discount.is_active = False
    await db.commit()
    await db.refresh(discount)
    return discount


@router.get("/stats/summary")
async def discount_stats(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    """Статистика по скидкам: сколько активных, сколько применений всего."""
    total = await db.scalar(select(func.count()).select_from(Discount))
    active = await db.scalar(select(func.count()).where(Discount.is_active == True))
    total_used = await db.scalar(select(func.sum(Discount.used_count))) or 0

    by_reason = await db.execute(
        select(Discount.reason, func.count().label("cnt"))
        .group_by(Discount.reason)
    )

    return {
        "total_discounts": total,
        "active_discounts": active,
        "total_applied": total_used,
        "by_reason": [
            {"reason": row.reason, "count": row.cnt}
            for row in by_reason.all()
        ],
    }
