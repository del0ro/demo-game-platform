"""Управление подключением к БД и создание сессий для demo."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database.base import Base

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker as AsyncSessionMaker

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_sessionmaker: AsyncSessionMaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Возвращает или создаёт глобальный engine с ленивой инициализацией."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
        )
    return _engine


def get_sessionmaker() -> AsyncSessionMaker[AsyncSession]:
    """Возвращает или создаёт `async_sessionmaker` для открытия сессий."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _sessionmaker


async def create_database() -> None:
    """Создаёт таблицы в БД. Импорт моделей — внутри, чтобы избежать циклов."""
    from app.modules.game.models import (  # noqa: F401
        GameHiloDetailsModel,
        GameSessionModel,
        GameSettingsModel,
    )
    from app.modules.identity.models import UserModel  # noqa: F401
    from app.modules.wallet.models import (  # noqa: F401
        BalanceModel,
        DepositInvoiceModel,
        TransactionModel,
    )

    logger.info("Creating database tables...")
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_engine() -> None:
    """Закрывает engine при завершении приложения."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None
        logger.info("Database engine disposed")
