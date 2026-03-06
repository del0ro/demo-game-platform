"""Конфигурация demo-приложения.

Настройки читаются из переменных окружения и файла `.env` через
`pydantic-settings`. Модуль используется как единая точка доступа к
конфигурации приложения и кэширует загруженный экземпляр `Settings`.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Типизированные настройки приложения."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    bot_token: str = ""
    admin_user_ids: list[int] = []

    # Optional channel IDs (None = disabled)
    games_channel_id: int | None = None
    wallets_channel_id: int | None = None
    admin_channel_id: int | None = None

    # Defaults for new users (use Money() / Decimal in use cases when needed)
    default_balance: str = "0"
    default_bet_amount: str = "0.1"

    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/demo"

    # Cryptopay
    cryptopay_token: str = ""
    cryptopay_testnet: bool = True

    # App
    debug: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_dir: str = "logs"
    shutdown_timeout_seconds: float = 15.0
    throttle_window_seconds: float = 10.0
    throttle_limit_per_user: int = 15
    user_action_lock_ttl_seconds: float = 30.0

    @field_validator("admin_user_ids", mode="before")
    @classmethod
    def parse_admin_user_ids(cls, v: object) -> list[int]:
        if isinstance(v, list):
            return [int(x) for x in v]
        if not v or not str(v).strip():
            return []
        return [int(x.strip()) for x in str(v).split(",") if x.strip()]

    @field_validator("games_channel_id", "wallets_channel_id", "admin_channel_id", mode="before")
    @classmethod
    def parse_channel_id(cls, v: object) -> int | None:
        if v is None:
            return None
        s = str(v).strip()
        if not s:
            return None
        return int(s)


@lru_cache
def get_settings() -> Settings:
    """Возвращает кэшированный экземпляр `Settings`."""
    return Settings()
