from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.notification import NotificationChannel, NotificationStatus, NotificationType


class NotificationCreate(BaseModel):
    title: str
    body: str
    notification_type: NotificationType = NotificationType.custom
    channel: NotificationChannel = NotificationChannel.email
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    scheduled_at: Optional[datetime] = None  # None = немедленно


class NotificationOut(BaseModel):
    id: int
    title: str
    body: str
    notification_type: NotificationType
    channel: NotificationChannel
    recipient_email: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_name: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: NotificationStatus
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class BulkNotificationCreate(BaseModel):
    """Массовая рассылка всем ученикам группы"""
    group_id: int
    title: str
    body: str
    channel: NotificationChannel = NotificationChannel.email
    scheduled_at: Optional[datetime] = None
