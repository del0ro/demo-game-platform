"""Промежуточный обработчик, отклоняющий новые запросы во время мягкой остановки."""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

from app.presentation.middlewares.utils import answer_event, cast_event_to_update

_DRAINING_TEXT = "Приложение завершает работу. Попробуйте снова через несколько секунд."


class DrainingMiddleware(BaseMiddleware):
    """Не даёт начинать новые операции, если приложение входит в режим остановки."""

    def __init__(self, shutdown_event: asyncio.Event) -> None:
        super().__init__()
        self._shutdown_event = shutdown_event

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if self._shutdown_event.is_set():
            await answer_event(event, _DRAINING_TEXT)
            return None

        return await handler(cast_event_to_update(event), data)
