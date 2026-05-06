from typing import Optional
"""
seed_full_demo.py
-----------------
Seeds a realistic demo dataset so the whole flow works end-to-end:
  students → groups → lessons → attendance → invoices → payments

Run from the backend/ directory:
    cd backend
    python seed_full_demo.py

Prerequisites:
  - Group id=1 must exist in the database.
  - Classroom id=1 must exist (created e.g. by seed_account_data.py); if it
    is missing the lesson inserts will fail with a FK violation.  Run the
    other seed scripts first or create a classroom row manually.
"""

import asyncio
import random
import sys
import os
from datetime import datetime, timedelta, time, date

from sqlalchemy import select

# Make sure the app package is importable when running from backend/
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Course, Group, StudentGroup
from app.models.schedule import Lesson, LessonStatus, DayOfWeek
from app.models.attendance import Attendance, AttendanceStatus
from app.models.payment import Invoice, Payment, PaymentStatus, PaymentMethod
from app.models.student import Student
from app.models.user import User, UserRole

# ─────────────────────────── constants ───────────────────────────

DEMO_GROUP_ID = 1
DEMO_PERIOD = "2026-04"          # period tag used for idempotency checks
TEACHER_ID = 1                   # existing teacher id to use for new lessons
STUDENT_IDS = list(range(1, 13))  # students 1–12

# Day-of-week helpers
_DOW_MAP = {
    0: DayOfWeek.monday,
    1: DayOfWeek.tuesday,
    2: DayOfWeek.wednesday,
    3: DayOfWeek.thursday,
    4: DayOfWeek.friday,
    5: DayOfWeek.saturday,
    6: DayOfWeek.sunday,
}


def _next_weekday(ref: date, weekday: int) -> date:
    """Return the next date >= ref that falls on weekday (0=Mon … 6=Sun)."""
    days_ahead = weekday - ref.weekday()
    if days_ahead < 0:
        days_ahead += 7
    return ref + timedelta(days=days_ahead)


# ─────────────────────────── helpers ─────────────────────────────

async def _get_or_create(session, model, lookup: dict, defaults: Optional[dict] = None):
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalar_one_or_none()
    if instance:
        return instance, False
    payload = {**lookup, **(defaults or {})}
    instance = model(**payload)
    session.add(instance)
    await session.flush()
    return instance, True


# ──────────────────────── main seeder ────────────────────────────

async def seed_full_demo() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:

        # ── 0. Fetch reference data ──────────────────────────────

        # Group
        group_result = await session.execute(select(Group).where(Group.id == DEMO_GROUP_ID))
        group = group_result.scalar_one_or_none()
        if group is None:
            print(f"❌  Group id={DEMO_GROUP_ID} not found. Aborting.")
            return

        # Course price
        course_result = await session.execute(select(Course).where(Course.id == group.course_id))
        course = course_result.scalar_one_or_none()
        price_per_month = int(course.price_per_month) if (course and course.price_per_month) else 5000

        # Admin user (received_by)
        admin_result = await session.execute(
            select(User).where(User.role == UserRole.admin).limit(1)
        )
        admin = admin_result.scalar_one_or_none()
        admin_id = admin.id if admin else None

        # Students 1–12
        students_result = await session.execute(
            select(Student).where(Student.id.in_(STUDENT_IDS))
        )
        students = students_result.scalars().all()

        # ── 1. student_groups ────────────────────────────────────

        now = datetime.utcnow()
        month_ago = now - timedelta(days=30)

        sg_created = 0
        sg_records: list[StudentGroup] = []

        for student in students:
            sg, created = await _get_or_create(
                session,
                StudentGroup,
                {"group_id": DEMO_GROUP_ID, "student_name": student.full_name},
                {
                    "student_phone": student.phone,
                    "student_email": student.email,
                    "student_type": student.student_type.value,
                    "form_id": None,
                    "enrolled_at": month_ago + timedelta(days=random.randint(0, 25)),
                    "is_active": True,
                },
            )
            sg_records.append(sg)
            if created:
                sg_created += 1

        await session.flush()

        # ── 2. lessons ───────────────────────────────────────────

        # Check how many new lessons already exist for this demo period
        existing_lesson_result = await session.execute(
            select(Lesson).where(
                Lesson.group_id == DEMO_GROUP_ID,
                Lesson.lesson_date >= now,
            )
        )
        existing_future_lessons = existing_lesson_result.scalars().all()

        lessons_created = 0
        lesson_records: list[Lesson] = []

        # Keep existing future lessons for attendance seeding
        lesson_records.extend(existing_future_lessons)

        # Schedule: Mon+Wed 10:00–11:30, Fri 16:00–17:30 — 2 lessons per weekday pattern
        lesson_slots = [
            (0, time(10, 0), time(11, 30), "Present Simple"),        # Monday
            (2, time(10, 0), time(11, 30), "Reading Practice"),      # Wednesday
            (4, time(16, 0), time(17, 30), "Speaking Club"),         # Friday
            (1, time(18, 0), time(19, 30), "Grammar Workshop"),      # Tuesday
            (3, time(18, 0), time(19, 30), "Vocabulary Building"),   # Thursday
            (0, time(10, 0), time(11, 30), "Listening Skills"),      # Monday (week 2)
        ]

        ref_date = now.date() + timedelta(days=1)  # start from tomorrow
        week_offset = 0

        for i, (weekday, t_start, t_end, topic) in enumerate(lesson_slots):
            if i == len(lesson_slots) - 1:
                week_offset = 7  # push last lesson to next week

            lesson_dt = datetime.combine(
                _next_weekday(ref_date + timedelta(days=week_offset), weekday),
                t_start,
            )

            # idempotency: skip if a lesson with exact lesson_date already exists
            exists_result = await session.execute(
                select(Lesson).where(
                    Lesson.group_id == DEMO_GROUP_ID,
                    Lesson.lesson_date == lesson_dt,
                )
            )
            if exists_result.scalar_one_or_none():
                continue

            lesson = Lesson(
                group_id=DEMO_GROUP_ID,
                teacher_id=TEACHER_ID,
                classroom_id=1,          # assume classroom id=1 exists
                branch_id=None,
                program_id=None,
                day_of_week=_DOW_MAP[weekday],
                time_start=t_start,
                time_end=t_end,
                topic=topic,
                status=LessonStatus.scheduled,
                lesson_date=lesson_dt,
                is_recurring=False,
            )
            session.add(lesson)
            await session.flush()
            lesson_records.append(lesson)
            lessons_created += 1

        # ── 3. attendance ────────────────────────────────────────

        attendance_created = 0
        statuses = [
            AttendanceStatus.present,
            AttendanceStatus.present,
            AttendanceStatus.present,
            AttendanceStatus.absent,
            AttendanceStatus.late,
            AttendanceStatus.excused,
        ]
        notes_map = {
            AttendanceStatus.absent:  "Не пришёл без предупреждения",
            AttendanceStatus.late:    "Опоздал на 10 минут",
            AttendanceStatus.excused: "Уважительная причина: болезнь",
        }

        for lesson in lesson_records:
            for sg in sg_records:
                # idempotency
                exists_result = await session.execute(
                    select(Attendance).where(
                        Attendance.lesson_id == lesson.id,
                        Attendance.student_group_id == sg.id,
                    )
                )
                if exists_result.scalar_one_or_none():
                    continue

                status = random.choice(statuses)
                att = Attendance(
                    lesson_id=lesson.id,
                    student_group_id=sg.id,
                    teacher_id=TEACHER_ID,
                    status=status,
                    note=notes_map.get(status),
                    # lesson_date is nullable in the schema; use the lesson's
                    # stored date when available (always set for newly created
                    # lessons), fall back to now() for legacy rows without it.
                    lesson_date=lesson.lesson_date if lesson.lesson_date is not None else datetime.utcnow(),
                )
                session.add(att)
                attendance_created += 1

        await session.flush()

        # ── 4. invoices ──────────────────────────────────────────

        # due_date = last day of the demo period month
        period_year, period_month = map(int, DEMO_PERIOD.split("-"))
        if period_month == 12:
            due_date = datetime(period_year + 1, 1, 1) - timedelta(days=1)
        else:
            due_date = datetime(period_year, period_month + 1, 1) - timedelta(days=1)

        invoices_created = 0
        invoice_records: list[tuple[StudentGroup, Invoice]] = []

        # 3 buckets: paid / partial / pending (cycle through)
        payment_scenarios = ["paid", "partial", "pending"]

        for idx, sg in enumerate(sg_records):
            # idempotency
            exists_result = await session.execute(
                select(Invoice).where(
                    Invoice.student_group_id == sg.id,
                    Invoice.period == DEMO_PERIOD,
                )
            )
            inv = exists_result.scalar_one_or_none()
            if inv:
                invoice_records.append((sg, inv))
                continue

            scenario = payment_scenarios[idx % len(payment_scenarios)]
            amount = price_per_month

            if scenario == "paid":
                amount_paid = amount
                status = PaymentStatus.paid
            elif scenario == "partial":
                amount_paid = amount // 2
                status = PaymentStatus.partial
            else:
                amount_paid = 0
                status = PaymentStatus.pending

            inv = Invoice(
                group_id=DEMO_GROUP_ID,
                student_group_id=sg.id,
                student_name=sg.student_name,
                amount=amount,
                amount_paid=amount_paid,
                period=DEMO_PERIOD,
                due_date=due_date,
                status=status,
                notes=None,
            )
            session.add(inv)
            await session.flush()
            invoice_records.append((sg, inv))
            invoices_created += 1

        # ── 5. payments ──────────────────────────────────────────

        payments_created = 0
        methods = [PaymentMethod.cash, PaymentMethod.card, PaymentMethod.online]

        for sg, inv in invoice_records:
            if inv.status not in (PaymentStatus.paid, PaymentStatus.partial):
                continue

            # idempotency: check if payment already exists for this invoice
            exists_result = await session.execute(
                select(Payment).where(Payment.invoice_id == inv.id)
            )
            if exists_result.scalars().first():
                continue

            total_paid = int(inv.amount_paid)

            if inv.status == PaymentStatus.paid:
                # 1 or 2 payments that sum to full amount
                if random.random() < 0.5:
                    # single payment
                    pay = Payment(
                        invoice_id=inv.id,
                        student_group_id=sg.id,
                        student_name=sg.student_name,
                        amount=total_paid,
                        method=random.choice(methods),
                        paid_at=now - timedelta(days=random.randint(1, 20)),
                        received_by=admin_id,
                        comment="Оплата за месяц",
                    )
                    session.add(pay)
                    payments_created += 1
                else:
                    # two payments
                    first = total_paid // 2
                    second = total_paid - first
                    for amt, note in [(first, "Первая часть оплаты"), (second, "Вторая часть оплаты")]:
                        pay = Payment(
                            invoice_id=inv.id,
                            student_group_id=sg.id,
                            student_name=sg.student_name,
                            amount=amt,
                            method=random.choice(methods),
                            paid_at=now - timedelta(days=random.randint(1, 20)),
                            received_by=admin_id,
                            comment=note,
                        )
                        session.add(pay)
                        payments_created += 1

            else:  # partial
                pay = Payment(
                    invoice_id=inv.id,
                    student_group_id=sg.id,
                    student_name=sg.student_name,
                    amount=total_paid,
                    method=random.choice(methods),
                    paid_at=now - timedelta(days=random.randint(1, 15)),
                    received_by=admin_id,
                    comment="Частичная оплата",
                )
                session.add(pay)
                payments_created += 1

        await session.commit()

        # ── Summary ──────────────────────────────────────────────
        print("✅  seed_full_demo завершён")
        print(f"   student_groups created : {sg_created}")
        print(f"   lessons created        : {lessons_created}")
        print(f"   attendance created     : {attendance_created}")
        print(f"   invoices created       : {invoices_created}")
        print(f"   payments created       : {payments_created}")


if __name__ == "__main__":
    asyncio.run(seed_full_demo())
