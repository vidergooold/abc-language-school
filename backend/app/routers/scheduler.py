from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date, time, timedelta
from pydantic import BaseModel
import sys
sys.path.append('..')

from database import get_db
from models import Lesson, Group, Room, User, LessonStatus

router = APIRouter(
    prefix="/api/v1/scheduler",
    tags=["scheduler"]
)

# Pydantic schemas
class LessonCreate(BaseModel):
    group_id: int
    teacher_id: int
    room_id: Optional[int] = None
    date: date
    start_time: time
    end_time: time
    topic: Optional[str] = None

class LessonResponse(BaseModel):
    id: int
    group_id: int
    teacher_id: int
    room_id: Optional[int]
    date: date
    start_time: time
    end_time: time
    topic: Optional[str]
    status: str
    
    class Config:
        from_attributes = True

class ConflictCheck(BaseModel):
    teacher_id: Optional[int] = None
    room_id: Optional[int] = None
    group_id: Optional[int] = None
    date: date
    start_time: time
    end_time: time

# Helper function to check for schedule conflicts
def check_schedule_conflicts(
    db: Session,
    date: date,
    start_time: time,
    end_time: time,
    teacher_id: Optional[int] = None,
    room_id: Optional[int] = None,
    group_id: Optional[int] = None,
    exclude_lesson_id: Optional[int] = None
) -> List[str]:
    """
    Check for scheduling conflicts:
    - Teacher cannot have overlapping lessons
    - Room cannot be double-booked
    - Group cannot have overlapping lessons
    """
    conflicts = []
    
    # Build base query for lessons on the same date
    query = db.query(Lesson).filter(
        Lesson.date == date,
        Lesson.status != LessonStatus.cancelled
    )
    
    if exclude_lesson_id:
        query = query.filter(Lesson.id != exclude_lesson_id)
    
    # Check time overlap condition
    time_overlap = or_(
        and_(Lesson.start_time <= start_time, Lesson.end_time > start_time),
        and_(Lesson.start_time < end_time, Lesson.end_time >= end_time),
        and_(Lesson.start_time >= start_time, Lesson.end_time <= end_time)
    )
    
    # Check teacher conflicts
    if teacher_id:
        teacher_conflicts = query.filter(
            Lesson.teacher_id == teacher_id,
            time_overlap
        ).count()
        if teacher_conflicts > 0:
            conflicts.append(f"Teacher {teacher_id} has {teacher_conflicts} conflicting lesson(s)")
    
    # Check room conflicts
    if room_id:
        room_conflicts = query.filter(
            Lesson.room_id == room_id,
            time_overlap
        ).count()
        if room_conflicts > 0:
            conflicts.append(f"Room {room_id} is already booked for this time")
    
    # Check group conflicts
    if group_id:
        group_conflicts = query.filter(
            Lesson.group_id == group_id,
            time_overlap
        ).count()
        if group_conflicts > 0:
            conflicts.append(f"Group {group_id} has {group_conflicts} conflicting lesson(s)")
    
    return conflicts

@router.post("/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(lesson: LessonCreate, db: Session = Depends(get_db)):
    """
    Create a new lesson with automatic conflict detection.
    Returns error if there are scheduling conflicts.
    """
    # Validate that end time is after start time
    if lesson.end_time <= lesson.start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check for conflicts
    conflicts = check_schedule_conflicts(
        db=db,
        date=lesson.date,
        start_time=lesson.start_time,
        end_time=lesson.end_time,
        teacher_id=lesson.teacher_id,
        room_id=lesson.room_id,
        group_id=lesson.group_id
    )
    
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Scheduling conflicts detected",
                "conflicts": conflicts
            }
        )
    
    # Verify that group, teacher, and room exist
    group = db.query(Group).filter(Group.id == lesson.group_id).first()
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group {lesson.group_id} not found"
        )
    
    teacher = db.query(User).filter(User.id == lesson.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher {lesson.teacher_id} not found"
        )
    
    if lesson.room_id:
        room = db.query(Room).filter(Room.id == lesson.room_id).first()
        if not room:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {lesson.room_id} not found"
            )
    
    # Create the lesson
    db_lesson = Lesson(**lesson.dict())
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    
    return db_lesson

@router.post("/check-conflicts", status_code=status.HTTP_200_OK)
def check_conflicts(conflict_check: ConflictCheck, db: Session = Depends(get_db)):
    """
    Check for potential scheduling conflicts without creating a lesson.
    Useful for UI validation.
    """
    conflicts = check_schedule_conflicts(
        db=db,
        date=conflict_check.date,
        start_time=conflict_check.start_time,
        end_time=conflict_check.end_time,
        teacher_id=conflict_check.teacher_id,
        room_id=conflict_check.room_id,
        group_id=conflict_check.group_id
    )
    
    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }

@router.get("/lessons", response_model=List[LessonResponse])
def get_lessons(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    teacher_id: Optional[int] = None,
    room_id: Optional[int] = None,
    group_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get lessons with optional filters.
    """
    query = db.query(Lesson)
    
    if start_date:
        query = query.filter(Lesson.date >= start_date)
    if end_date:
        query = query.filter(Lesson.date <= end_date)
    if teacher_id:
        query = query.filter(Lesson.teacher_id == teacher_id)
    if room_id:
        query = query.filter(Lesson.room_id == room_id)
    if group_id:
        query = query.filter(Lesson.group_id == group_id)
    
    lessons = query.all()
    return lessons

@router.get("/available-rooms", status_code=status.HTTP_200_OK)
def get_available_rooms(
    date: date,
    start_time: time,
    end_time: time,
    db: Session = Depends(get_db)
):
    """
    Get list of available rooms for a specific time slot.
    """
    # Get all rooms
    all_rooms = db.query(Room).filter(Room.is_available == True).all()
    
    # Get booked room IDs for the time slot
    time_overlap = or_(
        and_(Lesson.start_time <= start_time, Lesson.end_time > start_time),
        and_(Lesson.start_time < end_time, Lesson.end_time >= end_time),
        and_(Lesson.start_time >= start_time, Lesson.end_time <= end_time)
    )
    
    booked_rooms = db.query(Lesson.room_id).filter(
        Lesson.date == date,
        Lesson.status != LessonStatus.cancelled,
        Lesson.room_id.isnot(None),
        time_overlap
    ).distinct().all()
    
    booked_room_ids = [room[0] for room in booked_rooms]
    
    # Filter out booked rooms
    available_rooms = [
        {"id": room.id, "name": room.name, "capacity": room.capacity}
        for room in all_rooms
        if room.id not in booked_room_ids
    ]
    
    return {
        "available_rooms": available_rooms,
        "total_available": len(available_rooms)
    }

@router.get("/teacher-schedule/{teacher_id}", status_code=status.HTTP_200_OK)
def get_teacher_schedule(
    teacher_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get a teacher's complete schedule.
    """
    query = db.query(Lesson).filter(Lesson.teacher_id == teacher_id)
    
    if start_date:
        query = query.filter(Lesson.date >= start_date)
    if end_date:
        query = query.filter(Lesson.date <= end_date)
    
    lessons = query.order_by(Lesson.date, Lesson.start_time).all()
    
    return {
        "teacher_id": teacher_id,
        "total_lessons": len(lessons),
        "lessons": lessons
    }
