from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.forms import (
    ChildForm,
    AdultForm,
    PreschoolForm,
    TeacherForm,
    TestingForm,
    FeedbackForm,
)
from app.schemas.forms import (
    ChildFormCreate,
    AdultFormCreate,
    PreschoolFormCreate,
    TeacherFormCreate,
    TestingFormCreate,
    FeedbackFormCreate,
    FormResponse,
)

router = APIRouter(prefix="/forms", tags=["Forms"])


@router.post("/child", response_model=FormResponse)
async def create_child_form(
    data: ChildFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = ChildForm(
        fio=data.fio,
        age=data.age,
        birthdate=data.birthdate,
        school=data.school,
        grade=data.grade,
        shift=data.shift,
        extended=data.extended,
        parent_fio=data.parentFio,
        parent_work=data.parentWork,
        phone=data.phone,
        address=data.address,
        email=data.email,
        studied_before=data.studiedBefore,
        where_how=data.whereHow,
        notes=data.notes,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/adult", response_model=FormResponse)
async def create_adult_form(
    data: AdultFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = AdultForm(
        fio=data.fio,
        age=data.age,
        birthdate=data.birthdate,
        work=data.work,
        phone=data.phone,
        address=data.address,
        email=data.email,
        studied_before=data.studiedBefore,
        where_how=data.whereHow,
        notes=data.notes,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/preschool", response_model=FormResponse)
async def create_preschool_form(
    data: PreschoolFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = PreschoolForm(
        fio=data.fio,
        age=data.age,
        birthdate=data.birthdate,
        kindergarten=data.kindergarten,
        group=data.group,
        parent_fio=data.parentFio,
        parent_work=data.parentWork,
        phone=data.phone,
        address=data.address,
        email=data.email,
        pickup_time=data.pickupTime,
        notes=data.notes,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/teacher", response_model=FormResponse)
async def create_teacher_form(
    data: TeacherFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = TeacherForm(
        fio=data.fio,
        birth_info=data.birthInfo,
        marital_status=data.maritalStatus,
        education=data.education,
        work_experience=data.workExperience,
        language_level=data.languageLevel,
        skills=data.skills,
        qualities=data.qualities,
        address=data.address,
        phone=data.phone,
        email=data.email,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/testing", response_model=FormResponse)
async def create_testing_form(
    data: TestingFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = TestingForm(
        fio=data.fio,
        age=data.age,
        school=data.school,
        grade=data.grade,
        phone=data.phone,
        test_level=data.testLevel,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


@router.post("/feedback", response_model=FormResponse)
async def create_feedback_form(
    data: FeedbackFormCreate,
    db: AsyncSession = Depends(get_db),
):
    form = FeedbackForm(
        name=data.name,
        phone=data.phone,
        email=data.email,
        message=data.message,
    )
    db.add(form)
    await db.commit()
    await db.refresh(form)
    return form


# GET endpoints to retrieve submitted forms
@router.get("/")
async def get_all_forms(db: AsyncSession = Depends(get_db)):
    """Get all forms grouped by type"""
    child_forms = (await db.execute(select(ChildForm))).scalars().all()
    adult_forms = (await db.execute(select(AdultForm))).scalars().all()
    preschool_forms = (await db.execute(select(PreschoolForm))).scalars().all()
    teacher_forms = (await db.execute(select(TeacherForm))).scalars().all()
    testing_forms = (await db.execute(select(TestingForm))).scalars().all()
    feedback_forms = (await db.execute(select(FeedbackForm))).scalars().all()
    
    return {
        "child": child_forms,
        "adult": adult_forms,
        "preschool": preschool_forms,
        "teacher": teacher_forms,
        "testing": testing_forms,
        "feedback": feedback_forms
    }
