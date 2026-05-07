from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class MessageCreate(BaseModel):
    recipient_id: int
    body: str


class MessageRead(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    body: str
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UnreadCount(BaseModel):
    unread: int
