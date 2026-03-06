"""Вспомогательные функции для жизненного цикла Telegram-бота."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.core.logging import get_logger
from app.presentation.handlers import common_router, game_router, wallet_router
from app.presentation.middlewares import (
    DatabaseMiddleware,
    DrainingMiddleware,
    ErrorHandlingMiddleware,
    ThrottleMiddleware,
    UserLockMiddleware,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker as AsyncSessionMaker

logger = get_logger(__name__)


def build_bot(bot_token: str) -> Bot:
    """Создаёт экземпляр `Bot` с базовыми настройками."""
    return Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher(
    sessionmaker: "AsyncSessionMaker[AsyncSession]",
    shutdown_event: asyncio.Event | None,
) -> Dispatcher:
    """Собирает dispatcher, middleware и роутеры."""
    dispatcher = Dispatcher()
    dispatcher.update.middleware(ErrorHandlingMiddleware())
    if shutdown_event is not None:
        dispatcher.update.middleware(DrainingMiddleware(shutdown_event))
    dispatcher.update.middleware(ThrottleMiddleware())
    dispatcher.update.middleware(UserLockMiddleware())
    dispatcher.update.middleware(DatabaseMiddleware(sessionmaker))
    dispatcher.include_router(common_router)
    dispatcher.include_router(game_router)
    dispatcher.include_router(wallet_router)
    return dispatcher


async def stop_polling(dispatcher: Dispatcher, polling_task: asyncio.Task[None]) -> None:
    """Останавливает polling и дожидается завершения фоновой задачи."""
    if polling_task.done():
        return

    try:
        await asyncio.wait_for(dispatcher.stop_polling(), timeout=5.0)
    except asyncio.TimeoutError:
        logger.warning("Timeout stopping polling")

    polling_task.cancel()
    try:
        await asyncio.wait_for(polling_task, timeout=5.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        pass


async def cancel_tasks(tasks: set[asyncio.Task[Any]]) -> None:
    """Отменяет фоновые задачи и дожидается их завершения."""
    for task in tasks:
        if task.done():
            continue
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=5.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


async def close_dispatcher(dispatcher: Dispatcher | None) -> None:
    """Закрывает FSM storage dispatcher-а."""
    if dispatcher is None:
        return

    try:
        await asyncio.wait_for(dispatcher.fsm.storage.close(), timeout=5.0)
    except (asyncio.TimeoutError, Exception) as exc:
        logger.warning("Error closing dispatcher storage: %s", exc)


async def close_bot(bot: Bot | None) -> None:
    """Закрывает HTTP-сессию Telegram-бота."""
    if bot is None:
        return

    try:
        await asyncio.wait_for(bot.session.close(), timeout=5.0)
    except (asyncio.TimeoutError, Exception) as exc:
        logger.warning("Error closing bot session: %s", exc)
