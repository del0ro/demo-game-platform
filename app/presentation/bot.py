"""Жизненный цикл Telegram-бота.

Модуль содержит публичные точки входа для запуска и корректной остановки
polling-бота. Детали сборки диспетчера и вспомогательные функции завершения
вынесены отдельно, чтобы сам код оркестрации оставался компактным и читаемым.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher

from app.core.config import get_settings
from app.core.logging import get_logger
from app.presentation.bot_helpers import (
    build_bot,
    build_dispatcher,
    cancel_tasks,
    close_bot,
    close_dispatcher,
    stop_polling,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker as AsyncSessionMaker

logger = get_logger(__name__)

_bot: Bot | None = None
_dispatcher: Dispatcher | None = None


async def run_bot(
    sessionmaker: "AsyncSessionMaker[AsyncSession]",
    shutdown_event: asyncio.Event | None = None,
) -> None:
    """Запускает polling-бота и при необходимости отслеживает событие остановки."""
    global _bot, _dispatcher
    settings = get_settings()
    if not settings.bot_token:
        logger.warning("BOT_TOKEN is empty; bot will not start")
        return

    _bot = build_bot(settings.bot_token)
    _dispatcher = build_dispatcher(sessionmaker=sessionmaker, shutdown_event=shutdown_event)

    if shutdown_event is None:
        await _dispatcher.start_polling(
            _bot,
            allowed_updates=_dispatcher.resolve_used_update_types(),
        )
        return

    polling_task = asyncio.create_task(
        _dispatcher.start_polling(
            _bot,
            allowed_updates=_dispatcher.resolve_used_update_types(),
        ),
    )
    shutdown_task = asyncio.create_task(shutdown_event.wait())

    done, pending = await asyncio.wait(
        [polling_task, shutdown_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    if shutdown_event.is_set():
        logger.info("Shutdown event set, stopping polling...")
        await stop_polling(_dispatcher, polling_task)

    await cancel_tasks(pending)

    logger.info("run_bot completed")


async def shutdown_bot() -> None:
    """Закрывает ресурсы aiogram и очищает глобальные ссылки приложения."""
    global _bot, _dispatcher
    logger.info("Shutting down bot...")
    await close_dispatcher(_dispatcher)
    await close_bot(_bot)
    _bot = None
    _dispatcher = None
    logger.info("Bot shutdown complete")
