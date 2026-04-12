from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from app.core.database import Base


class AuditLog(Base):
    """
    Журнал действий администраторов и преподавателей.
    Фиксирует все операции создания, изменения, удаления данных.
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_email = Column(String(255), nullable=True)  # дублируем для истории
    action = Column(String(100), nullable=False)      # CREATE, UPDATE, DELETE, LOGIN
    entity_type = Column(String(100), nullable=False) # news, lesson, payment, student, ...
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)             # JSON-описание изменений
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
