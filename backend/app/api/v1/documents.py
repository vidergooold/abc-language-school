"""Документы (router).

Матрица доступа:
  GET  /documents/public   — без авторизации  (общие: политики, расписание, бланки)
  GET  /documents/my       — require_student (общие + персональные документы студента)
  GET  /documents          — require_admin   (все документы)
  POST /documents          — require_admin   (создать)
  PUT  /documents/{id}     — require_admin   (обновить)
  DELETE /documents/{id}   — require_admin   (архивировать, is_active=False)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_student, require_admin
from app.models.document import Document, DocumentCategory
from app.models.user import User
from app.schemas.document import DocumentOut, DocumentCreate, DocumentUpdate

router = APIRouter(tags=["Documents"])

# Категории, которые видят все без авторизации
PUBLIC_CATEGORIES = [
    DocumentCategory.policy,
    DocumentCategory.schedule,
    DocumentCategory.template,
]


@router.get("/documents/public", response_model=List[DocumentOut])
async def get_public_documents(db: AsyncSession = Depends(get_db)):
    """Общедоступные документы (политики, расписание, бланки) — без токена."""
    result = await db.execute(
        select(Document).where(
            Document.is_active == True,
            Document.user_id == None,
            Document.category.in_(PUBLIC_CATEGORIES),
        ).order_by(Document.category, Document.title)
    )
    return result.scalars().all()


@router.get("/documents/my", response_model=List[DocumentOut])
async def get_my_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_student),
):
    """Общие документы + персональные документы текущего пользователя."""
    result = await db.execute(
        select(Document).where(
            Document.is_active == True,
            or_(
                Document.user_id == None,          # Общие документы
                Document.user_id == current_user.id,  # Персональные
            ),
        ).order_by(Document.category, Document.title)
    )
    return result.scalars().all()


@router.get("/documents", response_model=List[DocumentOut])
async def get_all_documents(
    category: Optional[DocumentCategory] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Все документы (админ)."""
    query = select(Document).where(Document.is_active == True)
    if category:
        query = query.where(Document.category == category)
    if user_id is not None:
        query = query.where(Document.user_id == user_id)
    result = await db.execute(query.order_by(Document.category, Document.title))
    return result.scalars().all()


@router.post("/documents", response_model=DocumentOut)
async def create_document(
    data: DocumentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = Document(**data.model_dump())
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.put("/documents/{doc_id}", response_model=DocumentOut)
async def update_document(
    doc_id: int,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, field, value)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    doc.is_active = False
    await db.commit()
    return {"ok": True}
