"""APScheduler — фоновые задачи сервера.

Зарегистрированные задачи:
  1. process_notification_queue  — каждые 5 мин: отправляет pending-уведомления
  2. auto_publish_news           — каждые 10 мин: публикует статьи с истёкшим publish_at
  3. mark_overdue_invoices       — каждый день в 01:00: переводит просроченные счета в overdue
  4. remind_tomorrow_lessons     — каждый день в 18:00: ставит напоминания об уроках на завтра
  5. refresh_report_cache        — каждый час: удаляет устаревший кэш отчётов
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


# ──────────────────────────────────────────────────────────────────────
# 1. Обработка очереди уведомлений (каждые 5 минут)
# ──────────────────────────────────────────────────────────────────────
async def process_notification_queue():
    """Находит все pending-уведомления с scheduled_at <= now и отправляет."""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.notification import NotificationQueue, NotificationStatus

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            result = await db.execute(
                select(NotificationQueue).where(
                    and_(
                        NotificationQueue.status == NotificationStatus.pending,
                        NotificationQueue.scheduled_at <= now,
                        NotificationQueue.retry_count < 3,
                    )
                )
            )
            items = result.scalars().all()
            sent = 0
            for item in items:
                try:
                    # В production: вызов SMTP / Telegram / SMS API
                    logger.info(
                        f"[SCHEDULER] Отправка уведомления #{item.id} "
                        f"на {item.recipient_email or item.recipient_phone}"
                    )
                    item.status = NotificationStatus.sent
                    item.sent_at = now
                    sent += 1
                except Exception as e:
                    item.retry_count += 1
                    item.error_message = str(e)
                    if item.retry_count >= 3:
                        item.status = NotificationStatus.failed
            await db.commit()
            if sent:
                logger.info(f"[SCHEDULER] Отправлено уведомлений: {sent}")
        except Exception as e:
            logger.error(f"[SCHEDULER] Ошибка обработки очереди: {e}")


# ──────────────────────────────────────────────────────────────────────
# 2. Авто-публикация запланированных статей (каждые 10 минут)
# ──────────────────────────────────────────────────────────────────────
async def auto_publish_news():
    """
    Публикует статьи у которых:
      status = 'draft' И publish_at <= now
    Меняет статус на 'published'.
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.news import News, NewsStatus

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            result = await db.execute(
                select(News).where(
                    and_(
                        News.status == NewsStatus.draft,
                        News.publish_at <= now,
                        News.publish_at.isnot(None),
                    )
                )
            )
            articles = result.scalars().all()
            published = 0
            for article in articles:
                article.status = NewsStatus.published
                article.published_at = now
                published += 1
            await db.commit()
            if published:
                logger.info(f"[SCHEDULER] Авто-опубликовано статей: {published}")
        except Exception as e:
            logger.error(f"[SCHEDULER] Ошибка авто-публикации: {e}")


# ──────────────────────────────────────────────────────────────────────
# 3. Пометить просроченные счета как overdue (каждый день 01:00)
# ──────────────────────────────────────────────────────────────────────
async def mark_overdue_invoices():
    """
    Переводит счета в статус overdue если:
      due_date < now И status IN (pending, partial)
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.payment import Invoice, PaymentStatus

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            result = await db.execute(
                select(Invoice).where(
                    and_(
                        Invoice.due_date < now,
                        Invoice.status.in_([
                            PaymentStatus.pending,
                            PaymentStatus.partial,
                        ])
                    )
                )
            )
            overdue_count = 0
            for invoice in result.scalars().all():
                invoice.status = PaymentStatus.overdue
                overdue_count += 1
            await db.commit()
            if overdue_count:
                logger.info(f"[SCHEDULER] Помечено просроченных счетов: {overdue_count}")
        except Exception as e:
            logger.error(f"[SCHEDULER] Ошибка пометки overdue: {e}")


# ──────────────────────────────────────────────────────────────────────
# 4. Напоминания о занятиях на завтра (каждый день 18:00)
# ──────────────────────────────────────────────────────────────────────
async def remind_tomorrow_lessons():
    """
    Находит занятия на завтра (по lesson_date или по дню недели)
    и создаёт уведомления для студентов каждой группы.
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.schedule import Lesson, LessonStatus
    from app.models.group import StudentGroup
    from app.models.notification import Notification, NotificationQueue, NotificationStatus, NotificationType, NotificationChannel

    async with AsyncSessionLocal() as db:
        try:
            tomorrow = datetime.utcnow() + timedelta(days=1)
            tomorrow_weekday = tomorrow.strftime("%A").lower()  # monday, tuesday...
            result = await db.execute(
                select(Lesson).where(
                    and_(
                        Lesson.status == LessonStatus.scheduled,
                        Lesson.is_recurring == True,
                        Lesson.day_of_week == tomorrow_weekday,
                    )
                )
            )
            lessons = result.scalars().all()
            queued = 0
            for lesson in lessons:
                students_result = await db.execute(
                    select(StudentGroup).where(
                        and_(StudentGroup.group_id == lesson.group_id,
                             StudentGroup.is_active == True)
                    )
                )
                for student in students_result.scalars().all():
                    if not student.student_email and not student.student_phone:
                        continue
                    notif = Notification(
                        title="Напоминание о занятии",
                        body=(
                            f"Уважаемый(ая) {student.student_name}, напоминаем: "
                            f"завтра занятие в {lesson.time_start}."
                        ),
                        notification_type=NotificationType.schedule_reminder,
                        channel=NotificationChannel.email,
                        recipient_email=student.student_email,
                        recipient_phone=student.student_phone,
                        recipient_name=student.student_name,
                        scheduled_at=datetime.utcnow(),
                        status=NotificationStatus.pending,
                    )
                    db.add(notif)
                    await db.flush()
                    db.add(NotificationQueue(
                        notification_id=notif.id,
                        recipient_email=student.student_email,
                        recipient_phone=student.student_phone,
                        recipient_name=student.student_name,
                        subject=notif.title,
                        message=notif.body,
                        channel=NotificationChannel.email,
                        scheduled_at=datetime.utcnow(),
                        status=NotificationStatus.pending,
                    ))
                    queued += 1
            await db.commit()
            if queued:
                logger.info(f"[SCHEDULER] Поставлено напоминаний о занятиях: {queued}")
        except Exception as e:
            logger.error(f"[SCHEDULER] Ошибка напоминаний: {e}")


# ──────────────────────────────────────────────────────────────────────
# 5. Очистка устаревшего кэша отчётов (каждый час)
# ──────────────────────────────────────────────────────────────────────
async def refresh_report_cache():
    """Удаляет устаревшие записи кэша отчётов."""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import delete
    from app.models.report import ReportCache

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            result = await db.execute(
                delete(ReportCache).where(ReportCache.expires_at < now)
            )
            await db.commit()
            logger.info(f"[SCHEDULER] Очищено устаревших кэшей: {result.rowcount}")
        except Exception as e:
            logger.error(f"[SCHEDULER] Ошибка очистки кэша: {e}")


# ──────────────────────────────────────────────────────────────────────
# Регистрация задач
# ──────────────────────────────────────────────────────────────────────
def setup_scheduler():
    scheduler.add_job(
        process_notification_queue,
        trigger=IntervalTrigger(minutes=5),
        id="process_notifications",
        replace_existing=True,
    )
    scheduler.add_job(
        auto_publish_news,
        trigger=IntervalTrigger(minutes=10),
        id="auto_publish_news",
        replace_existing=True,
    )
    scheduler.add_job(
        mark_overdue_invoices,
        trigger=CronTrigger(hour=1, minute=0),
        id="mark_overdue",
        replace_existing=True,
    )
    scheduler.add_job(
        remind_tomorrow_lessons,
        trigger=CronTrigger(hour=18, minute=0),
        id="lesson_reminders",
        replace_existing=True,
    )
    scheduler.add_job(
        refresh_report_cache,
        trigger=IntervalTrigger(hours=1),
        id="refresh_cache",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[SCHEDULER] Планировщик запущен с 5 задачами")
