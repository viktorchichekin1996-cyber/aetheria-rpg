# backend/app/main.py
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .config import settings
from .database import engine, Base

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения (стартап/shutdown)"""
    logger.info("🚀 Запуск приложения Aetheria RPG...")
    # В продакшене миграции запускаются через Alembic, здесь только для dev проверки
    if settings.DEBUG:
        logger.info("📦 Проверка таблиц БД (Dev mode)...")
        # Base.metadata.create_all(bind=engine) # Раскомментировать только для первого запуска без Alembic
    yield
    logger.info("🛑 Остановка приложения...")

# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Текстовая RPG игра для VK Mini Apps с AI-повествованием",
    version="0.2.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)

# --- Настройка CORS для VK Mini Apps ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # https://vk.com, https://m.vk.com
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware: Логирование времени выполнения запросов ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# --- Global Exception Handlers ---

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Глобальный обработчик непредвиденных ошибок"""
    logger.error(f"Critical Error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Внутренняя ошибка сервера. Попробуйте позже.",
                "details": str(exc) if settings.DEBUG else None
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации данных (Pydantic)"""
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Ошибка валидации данных",
                "details": exc.errors()
            }
        }
    )

# --- Basic Endpoints ---

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": "0.2.0",
        "status": "running",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса (для Docker/K8s)"""
    return {
        "status": "healthy",
        "database": "connected", # Требуется реальная проверка подключения
        "redis": "connected"
    }

@app.get(f"{settings.API_V1_PREFIX}/ping")
async def ping():
    """Ping endpoint для API v1"""
    return {"message": "pong", "api_version": "v1"}

# Запуск через uvicorn выполняется командой в Dockerfile или CLI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )