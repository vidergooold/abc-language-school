# Импорт всех моделей для корректной инициализации маппера SQLAlchemy.
# Порядок важен: сначала независимые модели, затем те, что ссылаются на них.

from app.models.user import User
from app.models.teacher import Teacher
from app.models.schedule import Classroom, Lesson, DayOfWeek, LessonStatus
from app.models.group import Group
from app.models.attendance import Attendance
from app.models.enrollment import Enrollment
from app.models.payment import Payment
from app.models.news import News
from app.models.notification import Notification
from app.models.waitlist import Waitlist
from app.models.forms import Form
from app.models.discount import Discount
from app.models.room_booking import RoomBooking
from app.models.audit import AuditLog
from app.models.report import Report

__all__ = [
    "User",
    "Teacher",
    "Classroom",
    "Lesson",
    "DayOfWeek",
    "LessonStatus",
    "Group",
    "Attendance",
    "Enrollment",
    "Payment",
    "News",
    "Notification",
    "Waitlist",
    "Form",
    "Discount",
    "RoomBooking",
    "AuditLog",
    "Report",
]
