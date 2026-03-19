# backend/app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    vk_id: int
    is_new_user: bool

class UserData(BaseModel):
    vk_id: int
    first_name: str
    last_name: str
    avatar: Optional[str] = None