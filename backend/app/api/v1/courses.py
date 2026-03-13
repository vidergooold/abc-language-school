from typing import List
from fastapi import APIRouter

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("/")
async def get_courses():
    return []
