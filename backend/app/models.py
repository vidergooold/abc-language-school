from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

# Enums
class UserRole(str, enum.Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"
    manager = "manager"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class LessonStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    rescheduled = "rescheduled"

class NewsStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"

class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"

class CourseLevel(str, enum.Enum):
    beginner = "beginner"
    elementary = "elementary"
    intermediate = "intermediate"
    upper_intermediate = "upper_intermediate"
    advanced = "advanced"

# 1. Users Table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.student)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    enrollments = relationship("Enrollment", back_populates="student")
    payments = relationship("Payment", back_populates="user")
    teacher_lessons = relationship("Lesson", foreign_keys="Lesson.teacher_id", back_populates="teacher")
    notifications = relationship("Notification", back_populates="user")
    attendance_records = relationship("Attendance", back_populates="student")

# 2. Courses Table
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    level = Column(SQLEnum(CourseLevel), nullable=False)
    language = Column(String, nullable=False)
    duration_weeks = Column(Integer)
    price = Column(Float, nullable=False)
    max_students = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    groups = relationship("Group", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")

# 3. Groups Table
class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    max_students = Column(Integer, default=10)
    current_students = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", back_populates="groups")
    lessons = relationship("Lesson", back_populates="group")
    enrollments = relationship("Enrollment", back_populates="group")

# 4. Lessons Table (Schedule)
class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    topic = Column(String)
    status = Column(SQLEnum(LessonStatus), default=LessonStatus.scheduled)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("Group", back_populates="lessons")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_lessons")
    room = relationship("Room", back_populates="lessons")
    attendance_records = relationship("Attendance", back_populates="lesson")

# 5. Rooms Table
class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    capacity = Column(Integer, nullable=False)
    equipment = Column(Text)  # JSON string of available equipment
    is_available = Column(Boolean, default=True)
    
    # Relationships
    lessons = relationship("Lesson", back_populates="room")

# 6. Enrollments Table
class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"))
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    completion_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    
    # Relationships
    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    group = relationship("Group", back_populates="enrollments")
    payment = relationship("Payment", back_populates="enrollment")

# 7. Payments Table
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="RUB")
    payment_method = Column(String)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending)
    transaction_id = Column(String, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    enrollment = relationship("Enrollment", back_populates="payment", uselist=False)

# 8. Attendance Table
class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    present = Column(Boolean, default=False)
    late_minutes = Column(Integer, default=0)
    notes = Column(Text)
    marked_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lesson = relationship("Lesson", back_populates="attendance_records")
    student = relationship("User", back_populates="attendance_records")

# 9. News/Articles Table
class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(NewsStatus), default=NewsStatus.draft)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views = Column(Integer, default=0)
    image_url = Column(String)
    
    # Relationships
    author = relationship("User")

# 10. Notifications Table
class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String)  # email, sms, push
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.pending)
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

# 11. Waitlist Table
class Waitlist(Base):
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    position = Column(Integer)
    added_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)
    
    # Relationships
    student = relationship("User")
    course = relationship("Course")

# 12. Reviews Table
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_published = Column(Boolean, default=False)
    
    # Relationships
    student = relationship("User")
    course = relationship("Course")

# 13. Materials Table
class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_url = Column(String, nullable=False)
    file_type = Column(String)  # pdf, video, audio, etc.
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    course = relationship("Course")

# 14. Expenses Table
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)  # rent, salaries, utilities, etc.
    amount = Column(Float, nullable=False)
    currency = Column(String, default="RUB")
    description = Column(Text)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 15. Revenue Analytics Table
class RevenueAnalytics(Base):
    __tablename__ = "revenue_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    total_revenue = Column(Float, default=0)
    total_expenses = Column(Float, default=0)
    net_profit = Column(Float, default=0)
    student_count = Column(Integer, default=0)
    course_count = Column(Integer, default=0)
    average_revenue_per_student = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
