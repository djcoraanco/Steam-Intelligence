from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    APP_ENV: str = "development"
    APP_NAME: str = "Steam Intelligence"
    APP_URL: str = "http://localhost:3000"
    API_URL: str = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"
    
    # Secrets
    APP_SECRET_KEY: str = "CHANGE_ME_SECRET_KEY_AT_LEAST_32_CHARS"
    JWT_SECRET: str = "CHANGE_ME_JWT_SECRET_AT_LEAST_32_CHARS"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./steam_intelligence.db",
        description="Postgres or SQLite database connection URL"
    )
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # Steam API
    STEAM_WEB_API_KEY: Optional[str] = None
    STEAM_API_BASE_URL: str = "https://api.steampowered.com"
    STEAM_STORE_BASE_URL: str = "https://store.steampowered.com"
    STEAM_STORE_COUNTRY: str = "us"
    STEAM_STORE_LANGUAGE: str = "english"
    
    # Third-party integrations
    STEAMSPY_ENABLED: bool = False
    IGDB_ENABLED: bool = False
    IGDB_CLIENT_ID: Optional[str] = None
    IGDB_CLIENT_SECRET: Optional[str] = None
    ITCH_ENABLED: bool = False
    ITCH_API_KEY: Optional[str] = None
    EPIC_ENABLED: bool = False
    GOG_ENABLED: bool = False
    PCGAMINGWIKI_ENABLED: bool = False
    
    # Storage
    EXPORT_STORAGE_PATH: str = "./exports"
    EXPORT_RETENTION_DAYS: int = 30
    LOG_LEVEL: str = "INFO"



settings = Settings()
