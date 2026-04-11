from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.document import DocumentCategory


class DocumentOut(BaseModel):
    id:          int
    title:       str
    description: Optional[str] = None
    file_url:    str
    category:    DocumentCategory
    user_id:     Optional[int] = None
    created_at:  datetime

    model_config = {"from_attributes": True}


class DocumentCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    file_url:    str
    category:    DocumentCategory = DocumentCategory.other
    user_id:     Optional[int] = None


class DocumentUpdate(BaseModel):
    title:       Optional[str] = None
    description: Optional[str] = None
    file_url:    Optional[str] = None
    category:    Optional[DocumentCategory] = None
    is_active:   Optional[bool] = None
