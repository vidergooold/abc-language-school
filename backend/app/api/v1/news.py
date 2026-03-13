from typing import List
from fastapi import APIRouter

router = APIRouter(prefix="/news", tags=["News"])


@router.get("/")
async def get_news():
    return []
