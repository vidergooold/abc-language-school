"""Seed script for extended demo data.

Populates: courses, groups, news_categories, news, homeworks,
           enrollments, documents, discounts, notifications, waitlist.

Run with:
    cd backend && python seed_extended_data.py
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.discount import Discount, DiscountReason, DiscountType
from app.models.document import Document, DocumentCategory
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus
from app.models.homework import Homework, HomeworkStatus
from app.models.news import News, NewsCategory, NewsStatus
from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)
from app.models.teacher import Teacher
from app.models.user import User
from app.models.waitlist import WaitlistEntry, WaitlistStatus


async def _get_or_create(
    session, model, lookup: dict, defaults: Optional[dict] = None
):
    result = await session.execute(select(model).filter_by(**lookup))
    instance = result.scalar_one_or_none()
    if instance:
        return instance, False
    payload = {**lookup, **(defaults or {})}
    instance = model(**payload)
    session.add(instance)
    await session.flush()
    return instance, True


async def seed_extended_data() -> None:
    await init_db()

    counts = {
        "courses": 0,
        "groups": 0,
        "news_categories": 0,
        "news": 0,
        "homeworks": 0,
        "enrollments": 0,
        "documents": 0,
        "discounts": 0,
        "notifications": 0,
        "waitlist": 0,
    }

    async with AsyncSessionLocal() as session:

        # ── 1. Courses ──────────────────────────────────────────────────────────
        courses_data = [
            {
                "name": "Английский для школьников",
                "category": CourseCategory.school,
                "level": CourseLevel.beginner,       # A1
                "price_per_month": 4500,
                "duration_months": 9,
                "lessons_per_week": 2,
                "description": "Курс английского языка для школьников начального уровня A1.",
                "language": "Английский",
                "is_active": True,
            },
            {
                "name": "Английский для дошкольников",
                "category": CourseCategory.children,
                "level": CourseLevel.beginner,       # A1
                "price_per_month": 4000,
                "duration_months": 9,
                "lessons_per_week": 2,
                "description": "Курс английского языка для детей дошкольного возраста.",
                "language": "Английский",
                "is_active": True,
            },
            {
                "name": "Разговорный английский",
                "category": CourseCategory.adults,
                "level": CourseLevel.pre_intermediate,  # B1
                "price_per_month": 5000,
                "duration_months": 6,
                "lessons_per_week": 2,
                "description": "Разговорный курс английского языка для взрослых уровня B1.",
                "language": "Английский",
                "is_active": True,
            },
            {
                "name": "Английский интенсив",
                "category": CourseCategory.adults,
                "level": CourseLevel.upper_intermediate,  # B2
                "price_per_month": 6000,
                "duration_months": 3,
                "lessons_per_week": 3,
                "description": "Интенсивный курс английского языка для взрослых уровня B2.",
                "language": "Английский",
                "is_active": True,
            },
        ]

        new_courses: list[Course] = []
        for cd in courses_data:
            name = cd["name"]
            c, created = await _get_or_create(
                session,
                Course,
                {"name": name},
                {k: v for k, v in cd.items() if k != "name"},
            )
            new_courses.append(c)
            if created:
                counts["courses"] += 1

        # ── 2. Groups ───────────────────────────────────────────────────────────
        teacher_lookup = {
            "Белова Александра Анатольевна": None,
            "Данилова Мария Анатольевна": None,
            "Темлякова Анна Михайловна": None,
            "Лукьянова Светлана Ярославовна": None,
        }
        for full_name in list(teacher_lookup.keys()):
            res = await session.execute(
                select(Teacher).where(Teacher.full_name == full_name)
            )
            teacher_lookup[full_name] = res.scalar_one_or_none()
            if teacher_lookup[full_name] is None:
                print(f"  ⚠️  Преподаватель не найден: {full_name} — группа будет создана без преподавателя")

        course_by_name = {c.name: c for c in new_courses}

        groups_spec = [
            (
                "Группа School A1 Morning",
                course_by_name["Английский для школьников"],
                teacher_lookup["Белова Александра Анатольевна"],
            ),
            (
                "Группа Preschool Morning",
                course_by_name["Английский для дошкольников"],
                teacher_lookup["Данилова Мария Анатольевна"],
            ),
            (
                "Группа Adults B1 Evening",
                course_by_name["Разговорный английский"],
                teacher_lookup["Темлякова Анна Михайловна"],
            ),
            (
                "Группа Intensive B2",
                course_by_name["Английский интенсив"],
                teacher_lookup["Лукьянова Светлана Ярославовна"],
            ),
        ]

        new_groups: list[Group] = []
        for gname, gcourse, gteacher in groups_spec:
            g, created = await _get_or_create(
                session,
                Group,
                {"name": gname},
                {
                    "course_id": gcourse.id,
                    "teacher_id": gteacher.id if gteacher else None,
                    "status": GroupStatus.active,
                    "start_date": datetime.utcnow(),
                    "end_date": datetime.utcnow() + timedelta(days=gcourse.duration_months * 30),
                },
            )
            new_groups.append(g)
            if created:
                counts["groups"] += 1

        # ── 3. News categories ──────────────────────────────────────────────────
        categories_spec = [
            {"name": "Новости школы", "slug": "school-news", "color": "#4A90E2"},
            {"name": "Мероприятия",   "slug": "events",      "color": "#7ED321"},
            {"name": "Полезное",      "slug": "useful",       "color": "#F5A623"},
        ]

        new_cats: list[NewsCategory] = []
        for cd in categories_spec:
            cat, created = await _get_or_create(
                session,
                NewsCategory,
                {"slug": cd["slug"]},
                {"name": cd["name"], "color": cd["color"]},
            )
            new_cats.append(cat)
            if created:
                counts["news_categories"] += 1

        cat_school, cat_events, cat_useful = new_cats
        now = datetime.utcnow()

        # ── 4. News ─────────────────────────────────────────────────────────────
        news_spec = [
            # 6 published
            {
                "slug": "new-school-year-2025",
                "title": "Начало нового учебного года в ABC Language School",
                "body": (
                    "Мы рады объявить о начале нового учебного года! "
                    "Записи открыты на все курсы — от дошкольников до взрослых. "
                    "Наши преподаватели, в том числе Белова Александра Анатольевна "
                    "и Данилова Мария Анатольевна, готовы к новому учебному сезону."
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=30),
                "category_id": cat_school.id,
                "author_id": 1,
            },
            {
                "slug": "open-lesson-speaking",
                "title": "Открытый урок по разговорному английскому",
                "body": (
                    "Приглашаем всех желающих на бесплатный открытый урок по разговорному английскому. "
                    "Занятие проведёт Темлякова Анна Михайловна. "
                    "Регистрация обязательна — звоните по телефону школы."
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=20),
                "category_id": cat_events.id,
                "author_id": 1,
            },
            {
                "slug": "tips-learning-at-home",
                "title": "Советы по изучению английского дома",
                "body": (
                    "Наши преподаватели делятся советами, как эффективно заниматься английским языком дома. "
                    "Регулярная практика аудирования, ведение словаря и разговоры с носителями — ключ к успеху. "
                    "Подробнее рассказывает Лукьянова Светлана Ярославовна."
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=15),
                "category_id": cat_useful.id,
                "author_id": 1,
            },
            {
                "slug": "open-day-spring",
                "title": "День открытых дверей — приходите знакомиться!",
                "body": (
                    "Ждём всех на День открытых дверей ABC Language School! "
                    "Вы сможете познакомиться с преподавателями, пройти бесплатное тестирование уровня "
                    "и узнать о всех наших программах. Мероприятие пройдёт в субботу с 10:00 до 14:00."
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=10),
                "category_id": cat_events.id,
                "author_id": 1,
            },
            {
                "slug": "exam-results-2025",
                "title": "Результаты международных экзаменов наших учеников",
                "body": (
                    "Поздравляем наших учеников с успешной сдачей международных экзаменов! "
                    "В этом году 12 студентов успешно прошли IELTS, а 8 — получили сертификаты Cambridge. "
                    "Гордимся нашей командой и преподавателями!"
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=5),
                "category_id": cat_school.id,
                "author_id": 1,
            },
            {
                "slug": "new-adult-groups-2025",
                "title": "Новые группы для взрослых: запись открыта",
                "body": (
                    "ABC Language School открывает набор в новые группы для взрослых! "
                    "Курсы ведут опытные преподаватели Переведенцева Александра Андреевна "
                    "и Позднякова Виктория Сергеевна. Занятия по будням вечером, группы до 8 человек."
                ),
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=2),
                "category_id": cat_school.id,
                "author_id": 1,
            },
            # 2 draft
            {
                "slug": "how-to-choose-level",
                "title": "Как выбрать уровень курса: советы преподавателей",
                "body": (
                    "Многие студенты задают вопрос: как правильно определить свой уровень английского? "
                    "Осинина Светлана Николаевна и Пасикан Ангелина Сергеевна подготовили полезный гид "
                    "по выбору курса для начинающих и продолжающих."
                ),
                "status": NewsStatus.draft,
                "category_id": cat_useful.id,
                "author_id": 1,
            },
            {
                "slug": "summer-intensive-2025",
                "title": "Летняя интенсивная программа 2025",
                "body": (
                    "Готовим специальную летнюю интенсивную программу для всех желающих! "
                    "3 месяца, 3 занятия в неделю — и вы выйдете на новый уровень. "
                    "Преподаватели Рубе Дарья Васильевна и Стафеева Яна Викторовна уже разрабатывают программу."
                ),
                "status": NewsStatus.draft,
                "category_id": cat_events.id,
                "author_id": 1,
            },
            # 2 scheduled (publish_at within next 7 days)
            {
                "slug": "webinar-english-career",
                "title": "Вебинар: английский для карьерного роста",
                "body": (
                    "Планируем провести бесплатный вебинар о том, как английский язык помогает в карьере. "
                    "Ведущая — Федорова Анфиса Вячеславовна. "
                    "Зарегистрируйтесь заранее, количество мест ограничено."
                ),
                "status": NewsStatus.scheduled,
                "publish_at": now + timedelta(days=3),
                "category_id": cat_useful.id,
                "author_id": 1,
            },
            {
                "slug": "student-concert-spring",
                "title": "Праздничный концерт учеников",
                "body": (
                    "Приглашаем всех на ежегодный праздничный концерт наших учеников! "
                    "Дети и взрослые студенты представят мини-спектакли и диалоги на английском языке. "
                    "Вход свободный для родителей и гостей."
                ),
                "status": NewsStatus.scheduled,
                "publish_at": now + timedelta(days=5),
                "category_id": cat_events.id,
                "author_id": 1,
            },
        ]

        for nd in news_spec:
            slug = nd["slug"]
            _, created = await _get_or_create(
                session,
                News,
                {"slug": slug},
                {k: v for k, v in nd.items() if k != "slug"},
            )
            if created:
                counts["news"] += 1

        # ── 5. Homeworks ────────────────────────────────────────────────────────
        res = await session.execute(select(Group).limit(5))
        hw_groups = res.scalars().all()

        res = await session.execute(select(Teacher).limit(5))
        hw_teachers = res.scalars().all()

        if hw_groups and hw_teachers:
            teacher0 = hw_teachers[0]
            homeworks_spec = [
                (
                    "Present Simple: упражнения 1-5",
                    "Выполните упражнения на Present Simple из учебника, стр. 24-25. Составьте 5 предложений о себе.",
                    now + timedelta(days=3),
                    HomeworkStatus.assigned,
                    hw_groups[0 % len(hw_groups)],
                ),
                (
                    "Словарный список Unit 3",
                    "Выучите 20 новых слов из Unit 3. Составьте предложения с каждым словом.",
                    now + timedelta(days=5),
                    HomeworkStatus.assigned,
                    hw_groups[0 % len(hw_groups)],
                ),
                (
                    "Reading comprehension: текст о Лондоне",
                    "Прочитайте текст о Лондоне и ответьте на вопросы. Переведите выделенные абзацы.",
                    now + timedelta(days=7),
                    HomeworkStatus.submitted,
                    hw_groups[1 % len(hw_groups)],
                ),
                (
                    "Подготовка к грамматическому тесту",
                    "Повторите Past Simple и Past Continuous. Решите тест на с. 48 учебника.",
                    now + timedelta(days=4),
                    HomeworkStatus.assigned,
                    hw_groups[1 % len(hw_groups)],
                ),
                (
                    "Диалог на тему «В магазине»",
                    "Составьте диалог из 10 реплик на тему «Покупки в магазине». Подготовьтесь к устному выступлению.",
                    now + timedelta(days=6),
                    HomeworkStatus.completed,
                    hw_groups[2 % len(hw_groups)],
                ),
                (
                    "Present Perfect: 10 предложений",
                    "Составьте 10 предложений с Present Perfect, используя слова из Unit 5.",
                    now + timedelta(days=8),
                    HomeworkStatus.assigned,
                    hw_groups[2 % len(hw_groups)],
                ),
                (
                    "Listening: подкаст BBC Learning English",
                    "Прослушайте подкаст BBC Learning English и заполните пропуски в транскрипте.",
                    now + timedelta(days=10),
                    HomeworkStatus.submitted,
                    hw_groups[3 % len(hw_groups)],
                ),
                (
                    "Эссе: моя любимая книга (100 слов)",
                    "Напишите небольшое эссе о вашей любимой книге (около 100 слов). Используйте описательные прилагательные.",
                    now + timedelta(days=12),
                    HomeworkStatus.assigned,
                    hw_groups[3 % len(hw_groups)],
                ),
                (
                    "Фразовые глаголы: Unit 7",
                    "Выучите 15 фразовых глаголов из Unit 7. Составьте предложения с каждым из них в контексте.",
                    now + timedelta(days=9),
                    HomeworkStatus.completed,
                    hw_groups[4 % len(hw_groups)],
                ),
                (
                    "Условные предложения: типы 1 и 2",
                    "Выполните упражнения на условные предложения 1-го и 2-го типа. Стр. 62-63 учебника.",
                    now + timedelta(days=14),
                    HomeworkStatus.assigned,
                    hw_groups[0 % len(hw_groups)],
                ),
            ]

            for i, (title, desc, due, status, group) in enumerate(homeworks_spec):
                _, created = await _get_or_create(
                    session,
                    Homework,
                    {"title": title, "group_id": group.id},
                    {
                        "description": desc,
                        "due_date": due,
                        "status": status,
                        "teacher_id": teacher0.id,
                        "lesson_date": now - timedelta(days=i + 1),
                    },
                )
                if created:
                    counts["homeworks"] += 1

        # ── 6. Enrollments ──────────────────────────────────────────────────────
        res = await session.execute(select(Course).limit(5))
        enroll_courses = res.scalars().all()

        def _cid(idx: int) -> Optional[int]:
            return enroll_courses[idx].id if len(enroll_courses) > idx else None

        enrollments_spec = [
            {
                "name": "Иванова Анастасия Петровна",
                "phone": "+79139001122",
                "email": "ivanova.anastasia@mail.ru",
                "comment": "Хотим записать дочку 8 лет в группу по английскому",
                "desired_course_id": _cid(0),
                "student_type": "child",
                "age": 8,
                "source": "instagram",
                "status": EnrollmentStatus.pending,
            },
            {
                "name": "Петров Алексей Владимирович",
                "phone": "+79138002233",
                "email": "petrov.alexey@gmail.com",
                "comment": "Хочу улучшить разговорный английский для работы",
                "desired_course_id": _cid(2),
                "student_type": "adult",
                "age": 32,
                "source": "рекомендация",
                "status": EnrollmentStatus.confirmed,
            },
            {
                "name": "Смирнова Екатерина Игоревна",
                "phone": "+79137003344",
                "email": "smirnova.katerina@yandex.ru",
                "comment": "Записываю сына 5 лет в группу дошкольников",
                "desired_course_id": _cid(1),
                "student_type": "child",
                "age": 5,
                "source": "2gis",
                "status": EnrollmentStatus.active,
            },
            {
                "name": "Козлов Дмитрий Николаевич",
                "phone": "+79136004455",
                "email": "kozlov.dmitry@mail.ru",
                "comment": "Готовлюсь к IELTS, нужна интенсивная программа",
                "desired_course_id": _cid(3),
                "student_type": "adult",
                "age": 27,
                "source": "сайт",
                "status": EnrollmentStatus.active,
            },
            {
                "name": "Новикова Ольга Сергеевна",
                "phone": "+79135005566",
                "email": "novikova.olga@yandex.ru",
                "comment": "Интересует группа для взрослых вечером",
                "desired_course_id": _cid(2),
                "student_type": "adult",
                "age": 45,
                "source": "листовка",
                "status": EnrollmentStatus.pending,
            },
            {
                "name": "Орлов Максим Андреевич",
                "phone": "+79134006677",
                "email": "orlov.maxim@gmail.com",
                "comment": "Ребёнок 7 лет, хотим начать с нуля",
                "desired_course_id": _cid(0),
                "student_type": "child",
                "age": 7,
                "source": "отзывы на яндексе",
                "status": EnrollmentStatus.confirmed,
            },
            {
                "name": "Захарова Виктория Павловна",
                "phone": "+79133007788",
                "email": "zakharova.victoria@mail.ru",
                "comment": "Хочу записаться на разговорный клуб",
                "desired_course_id": _cid(2),
                "student_type": "adult",
                "age": 38,
                "source": "instagram",
                "status": EnrollmentStatus.rejected,
                "rejection_reason": "Нет свободных мест в желаемое время",
            },
            {
                "name": "Кузнецов Илья Романович",
                "phone": "+79132008899",
                "email": "kuznetsov.ilya@yandex.ru",
                "comment": "Нужна подготовка к ЕГЭ по английскому",
                "desired_course_id": _cid(0),
                "student_type": "child",
                "age": 16,
                "source": "рекомендация",
                "status": EnrollmentStatus.active,
            },
            {
                "name": "Морозова Татьяна Алексеевна",
                "phone": "+79131009900",
                "email": "morozova.tatyana@gmail.com",
                "comment": "Интересует программа для дошкольников 4 года",
                "desired_course_id": _cid(1),
                "student_type": "child",
                "age": 4,
                "source": "сайт",
                "status": EnrollmentStatus.pending,
            },
            {
                "name": "Лебедев Андрей Сергеевич",
                "phone": "+79130001010",
                "email": "lebedev.andrey@mail.ru",
                "comment": "Хочу освоить деловой английский для командировок",
                "desired_course_id": _cid(3),
                "student_type": "adult",
                "age": 41,
                "source": "коллеги",
                "status": EnrollmentStatus.confirmed,
            },
        ]

        for i, ed in enumerate(enrollments_spec):
            rejection_reason = ed.pop("rejection_reason", None)
            phone = ed["phone"]
            email = ed["email"]
            _, created = await _get_or_create(
                session,
                Enrollment,
                {"phone": phone, "email": email},
                {
                    **{k: v for k, v in ed.items() if k not in ("phone", "email")},
                    "rejection_reason": rejection_reason,
                    "created_at": now - timedelta(days=30 - i),
                },
            )
            if created:
                counts["enrollments"] += 1

        # ── 7. Documents ────────────────────────────────────────────────────────
        res = await session.execute(select(User).limit(5))
        doc_users = res.scalars().all()

        def _uid(idx: int) -> Optional[int]:
            return doc_users[idx].id if len(doc_users) > idx else None

        documents_spec = [
            {
                "title": "Договор об оказании образовательных услуг №001",
                "description": "Договор с родителем на обучение ребёнка в ABC Language School",
                "file_url": "/documents/contract_001.pdf",
                "category": DocumentCategory.contract,
                "user_id": _uid(0),
                "is_active": True,
            },
            {
                "title": "Справка об обучении",
                "description": "Справка, подтверждающая факт обучения в школе для предъявления по месту требования",
                "file_url": "/documents/certificate_study.pdf",
                "category": DocumentCategory.other,
                "user_id": _uid(0),
                "is_active": True,
            },
            {
                "title": "Договор об оказании образовательных услуг №002",
                "description": "Договор со студентом на прохождение курса разговорного английского",
                "file_url": "/documents/contract_002.pdf",
                "category": DocumentCategory.contract,
                "user_id": _uid(1),
                "is_active": True,
            },
            {
                "title": "Политика конфиденциальности",
                "description": "Политика обработки персональных данных ABC Language School",
                "file_url": "/documents/privacy_policy.pdf",
                "category": DocumentCategory.policy,
                "user_id": None,   # общедоступный документ
                "is_active": True,
            },
            {
                "title": "Расписание занятий — весенний семестр 2025",
                "description": "Актуальное расписание занятий для всех групп на весенний семестр",
                "file_url": "/documents/schedule_spring_2025.pdf",
                "category": DocumentCategory.schedule,
                "user_id": None,   # общедоступный документ
                "is_active": True,
            },
        ]

        for dd in documents_spec:
            title = dd["title"]
            _, created = await _get_or_create(
                session,
                Document,
                {"title": title},
                {k: v for k, v in dd.items() if k != "title"},
            )
            if created:
                counts["documents"] += 1

        # ── 8. Discounts ────────────────────────────────────────────────────────
        res = await session.execute(select(Group).limit(5))
        discount_groups = res.scalars().all()

        def _gid(idx: int) -> Optional[int]:
            return discount_groups[idx].id if len(discount_groups) > idx else None

        discounts_spec = [
            {
                "promo_code": "FAMILY15",
                "description": "Скидка для многодетных семей",
                "reason": DiscountReason.social,
                "discount_type": DiscountType.percentage,
                "value": 15,
                "group_id": _gid(0),
                "valid_from": now,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
            {
                "promo_code": "YEAR10",
                "description": "Скидка при оплате за год",
                "reason": DiscountReason.early_payment,
                "discount_type": DiscountType.percentage,
                "value": 10,
                "group_id": None,
                "valid_from": now,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
            {
                "promo_code": "CORP20",
                "description": "Скидка для сотрудников партнёров",
                "reason": DiscountReason.corporate,
                "discount_type": DiscountType.percentage,
                "value": 20,
                "group_id": _gid(1),
                "valid_from": now,
                "valid_until": now + timedelta(days=180),
                "is_active": True,
            },
            {
                "promo_code": "SIBLING10",
                "description": "Скидка за второго ребёнка",
                "reason": DiscountReason.sibling,
                "discount_type": DiscountType.percentage,
                "value": 10,
                "group_id": _gid(2),
                "valid_from": now,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
            {
                "promo_code": "LOYAL10",
                "description": "Скидка постоянного ученика (более 1 года)",
                "reason": DiscountReason.loyalty,
                "discount_type": DiscountType.percentage,
                "value": 10,
                "group_id": None,
                "valid_from": now,
                "valid_until": now + timedelta(days=365),
                "is_active": True,
            },
        ]

        for dd in discounts_spec:
            promo_code = dd["promo_code"]
            _, created = await _get_or_create(
                session,
                Discount,
                {"promo_code": promo_code},
                {k: v for k, v in dd.items() if k != "promo_code"},
            )
            if created:
                counts["discounts"] += 1

        # ── 9. Notifications ────────────────────────────────────────────────────
        res = await session.execute(select(User).limit(4))
        notif_users = res.scalars().all()

        def _nuser(idx: int) -> tuple[str, str]:
            """Return (full_name, email) for notification recipient."""
            if len(notif_users) > idx:
                u = notif_users[idx]
                return u.full_name or "Студент", u.email or f"student{idx}@example.com"
            return "Студент", f"student{idx}@example.com"

        n0_name, n0_email = _nuser(0)
        n1_name, n1_email = _nuser(1)
        n2_name, n2_email = _nuser(2)
        n3_name, n3_email = _nuser(3)

        notifications_spec = [
            {
                "title": "Напоминание об оплате за май",
                "body": (
                    "Уважаемый студент, напоминаем, что оплата за май должна быть произведена до 5-го числа. "
                    "Пожалуйста, оплатите своевременно во избежание приостановки занятий."
                ),
                "notification_type": NotificationType.payment_reminder,
                "channel": NotificationChannel.email,
                "recipient_name": n0_name,
                "recipient_email": n0_email,
                "status": NotificationStatus.sent,
                "sent_at": now - timedelta(days=5),
                "created_by": 1,
            },
            {
                "title": "Изменение расписания: перенос занятия в среду",
                "body": (
                    "Информируем вас о переносе занятия в среду 10:00 на пятницу 10:00 в связи с праздничным днём. "
                    "Преподаватель Белова Александра Анатольевна ждёт вас в пятницу."
                ),
                "notification_type": NotificationType.schedule_reminder,
                "channel": NotificationChannel.email,
                "recipient_name": n1_name,
                "recipient_email": n1_email,
                "status": NotificationStatus.sent,
                "sent_at": now - timedelta(days=3),
                "created_by": 1,
            },
            {
                "title": "Подтверждение записи на курс «Разговорный английский»",
                "body": (
                    "Ваша заявка на курс «Разговорный английский» подтверждена. "
                    "Первое занятие состоится в понедельник в 18:30. "
                    "Преподаватель — Темлякова Анна Михайловна. Ждём вас!"
                ),
                "notification_type": NotificationType.enrollment_confirm,
                "channel": NotificationChannel.email,
                "recipient_name": n2_name,
                "recipient_email": n2_email,
                "status": NotificationStatus.sent,
                "sent_at": now - timedelta(days=1),
                "created_by": 1,
            },
            {
                "title": "Новость: День открытых дверей ABC Language School",
                "body": (
                    "Приглашаем вас на День открытых дверей в эту субботу с 10:00 до 14:00! "
                    "Знакомьтесь с преподавателями, проходите бесплатное тестирование уровня "
                    "и узнавайте о наших программах."
                ),
                "notification_type": NotificationType.news_published,
                "channel": NotificationChannel.internal,
                "recipient_name": n3_name,
                "recipient_email": n3_email,
                "status": NotificationStatus.pending,
                "created_by": 1,
            },
            {
                "title": "Напоминание об оплате за июнь",
                "body": (
                    "Уважаемый студент, напоминаем о предстоящей оплате за июнь до 5-го числа. "
                    "В случае вопросов обращайтесь к администратору."
                ),
                "notification_type": NotificationType.payment_reminder,
                "channel": NotificationChannel.email,
                "recipient_name": n0_name,
                "recipient_email": n0_email,
                "status": NotificationStatus.pending,
                "scheduled_at": now + timedelta(days=2),
                "created_by": 1,
            },
        ]

        for nd in notifications_spec:
            title = nd["title"]
            recipient_email = nd.get("recipient_email")
            _, created = await _get_or_create(
                session,
                Notification,
                {"title": title, "recipient_email": recipient_email},
                {k: v for k, v in nd.items() if k not in ("title", "recipient_email")},
            )
            if created:
                counts["notifications"] += 1

        # ── 10. Waitlist ────────────────────────────────────────────────────────
        res = await session.execute(select(Course).limit(5))
        wl_courses = res.scalars().all()

        def _wcid(idx: int) -> Optional[Course]:
            return wl_courses[idx % len(wl_courses)] if wl_courses else None

        waitlist_spec = [
            {
                "student_name": "Соколова Марина Дмитриевна",
                "student_phone": "+79139110011",
                "student_email": "sokolova.marina@mail.ru",
                "course": _wcid(0),
                "student_type": "adult",
                "comment": "Жду открытия новой группы по разговорному английскому вечером",
                "position": 1,
                "status": WaitlistStatus.waiting,
                "created_at": now - timedelta(days=45),
            },
            {
                "student_name": "Попов Артём Викторович",
                "student_phone": "+79138220022",
                "student_email": "popov.artem@gmail.com",
                "course": _wcid(1),
                "student_type": "child",
                "comment": "Записываю сына 9 лет, жду освобождения места в группе",
                "position": 2,
                "status": WaitlistStatus.waiting,
                "created_at": now - timedelta(days=40),
            },
            {
                "student_name": "Волкова Юлия Александровна",
                "student_phone": "+79137330033",
                "student_email": "volkova.yulia@yandex.ru",
                "course": _wcid(2),
                "student_type": "adult",
                "comment": "Интересует интенсивный курс, готова к любому времени занятий",
                "position": 1,
                "status": WaitlistStatus.notified,
                "created_at": now - timedelta(days=30),
            },
            {
                "student_name": "Зайцев Николай Петрович",
                "student_phone": "+79136440044",
                "student_email": "zaitsev.nikolay@mail.ru",
                "course": _wcid(3),
                "student_type": "adult",
                "comment": "Хочу в утреннюю группу для взрослых",
                "position": 3,
                "status": WaitlistStatus.waiting,
                "created_at": now - timedelta(days=25),
            },
            {
                "student_name": "Белова Ксения Михайловна",
                "student_phone": "+79135550055",
                "student_email": "belova.ksenia@gmail.com",
                "course": _wcid(4),
                "student_type": "child",
                "comment": "Дочь 4 года, ждём место в дошкольной группе",
                "position": 1,
                "status": WaitlistStatus.enrolled,
                "created_at": now - timedelta(days=55),
            },
        ]

        for wd in waitlist_spec:
            course = wd.pop("course")
            if not course:
                continue
            student_email = wd["student_email"]
            _, created = await _get_or_create(
                session,
                WaitlistEntry,
                {"student_email": student_email, "course_id": course.id},
                {k: v for k, v in wd.items() if k != "student_email"},
            )
            if created:
                counts["waitlist"] += 1

        await session.commit()

    print("\n✅ Расширенные демо-данные успешно загружены!")
    print("─" * 40)
    for table, count in counts.items():
        print(f"  {table:20s}: +{count} строк")
    print("─" * 40)


if __name__ == "__main__":
    asyncio.run(seed_extended_data())
