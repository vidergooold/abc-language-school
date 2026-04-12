from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class WaitlistStatus(str, enum.Enum):
    waiting   = "waiting"    # в очереди
    notified  = "notified"   # уведомлён о месте
    enrolled  = "enrolled"   # зачислен
    cancelled = "cancelled"  # отказался


class WaitlistEntry(Base):
    """
    Лист ожидания на группу.
    Когда в группе освобождается место — первому в очереди
    автоматически уходит уведомление (статус → notified).
    """
    __tablename__ = "waitlist"

    id           = Column(Integer, primary_key=True, index=True)
    course_id    = Column(Integer, ForeignKey("courses.id"), nullable=False)
    group_id     = Column(Integer, ForeignKey("groups.id"), nullable=True)  # желаемая группа
    student_name  = Column(String(255), nullable=False)
    student_phone = Column(String(50),  nullable=True)
    student_email = Column(String(255), nullable=True)
    student_type  = Column(String(50),  nullable=False, default="adult")  # child/adult/preschool
    comment       = Column(Text,        nullable=True)
    position      = Column(Integer,     nullable=False, default=1)  # порядковый номер в очереди
    status        = Column(SAEnum(WaitlistStatus), nullable=False, default=WaitlistStatus.waiting)
    notified_at   = Column(DateTime, nullable=True)
    enrolled_at   = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", lazy="select")
    group  = relationship("Group",  lazy="select")
