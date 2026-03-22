# backend/app/schemas/class_selection.py
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ClassInfoResponse(BaseModel):
    id: str
    name: str
    description: str
    base_stats: Dict[str, int]

class ClassListResponse(BaseModel):
    classes: list[ClassInfoResponse]

class ClassSelectionRequest(BaseModel):
    class_id: str

class ClassSelectionResponse(BaseModel):
    success: bool
    message: str
    character_class: str
    stats: Optional[Dict[str, Any]] = None