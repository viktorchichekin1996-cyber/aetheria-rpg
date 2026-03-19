# backend/app/services/player_service.py
from sqlalchemy.orm import Session
from typing import Optional  # <-- Добавлен импорт Optional
from fastapi import HTTPException, status
from datetime import datetime

from app.models.users import User
from app.schemas.user import UserUpdate


def get_player_by_vk_id(db: Session, vk_id: int) -> Optional[User]:
    """
    Получить игрока по VK ID.
    Возвращает объект User или None, если пользователь не найден.
    """
    return db.query(User).filter(User.vk_id == vk_id).first()


def create_or_update_player(db: Session, vk_id: int, username: str, avatar: str = "") -> User:
    """
    Создать нового игрока или обновить данные существующего при входе.
    """
    user = get_player_by_vk_id(db, vk_id)
    
    if not user:
        # Создание нового пользователя с базовыми статами
        # Значения по умолчанию берутся из модели SQLAlchemy
        user = User(
            vk_id=vk_id,
            username=username,
            avatar=avatar
        )
        db.add(user)
    else:
        # Обновление имени и аватара (синхронизация с VK)
        user.username = username
        if avatar:
            user.avatar = avatar
        user.last_login = datetime.utcnow()
    
    db.commit()
    db.refresh(user)
    return user


def get_player_full_data(db: Session, vk_id: int) -> dict:
    """
    Получить полные данные игрока с рассчитанными характеристиками.
    Вызывает метод get_full_stats() модели User.
    """
    user = get_player_by_vk_id(db, vk_id)
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")
    
    return {
        "user": user,
        "calculated_stats": user.get_full_stats()
    }


def update_player_location(db: Session, vk_id: int, new_location: str) -> User:
    """
    Обновить локацию игрока.
    """
    user = get_player_by_vk_id(db, vk_id)
    if not user:
        raise HTTPException(status_code=404, detail="Player not found")
    
    user.location = new_location
    db.commit()
    db.refresh(user)
    return user