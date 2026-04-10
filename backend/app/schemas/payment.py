from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel
from app.models.payment import PaymentStatus, PaymentMethod


class InvoiceCreate(BaseModel):
    group_id: int
    student_group_id: Optional[int] = None
    student_name: str
    amount: Decimal
    period: str   # напр. "2026-04"
    due_date: datetime
    notes: Optional[str] = None


class InvoiceOut(BaseModel):
    id: int
    group_id: int
    student_group_id: Optional[int] = None
    student_name: str
    amount: Decimal
    amount_paid: Decimal
    period: str
    due_date: datetime
    status: PaymentStatus
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    invoice_id: Optional[int] = None
    student_group_id: Optional[int] = None
    student_name: str
    amount: Decimal
    method: PaymentMethod = PaymentMethod.cash
    comment: Optional[str] = None


class PaymentOut(BaseModel):
    id: int
    invoice_id: Optional[int] = None
    student_group_id: Optional[int] = None
    student_name: str
    amount: Decimal
    method: PaymentMethod
    paid_at: datetime
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
