# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB  # Явный импорт для типов
from .config import settings

# Создание движка БД
# pool_pre_ping=True проверяет соединение перед использованием
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG  # Логирование SQL запросов в режиме отладки
)

# Сессия БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """
    Dependency для получения сессии БД в FastAPI endpoints.
    Гарантирует закрытие сессии после запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()