# backend/app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .models import users, items, combats, stamina_logs # Импортируем модели для регистрации метаданных

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Запуск приложения Aetheria RPG...")
    # В продакшене миграции запускаются через Alembic
    yield
    logger.info("🛑 Остановка приложения...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Текстовая RPG игра для VK Mini Apps с AI-повествованием",
    version="0.2.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
from app.api import auth
from app.api import player
from app.api import classes # Новый роутер классов

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(player.router, prefix=settings.API_V1_PREFIX)
app.include_router(classes.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "status": "running", "docs": f"{settings.API_V1_PREFIX}/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)