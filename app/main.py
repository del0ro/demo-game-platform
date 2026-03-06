"""Composition root demo-приложения.

Модуль отвечает за запуск runtime:
- настраивает логирование;
- инициализирует БД;
- запускает восстановительную проверку при старте;
- поднимает Telegram-бота;
- координирует graceful shutdown.
"""

from __future__ import annotations

import asyncio
import signal
import sys
from typing import Any

from app.core import get_settings, logger, setup_logging
from app.core.database import close_engine, create_database, get_sessionmaker
from app.core.recovery import run_startup_recovery
from app.presentation.bot import run_bot, shutdown_bot

_shutdown_event: asyncio.Event | None = None


def _signal_handler_sync(signum: int, frame: Any) -> None:
    """Обрабатывает системный сигнал и инициирует остановку приложения."""
    try:
        name = signal.Signals(signum).name
    except ValueError:
        name = str(signum)
    logger.info("Получен сигнал %s, запуск graceful shutdown...", name)
    if _shutdown_event is not None:
        _shutdown_event.set()
    else:
        logger.warning("Shutdown event не инициализирован")
        sys.exit(1)


async def main() -> None:
    """Запускает приложение и управляет его жизненным циклом."""
    global _shutdown_event

    setup_logging()
    settings = get_settings()

    _shutdown_event = asyncio.Event()

    if sys.platform != "win32":
        try:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, lambda: _shutdown_event.set())
            loop.add_signal_handler(signal.SIGINT, lambda: _shutdown_event.set())
        except (NotImplementedError, RuntimeError):
            signal.signal(signal.SIGTERM, _signal_handler_sync)
            signal.signal(signal.SIGINT, _signal_handler_sync)
    else:
        signal.signal(signal.SIGINT, _signal_handler_sync)

    await create_database()
    sessionmaker = get_sessionmaker()

    await run_startup_recovery(sessionmaker)

    try:
        logger.info("Запуск бота...")
        bot_task = asyncio.create_task(run_bot(sessionmaker, _shutdown_event))
        shutdown_wait = asyncio.create_task(_shutdown_event.wait())

        done, pending = await asyncio.wait(
            [bot_task, shutdown_wait],
            return_when=asyncio.FIRST_COMPLETED,
        )

        if _shutdown_event.is_set() or shutdown_wait in done:
            logger.info("Запрос на остановку, останавливаем бота...")
            if not _shutdown_event.is_set():
                _shutdown_event.set()
            try:
                await asyncio.wait_for(
                    bot_task,
                    timeout=settings.shutdown_timeout_seconds,
                )
            except asyncio.TimeoutError:
                logger.warning("Бот не завершился сам вовремя, принудительная отмена...")
                if not bot_task.done():
                    bot_task.cancel()
                    try:
                        await bot_task
                    except asyncio.CancelledError:
                        pass

            try:
                await asyncio.wait_for(
                    shutdown_bot(),
                    timeout=settings.shutdown_timeout_seconds,
                )
            except asyncio.TimeoutError:
                logger.warning("Таймаут при остановке бота")
        else:
            if bot_task in done:
                try:
                    await bot_task
                except Exception as e:
                    logger.exception("Ошибка задачи бота: %s", e)
                    raise

        for t in pending:
            if not t.done():
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass

        logger.info("Graceful shutdown завершён")
    except asyncio.CancelledError:
        logger.info("Главная задача отменена")
    finally:
        logger.info("Закрытие подключений к БД...")
        try:
            await asyncio.wait_for(close_engine(), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Таймаут при закрытии engine")
        logger.info("Завершение приложения")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановка по Ctrl+C")
        sys.exit(0)
    except Exception as e:
        logger.exception("Критическая ошибка: %s", e)
        sys.exit(1)
