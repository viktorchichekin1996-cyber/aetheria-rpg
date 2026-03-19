# backend/app/api/player.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services import player_service
from app.schemas.user import UserPublic, UserStatsResponse
from app.models.users import User

router = APIRouter(prefix="/player", tags=["Players"])

@router.get("/{vk_id}", response_model=UserPublic)
async def get_player(vk_id: int, db: Session = Depends(get_db)):
    """
    Получить данные игрока по VK ID.
    Включает базовую информацию и уровень.
    """
    user = player_service.get_player_by_vk_id(db, vk_id)
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")
    return user

@router.get("/{vk_id}/stats")
async def get_player_stats(vk_id: int, db: Session = Depends(get_db)):
    """
    Получить подробные характеристики игрока с расчетом модификаторов.
    Возвращает базовые статы, модификаторы и текущие ресурсы.
    """
    try:
        data = player_service.get_player_full_data(db, vk_id)
        return {
            "success": True,
            "data": {
                "vk_id": data["user"].vk_id,
                "username": data["user"].username,
                "stats": data["calculated_stats"]
            }
        }
    except HTTPException:
        raise

@router.post("/{vk_id}/location")
async def set_player_location(vk_id: int, location: str, db: Session = Depends(get_db)):
    """Обновить локацию игрока (используется при перемещении)"""
    user = player_service.update_player_location(db, vk_id, location)
    return {
        "success": True,
        "message": f"Location updated to {location}",
        "data": {"location": user.location}
    }