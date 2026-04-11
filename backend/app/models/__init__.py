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
from app.models.waitlist import WaitlistEntry, WaitlistStatus
from app.models.forms import ChildForm, AdultForm, PreschoolForm, TeacherForm, TestingForm, FeedbackForm
from app.models.discount import Discount, DiscountType, DiscountReason
from app.models.room_booking import RoomBooking, BookingStatus, BookingPurpose
from app.models.audit import AuditLog
from app.models.report import ReportCache

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
    "WaitlistEntry",
    "WaitlistStatus",
    "ChildForm",
    "AdultForm",
    "PreschoolForm",
    "TeacherForm",
    "TestingForm",
    "FeedbackForm",
    "Discount",
    "DiscountType",
    "DiscountReason",
    "RoomBooking",
    "BookingStatus",
    "BookingPurpose",
    "AuditLog",
    "ReportCache",
]
