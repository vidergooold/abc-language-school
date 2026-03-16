from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    tag = Column(String(100), nullable=True)
    body = Column(Text, nullable=False)
    date = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
