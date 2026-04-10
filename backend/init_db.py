#!/usr/bin/env python3
"""
Database Initialization Script
Creates all database tables based on models
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.database import engine, Base
from app.models import (
    User, Course, Group, Lesson, Room, Enrollment,
    Payment, Attendance, News, Notification, Waitlist,
    Review, Material, Expense, RevenueAnalytics
)

def init_database():
    """
    Initialize the database by creating all tables.
    """
    print("Initializing database...")
    print("Creating tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✓ Database initialized successfully!")
        print("\nCreated tables:")
        print("  - users")
        print("  - courses")
        print("  - groups")
        print("  - lessons")
        print("  - rooms")
        print("  - enrollments")
        print("  - payments")
        print("  - attendance")
        print("  - news")
        print("  - notifications")
        print("  - waitlist")
        print("  - reviews")
        print("  - materials")
        print("  - expenses")
        print("  - revenue_analytics")
        print("\nTotal: 15 tables created")
        
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("ABC Language School - Database Initialization")
    print("="*60)
    init_database()
    print("\nYou can now run 'python seed_real_data.py' to populate with sample data")
    print("="*60)
