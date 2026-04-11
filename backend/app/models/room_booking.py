from datetime import datetime, date, time
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Boolean, Text, Date, Time
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class BookingStatus(str, enum.Enum):
    pending = "pending"       # заявка ожидает подтверждения
    confirmed = "confirmed"   # подтверждена
    cancelled = "cancelled"   # отменена
    completed = "completed"   # завершена


class BookingPurpose(str, enum.Enum):
    lesson = "lesson"             # регулярное занятие
    exam = "exam"                 # экзамен / тестирование
    event = "event"               # мероприятие / вечеринка
    consultation = "consultation" # индивидуальная консультация
    staff = "staff"               # педсовещание, прочее
    maintenance = "maintenance"   # техническое обслуживание


class RoomBooking(Base):
    """
    Бронирование аудитории на разовый случай или регулярное мероприятие,
    не входящее в основное расписание (lessons).

    Бизнес-правила:
    - Перед созданием брони СЕРВИС проверяет конфликты в таблице lessons
    - Статус pending — до подтверждения администратором
    - Статус confirmed — комната занята, никто другой не может забронировать
    - Автоматическая отмена если бронь не подтверждена за 24ч
    """
    __tablename__ = "room_bookings"

    id = Column(Integer, primary_key=True, index=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    booked_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)

    booking_date = Column(Date, nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)

    purpose = Column(SAEnum(BookingPurpose), nullable=False, default=BookingPurpose.lesson)
    status = Column(SAEnum(BookingStatus), nullable=False, default=BookingStatus.pending)
    title = Column(String(255), nullable=True)    # название мероприятия
    description = Column(Text, nullable=True)
    expected_attendees = Column(Integer, nullable=True)

    is_recurring = Column(Boolean, default=False)          # повторяющееся
    recurrence_rule = Column(String(255), nullable=True)   # напр., "weekly:MON,WED"
    parent_booking_id = Column(Integer, ForeignKey("room_bookings.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancel_reason = Column(Text, nullable=True)

    # Связи
    classroom = relationship("Classroom", backref="bookings")
    teacher = relationship("Teacher", backref="room_bookings")

    # Самоссылочная связь: родительская бронь → дочерние брони
    # remote_side=[id] указывает «этот id — сторона родителя»
    parent = relationship(
        "RoomBooking",
        back_populates="children",
        foreign_keys=[parent_booking_id],
        remote_side="RoomBooking.id",
    )
    children = relationship(
        "RoomBooking",
        back_populates="parent",
        foreign_keys=[parent_booking_id],
    )
