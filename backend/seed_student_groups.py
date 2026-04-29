"""
Seed student_groups for every existing group so the attendance matrix is never empty.

Run from the backend/ directory:
    cd backend
    python seed_student_groups.py
"""
import asyncio
import os
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import select

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import AsyncSessionLocal, init_db
from app.models.group import Course, CourseCategory, Group, StudentGroup
from app.models.student import Student, StudentType

# Course categories that call for child-type students
CHILD_CATEGORIES = {CourseCategory.children, CourseCategory.school}

# Mapping from CourseCategory to preferred StudentType
PREFERRED_TYPE: dict[CourseCategory, StudentType] = {
    CourseCategory.children: StudentType.child,
    CourseCategory.school: StudentType.child,
    CourseCategory.adults: StudentType.adult,
    CourseCategory.corporate: StudentType.adult,
    CourseCategory.exam_prep: StudentType.adult,
}


async def seed_student_groups() -> None:
    await init_db()

    async with AsyncSessionLocal() as session:
        # Load all groups with their courses
        groups_result = await session.execute(
            select(Group).join(Course, Group.course_id == Course.id)
        )
        groups = groups_result.scalars().all()

        # Load all students
        students_result = await session.execute(select(Student))
        all_students = students_result.scalars().all()

        if not all_students:
            print("⚠️  Таблица students пуста — сначала запустите seed для студентов.")
            return

        # Load all courses into a dict to avoid N+1 queries
        courses_result = await session.execute(select(Course))
        courses_by_id: dict[int, Course] = {
            c.id: c for c in courses_result.scalars().all()
        }

        groups_processed = 0
        created_total = 0
        skipped_total = 0

        for group in groups:
            # Determine preferred student type from course category
            course = courses_by_id.get(group.course_id)
            preferred_type = PREFERRED_TYPE.get(
                course.category if course else None,
                StudentType.adult,
            )

            # Partition students by preferred type vs. others
            preferred = [s for s in all_students if s.student_type == preferred_type]
            others = [s for s in all_students if s.student_type != preferred_type]

            # Build a pool: preferred first, then fill with others
            pool = preferred + others

            # Fetch existing student names already linked to this group
            existing_result = await session.execute(
                select(StudentGroup.student_name).where(
                    StudentGroup.group_id == group.id
                )
            )
            existing_names = {row[0] for row in existing_result.fetchall()}

            # Filter out already-linked students
            available = [s for s in pool if s.full_name not in existing_names]

            target_count = random.randint(4, 8)
            to_enroll = available[:target_count]

            for student in to_enroll:
                days_ago = random.randint(14, 60)
                sg = StudentGroup(
                    group_id=group.id,
                    student_name=student.full_name,
                    student_phone=student.phone or None,
                    student_email=student.email or None,
                    student_type=student.student_type.value,
                    form_id=None,
                    enrolled_at=datetime.utcnow() - timedelta(days=days_ago),
                    is_active=True,
                )
                session.add(sg)
                created_total += 1

            skipped_total += len(existing_names)
            groups_processed += 1

        await session.commit()

    print(
        f"✅ seed_student_groups завершён:\n"
        f"   Групп обработано: {groups_processed}\n"
        f"   Записей student_groups создано: {created_total}\n"
        f"   Пропущено (уже существуют): {skipped_total}"
    )


if __name__ == "__main__":
    asyncio.run(seed_student_groups())
