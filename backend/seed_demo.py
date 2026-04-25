import asyncio
from datetime import datetime, time

from sqlalchemy import select

from app.core.database import AsyncSessionLocal, init_db
from app.models.branch import Branch
from app.models.educational_program import EducationalProgram
from app.models.group import Course, CourseCategory, CourseLevel, Group, GroupStatus, StudentGroup
from app.models.news import News, NewsCategory, NewsStatus
from app.models.schedule import Classroom, DayOfWeek, Lesson, LessonStatus
from app.models.student import Student, StudentStatus, StudentType
from app.models.teacher import Teacher

async def get_or_create(session, model, defaults=None, **kwargs):
    stmt = select(model).filter_by(**kwargs)
    res = await session.execute(stmt)
    instance = res.scalars().first()
    if instance:
        return instance
    else:
        params = {**kwargs, **(defaults or {})}
        instance = model(**params)
        session.add(instance)
        await session.flush()
        return instance


async def seed():
    await init_db()

    async with AsyncSessionLocal() as session:
        branch = await get_or_create(
            session,
            Branch,
            name="Филиал Центр",
            defaults={
                "address": "г. Новосибирск, ул. Ленина, 18",
                "phone": "+73832090099",
                "email": "center@abc-school.ru",
                "is_active": True,
            },
        )

        p1 = await get_or_create(
            session,
            EducationalProgram,
            name="Английский для школьников",
            defaults={
                "code": "ENG-SCHOOL",
                "language": "Английский",
                "level": "A2",
                "target_group": "школьники",
                "duration_months": 9,
                "description": "Программа для учеников 5-11 классов: грамматика, лексика, разговорная практика.",
                "is_active": True,
            },
        )

        p2 = await get_or_create(
            session,
            EducationalProgram,
            name="Разговорный английский для взрослых",
            defaults={
                "code": "ENG-ADULT",
                "language": "Английский",
                "level": "B1",
                "target_group": "взрослые",
                "duration_months": 6,
                "description": "Курс для уверенного общения в поездках, работе и повседневных ситуациях.",
                "is_active": True,
            },
        )

        c_res = await session.execute(select(Course).limit(1))
        c1 = c_res.scalars().first()
        if not c1:
            c1 = await get_or_create(
                session,
                Course,
                name="English A2.1",
                defaults={
                    "description": "Базовый разговорный курс",
                    "language": "Английский",
                    "level": CourseLevel.elementary,
                    "category": CourseCategory.school,
                    "duration_months": 9,
                    "lessons_per_week": 2,
                    "price_per_month": 5200,
                    "max_students": 10,
                    "is_active": True,
                },
            )

        g1 = await get_or_create(
            session,
            Group,
            name="A2 Подростки Вт/Чт 17:00",
            defaults={"course_id": c1.id, "status": GroupStatus.active},
        )
        g2 = await get_or_create(
            session,
            Group,
            name="A2 Подростки Сб 11:00",
            defaults={"course_id": c1.id, "status": GroupStatus.active},
        )
        g3 = await get_or_create(
            session,
            Group,
            name="A2 Взрослые Пн/Ср 19:00",
            defaults={"course_id": c1.id, "status": GroupStatus.active},
        )

        teacher = (await session.execute(select(Teacher).where(Teacher.is_active == True).limit(1))).scalars().first()
        if teacher is None:
            teacher = await get_or_create(
                session,
                Teacher,
                email="demo.teacher@abc-school.ru",
                defaults={
                    "full_name": "Демо Преподаватель",
                    "phone": "+79000000000",
                    "subject": "Английский",
                    "language_level": "C1",
                    "experience_years": 5,
                    "bio": "Демо преподаватель",
                    "is_active": True,
                },
            )

        classroom_1 = await get_or_create(
            session,
            Classroom,
            name="Кабинет 301",
            defaults={"capacity": 12, "floor": 3, "has_projector": True, "has_whiteboard": True, "is_active": True},
        )
        classroom_2 = await get_or_create(
            session,
            Classroom,
            name="Кабинет 204",
            defaults={"capacity": 10, "floor": 2, "has_projector": True, "has_whiteboard": True, "is_active": True},
        )

        students = []
        student_seed = [
            ("petrov.nikita@abc-school.ru", "Петров Никита Сергеевич"),
            ("smirnova.alina@abc-school.ru", "Смирнова Алина Игоревна"),
            ("orlov.daniil@abc-school.ru", "Орлов Даниил Романович"),
            ("novikova.elena@abc-school.ru", "Новикова Елена Андреевна"),
            ("kozlov.maxim@abc-school.ru", "Козлов Максим Олегович"),
            ("sokolova.vlada@abc-school.ru", "Соколова Влада Артемовна"),
        ]
        group_pool = [g1, g1, g1, g2, g2, g3]
        for idx, (email, full_name) in enumerate(student_seed):
            s = await get_or_create(
                session,
                Student,
                email=email,
                defaults={
                    "full_name": full_name,
                    "student_type": StudentType.adult,
                    "status": StudentStatus.active,
                    "phone": f"+7900100{idx:04d}",
                    "language_level": "A2",
                    "is_active": True,
                },
            )
            students.append(s)
            target_group = group_pool[idx]
            await get_or_create(
                session,
                StudentGroup,
                group_id=target_group.id,
                student_email=s.email,
                defaults={
                    "student_name": s.full_name,
                    "student_phone": s.phone,
                    "student_type": "adult",
                    "is_active": True,
                },
            )

        lessons = [
            (g1, p1, DayOfWeek.tuesday, time(17, 0), time(18, 30), "Present Simple vs Present Continuous", classroom_1),
            (g1, p1, DayOfWeek.thursday, time(17, 0), time(18, 30), "Travel vocabulary and airport situations", classroom_1),
            (g2, p1, DayOfWeek.saturday, time(11, 0), time(12, 30), "Reading club: short stories discussion", classroom_2),
            (g3, p2, DayOfWeek.monday, time(19, 0), time(20, 30), "Listening practice: everyday conversations", classroom_2),
            (g3, p2, DayOfWeek.wednesday, time(19, 0), time(20, 30), "Speaking drills and role-play", classroom_2),
        ]
        for group, program, dow, t_start, t_end, topic, classroom in lessons:
            await get_or_create(
                session,
                Lesson,
                group_id=group.id,
                teacher_id=teacher.id,
                classroom_id=classroom.id,
                day_of_week=dow,
                time_start=t_start,
                defaults={
                    "time_end": t_end,
                    "topic": topic,
                    "status": LessonStatus.scheduled,
                    "branch_id": branch.id,
                    "program_id": program.id,
                    "is_recurring": True,
                },
            )

        cat = await get_or_create(
            session,
            NewsCategory,
            name="Объявления",
            defaults={"slug": "obyavleniya", "color": "#1E90FF"},
        )
        news_items = [
            (
                "Открыт набор в летние интенсивы",
                "С 3 июня стартуют интенсивные курсы для школьников и взрослых. Формируются группы уровней A1-B2.",
            ),
            (
                "Разговорный клуб с носителем по субботам",
                "Каждую субботу в 16:00 проводим Speaking Club. Участие по предварительной записи у администратора филиала.",
            ),
            (
                "Пробное тестирование перед новым модулем",
                "С 20 по 24 мая пройдет входное тестирование для распределения в группы нового учебного блока.",
            ),
            (
                "Обновление расписания на осенний семестр",
                "Новая сетка занятий опубликована в личном кабинете. Проверьте изменения по времени и аудиториям.",
            ),
            (
                "Семинар для родителей по школьному английскому",
                "15 сентября в 19:00 методист расскажет, как помогать ребенку с домашними заданиями без перегрузки.",
            ),
        ]
        for title, content in news_items:
            await get_or_create(
                session,
                News,
                title=title,
                defaults={
                    "category_id": cat.id,
                    "body": content,
                    "tag": "Новости",
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "status": NewsStatus.published,
                    "published_at": datetime.utcnow(),
                },
            )

        await session.commit()
        print("✅ Демо-данные загружены: студенты, группы, расписание и новости")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(seed())
