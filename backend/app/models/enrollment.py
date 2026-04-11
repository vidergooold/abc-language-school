from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, Enum as SAEnum, Boolean
)
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class EnrollmentStatus(str, enum.Enum):
    pending            = "pending"             # новая заявка, не обработана
    confirmed          = "confirmed"           # подтверждена — ожидает зачисления в группу
    awaiting_payment   = "awaiting_payment"    # зачислен в группу, счёт выставлен
    active             = "active"              # оплачен, обучается
    cancelled          = "cancelled"           # отменён администратором
    rejected           = "rejected"            # отклонён (нет мест, не подошёл уровень)
    withdrawn          = "withdrawn"           # студент отчислен по своему желанию


# Допустимые переходы статусов (FSM)
ENROLLMENT_STATUS_TRANSITIONS: dict[EnrollmentStatus, list[EnrollmentStatus]] = {
    EnrollmentStatus.pending:          [EnrollmentStatus.confirmed, EnrollmentStatus.rejected, EnrollmentStatus.cancelled],
    EnrollmentStatus.confirmed:        [EnrollmentStatus.awaiting_payment, EnrollmentStatus.cancelled, EnrollmentStatus.rejected],
    EnrollmentStatus.awaiting_payment: [EnrollmentStatus.active, EnrollmentStatus.cancelled],
    EnrollmentStatus.active:           [EnrollmentStatus.withdrawn],
    EnrollmentStatus.cancelled:        [],
    EnrollmentStatus.rejected:         [EnrollmentStatus.pending],  # повторная подача
    EnrollmentStatus.withdrawn:        [],
}


class Enrollment(Base):
    """Заявка на зачисление.

    Цикл: pending → confirmed → awaiting_payment → active
    """
    __tablename__ = "enrollments"

    id      = Column(Integer, primary_key=True, index=True)
    # Контактные данные
    name    = Column(String(255), nullable=False)
    phone   = Column(String(50),  nullable=False)
    email   = Column(String(255), nullable=True)
    comment = Column(Text, nullable=True)

    # Предпочтения студента
    desired_course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    student_type      = Column(String(50), nullable=True)  # child / adult / preschool
    age               = Column(Integer, nullable=True)
    source            = Column(String(100), nullable=True)  # источник (реклама, рекомендация)

    # Статус workflow
    status      = Column(SAEnum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.pending, index=True)
    assigned_at = Column(DateTime, nullable=True)   # когда подтверждён
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # админ

    # Связи с другими сущностями
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=True)   # аккаунт (если есть)
    group_id        = Column(Integer, ForeignKey("groups.id"), nullable=True)  # зачисление в группу
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)  # StudentGroup
    invoice_id      = Column(Integer, ForeignKey("invoices.id"), nullable=True)  # счёт на оплату
    rejection_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Отношения
    user          = relationship("User", foreign_keys=[user_id], backref="enrollments")
    assigned_user = relationship("User", foreign_keys=[assigned_by])
    desired_course = relationship("Course", foreign_keys=[desired_course_id])
    group         = relationship("Group", foreign_keys=[group_id])
    student_group = relationship("StudentGroup", foreign_keys=[student_group_id])
    status_history = relationship(
        "EnrollmentStatusHistory", back_populates="enrollment",
        order_by="EnrollmentStatusHistory.created_at",
        cascade="all, delete-orphan", lazy="selectin"
    )


class EnrollmentStatusHistory(Base):
    """Журнал переходов статусов заявки."""
    __tablename__ = "enrollment_status_history"

    id          = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id", ondelete="CASCADE"), nullable=False)
    from_status = Column(SAEnum(EnrollmentStatus), nullable=True)
    to_status   = Column(SAEnum(EnrollmentStatus), nullable=False)
    changed_by  = Column(Integer, ForeignKey("users.id"), nullable=True)
    comment     = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    enrollment = relationship("Enrollment", back_populates="status_history")
