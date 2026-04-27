"""
seed_extended_data.py
---------------------
Seeds extended demo data for the ABC Language School application.

Tables populated:
  courses, groups, news_categories, news, homeworks, enrollments,
  documents, discounts, notifications, waitlist

Run from the backend/ directory:
    cd backend
    python seed_extended_data.py

Idempotent: skips rows that already exist (checked by unique field).
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import (
    Course, CourseCategory, CourseLevel,
    Group, GroupStatus,
)
from app.models.teacher import Teacher
from app.models.news import News, NewsCategory, NewsStatus
from app.models.homework import Homework, HomeworkStatus
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.document import Document, DocumentCategory
from app.models.discount import Discount, DiscountType, DiscountReason
from app.models.notification import (
    Notification, NotificationType, NotificationChannel, NotificationStatus,
)
from app.models.waitlist import WaitlistEntry, WaitlistStatus
from app.models.schedule import Lesson
from app.models.user import User


# ─────────────────────────── helpers ─────────────────────────────

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


# ──────────────────────── main seeder ────────────────────────────

async def seed_extended_data() -> None:
    await init_db()

    counts: dict[str, int] = {}

    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()

        # ── 0. Fetch reference data ───────────────────────────────

        # Teachers by name
        teacher_names = {
            "Белова Александра Анатольевна": None,
            "Данилова Мария Анатольевна": None,
            "Темлякова Анна Михайловна": None,
            "Лукьянова Светлана Ярославовна": None,
        }
        for name in list(teacher_names.keys()):
            res = await session.execute(
                select(Teacher).where(Teacher.full_name == name)
            )
            teacher_names[name] = res.scalar_one_or_none()

        # Fetch all teacher ids for homework seeding
        all_teachers_res = await session.execute(select(Teacher).limit(10))
        all_teachers = all_teachers_res.scalars().all()

        # Admin user id=1
        admin_res = await session.execute(select(User).where(User.id == 1))
        admin = admin_res.scalar_one_or_none()
        admin_id = admin.id if admin else 1

        # Existing users ids 1-4 for notifications
        users_res = await session.execute(
            select(User).where(User.id.in_([1, 2, 3, 4]))
        )
        users = users_res.scalars().all()

        # ── 1. Courses ────────────────────────────────────────────

        course_data = [
            {
                "name": "Английский для школьников",
                "category": CourseCategory.school,
                "level": CourseLevel.beginner,
                "price_per_month": 4500,
                "duration_months": 9,
                "lessons_per_week": 2,
                "description": "Курс английского языка для школьников 5-11 классов.",
            },
            {
                "name": "Английский для дошкольников",
                "category": CourseCategory.children,
                "level": CourseLevel.beginner,
                "price_per_month": 4000,
                "duration_months": 9,
                "lessons_per_week": 2,
                "description": "Английский в игровой форме для детей 4-6 лет.",
            },
            {
                "name": "Разговорный английский",
                "category": CourseCategory.adults,
                "level": CourseLevel.intermediate,
                "price_per_month": 5000,
                "duration_months": 6,
                "lessons_per_week": 2,
                "description": "Развитие разговорных навыков для взрослых уровня B1.",
            },
            {
                "name": "Английский интенсив",
                "category": CourseCategory.adults,
                "level": CourseLevel.upper_intermediate,
                "price_per_month": 6000,
                "duration_months": 3,
                "lessons_per_week": 3,
                "description": "Интенсивный курс для взрослых уровня B2.",
            },
        ]

        courses_created = 0
        new_courses: list[Course] = []

        for cd in course_data:
            course, created = await _get_or_create(
                session,
                Course,
                {"name": cd["name"]},
                {
                    "category": cd["category"],
                    "level": cd["level"],
                    "price_per_month": cd["price_per_month"],
                    "duration_months": cd["duration_months"],
                    "lessons_per_week": cd["lessons_per_week"],
                    "description": cd["description"],
                    "is_active": True,
                },
            )
            new_courses.append(course)
            if created:
                courses_created += 1

        counts["courses"] = courses_created

        # ── 2. Groups ─────────────────────────────────────────────

        group_data = [
            {
                "name": "Группа School A1 Morning",
                "course_name": "Английский для школьников",
                "teacher_name": "Белова Александра Анатольевна",
            },
            {
                "name": "Группа Preschool Morning",
                "course_name": "Английский для дошкольников",
                "teacher_name": "Данилова Мария Анатольевна",
            },
            {
                "name": "Группа Adults B1 Evening",
                "course_name": "Разговорный английский",
                "teacher_name": "Темлякова Анна Михайловна",
            },
            {
                "name": "Группа Intensive B2",
                "course_name": "Английский интенсив",
                "teacher_name": "Лукьянова Светлана Ярославовна",
            },
        ]

        # Map course name → Course object
        course_map: dict[str, Course] = {c.name: c for c in new_courses}

        groups_created = 0
        new_groups: list[Group] = []

        for gd in group_data:
            course_obj = course_map.get(gd["course_name"])
            teacher_obj = teacher_names.get(gd["teacher_name"])
            teacher_id = teacher_obj.id if teacher_obj else None

            group, created = await _get_or_create(
                session,
                Group,
                {"name": gd["name"]},
                {
                    "course_id": course_obj.id if course_obj else None,
                    "teacher_id": teacher_id,
                    "status": GroupStatus.active,
                    "start_date": now,
                },
            )
            new_groups.append(group)
            if created:
                groups_created += 1

        counts["groups"] = groups_created

        # ── 3. News categories ────────────────────────────────────

        category_data = [
            {"name": "Новости школы", "slug": "school-news", "color": "#3B82F6"},
            {"name": "Мероприятия", "slug": "events", "color": "#10B981"},
            {"name": "Полезное", "slug": "useful", "color": "#F59E0B"},
        ]

        cats_created = 0
        news_cats: list[NewsCategory] = []

        for catd in category_data:
            cat, created = await _get_or_create(
                session,
                NewsCategory,
                {"slug": catd["slug"]},
                {"name": catd["name"], "color": catd["color"]},
            )
            news_cats.append(cat)
            if created:
                cats_created += 1

        counts["news_categories"] = cats_created

        # Assign categories by index
        cat_school = news_cats[0]
        cat_events = news_cats[1]
        cat_useful = news_cats[2]

        # ── 4. News ───────────────────────────────────────────────

        news_data = [
            # 6 published
            {
                "title": "Новый учебный год в ABC Language School",
                "body": (
                    "Мы рады объявить о начале нового учебного года! "
                    "Запись в группы уже открыта. "
                    "Приходите знакомиться и получайте специальные условия при ранней записи."
                ),
                "category": cat_school,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=30),
                "slug": "new-school-year-2025",
            },
            {
                "title": "Преподаватель Белова Александра — победитель конкурса педагогов",
                "body": (
                    "Поздравляем Белову Александру Анатольевну с победой в городском конкурсе "
                    "«Лучший преподаватель иностранного языка»! "
                    "Этот успех отражает высокий профессионализм всей нашей команды."
                ),
                "category": cat_school,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=20),
                "slug": "belova-teacher-award-2025",
            },
            {
                "title": "Мастер-класс по разговорному английскому",
                "body": (
                    "Темлякова Анна Михайловна проводит открытый мастер-класс "
                    "по разговорному английскому языку. "
                    "Мероприятие состоится 15 мая, вход свободный."
                ),
                "category": cat_events,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=15),
                "slug": "speaking-masterclass-may-2025",
            },
            {
                "title": "Советы по запоминанию английских слов",
                "body": (
                    "Данилова Мария Анатольевна делится эффективными техниками "
                    "запоминания иностранной лексики. "
                    "Используйте карточки, ассоциации и регулярное повторение для лучшего результата."
                ),
                "category": cat_useful,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=10),
                "slug": "vocabulary-tips-2025",
            },
            {
                "title": "Летний интенсив для взрослых — запись открыта",
                "body": (
                    "Объявляем набор на летний интенсивный курс английского языка. "
                    "Программа рассчитана на уровень B2 и выше. "
                    "Занятия ведёт Лукьянова Светлана Ярославовна."
                ),
                "category": cat_school,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=7),
                "slug": "summer-intensive-adults-2025",
            },
            {
                "title": "День открытых дверей в ABC Language School",
                "body": (
                    "Приглашаем всех желающих на день открытых дверей! "
                    "Вы познакомитесь с нашими преподавателями, узнаете о программах и пройдёте "
                    "бесплатное тестирование уровня."
                ),
                "category": cat_events,
                "status": NewsStatus.published,
                "published_at": now - timedelta(days=3),
                "slug": "open-day-2025",
            },
            # 2 draft
            {
                "title": "Обновление учебной программы — что нового",
                "body": (
                    "В следующем учебном году мы обновляем программы для всех уровней. "
                    "Особое внимание уделено разговорной практике и деловому английскому."
                ),
                "category": cat_school,
                "status": NewsStatus.draft,
                "published_at": None,
                "slug": "curriculum-update-draft-2025",
            },
            {
                "title": "Фотоотчёт: выпускной вечер 2024",
                "body": (
                    "Наши выпускники отметили окончание курса! "
                    "Смотрите фотографии и тёплые отзывы студентов."
                ),
                "category": cat_events,
                "status": NewsStatus.draft,
                "published_at": None,
                "slug": "graduation-photo-2024-draft",
            },
            # 2 scheduled
            {
                "title": "Скидки при записи на курс в июне",
                "body": (
                    "С 1 по 30 июня действуют специальные скидки на все курсы. "
                    "Успейте записаться и получить выгодные условия обучения!"
                ),
                "category": cat_school,
                "status": NewsStatus.scheduled,
                "publish_at": now + timedelta(days=3),
                "published_at": None,
                "slug": "june-discount-scheduled-2025",
            },
            {
                "title": "Конкурс «Лучший ученик месяца» — итоги мая",
                "body": (
                    "Подводим итоги конкурса «Лучший ученик месяца»! "
                    "Победители получат памятные призы и дипломы."
                ),
                "category": cat_events,
                "status": NewsStatus.scheduled,
                "publish_at": now + timedelta(days=5),
                "published_at": None,
                "slug": "best-student-may-2025-scheduled",
            },
        ]

        news_created = 0
        for nd in news_data:
            news, created = await _get_or_create(
                session,
                News,
                {"slug": nd["slug"]},
                {
                    "title": nd["title"],
                    "body": nd["body"],
                    "category_id": nd["category"].id,
                    "status": nd["status"],
                    "author_id": admin_id,
                    "published_at": nd.get("published_at"),
                    "publish_at": nd.get("publish_at"),
                },
            )
            if created:
                news_created += 1

        counts["news"] = news_created

        # ── 5. Homeworks ──────────────────────────────────────────

        # Fetch existing lessons to link homeworks
        lessons_res = await session.execute(
            select(Lesson).order_by(Lesson.id).limit(20)
        )
        lessons = lessons_res.scalars().all()

        # Fetch existing groups (all) for fallback
        groups_res = await session.execute(select(Group).order_by(Group.id).limit(10))
        existing_groups = groups_res.scalars().all()

        # Build list of (group_id, teacher_id) from lessons or groups
        def _lesson_group_teacher(idx: int):
            if lessons:
                lesson = lessons[idx % len(lessons)]
                return lesson.group_id, lesson.teacher_id
            # fallback: use existing groups
            grp = existing_groups[idx % len(existing_groups)] if existing_groups else None
            t_id = all_teachers[idx % len(all_teachers)].id if all_teachers else None
            return (grp.id if grp else None), t_id

        homework_data = [
            {
                "title": "Present Simple exercises",
                "description": "Выполните упражнения 1-5 на стр. 34. Составьте 5 предложений с глаголом to be.",
                "status": HomeworkStatus.assigned,
            },
            {
                "title": "Vocabulary list Unit 3",
                "description": "Выучить слова из Unit 3 (стр. 45-46). Записать транскрипцию и перевод.",
                "status": HomeworkStatus.submitted,
            },
            {
                "title": "Reading comprehension — текст «School Life»",
                "description": "Прочитать текст на стр. 52 и ответить на вопросы 1-8.",
                "status": HomeworkStatus.assigned,
            },
            {
                "title": "Grammar test preparation",
                "description": "Повторить правила употребления Present Continuous. Сделать тест на стр. 60.",
                "status": HomeworkStatus.submitted,
            },
            {
                "title": "Listening task — Unit 5",
                "description": "Прослушать аудиозапись Unit 5 и заполнить пропуски в тексте.",
                "status": HomeworkStatus.assigned,
            },
            {
                "title": "Writing — My favourite hobby",
                "description": "Написать сочинение о любимом хобби (80-100 слов) с использованием Present Simple.",
                "status": HomeworkStatus.submitted,
            },
            {
                "title": "Irregular verbs table",
                "description": "Выучить неправильные глаголы из таблицы (столбцы A-D). Записать формы V1/V2/V3.",
                "status": HomeworkStatus.completed,
            },
            {
                "title": "Dialogue practice — At the shop",
                "description": "Составить диалог в магазине (не менее 10 реплик). Подготовиться к инсценировке.",
                "status": HomeworkStatus.assigned,
            },
            {
                "title": "Past Simple — story retelling",
                "description": "Прочитать рассказ и пересказать его письменно, используя Past Simple (100-120 слов).",
                "status": HomeworkStatus.completed,
            },
            {
                "title": "Prepositions of time and place",
                "description": "Выполнить упражнения 1-7 на стр. 78. Особое внимание — in/on/at.",
                "status": HomeworkStatus.submitted,
            },
        ]

        homeworks_created = 0
        for i, hd in enumerate(homework_data):
            group_id, teacher_id = _lesson_group_teacher(i)
            if group_id is None:
                continue
            hw, created = await _get_or_create(
                session,
                Homework,
                {"title": hd["title"], "group_id": group_id},
                {
                    "description": hd["description"],
                    "due_date": now + timedelta(days=(i % 14) + 1),
                    "status": hd["status"],
                    "teacher_id": teacher_id,
                    "lesson_date": now - timedelta(days=i),
                },
            )
            if created:
                homeworks_created += 1

        counts["homeworks"] = homeworks_created

        # ── 6. Enrollments ────────────────────────────────────────

        # Fetch existing courses ids 1-5
        courses_res = await session.execute(
            select(Course).where(Course.id.in_([1, 2, 3, 4, 5]))
        )
        existing_courses = courses_res.scalars().all()
        if not existing_courses:
            existing_courses = new_courses[:5]

        enrollment_data = [
            {
                "name": "Иванова Мария Петровна",
                "phone": "+79130001111",
                "email": "ivanova.maria@example.com",
                "comment": "Ребёнок 8 лет, хочет начать с нуля",
                "student_type": "child",
                "age": 8,
                "status": EnrollmentStatus.pending,
                "source": "instagram",
            },
            {
                "name": "Козлов Дмитрий Сергеевич",
                "phone": "+79130002222",
                "email": "kozlov.dmitry@example.com",
                "comment": "Взрослый студент, уровень B1, хочет на разговорный",
                "student_type": "adult",
                "age": 28,
                "status": EnrollmentStatus.confirmed,
                "source": "сайт",
            },
            {
                "name": "Сидорова Анна Игоревна",
                "phone": "+79130003333",
                "email": "sidorova.anna@example.com",
                "comment": "Девочка 5 лет, интересует дошкольная программа",
                "student_type": "preschool",
                "age": 5,
                "status": EnrollmentStatus.active,
                "source": "рекомендация",
            },
            {
                "name": "Попов Алексей Владимирович",
                "phone": "+79130004444",
                "email": "popov.alex@example.com",
                "comment": "Нужен интенсив перед командировкой",
                "student_type": "adult",
                "age": 35,
                "status": EnrollmentStatus.active,
                "source": "реклама",
            },
            {
                "name": "Новикова Елена Андреевна",
                "phone": "+79130005555",
                "email": "novikova.elena@example.com",
                "comment": "Школьница 12 лет, готовится к олимпиаде",
                "student_type": "child",
                "age": 12,
                "status": EnrollmentStatus.pending,
                "source": "сайт",
            },
            {
                "name": "Морозов Кирилл Олегович",
                "phone": "+79130006666",
                "email": "morozov.kirill@example.com",
                "comment": "Взрослый, начинает с нуля, занятость вечерняя",
                "student_type": "adult",
                "age": 41,
                "status": EnrollmentStatus.rejected,
                "source": "партнёр",
            },
            {
                "name": "Федотова Светлана Борисовна",
                "phone": "+79130007777",
                "email": "fedotova.sv@example.com",
                "comment": "Хочет группу для ребёнка 7 лет",
                "student_type": "child",
                "age": 7,
                "status": EnrollmentStatus.confirmed,
                "source": "instagram",
            },
            {
                "name": "Белкин Роман Николаевич",
                "phone": "+79130008888",
                "email": "belkin.roman@example.com",
                "comment": "Взрослый B2, интересует интенсив",
                "student_type": "adult",
                "age": 30,
                "status": EnrollmentStatus.active,
                "source": "сайт",
            },
            {
                "name": "Зайцева Ольга Михайловна",
                "phone": "+79130009999",
                "email": "zaitseva.olga@example.com",
                "comment": "Ребёнок 10 лет, школа",
                "student_type": "child",
                "age": 10,
                "status": EnrollmentStatus.pending,
                "source": "рекомендация",
            },
            {
                "name": "Кузнецов Павел Игоревич",
                "phone": "+79131000000",
                "email": "kuznetsov.pavel@example.com",
                "comment": "Взрослый, хочет разговорный курс для путешествий",
                "student_type": "adult",
                "age": 26,
                "status": EnrollmentStatus.confirmed,
                "source": "реклама",
            },
        ]

        enrollments_created = 0
        for i, ed in enumerate(enrollment_data):
            course_obj = existing_courses[i % len(existing_courses)] if existing_courses else None
            enroll, created = await _get_or_create(
                session,
                Enrollment,
                {"phone": ed["phone"], "email": ed["email"]},
                {
                    "name": ed["name"],
                    "comment": ed["comment"],
                    "student_type": ed["student_type"],
                    "age": ed["age"],
                    "status": ed["status"],
                    "source": ed["source"],
                    "desired_course_id": course_obj.id if course_obj else None,
                    "created_at": now - timedelta(days=30 - i * 3),
                },
            )
            if created:
                enrollments_created += 1

        counts["enrollments"] = enrollments_created

        # ── 7. Documents ──────────────────────────────────────────

        # Fetch users 1-5 for document linking
        doc_users_res = await session.execute(
            select(User).where(User.id.in_([1, 2, 3, 4, 5]))
        )
        doc_users = doc_users_res.scalars().all()

        documents_data = [
            {
                "title": "Договор об оказании образовательных услуг №001",
                "description": "Договор с учеником группы School A1 Morning",
                "file_url": "/documents/contracts/contract_001.pdf",
                "category": DocumentCategory.contract,
                "is_public": False,
                "user_idx": 0,
            },
            {
                "title": "Справка об обучении",
                "description": "Подтверждение факта обучения в ABC Language School",
                "file_url": "/documents/certificates/study_cert_001.pdf",
                "category": DocumentCategory.other,
                "is_public": False,
                "user_idx": 1,
            },
            {
                "title": "Договор об оказании образовательных услуг №002",
                "description": "Договор с учеником группы Adults B1 Evening",
                "file_url": "/documents/contracts/contract_002.pdf",
                "category": DocumentCategory.contract,
                "is_public": False,
                "user_idx": 2,
            },
            {
                "title": "Политика конфиденциальности ABC Language School",
                "description": "Документ для ознакомления всех студентов",
                "file_url": "/documents/policy/privacy_policy.pdf",
                "category": DocumentCategory.policy,
                "is_public": True,
                "user_idx": None,
            },
            {
                "title": "Сертификат об окончании курса — уровень A1",
                "description": "Сертификат выпускника курса Английский для школьников",
                "file_url": "/documents/certificates/cert_a1_001.pdf",
                "category": DocumentCategory.other,
                "is_public": False,
                "user_idx": 3,
            },
        ]

        docs_created = 0
        for dd in documents_data:
            user_id_val = None
            if not dd["is_public"] and dd["user_idx"] is not None and doc_users:
                user_id_val = doc_users[dd["user_idx"] % len(doc_users)].id

            doc, created = await _get_or_create(
                session,
                Document,
                {"title": dd["title"]},
                {
                    "description": dd["description"],
                    "file_url": dd["file_url"],
                    "category": dd["category"],
                    "user_id": user_id_val,
                    "is_active": True,
                },
            )
            if created:
                docs_created += 1

        counts["documents"] = docs_created

        # ── 8. Discounts ──────────────────────────────────────────

        # Use groups from new_groups or existing for discount linking
        all_groups_res = await session.execute(
            select(Group).order_by(Group.id).limit(10)
        )
        all_groups = all_groups_res.scalars().all()

        discounts_data = [
            {
                "description": "Скидка для многодетных семей",
                "reason": DiscountReason.social,
                "discount_type": DiscountType.percentage,
                "value": 15,
                "group_idx": 0,
                "valid_months": 9,
            },
            {
                "description": "Скидка при оплате за год",
                "reason": DiscountReason.early_payment,
                "discount_type": DiscountType.percentage,
                "value": 20,
                "group_idx": 1,
                "valid_months": 12,
            },
            {
                "description": "Скидка для сотрудников партнёров",
                "reason": DiscountReason.corporate,
                "discount_type": DiscountType.percentage,
                "value": 10,
                "group_idx": 2,
                "valid_months": 6,
            },
            {
                "description": "Скидка за второго ребёнка в семье",
                "reason": DiscountReason.sibling,
                "discount_type": DiscountType.percentage,
                "value": 10,
                "group_idx": 0,
                "valid_months": 9,
            },
            {
                "description": "Скидка постоянного ученика (2 года обучения)",
                "reason": DiscountReason.loyalty,
                "discount_type": DiscountType.percentage,
                "value": 15,
                "group_idx": 3,
                "valid_months": 12,
            },
        ]

        discounts_created = 0
        for dd in discounts_data:
            group_obj = all_groups[dd["group_idx"] % len(all_groups)] if all_groups else None
            discount, created = await _get_or_create(
                session,
                Discount,
                {"description": dd["description"]},
                {
                    "reason": dd["reason"],
                    "discount_type": dd["discount_type"],
                    "value": dd["value"],
                    "group_id": group_obj.id if group_obj else None,
                    "valid_from": now,
                    "valid_until": now + timedelta(days=30 * dd["valid_months"]),
                    "is_active": True,
                },
            )
            if created:
                discounts_created += 1

        counts["discounts"] = discounts_created

        # ── 9. Notifications ──────────────────────────────────────

        notifications_data = [
            {
                "title": "Напоминание об оплате за май",
                "body": (
                    "Уважаемый студент, напоминаем, что срок оплаты за май истекает 31 мая. "
                    "Пожалуйста, произведите оплату своевременно."
                ),
                "notification_type": NotificationType.payment_reminder,
                "channel": NotificationChannel.email,
                "status": NotificationStatus.sent,
                "user_idx": 0,
                "recipient_name": "Студент ABC School",
            },
            {
                "title": "Изменение расписания — группа School A1 Morning",
                "body": (
                    "Занятие в среду перенесено с 10:00 на 11:00. "
                    "Аудитория остаётся прежней. Просим учесть изменение."
                ),
                "notification_type": NotificationType.schedule_reminder,
                "channel": NotificationChannel.internal,
                "status": NotificationStatus.sent,
                "user_idx": 1,
                "recipient_name": "Группа School A1 Morning",
            },
            {
                "title": "Напоминание об оплате — просрочка",
                "body": (
                    "Обращаем ваше внимание, что оплата за текущий месяц не поступила. "
                    "Для продолжения обучения необходимо погасить задолженность."
                ),
                "notification_type": NotificationType.payment_reminder,
                "channel": NotificationChannel.email,
                "status": NotificationStatus.pending,
                "user_idx": 2,
                "recipient_name": "Студент ABC School",
            },
            {
                "title": "День открытых дверей — приглашение",
                "body": (
                    "Приглашаем вас и ваших близких на день открытых дверей в ABC Language School. "
                    "Мероприятие состоится в субботу с 11:00 до 15:00."
                ),
                "notification_type": NotificationType.custom,
                "channel": NotificationChannel.email,
                "status": NotificationStatus.sent,
                "user_idx": 3,
                "recipient_name": "Студент ABC School",
            },
            {
                "title": "Подтверждение записи на курс",
                "body": (
                    "Ваша заявка на курс «Разговорный английский» успешно подтверждена. "
                    "Занятия начинаются в следующий понедельник. Ждём вас!"
                ),
                "notification_type": NotificationType.enrollment_confirm,
                "channel": NotificationChannel.email,
                "status": NotificationStatus.sent,
                "user_idx": 0,
                "recipient_name": "Студент ABC School",
            },
        ]

        notifs_created = 0
        for nd in notifications_data:
            user_obj = users[nd["user_idx"] % len(users)] if users else None
            recipient_email = user_obj.email if user_obj and hasattr(user_obj, "email") else None

            notif, created = await _get_or_create(
                session,
                Notification,
                {"title": nd["title"]},
                {
                    "body": nd["body"],
                    "notification_type": nd["notification_type"],
                    "channel": nd["channel"],
                    "status": nd["status"],
                    "recipient_email": recipient_email,
                    "recipient_name": nd["recipient_name"],
                    "created_by": admin_id,
                    "sent_at": now - timedelta(hours=5) if nd["status"] == NotificationStatus.sent else None,
                },
            )
            if created:
                notifs_created += 1

        counts["notifications"] = notifs_created

        # ── 10. Waitlist ──────────────────────────────────────────

        # Fetch courses 1-5 for waitlist
        waitlist_courses_res = await session.execute(
            select(Course).where(Course.id.in_([1, 2, 3, 4, 5]))
        )
        waitlist_courses = waitlist_courses_res.scalars().all()
        if not waitlist_courses:
            waitlist_courses = new_courses

        waitlist_data = [
            {
                "student_name": "Громова Татьяна Александровна",
                "student_phone": "+79134001001",
                "student_email": "gromova.tatyana@example.com",
                "student_type": "adult",
                "comment": "Интересует вечерняя группа уровня B1",
                "position": 1,
                "status": WaitlistStatus.waiting,
                "course_idx": 0,
                "days_ago": 45,
            },
            {
                "student_name": "Суворов Иван Петрович",
                "student_phone": "+79134002002",
                "student_email": "suvorov.ivan@example.com",
                "student_type": "adult",
                "comment": "Ждёт место в группе интенсива",
                "position": 2,
                "status": WaitlistStatus.waiting,
                "course_idx": 1,
                "days_ago": 30,
            },
            {
                "student_name": "Петрова Наталья Сергеевна",
                "student_phone": "+79134003003",
                "student_email": "petrova.natasha@example.com",
                "student_type": "child",
                "comment": "Ребёнок 9 лет, ждёт место в школьной группе",
                "position": 1,
                "status": WaitlistStatus.notified,
                "course_idx": 2,
                "days_ago": 20,
            },
            {
                "student_name": "Орлов Максим Дмитриевич",
                "student_phone": "+79134004004",
                "student_email": "orlov.maxim@example.com",
                "student_type": "adult",
                "comment": "Хочет на утреннюю группу B2",
                "position": 3,
                "status": WaitlistStatus.waiting,
                "course_idx": 3,
                "days_ago": 15,
            },
            {
                "student_name": "Яковлева Виктория Олеговна",
                "student_phone": "+79134005005",
                "student_email": "yakovleva.v@example.com",
                "student_type": "preschool",
                "comment": "Девочка 4 года, ждёт место в дошкольной группе",
                "position": 2,
                "status": WaitlistStatus.waiting,
                "course_idx": 4 % len(waitlist_courses),
                "days_ago": 10,
            },
        ]

        waitlist_created = 0
        for i, wd in enumerate(waitlist_data):
            course_obj = waitlist_courses[wd["course_idx"] % len(waitlist_courses)]
            entry, created = await _get_or_create(
                session,
                WaitlistEntry,
                {"student_phone": wd["student_phone"], "course_id": course_obj.id},
                {
                    "student_name": wd["student_name"],
                    "student_email": wd["student_email"],
                    "student_type": wd["student_type"],
                    "comment": wd["comment"],
                    "position": wd["position"],
                    "status": wd["status"],
                    "created_at": now - timedelta(days=wd["days_ago"]),
                },
            )
            if created:
                waitlist_created += 1

        counts["waitlist"] = waitlist_created

        # ── Commit ────────────────────────────────────────────────
        await session.commit()

    # ── Summary ───────────────────────────────────────────────────
    print("\n✅  seed_extended_data завершён")
    print("-" * 40)
    total = 0
    for table, count in counts.items():
        print(f"   {table:<20}: {count:>3} rows created")
        total += count
    print("-" * 40)
    print(f"   {'TOTAL':<20}: {total:>3} rows created")


if __name__ == "__main__":
    asyncio.run(seed_extended_data())
