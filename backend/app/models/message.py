from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    """Сообщение от преподавателя администратору."""
    __tablename__ = "messages"

    id           = Column(Integer, primary_key=True, index=True)
    sender_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body         = Column(Text, nullable=False)
    is_read      = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    sender    = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])
