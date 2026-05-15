from datetime import datetime, time
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.models.group import CourseLevel, CourseCategory, GroupStatus
from app.models.schedule import DayOfWeek


class CourseCreate(BaseModel):
    name: str
    description: Optional[str] = None
    language: str = "Английский"
    level: CourseLevel
    category: CourseCategory
    duration_months: int = 9
    lessons_per_week: int = 2
    price_per_month: int
    max_students: int = 8


class CourseOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    language: str
    level: CourseLevel
    category: CourseCategory
    duration_months: Optional[int] = None
    lessons_per_week: Optional[int] = None
    price_per_month: Optional[int] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GroupCreate(BaseModel):
    name: Optional[str] = None
    course_id: Optional[int] = None
    language: Optional[str] = None
    program_id: Optional[int] = None
    teacher_id: Optional[int] = None
    branch_id: Optional[int] = None
    classroom_id: Optional[int] = None
    time_start: Optional[time] = None
    lesson_days: list[DayOfWeek] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_create_mode(self):
        uses_schedule_create_flow = any(
            [
                self.language,
                self.program_id is not None,
                self.branch_id is not None,
                self.classroom_id is not None,
                self.time_start is not None,
                bool(self.lesson_days),
            ]
        )

        if uses_schedule_create_flow:
            missing_fields = []
            if not self.language:
                missing_fields.append("language")
            if self.program_id is None:
                missing_fields.append("program_id")
            if self.teacher_id is None:
                missing_fields.append("teacher_id")
            if self.branch_id is None:
                missing_fields.append("branch_id")
            if self.classroom_id is None:
                missing_fields.append("classroom_id")
            if self.time_start is None:
                missing_fields.append("time_start")
            if not self.lesson_days:
                missing_fields.append("lesson_days")
            if missing_fields:
                missing = ", ".join(missing_fields)
                raise ValueError(f"Для создания группы через расписание обязательны поля: {missing}")
            return self

        if not self.name or self.course_id is None:
            raise ValueError("Укажите название группы и курс")
        return self


class GroupOut(BaseModel):
    id: int
    name: str
    course_id: int
    teacher_id: Optional[int] = None
    language: Optional[str] = None
    program_name: Optional[str] = None
    status: GroupStatus
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StudentGroupCreate(BaseModel):
    group_id: int
    student_name: str
    student_phone: Optional[str] = None
    student_email: Optional[str] = None
    student_type: str  # child, adult, preschool
    form_id: Optional[int] = None


class StudentGroupOut(BaseModel):
    id: int
    group_id: int
    student_name: str
    student_phone: Optional[str] = None
    student_email: Optional[str] = None
    student_type: str
    form_id: Optional[int] = None
    enrolled_at: Optional[datetime] = None
    is_active: bool

    model_config = {"from_attributes": True}
