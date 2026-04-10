from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Text, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    pending = "pending"       # ожидает оплаты
    paid = "paid"             # оплачено
    partial = "partial"       # частично оплачено
    overdue = "overdue"       # просрочено
    refunded = "refunded"     # возврат


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    card = "card"
    transfer = "transfer"
    online = "online"


class Invoice(Base):
    """Счёт на оплату (начисление за месяц/период)"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)
    student_name = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)       # начислено
    amount_paid = Column(Numeric(10, 2), default=0)       # оплачено
    period = Column(String(20), nullable=False)            # напр. "2026-04"
    due_date = Column(DateTime, nullable=False)
    status = Column(SAEnum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    group = relationship("Group", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice", lazy="select")


class Payment(Base):
    """Факт оплаты по счёту"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)
    student_name = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    method = Column(SAEnum(PaymentMethod), nullable=False, default=PaymentMethod.cash)
    paid_at = Column(DateTime, default=datetime.utcnow)
    received_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # кто принял
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    invoice = relationship("Invoice", back_populates="payments")
    student_group = relationship("StudentGroup", back_populates="payments")
