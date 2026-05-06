import enum
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin   = "admin"


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(Integer, primary_key=True)
    email:           Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(255), nullable=False)
    full_name:       Mapped[str]      = mapped_column(String(255), nullable=True)
    phone:           Mapped[str]      = mapped_column(String(32),  nullable=True)
    role:            Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.student, nullable=False)
    is_active:       Mapped[bool]     = mapped_column(Boolean, default=True, nullable=False)
    created_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    documents = relationship("Document", back_populates="user", lazy="selectin")
