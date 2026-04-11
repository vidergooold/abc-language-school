from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    admin = "admin"
    teacher = "teacher"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.teacher)
    is_active = Column(Boolean, nullable=False, default=True)
