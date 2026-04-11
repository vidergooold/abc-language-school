"""APScheduler — фоновые задачи сервера.

Зарегистрированные задачи:
  1. process_notification_queue  — каждые 5 мин: отправляет pending-уведомления
  2. auto_publish_news           — каждые 10 мин: публикует статьи с истёкшим publish_at
  3. mark_overdue_invoices       — каждый день в 01:00: переводит просроченные счета в overdue
  4. remind_tomorrow_lessons     — каждый день в 18:00: ставит напоминания об уроках на завтра
  5. refresh_report_cache        — каждый час: удаляет устаревший кэш отчётов
  6. expire_stale_enrollments    — каждый день в 02:00: отменяет pending-заявки старше 7 дней
  7. send_overdue_invoice_reminders — каждый день в 10:00: уведомляет о просроченных счетах
────────────────────────────────────────────────────────────────────────
Bug fixes (по сравнению с предыдущей версией):
  - auto_publish_news: ошибочно проверялся status==draft вместо status==scheduled
  - auto_publish_news: не записывался переход в NewsStatusHistory
  - setup_scheduler: добавлены misfire_grace_time=60 и max_instances=1
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


# ───────────────────────────────────────────────────────────────────────
# 1. Обработка очереди уведомлений (каждые 5 минут)
# ───────────────────────────────────────────────────────────────────────
async def process_notification_queue():
    """Находит все pending-уведомления с scheduled_at <= now и отправляет.

    retry_count < 3: неудачная отправка увеличивает счётчик.
    После 3 попыток статус = failed.
    """
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
                    # production: здесь SMTP / Telegram / SMS API
                    logger.info(
                        f"[NOTIF] Отправка #{item.id} → "
                        f"{item.recipient_email or item.recipient_phone}"
                    )
                    item.status = NotificationStatus.sent
                    item.sent_at = now
                    sent += 1
                except Exception as send_err:
                    item.retry_count += 1
                    item.error_message = str(send_err)
                    if item.retry_count >= 3:
                        item.status = NotificationStatus.failed
                        logger.warning(f"[NOTIF] Уведомление #{item.id} failed после 3 попыток")
            await db.commit()
            if sent:
                logger.info(f"[NOTIF] Отправлено: {sent}")
        except Exception as e:
            logger.error(f"[NOTIF] Ошибка очереди: {e}")


# ───────────────────────────────────────────────────────────────────────
# 2. Авто-публикация запланированных статей (каждые 10 минут)
# ───────────────────────────────────────────────────────────────────────
async def auto_publish_news():
    """Публикует статьи, у которых status = 'scheduled' И publish_at <= now.

    FIX: в предыдущей версии ошибочно проверяли status==draft.
    FIX: теперь записывает переход в NewsStatusHistory.
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.news import News, NewsStatus, NewsStatusHistory

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            result = await db.execute(
                select(News).where(
                    and_(
                        # ИСПРАВЛЕНО: было draft — нужно scheduled
                        News.status == NewsStatus.scheduled,
                        News.publish_at <= now,
                        News.publish_at.isnot(None),
                    )
                )
            )
            articles = result.scalars().all()
            published = 0
            for article in articles:
                old_status = article.status
                article.status = NewsStatus.published
                article.published_at = now
                # ИСПРАВЛЕНО: запись в журнал теперь есть
                db.add(NewsStatusHistory(
                    news_id=article.id,
                    from_status=old_status,
                    to_status=NewsStatus.published,
                    changed_by=None,  # системный переход
                    comment=f"Автопубликация по publish_at={article.publish_at.isoformat()}",
                ))
                published += 1
            await db.commit()
            if published:
                logger.info(f"[NEWS] Авто-опубликовано: {published}")
        except Exception as e:
            logger.error(f"[NEWS] Ошибка авто-публикации: {e}")


# ───────────────────────────────────────────────────────────────────────
# 3. Пометить просроченные счета как overdue (каждый день 01:00)
# ───────────────────────────────────────────────────────────────────────
async def mark_overdue_invoices():
    """due_date < now И status в (pending, partial) → overdue."""
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
            count = 0
            for invoice in result.scalars().all():
                invoice.status = PaymentStatus.overdue
                count += 1
            await db.commit()
            if count:
                logger.info(f"[INVOICE] Помечено overdue: {count}")
        except Exception as e:
            logger.error(f"[INVOICE] Ошибка пометки overdue: {e}")


# ───────────────────────────────────────────────────────────────────────
# 4. Напоминания о занятиях на завтра (каждый день 18:00)
# ───────────────────────────────────────────────────────────────────────
async def remind_tomorrow_lessons():
    """Находит повторяющиеся занятия на завтра и добавляет
    уведомления для всех активных студентов каждой группы."""
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.schedule import Lesson, LessonStatus
    from app.models.group import StudentGroup
    from app.models.notification import (
        Notification, NotificationQueue,
        NotificationStatus, NotificationType, NotificationChannel,
    )

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
                        and_(
                            StudentGroup.group_id == lesson.group_id,
                            StudentGroup.is_active == True,
                        )
                    )
                )
                for student in students_result.scalars().all():
                    if not student.student_email and not student.student_phone:
                        continue
                    notif = Notification(
                        title="Напоминание о занятии",
                        body=(
                            f"Уважаемый(ая) {student.student_name}, "
                            f"напоминаем: завтра занятие в {lesson.time_start}."
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
                logger.info(f"[SCHEDULE] Напоминаний поставлено: {queued}")
        except Exception as e:
            logger.error(f"[SCHEDULE] Ошибка напоминаний: {e}")


# ───────────────────────────────────────────────────────────────────────
# 5. Очистка устаревшего кэша отчётов (каждый час)
# ───────────────────────────────────────────────────────────────────────
async def refresh_report_cache():
    """Удаляет устаревшие записи кэша отчётов (expires_at < now)."""
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
            logger.info(f"[CACHE] Очищено: {result.rowcount}")
        except Exception as e:
            logger.error(f"[CACHE] Ошибка очистки: {e}")


# ───────────────────────────────────────────────────────────────────────
# 6. [НОВАЯ] Авто-отмена зависших заявок (каждый день 02:00)
# ───────────────────────────────────────────────────────────────────────
async def expire_stale_enrollments():
    """Автоматически отменяет заявки, на которые не отреагировали за 7 дней.

    Логика:
      - Заявки со статусом pending и created_at < 7 дней назад → cancelled
      - Заявки со статусом awaiting_payment и invoice overdue и
        assigned_at < 14 дней назад → cancelled
      - Для каждой отменённой заявки запись в EnrollmentStatusHistory
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_
    from app.models.enrollment import (
        Enrollment, EnrollmentStatus, EnrollmentStatusHistory,
    )
    from app.models.payment import Invoice, PaymentStatus

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            cancelled = 0

            # ─ 2.1 pending > 7 дней ─────────────────────────────────────────────
            cutoff_pending = now - timedelta(days=7)
            res = await db.execute(
                select(Enrollment).where(
                    and_(
                        Enrollment.status == EnrollmentStatus.pending,
                        Enrollment.created_at < cutoff_pending,
                    )
                )
            )
            for enr in res.scalars().all():
                db.add(EnrollmentStatusHistory(
                    enrollment_id=enr.id,
                    from_status=enr.status,
                    to_status=EnrollmentStatus.cancelled,
                    changed_by=None,
                    comment="Автоотмена: заявка без ответа более 7 дней",
                ))
                enr.status = EnrollmentStatus.cancelled
                cancelled += 1

            # ─ 2.2 awaiting_payment > 14 дней + invoice overdue ────────────────
            cutoff_awaiting = now - timedelta(days=14)
            res2 = await db.execute(
                select(Enrollment).where(
                    and_(
                        Enrollment.status == EnrollmentStatus.awaiting_payment,
                        Enrollment.assigned_at < cutoff_awaiting,
                    )
                )
            )
            for enr in res2.scalars().all():
                # Дополнительно проверяем, что счёт просрочен
                if enr.invoice_id:
                    inv_res = await db.execute(
                        select(Invoice).where(Invoice.id == enr.invoice_id)
                    )
                    inv = inv_res.scalar_one_or_none()
                    if inv and inv.status != PaymentStatus.overdue:
                        continue  # счёт ещё активен — не отменяем
                db.add(EnrollmentStatusHistory(
                    enrollment_id=enr.id,
                    from_status=enr.status,
                    to_status=EnrollmentStatus.cancelled,
                    changed_by=None,
                    comment="Автоотмена: оплата не поступила за 14 дней",
                ))
                enr.status = EnrollmentStatus.cancelled
                cancelled += 1

            await db.commit()
            if cancelled:
                logger.info(f"[ENROLL] Автоотменено заявок: {cancelled}")
        except Exception as e:
            logger.error(f"[ENROLL] Ошибка автоотмены: {e}")


# ───────────────────────────────────────────────────────────────────────
# 7. [НОВАЯ] Рассылка напоминаний о просроченных счетах (каждый день 10:00)
# ───────────────────────────────────────────────────────────────────────
async def send_overdue_invoice_reminders():
    """Для каждого overdue-счёта создаёт уведомление в очередь.

    Логика:
      - Invoice.status == overdue
      - Дата просрочки <= сегодня (т.е. уже зафиксирована как overdue)
      - Не отправляем, если за последние 24 часа уже было уведомление об этом счёте
    """
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, and_, exists
    from app.models.payment import Invoice, PaymentStatus
    from app.models.notification import (
        NotificationQueue, NotificationStatus, NotificationChannel,
    )

    async with AsyncSessionLocal() as db:
        try:
            now = datetime.utcnow()
            since_24h = now - timedelta(hours=24)

            # Находим overdue-счета без недавнего уведомления
            already_notified_subq = (
                select(NotificationQueue.id)
                .where(
                    and_(
                        NotificationQueue.subject.contains("Счёт #"),
                        NotificationQueue.created_at >= since_24h,
                    )
                )
                .correlate(Invoice)
            )
            inv_result = await db.execute(
                select(Invoice).where(
                    Invoice.status == PaymentStatus.overdue
                )
            )
            invoices = inv_result.scalars().all()
            queued = 0
            for invoice in invoices:
                # Проверяем: есть ли связанная StudentGroup с email или телефоном
                if not invoice.student_group:
                    continue
                sg = invoice.student_group
                if not sg.student_email and not sg.student_phone:
                    continue

                # Проверяем: не отправляли в последние 24 часа
                recent = await db.execute(
                    select(NotificationQueue).where(
                        and_(
                            NotificationQueue.recipient_email == sg.student_email,
                            NotificationQueue.subject.contains(f"Счёт #{invoice.id}"),
                            NotificationQueue.created_at >= since_24h,
                        )
                    ).limit(1)
                )
                if recent.scalar_one_or_none():
                    continue  # уже отправляли сегодня

                msg = (
                    f"Уважаемый(ая) {sg.student_name}, "
                    f"напоминаем о задолженности. "
                    f"Счёт #{invoice.id} на сумму {invoice.amount} руб. "
                    f"Срок оплаты был: {invoice.due_date.strftime('%d.%m.%Y')}."
                )
                db.add(NotificationQueue(
                    recipient_email=sg.student_email,
                    recipient_phone=sg.student_phone,
                    recipient_name=sg.student_name,
                    subject=f"Счёт #{invoice.id}: задолженность по оплате",
                    message=msg,
                    channel=NotificationChannel.email,
                    scheduled_at=now,
                    status=NotificationStatus.pending,
                ))
                queued += 1
            await db.commit()
            if queued:
                logger.info(f"[INVOICE] Напоминаний о долгах поставлено: {queued}")
        except Exception as e:
            logger.error(f"[INVOICE] Ошибка напоминаний о долгах: {e}")


# ═══════════════════════════════════════════════════════════════════════
# РЕГИСТРАЦИЯ ЗАДАЧ
# ═══════════════════════════════════════════════════════════════════════
def setup_scheduler():
    """Register all jobs and start the scheduler.

    misfire_grace_time=60 : если сервер был до 60с недоступен, задача всё равно запустится.
    max_instances=1    : защита от параллельного запуска одной и той же задачи.
    """
    # 1. Очередь уведомлений
    scheduler.add_job(
        process_notification_queue,
        trigger=IntervalTrigger(minutes=5),
        id="process_notifications",
        replace_existing=True,
        misfire_grace_time=60,
        max_instances=1,
    )
    # 2. Авто-публикация статей
    scheduler.add_job(
        auto_publish_news,
        trigger=IntervalTrigger(minutes=10),
        id="auto_publish_news",
        replace_existing=True,
        misfire_grace_time=60,
        max_instances=1,
    )
    # 3. overdue-счета
    scheduler.add_job(
        mark_overdue_invoices,
        trigger=CronTrigger(hour=1, minute=0),
        id="mark_overdue",
        replace_existing=True,
        misfire_grace_time=300,
        max_instances=1,
    )
    # 4. Напоминания о занятиях
    scheduler.add_job(
        remind_tomorrow_lessons,
        trigger=CronTrigger(hour=18, minute=0),
        id="lesson_reminders",
        replace_existing=True,
        misfire_grace_time=300,
        max_instances=1,
    )
    # 5. Очистка кэша
    scheduler.add_job(
        refresh_report_cache,
        trigger=IntervalTrigger(hours=1),
        id="refresh_cache",
        replace_existing=True,
        misfire_grace_time=120,
        max_instances=1,
    )
    # 6. Автоотмена зависших заявок
    scheduler.add_job(
        expire_stale_enrollments,
        trigger=CronTrigger(hour=2, minute=0),
        id="expire_enrollments",
        replace_existing=True,
        misfire_grace_time=300,
        max_instances=1,
    )
    # 7. Напоминания о просроченных счетах
    scheduler.add_job(
        send_overdue_invoice_reminders,
        trigger=CronTrigger(hour=10, minute=0),
        id="overdue_reminders",
        replace_existing=True,
        misfire_grace_time=300,
        max_instances=1,
    )
    scheduler.start()
    logger.info("[SCHEDULER] Запущен с 7 задачами")
