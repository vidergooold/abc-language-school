from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.enrollment import EnrollmentStatus


# ── История статусов ─────────────────────────────────────────────────
class EnrollmentStatusHistoryOut(BaseModel):
    id: int
    from_status: Optional[EnrollmentStatus]
    to_status: EnrollmentStatus
    changed_by: Optional[int]
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Создание заявки ────────────────────────────────────────────────
class EnrollmentCreate(BaseModel):
    name:    str  = Field(..., max_length=255)
    phone:   str  = Field(..., max_length=50)
    email:   Optional[str]  = Field(None, max_length=255)
    comment: Optional[str]  = None
    desired_course_id: Optional[int] = None
    student_type: Optional[str] = Field(None, max_length=50)  # child/adult/preschool
    age:    Optional[int] = None
    source: Optional[str] = Field(None, max_length=100)


# ── Действия администратора ───────────────────────────────────────────
class EnrollmentConfirm(BaseModel):
    """confirmed: подтверждение заявки без зачисления в группу."""
    comment: Optional[str] = None


class EnrollmentAssignGroup(BaseModel):
    """awaiting_payment: зачисление в группу + автосоздание invoice."""
    group_id:  int
    due_days:  int = Field(7, ge=1, le=90, description="Срок оплаты в днях")  
    comment:   Optional[str] = None


class EnrollmentReject(BaseModel):
    reason: str = Field(..., min_length=5, max_length=500)


class EnrollmentWithdraw(BaseModel):
    reason: Optional[str] = None


# ── Ответы ────────────────────────────────────────────────────────────────
class EnrollmentResponse(BaseModel):
    """POST /enrollments/ — подтверждение получения заявки."""
    id: int
    name: str
    phone: str
    email: Optional[str]
    status: EnrollmentStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class EnrollmentOut(BaseModel):
    """Full detail — для админки и личного кабинета."""
    id: int
    name: str
    phone: str
    email: Optional[str]
    comment: Optional[str]
    desired_course_id: Optional[int]
    student_type: Optional[str]
    age: Optional[int]
    source: Optional[str]
    status: EnrollmentStatus
    assigned_at: Optional[datetime]
    assigned_by: Optional[int]
    user_id: Optional[int]
    group_id: Optional[int]
    student_group_id: Optional[int]
    invoice_id: Optional[int]
    rejection_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    status_history: List[EnrollmentStatusHistoryOut] = []

    model_config = {"from_attributes": True}


class EnrollmentListOut(BaseModel):
    """Compact — для таблиц в админке."""
    id: int
    name: str
    phone: str
    email: Optional[str]
    status: EnrollmentStatus
    desired_course_id: Optional[int]
    student_type: Optional[str]
    group_id: Optional[int]
    invoice_id: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
