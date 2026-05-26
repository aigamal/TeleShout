from __future__ import annotations
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    app_name: str = "Telegram Notification API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/telegram_notifier"

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-in-production"
    encryption_key: str = "change-me-in-production-must-be-32-bytes-long-"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: List[str] = ["*"]

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    default_message_rate_per_minute: int = 5
    default_message_rate_per_day: int = 100
    default_max_bots: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
