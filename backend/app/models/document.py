"""Document model.

Таблица documents — документы, привязанные к пользователю.
Если user_id IS NULL — документ общедоступный (политики, бланки анкет).
"""
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class DocumentCategory(str, enum.Enum):
    policy   = "policy"    # Политики и согласия
    schedule = "schedule"  # Расписание
    template = "template"  # Бланки анкет
    contract = "contract"  # Договор (персональный)
    receipt  = "receipt"   # Квитанция / чек (персональный)
    other    = "other"     # Прочее


class Document(Base):
    __tablename__ = "documents"

    id:          Mapped[int]               = mapped_column(Integer, primary_key=True)
    title:       Mapped[str]               = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]]     = mapped_column(String(512), nullable=True)
    file_url:    Mapped[str]               = mapped_column(String(512), nullable=False)
    category:    Mapped[DocumentCategory]  = mapped_column(
        SAEnum(DocumentCategory), default=DocumentCategory.other, nullable=False
    )
    # NULL = общий документ; заполнено = персональный
    user_id:     Mapped[Optional[int]]     = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    is_active:   Mapped[bool]              = mapped_column(Boolean, default=True, nullable=False)
    created_at:  Mapped[datetime]          = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="documents", lazy="selectin")
