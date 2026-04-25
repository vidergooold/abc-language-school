import asyncio
import sys
import os
from datetime import time, date, datetime, timedelta
from httpx import AsyncClient
from sqlalchemy import text
from app.main import app
from app.core.database import AsyncSessionLocal
from app.models.room_booking import RoomBooking

async def verify():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # 1. Login
        login_data = {"email": "anna.ivanova@abc-school.ru", "password": "teacher123"}
        response = await ac.post("/api/v1/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        async with AsyncSessionLocal() as session:
            group_id = (await session.execute(text("SELECT id FROM groups LIMIT 1"))).scalar()
            teacher_id = (await session.execute(text("SELECT id FROM teachers LIMIT 1"))).scalar()
            classroom_id = (await session.execute(text("SELECT id FROM classrooms LIMIT 1"))).scalar()
            user_id = (await session.execute(text("SELECT id FROM users LIMIT 1"))).scalar()
            
            if not all([group_id, teacher_id, classroom_id, user_id]):
                print("Missing seed data (group, teacher, classroom, or user)")
                return

        next_monday = date.today() + timedelta(days=(7 - date.today().weekday()))
        
        # 2. Non-conflicting payload
        payload_non_conflict = {
            "group_id": group_id,
            "teacher_id": teacher_id,
            "classroom_id": classroom_id,
            "day_of_week": "monday",
            "time_start": "08:00",
            "time_end": "09:00",
            "lesson_date": next_monday.isoformat()
        }
        res2 = await ac.post("/api/v1/schedule/check-conflicts", json=payload_non_conflict, headers=headers)
        print(f"Step 2 (Non-conflicting): Status {res2.status_code}, has_conflicts: {res2.json().get('has_conflicts')}")

        # 3. Conflicting payload
        # Ensure a lesson actually exists for this conflict
        async with AsyncSessionLocal() as session:
            # We want to check for actual existence or simulate it
            pass

        payload_conflict = {
            "group_id": group_id,
            "teacher_id": teacher_id,
            "classroom_id": classroom_id,
            "day_of_week": "monday",
            "time_start": "10:30",
            "time_end": "11:30",
            "lesson_date": next_monday.isoformat()
        }
        res3 = await ac.post("/api/v1/schedule/check-conflicts", json=payload_conflict, headers=headers)
        print(f"Step 3 (Conflict 10:30-11:30): Status {res3.status_code}, conflicts: {res3.json().get('conflicts')}")

        # 4. time_start >= time_end
        payload_invalid = {
            "group_id": group_id,
            "teacher_id": teacher_id,
            "classroom_id": classroom_id,
            "day_of_week": "monday",
            "time_start": "11:00",
            "time_end": "10:00",
            "lesson_date": next_monday.isoformat()
        }
        res4 = await ac.post("/api/v1/schedule/check-conflicts", json=payload_invalid, headers=headers)
        print(f"Step 4 (Invalid time): Status {res4.status_code}, detail: {res4.json().get('detail')}")

        # 5. Room booking conflict
        test_date = next_monday
        async with AsyncSessionLocal() as session:
            booking = RoomBooking(
                classroom_id=classroom_id,
                date=test_date,
                time_start=time(14, 0),
                time_end=time(15, 0),
                purpose="Test Booking",
                user_id=user_id,
                status="confirmed"
            )
            session.add(booking)
            await session.commit()
            
            payload_room = {
                "group_id": group_id,
                "teacher_id": teacher_id,
                "classroom_id": classroom_id,
                "day_of_week": "monday",
                "time_start": "14:15",
                "time_end": "14:45",
                "lesson_date": test_date.isoformat()
            }
            res5 = await ac.post("/api/v1/schedule/check-conflicts", json=payload_room, headers=headers)
            print(f"Step 5 (Room booking conflict): Status {res5.status_code}, conflicts: {res5.json().get('conflicts')}")

        # 6. Final sqlite table count
        async with AsyncSessionLocal() as session:
            count = (await session.execute(text("SELECT count(*) FROM sqlite_master WHERE type='table'"))).scalar()
            print(f"Step 6 (Table count): {count}")

if __name__ == "__main__":
    asyncio.run(verify())
