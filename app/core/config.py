from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Основные настройки приложения
    PROJECT_NAME: str = "Task Management API"
    PROJECT_VERSION: str = "1.0.0"
    PROJECT_DESCRIPTION: str = "API for managing tasks with translation support"
    DEBUG: bool = True

    # Настройки сервера
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # Настройки базы данных
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/dbname"

    # Настройки безопасности
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS настройки
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000"
    ]

    # Настройки переводчика
    TRANSLATION_API_KEY: str = "your-translation-api-key"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()