# backend/app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from typing import Dict, Any

from app.database import get_db
from app.models.users import User
from app.schemas.auth import TokenResponse
from app.utils.vk_auth import validate_vk_sign
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authorization"])

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
async def vk_login(
    vk_id: int = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    sign: str = Form(...),
    auth_date: int = Form(...),
    db: Session = Depends(get_db),
    # Принимаем все остальные параметры через Query, чтобы передать их в валидатор
    **kwargs
):
    """
    Авторизация через VK Mini Apps.
    Клиент отправляет данные формы, полученные через VK Bridge.
    """
    # Собираем все параметры запроса для проверки подписи
    query_params = {
        "vk_id": str(vk_id),
        "first_name": first_name,
        "last_name": last_name,
        "sign": sign,
        "auth_date": str(auth_date),
        **{k: str(v) for k, v in kwargs.items()}
    }

    # 1. Проверка подписи
    user_data = validate_vk_sign(query_params)
    
    # Дополнительная проверка актульности данных (защита от replay атак)
    # Данные не должны быть старше 24 часов
    if datetime.utcnow().timestamp() - auth_date > 86400:
        raise HTTPException(status_code=401, detail="Время жизни данных истекло")

    vk_id_int = int(user_data['vk_id'])

    # 2. Поиск или создание пользователя
    user = db.query(User).filter(User.vk_id == vk_id_int).first()
    is_new_user = False

    if not user:
        is_new_user = True
        user = User(
            vk_id=vk_id_int,
            username=f"{user_data.get('first_name', 'Игрок')} {user_data.get('last_name', '')}".strip(),
            avatar=user_data.get('photo', ''), # VK может присылать photo или avatar
            # Инициализация базовых статов (будут перезаписаны при выборе класса)
            strength=10, agility=10, intelligence=10, spirit=10, vitality=10,
            hp=150, max_hp=150, mana=50, max_mana=50, stamina=150, max_stamina=150
        )
        db.add(user)
    else:
        # Обновление имени и аватара при каждом входе
        user.username = f"{user_data.get('first_name', 'Игрок')} {user_data.get('last_name', '')}".strip()
        if user_data.get('photo'):
            user.avatar = user_data.get('photo')
        user.last_login = datetime.utcnow()

    db.commit()
    db.refresh(user)

    # 3. Генерация JWT токена
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.vk_id)}, 
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=access_token,
        vk_id=user.vk_id,
        is_new_user=is_new_user
    )