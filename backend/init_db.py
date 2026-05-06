#!/usr/bin/env python3
"""
Database Initialization Script
Creates all database tables based on models using the async engine.

NOTE: For production use, run Alembic migrations instead:
    alembic upgrade head
This script is intended for local development / fresh setup only.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import engine, Base
from app.models import (  # noqa: F401 - imports register all tables on Base.metadata
    User, Document, Teacher, Branch, EducationalProgram, Student,
    Classroom, Lesson, Group, Attendance, Enrollment, Payment,
    News, Notification, WaitlistEntry, ChildForm, AdultForm,
    PreschoolForm, TeacherForm, TestingForm, FeedbackForm,
    Discount, RoomBooking, AuditLog, ReportCache
)


async def init_database():
    """Initialize the database by creating all tables."""
    print("Initializing database...")
    print("Creating tables...")

    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("\n✓ Database initialized successfully!")
        table_names = sorted(Base.metadata.tables.keys())
        for name in table_names:
            print(f"  - {name}")
        print(f"\nTotal: {len(table_names)} tables created")

    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("ABC Language School - Database Initialization")
    print("=" * 60)
    asyncio.run(init_database())
    print("\nYou can now run 'python seed_real_data.py' to populate with sample data")
    print("=" * 60)
