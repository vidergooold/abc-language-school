from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import sys
sys.path.append('..')

from database import get_db
from models import Notification, User, NotificationStatus

router = APIRouter(
    prefix="/api/v1/notifications",
    tags=["notifications"]
)

# Pydantic schemas
class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: str  # email, sms, push
    scheduled_at: datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    status: str
    scheduled_at: datetime
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class BulkNotificationCreate(BaseModel):
    title: str
    message: str
    notification_type: str
    scheduled_at: datetime
    user_ids: Optional[List[int]] = None  # If None, send to all users
    role_filter: Optional[str] = None  # Filter by role: student, teacher, etc.

# Background task to send notification
async def send_notification_task(notification_id: int, db: Session):
    """
    Background task to actually send the notification.
    In production, this would integrate with email/SMS services.
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        return
    
    # Simulate sending notification
    # In production: integrate with SendGrid, Twilio, Firebase, etc.
    try:
        if notification.notification_type == "email":
            # Send email
            pass
        elif notification.notification_type == "sms":
            # Send SMS
            pass
        elif notification.notification_type == "push":
            # Send push notification
            pass
        
        # Mark as sent
        notification.status = NotificationStatus.sent
        notification.sent_at = datetime.utcnow()
    except Exception as e:
        # Mark as failed
        notification.status = NotificationStatus.failed
    
    db.commit()

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a scheduled notification for a user.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == notification.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {notification.user_id} not found"
        )
    
    # Create notification
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    
    # If scheduled for now or past, send immediately
    if notification.scheduled_at <= datetime.utcnow():
        background_tasks.add_task(send_notification_task, db_notification.id, db)
    
    return db_notification

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
async def create_bulk_notifications(
    bulk_notification: BulkNotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create notifications for multiple users at once.
    Useful for announcements, reminders, etc.
    """
    # Determine target users
    query = db.query(User).filter(User.is_active == True)
    
    if bulk_notification.user_ids:
        query = query.filter(User.id.in_(bulk_notification.user_ids))
    
    if bulk_notification.role_filter:
        from models import UserRole
        query = query.filter(User.role == UserRole(bulk_notification.role_filter))
    
    target_users = query.all()
    
    if not target_users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found matching the criteria"
        )
    
    # Create notifications for all target users
    created_notifications = []
    for user in target_users:
        db_notification = Notification(
            user_id=user.id,
            title=bulk_notification.title,
            message=bulk_notification.message,
            notification_type=bulk_notification.notification_type,
            scheduled_at=bulk_notification.scheduled_at
        )
        db.add(db_notification)
        created_notifications.append(db_notification)
    
    db.commit()
    
    # Schedule sending if needed
    if bulk_notification.scheduled_at <= datetime.utcnow():
        for notification in created_notifications:
            background_tasks.add_task(send_notification_task, notification.id, db)
    
    return {
        "message": f"Created {len(created_notifications)} notifications",
        "total_notifications": len(created_notifications),
        "target_users": [user.id for user in target_users]
    }

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    notification_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get notifications with optional filters.
    """
    query = db.query(Notification)
    
    if user_id:
        query = query.filter(Notification.user_id == user_id)
    if status:
        query = query.filter(Notification.status == NotificationStatus(status))
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    notifications = query.order_by(Notification.scheduled_at.desc()).offset(skip).limit(limit).all()
    return notifications

@router.get("/pending", status_code=status.HTTP_200_OK)
def get_pending_notifications(db: Session = Depends(get_db)):
    """
    Get all pending notifications that need to be sent.
    """
    now = datetime.utcnow()
    pending = db.query(Notification).filter(
        Notification.status == NotificationStatus.pending,
        Notification.scheduled_at <= now
    ).all()
    
    return {
        "total_pending": len(pending),
        "notifications": pending
    }

@router.post("/send-pending", status_code=status.HTTP_200_OK)
async def send_pending_notifications(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger sending of all pending notifications.
    This endpoint can be called by a cron job.
    """
    now = datetime.utcnow()
    pending = db.query(Notification).filter(
        Notification.status == NotificationStatus.pending,
        Notification.scheduled_at <= now
    ).all()
    
    for notification in pending:
        background_tasks.add_task(send_notification_task, notification.id, db)
    
    return {
        "message": f"Queued {len(pending)} notifications for sending",
        "total_queued": len(pending)
    }

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Cancel a pending notification.
    """
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found"
        )
    
    if notification.status != NotificationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending notifications"
        )
    
    db.delete(notification)
    db.commit()
    
    return None

@router.get("/stats", status_code=status.HTTP_200_OK)
def get_notification_stats(db: Session = Depends(get_db)):
    """
    Get notification statistics.
    """
    total = db.query(Notification).count()
    pending = db.query(Notification).filter(Notification.status == NotificationStatus.pending).count()
    sent = db.query(Notification).filter(Notification.status == NotificationStatus.sent).count()
    failed = db.query(Notification).filter(Notification.status == NotificationStatus.failed).count()
    
    return {
        "total_notifications": total,
        "pending": pending,
        "sent": sent,
        "failed": failed,
        "success_rate": round((sent / total * 100) if total > 0 else 0, 2)
    }
