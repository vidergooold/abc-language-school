from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    telegram = "telegram"
    internal = "internal"   # внутреннее уведомление в кабинете


class NotificationStatus(str, enum.Enum):
    pending = "pending"       # в очереди
    sent = "sent"             # отправлено
    failed = "failed"         # ошибка отправки
    cancelled = "cancelled"   # отменено


class NotificationType(str, enum.Enum):
    schedule_reminder = "schedule_reminder"   # напоминание о занятии
    payment_reminder = "payment_reminder"     # напоминание об оплате
    enrollment_confirm = "enrollment_confirm" # подтверждение записи
    news_published = "news_published"         # опубликована новость
    custom = "custom"                         # произвольное


class Notification(Base):
    """Шаблон / событие уведомления"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(SAEnum(NotificationType), nullable=False, default=NotificationType.custom)
    channel = Column(SAEnum(NotificationChannel), nullable=False, default=NotificationChannel.email)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    scheduled_at = Column(DateTime, nullable=True)    # когда отправить (None = немедленно)
    sent_at = Column(DateTime, nullable=True)
    status = Column(SAEnum(NotificationStatus), nullable=False, default=NotificationStatus.pending)
    error_message = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class NotificationQueue(Base):
    """
    Очередь автоматических оповещений.
    Планировщик (APScheduler) каждые 5 минут проверяет
    записи с scheduled_at <= now и status=pending и отправляет их.
    """
    __tablename__ = "notification_queue"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(50), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(SAEnum(NotificationChannel), nullable=False, default=NotificationChannel.email)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(SAEnum(NotificationStatus), nullable=False, default=NotificationStatus.pending)
    sent_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
