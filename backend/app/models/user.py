import enum
from sqlalchemy import String, Integer, Boolean, Enum as SAEnum
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

    documents = relationship("Document", back_populates="user", lazy="selectin")
