# backend/app/api/classes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.database import get_db
from app.models.users import User
from app.api.auth import get_current_user # Теперь этот импорт сработает
from app.utils.class_stats import get_all_classes, get_class_info, apply_class_bonuses

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_classes():
    """Получить список всех доступных классов."""
    return get_all_classes()

@router.get("/{class_id}", response_model=Dict[str, Any])
async def get_class_details(class_id: str):
    """Получить подробную информацию о конкретном классе."""
    class_data = get_class_info(class_id)
    if not class_data:
        raise HTTPException(status_code=404, detail="Class not found")
    return class_data

@router.post("/select")
async def select_class(
    class_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Выбрать класс для текущего пользователя."""
    # Проверка: класс уже выбран?
    if current_user.character_class and current_user.character_class != 'warrior':
         # Если пользователь явно сменил класс ранее (не дефолтный воин)
         # Для упрощения считаем, что если класс != 'warrior', то он уже выбран.
         # В реальной системе лучше иметь флаг is_class_locked.
         if current_user.character_class != class_id: # Если пытается сменить на другой
             raise HTTPException(status_code=400, detail="Character class already selected and cannot be changed.")

    if class_id not in [c['id'] for c in get_all_classes()]:
        raise HTTPException(status_code=400, detail="Invalid class ID")

    # Применяем бонусы
    if apply_class_bonuses(current_user, class_id):
        current_user.character_class = class_id
        db.commit()
        db.refresh(current_user)
        return {"success": True, "message": f"Class {class_id} selected!", "stats": current_user.get_full_stats()}
    else:
        raise HTTPException(status_code=500, detail="Failed to apply class bonuses")