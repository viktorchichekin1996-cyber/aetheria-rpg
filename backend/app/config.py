# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Настройки приложения с валидацией типов"""
    
    # Application
    APP_NAME: str = "Aetheria RPG"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-prod"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    
    # AI (Inference API) - Важно: модель обновлена
    INFERENCE_API_KEY: str
    INFERENCE_API_BASE_URL: str = "https://api.inference.net/v1"
    INFERENCE_MODEL: str = "google/gemma-3-27b-instruct"
    INFERENCE_MAX_TOKENS: int = 250
    INFERENCE_TEMPERATURE: float = 0.7
    INFERENCE_TIMEOUT: float = 3.0
    
    # VK Mini Apps
    VK_APP_ID: str
    VK_CLIENT_SECRET: str
    
    # Security
    JWT_SECRET_KEY: str = "dev-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS: Добавляем домены VK для Mini Apps
    ALLOWED_ORIGINS: str = "https://vk.com,https://m.vk.com,http://localhost:3000"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Парсит строку origins в список"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env.dev"  # По умолчанию dev окружение
        case_sensitive = True


# Глобальный экземпляр настроек
settings = Settings()