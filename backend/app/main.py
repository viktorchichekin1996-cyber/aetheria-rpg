# backend/app/main.py
# ... импорты ...

from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime
from app.api import player

from .config import settings
from .database import engine, Base, get_db
from .models.users import User

# ... (код создания таблиц и CORS остается прежним) ...

app = FastAPI(
    title=settings.APP_NAME,
    description="Текстовая RPG игра для VK Mini Apps",
    version="0.2.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security Schemes ---
security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Зависимость для получения текущего пользователя из JWT токена"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        vk_id: str = payload.get("sub")
        if vk_id is None:
            raise HTTPException(status_code=401, detail="Неверный токен")
        
        user = db.query(User).filter(User.vk_id == int(vk_id)).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Неверный или истекший токен")

# --- Endpoints ---

@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": f"{settings.API_V1_PREFIX}/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Подключаем роутер авторизации
from app.api import auth
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Пример защищенного эндпоинта
@app.get(f"{settings.API_V1_PREFIX}/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить данные текущего авторизованного пользователя"""
    return {
        "vk_id": current_user.vk_id,
        "username": current_user.username,
        "level": current_user.level,
        "class": current_user.character_class
    }

app.include_router(player.router, prefix=settings.API_V1_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)