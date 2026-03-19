# backend/app/schemas/user.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class UserStatsResponse(BaseModel):
    strength: Dict[str, Any]
    agility: Dict[str, Any]
    intelligence: Dict[str, Any]
    spirit: Dict[str, Any]
    vitality: Dict[str, Any]
    resources: Dict[str, str]
    status: Dict[str, Any]

class UserPublic(BaseModel):
    vk_id: int
    username: str
    avatar: Optional[str] = ""
    character_class: str
    level: int
    experience: int
    gold: int
    location: str
    stats: Optional[UserStatsResponse] = None
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    location: Optional[str] = None
    # В реальном проекте обновление статов должно быть защищено